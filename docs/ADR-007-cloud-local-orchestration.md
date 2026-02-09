# ADR-007: Cloud-Local Orchestration (Azure Batch + Local)

**Status**: DECIDED (2026-02-09)
**Context**: DNA repair simulations exhibit embarrassingly parallel workload pattern; cost-sensitive compute allocation critical

## Problem

Simulations range from 30 seconds (single cell) to 24 hours (population sweep, 10K configs). Must decide:
- When to compute locally (free, Apple Silicon optimized)
- When to offload to Azure (scalable, pay-per-compute)
- How to make this transparent to user

## Candidates

1. **Local-only** — 8 cores, free, but limited to 10-hour jobs max
2. **Cloud-only** — Azure Batch always, scales but costly ($0.66-3.00 per job)
3. **Hybrid (Local-Primary)** — Default local, cloud for >1 hour jobs
4. **User Choice** — Let user decide ("local" / "cloud" / "auto")

## Decision

**Use Hybrid (Local-Primary) with User Override**.

### Rationale

**Cost Analysis**:
- Local (Apple Silicon): 1000 × 5-min simulations = 10.4 hours wall-time = **$0.12 total** (electricity)
- Cloud (Azure Batch, Spot): 1000 × 5-min = 6 min wall-time = **$0.66 total** (Spot VMs)
- **Break-even**: ~100+ hours total execution time

**Decision Rule**:
```
runtime_estimate < 1 hour  → LOCAL (free, fast)
runtime_estimate 1-10 hour → ASK USER ("local", "cloud", or "auto")
runtime_estimate > 10 hour → CLOUD (default, parallelism wins)
```

### Runtime Estimation Heuristic (3-Tier)

**Tier 1: Cached** (fastest)
- If config_hash matches prior run, return cached time

**Tier 2: Parameter-based** (educated guess)
- Population size × time-per-cell × pathway_count
- e.g., 100 cells × 0.5 sec/cell × 3 pathways = 150 seconds

**Tier 3: Default** (fallback)
- Assume 5 minutes per simulation

### Configuration

```yaml
# simulation.yaml
simulation:
  type: "radiation_dna_repair"
  population_size: 1000
  compute_backend: "auto"  # or "local", "cloud", "hybrid"

orchestration:
  estimate_runtime: true     # Predict before running
  cache_results: true        # SQLite local cache
  auto_route_threshold_hours: 1.0

  cloud:
    provider: "azure"
    batch_account: "happygenebatch"
    spot_instances: true     # 80-90% cost savings
    max_parallel_jobs: 100
    timeout_hours: 24
```

## Implementation: Decision Flow

```
Given: simulation config
  ├─ Estimate runtime
  │  ├─ Hit cache? → use cached time
  │  └─ Else? → estimate from parameters
  │
  ├─ Check runtime estimate
  │  ├─ < 1 hour → LOCAL
  │  ├─ 1-10 hour → ASK USER
  │  └─ > 10 hour → CLOUD (default)
  │
  ├─ Execute on chosen backend
  │  ├─ LOCAL: subprocess → python dna_sim.py
  │  └─ CLOUD: azure batch submit job → poll results → download
  │
  └─ Cache results + time for next run
```

## Azure Batch Setup (Infrastructure)

**Cost-Optimized Configuration**:
```bash
# Create Batch account
az batch account create \
  --name happygenebatch \
  --resource-group rg-happygene \
  --location eastus

# Create pool with Spot VMs (80-90% cheaper)
az batch pool create \
  --account-name happygenebatch \
  --id happygene-pool \
  --vm-size Standard_D4s_v3 \
  --target-dedicated-nodes 0 \
  --target-low-priority-nodes 100 \
  --node-agent-sku-id "batch.node.ubuntu 20.04"
```

**Autoscaling Formula**:
```
$TargetLowPriorityNodes = min(100, $ActiveTasks + $RunningTasks + 10)
```

## Fault Tolerance Strategy

If Azure job fails (preemption, timeout):

