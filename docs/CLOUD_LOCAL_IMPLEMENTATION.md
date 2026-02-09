# Cloud-Local Orchestration: Implementation Guide

**Purpose**: Practical, production-ready code patterns for hybrid compute routing.

## Quick Start (5 Minutes)

**Decision Heuristic**:
```python
from happygene.orchestration import SimulationFacade

config = ConfigSchema.from_yaml("simulation.yaml")

# Automatically routes based on estimated runtime
facade = SimulationFacade(config, backend="auto")
results = facade.run()  # Local? Cloud? You don't need to know.
```

**That's it.** User sees results. Backend is transparent.

---

## The Three Backends

### Backend 1: Local (Default, <1 hour)

```python
# engine/orchestration/backends.py
class LocalBackend:
    """Run on macOS with 8 cores."""

    def submit(self, config: ConfigSchema) -> JobHandle:
        """Spawn subprocess, return handle."""
        self.job_id = str(uuid.uuid4())
        self.process = subprocess.Popen(
            [sys.executable, "-m", "happygene.cli", "run",
             "--config", config.model_dump_json(),
             "--output", self._output_path(self.job_id)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return JobHandle(job_id=self.job_id, backend="local")

    def poll(self, job_id: str) -> Optional[PopulationOutcome]:
        """Check if done, return result if ready."""
        if self.process.poll() is not None:  # Process finished
            result_path = self._output_path(job_id)
            with h5py.File(result_path, "r") as f:
                return PopulationOutcome.from_hdf5(f)
        return None

    def abort(self, job_id: str):
        """Kill process if needed."""
        self.process.terminate()
        self.process.wait(timeout=5)
```

**Advantages**:
- Zero cost (electricity ~$0.01)
- Fast (Apple Silicon native, 12 sec per 1000 simulations)
- No network latency

**Constraints**:
- Single machine (8 cores, 16 GB RAM)
- ~10 hours max execution time (before user timeout)

### Backend 2: Cloud (1-24 hours)

```python
# engine/orchestration/backends.py
class AzureBatchBackend:
    """Azure Batch for embarrassingly parallel workloads."""

    def __init__(self, account_name: str, account_key: str):
        self.batch_client = batch.BatchServiceClient(
            credentials.SharedKeyCredentials(account_name, account_key),
            batch_url=f"https://{account_name}.eastus.batch.azure.com"
        )

    def submit(self, config: ConfigSchema) -> JobHandle:
        """Submit job to Batch, return handle."""
        job_id = str(uuid.uuid4())

        # Create job
        self.batch_client.job.add(
            batch.models.JobAddParameter(
                id=job_id,
                pool_info=batch.models.PoolInformation(pool_id="happygene-pool"),
                uses_task_dependencies=True
            )
        )

        # Create task (one task = one simulation)
        task = batch.models.TaskAddParameter(
            id="task-0",
            command_line=f"/bin/bash -c "python -m happygene.cli run {config.model_dump_json()}"",
            resource_files=[
                batch.models.ResourceFile(
                    http_url=self._docker_image_url(),  # Container image
                    file_path="docker_image.tar"
                )
            ],
            output_files=[
                batch.models.OutputFile(
                    pattern="results.h5",
                    destination=batch.models.OutputFileDestination(
                        container=batch.models.OutputFileBlobContainerDestination(
                            container_url=self._results_container_url()
                        )
                    )
                )
            ]
        )
        self.batch_client.task.add(job_id, task)

        return JobHandle(job_id=job_id, backend="cloud")

    def poll(self, job_id: str) -> Optional[PopulationOutcome]:
        """Check job status."""
        task = self.batch_client.task.get(job_id, "task-0")
        if task.state == batch.models.TaskState.completed:
            # Download result from blob storage
            result = self._download_from_blob(f"{job_id}/results.h5")
            return PopulationOutcome.from_hdf5(result)
        return None

    def abort(self, job_id: str):
        """Terminate job."""
        self.batch_client.job.terminate(job_id)
```

**Advantages**:
- Scales to 100+ parallel tasks
- Cheap with Spot VMs (80-90% discount)
- Ideal for parameter sweeps (1000 simulations)

**Constraints**:
- Network latency (upload config, download results)
- Preemption risk (Spot VMs interrupted at any time)
- Cold start overhead (Docker container startup)

### Backend 3: Hybrid (Smart Router)

```python
# engine/orchestration/router.py
class HybridRouter:
    """Route to local or cloud based on runtime estimate."""

    def __init__(self, local_backend: LocalBackend,
                 cloud_backend: AzureBatchBackend,
                 cache: ResultCache):
        self.local = local_backend
        self.cloud = cloud_backend
        self.cache = cache

    def route(self, config: ConfigSchema) -> Tuple[str, JobHandle]:
        """Decide: "local" or "cloud", then submit."""

        # 1. Check cache first
        cached_result = self.cache.lookup(config.config_hash)
        if cached_result:
            return ("cache", cached_result)

        # 2. Estimate runtime
        estimated_hours = self._estimate_runtime(config)

        # 3. Route based on estimate
        if estimated_hours < 1.0:
            backend = "local"
            handle = self.local.submit(config)
        elif estimated_hours < 10.0:
            # Ask user
            backend = config.orchestration.compute_backend or "auto"
            if backend == "auto":
                backend = "local"  # Default to local if unsure
            handle = (self.local if backend == "local" else self.cloud).submit(config)
        else:
            backend = "cloud"
            handle = self.cloud.submit(config)

        return (backend, handle)

    def _estimate_runtime(self, config: ConfigSchema) -> float:
        """Estimate hours from config parameters."""
        # Heuristic: population_size × time_per_cell × pathways
        time_per_cell = 0.0005  # 500 microseconds per cell simulation
        pathways = len(config.simulation.repair_pathways)
        total_seconds = (config.simulation.population_size *
                        time_per_cell * pathways)
        return total_seconds / 3600.0  # Convert to hours
```

---

## Cost Model: When Cloud Wins

**Example: 1000 independent simulations, 5 minutes each**

| Backend | Compute Time | Resource Cost | Notes |
|---------|---|---|---|
| **Local** | 10.4 hours | $0.12 | Apple Silicon, electricity |
| **Cloud (Spot)** | 6 minutes | $0.66 | 100 parallel cores, preemptible |

**Break-even Analysis**:
- Local electricity: ~$0.01 per simulation
- Cloud (Spot): ~$0.0006 per simulation (100 parallel)
- **Cloud wins** when: Execution time > 24 hours (parallelism exceeds cost overhead)

**Budget Guardrail**:
```python
# In orchestration config
max_cloud_spend_per_job: 5.0  # Abort if exceeds $5

# Check before submitting
estimated_cost = estimated_hours * HOURLY_RATE
if estimated_cost > max_cloud_spend_per_job:
    raise BudgetExceededError(f"Estimated ${estimated_cost}, max ${max_cloud_spend_per_job}")
```

---

## Containerization (Docker for Reproducibility)

**Dockerfile** (multi-stage, optimized):

```dockerfile
# Build stage: compile dependencies
FROM python:3.12-slim as builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gfortran libopenblas-dev

COPY pyproject.toml .
RUN pip install --user --no-cache-dir \
    --disable-pip-version-check \
    -e .[science]

# Runtime stage: minimal image
FROM python:3.12-slim
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY engine ./engine
COPY cli ./cli
COPY knowledge_graph ./knowledge_graph

# Health check
HEALTHCHECK --interval=30s --timeout=5s \
    CMD python -m happygene --version

ENTRYPOINT ["python", "-m", "happygene.cli"]
CMD ["--help"]
```

**Build & Push**:
```bash
# Build locally (test)
docker build -t happygene:latest .

# Tag for Azure Registry
docker tag happygene:latest acrsovereignty.azurecr.io/happygene:latest

# Login to Azure Container Registry
az acr login --name acrsovereignty

# Push
docker push acrsovereignty.azurecr.io/happygene:latest

# Verify
az acr repository list --name acrsovereignty
```

---

## Result Caching

**SQLite Cache Schema**:

```sql
CREATE TABLE simulation_results (
    config_hash TEXT PRIMARY KEY,
    git_commit TEXT NOT NULL,
    random_seed INTEGER,
    result_json TEXT NOT NULL,
    computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    execution_time_seconds FLOAT,
    backend TEXT,
    cost_dollars FLOAT
);

CREATE INDEX idx_git_commit ON simulation_results(git_commit);
CREATE INDEX idx_backend ON simulation_results(backend);
```

**Cache Operations**:

```python
# engine/orchestration/cache.py
class ResultCache:
    def __init__(self, db_path: str = "~/.happygene/cache.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.executescript(SCHEMA)

    def lookup(self, config_hash: str) -> Optional[PopulationOutcome]:
        """Fetch cached result if exists."""
        row = self.conn.execute(
            "SELECT result_json FROM simulation_results WHERE config_hash = ?",
            (config_hash,)
        ).fetchone()
        if row:
            return PopulationOutcome.model_validate_json(row[0])
        return None

    def store(self, config_hash: str, git_commit: str, seed: int,
              result: PopulationOutcome, backend: str, cost: float,
              elapsed_seconds: float):
        """Store result."""
        self.conn.execute(
            """INSERT INTO simulation_results
               (config_hash, git_commit, random_seed, result_json, backend, cost_dollars, execution_time_seconds)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (config_hash, git_commit, seed,
             result.model_dump_json(), backend, cost, elapsed_seconds)
        )
        self.conn.commit()

    def invalidate(self, older_than_days: int = 30):
        """Invalidate stale entries."""
        self.conn.execute(
            "DELETE FROM simulation_results WHERE datetime(computed_at) < datetime('now', ? || ' days')",
            (f"-{older_than_days}",)
        )
        self.conn.commit()
```