```python
def run_with_fallback(config, backend="auto"):
    try:
        if backend in ["cloud", "auto"]:
            return run_cloud(config)
    except (AzureError, TimeoutError) as e:
        if config.estimated_runtime < 1:  # Can't run locally if >1hr
            return run_local(config)  # Fallback
        else:
            raise  # Re-raise if too large

def run_local(config):
    """Local subprocess execution."""
    subprocess.run([
        "python", "-m", "happygene.cli", "run",
        "--config", config.to_json()
    ])

def run_cloud(config):
    """Azure Batch job submission."""
    job_id = azure_batch.submit_job({
        "config": config.model_dump_json(),
        "seed": config.random_seed
    })
    return poll_until_complete(job_id)
```

## Monitoring & Cost Control

**Application Insights Queries**:

```kusto
// Daily cost by backend
customMetrics
| where name == "cost_per_job"
| summarize sum(value) by bin(timestamp, 1d), tostring(customDimensions.backend)

// Job duration by backend
customEvents
| where name == "job_completed"
| summarize avg(todouble(customDimensions.duration_seconds))
  by tostring(customDimensions.backend)
```

**Cost Alert (CRITICAL)**:
```bash
az costmanagement budget create \
  --name 'HappyGene-Safe' \
  --category Cost \
  --amount 50 \
  --scope '/subscriptions/e71e065e-f501-49ad-8eb8-225a5811d60a' \
  --time-grain Monthly
```

## Result Caching Strategy

**SQLite Local Cache**:
```python
# Cache schema
CREATE TABLE results (
    config_hash TEXT PRIMARY KEY,
    git_commit TEXT,
    random_seed INTEGER,
    result_json TEXT,
    computed_at TIMESTAMP,
    execution_time_seconds FLOAT,
    backend TEXT
);

# Check cache before running
cache_hit = db.execute(
    "SELECT result_json FROM results WHERE config_hash = ?",
    (config_hash,)
).fetchone()

if cache_hit:
    return cached_result
else:
    result = run_simulation(config)
    db.execute(
        "INSERT INTO results VALUES (?, ?, ?, ?, ?, ?, ?)",
        (config_hash, git_commit, seed, result_json, now(), elapsed, "local")
    )
    return result
```

**Cache Invalidation**:
- Invalidate if `git_commit` changed (code evolved)
- Invalidate if `rtol`/`atol` changed (solver precision)
- Cache valid for 30 days (periodic re-validation)

## Data Transfer Optimization

**Result Compression** (10x savings):

```python
# Result compression on cloud
import gzip
import json

result_json = json.dumps(result).encode()
compressed = gzip.compress(result_json, compresslevel=9)
# 50 MB → 5 MB typical
```

## Phase 2: Advanced Features (Not MVP)

- **Warm Pool**: Keep 10% of pool warm for faster task pickup
- **Priority Queues**: UI simulations prioritized over batch sweeps
- **Cost Prediction**: Show user estimated cost before submission
- **GPU Support**: Enable NVIDIA V100 for future MD simulations

## Related Decisions

- ADR-002: Modular monolith (enables stateless cloud deployment)
- ADR-003: YAML config (serializable for cloud transmission)
- ADR-004: Git + provenance (reproducible cloud execution)

## Testing Strategy

1. **Local routing**: Verify <1 hr jobs never go to cloud
2. **Cloud routing**: Verify >1 hr jobs offer cloud option
3. **Fallback**: Simulate cloud failure, verify local retry works
4. **Cost**: Compare electricity ($0.01 per KWh) vs Azure Batch ($0.25/hr Spot)
5. **Reproducibility**: Run same config (local vs cloud), verify identical results

## References

- [Azure Batch Autoscaling Formulas](https://learn.microsoft.com/en-us/azure/batch/batch-automatic-scaling)
- [Azure Batch Spot VMs (80-90% discount)](https://learn.microsoft.com/en-us/azure/batch/batch-spot-vms)
- [Cost Management + Budgets](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)
- [Azure SDK for Python](https://github.com/Azure/azure-sdk-for-python)
- [Hybrid Cloud Best Practices (AWS/Azure)](https://arxiv.org/html/2601.04349)