---

## Fault Tolerance & Retry

**Exponential Backoff with Jitter** (AWS best practice):

```python
# engine/orchestration/retry.py
def submit_with_retry(backend, config, max_attempts=3):
    """Submit with exponential backoff + jitter."""
    for attempt in range(max_attempts):
        try:
            return backend.submit(config)
        except (TimeoutError, ConnectionError) as e:
            if attempt == max_attempts - 1:
                raise  # Give up

            # Exponential backoff: 2^attempt * 100ms + jitter
            delay = (2 ** attempt) * 0.1 + random.uniform(0, 0.1)
            logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
            time.sleep(delay)

def fallback_to_local(job_id: str, config: ConfigSchema):
    """If cloud fails, retry locally (if fast enough)."""
    if config.orchestration.estimated_runtime < 1.0:
        logger.info(f"Cloud job {job_id} failed, falling back to local")
        return LocalBackend().submit(config)
    else:
        logger.error(f"Cloud job {job_id} failed, too large for local fallback")
        raise
```

---

## Monitoring Dashboard (Application Insights)

**Key Metrics to Track**:

```python
# engine/orchestration/telemetry.py
def log_job_complete(job_id: str, backend: str, duration_seconds: float,
                     cost_dollars: float, status: str):
    """Log job completion for dashboard."""
    properties = {
        'job_id': job_id,
        'backend': backend,
        'status': status,
        'duration_seconds': duration_seconds,
        'cost_dollars': cost_dollars
    }
    telemetry_client.track_event('job_completed', properties)

def log_cost_projection(estimated_total: float, current_spend: float, budget: float):
    """Track spending relative to budget."""
    properties = {
        'estimated_total': estimated_total,
        'current_spend': current_spend,
        'budget': budget,
        'percent_of_budget': (current_spend / budget) * 100
    }
    telemetry_client.track_event('cost_projection', properties)
```

**Kusto Query Examples**:

```kusto
// Daily cost breakdown
customEvents
| where name == 'job_completed'
| extend backend = tostring(customDimensions.backend),
         cost = todouble(customDimensions.cost_dollars)
| summarize TotalCost = sum(cost), JobCount = dcount(customDimensions.job_id)
  by bin(timestamp, 1d), backend
| render columnchart

// Average duration by backend
customEvents
| where name == 'job_completed'
| extend backend = tostring(customDimensions.backend),
         duration = todouble(customDimensions.duration_seconds)
| summarize AvgDuration = avg(duration), MaxDuration = max(duration), P95 = percentile(duration, 95)
  by backend
```

---

## Configuration Example

```yaml
# ~/.happygene/config.yaml
orchestration:
  backends:
    local:
      enabled: true
      max_cores: 8
      max_runtime_hours: 10

    cloud:
      enabled: true
      provider: "azure"
      batch_account: "happygenebatch"
      batch_account_key: "${AZURE_BATCH_KEY}"
      container_registry: "acrsovereignty.azurecr.io"
      spot_instances: true
      max_parallel_jobs: 100

  routing:
    threshold_local_hours: 1.0
    threshold_cloud_hours: 10.0
    ask_user_between: true
    default_backend: "auto"

  caching:
    enabled: true
    db_path: "~/.happygene/cache.db"
    invalidate_after_days: 30

  monitoring:
    enabled: true
    application_insights_key: "${APP_INSIGHTS_KEY}"
    log_every_job: true

  cost_control:
    max_spend_per_job: 5.0
    daily_budget_alert: 10.0
    hourly_rate: 0.25
```

---

## Checklist: Before First Cloud Deployment

- [ ] Azure Batch account created
- [ ] Spot VM pool configured (100 nodes, auto-scale)
- [ ] Docker image built and pushed to ACR
- [ ] Cost budget alert set ($50/month)
- [ ] Application Insights monitoring enabled
- [ ] SQLite cache initialized locally
- [ ] Retry logic tested (simulate failure)
- [ ] Result compression tested (10x reduction verified)
- [ ] Fallback to local tested
- [ ] Cost per job calculated and logged
