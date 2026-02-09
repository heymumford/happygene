# Cost Reference: Local vs Cloud Compute

**Bottom line**: Local is 6-90x cheaper for typical DNA repair workloads. Cloud wins for parameter sweeps >100 hours total execution.

---

## Quick Calculator

**Formula**:
```
Local cost = Hours × $0.001 (Apple Silicon electricity)
Cloud cost = Parallel jobs × Hours × $0.0625 (Azure Spot VM hourly)
```

**Examples**:

| Workload | Duration | Local Cost | Cloud Cost | Recommendation |
|----------|----------|-----------|-----------|-----------------|
| Single cell (simple) | 30 sec | $0.00001 | $0.01 | **LOCAL** (1000x cheaper) |
| Single cell (full pathways) | 5 min | $0.00008 | $0.10 | **LOCAL** (1000x cheaper) |
| Population (100 cells) | 45 min | $0.00045 | $0.50 | **LOCAL** (1000x cheaper) |
| **Typical sweep (1000 sims, 5 min each)** | **10.4 hr** | **$0.10** | **$0.66** | **LOCAL** (6.6x cheaper) |
| Large sweep (10K sims) | 104 hr | $0.10 | $6.60 | **CLOUD** (scales well) |
| Marathon sweep (100K sims) | 1040 hr | $1.04 | $65 | **CLOUD** |

---

## Cost Breakdown: Your Azure Subscription

**Ryorin-do.org subscription (e71e065e-f501-49ad-8eb8-225a5811d60a)**

### Current Status (as of 2026-02-09)
- No VMs running
- No Batch accounts provisioned yet
- One Container Registry: `acrsovereignty` (eastus, Basic SKU = $5/month)
- No cost alerts configured

### Estimated Monthly Costs (After HappyGene Deployment)

| Service | Usage | Cost | Notes |
|---------|-------|------|-------|
| **Container Registry** | Basic, ~100 MB images | $5 | Already running |
| **Batch (if active)** | 100 Spot nodes, 1 hr/day | $15 | 80-90% discount vs on-demand |
| **Storage (results)** | 100 GB hot, 1 TB cool | $8 | Results archival |
| **Application Insights** | 5 GB ingestion | $5 | Monitoring |
| **Bandwidth (upload/download)** | 100 GB/month | $8 | Data transfer |
| **TOTAL (Batch active)** | - | **~$41/month** | Well under typical quotas |
| **TOTAL (No Batch)** | - | **~$13/month** | Registry only |

### Budget Alert (CRITICAL)

**Current status**: ⚠️ **NO ALERTS CONFIGURED**

**Recommended**: Set $50/month alert to prevent runaway costs

```bash
# Create budget alert
az costmanagement budget create \
  --name 'HappyGene-Safety-Limit' \
  --category Cost \
  --amount 50 \
  --scope '/subscriptions/e71e065e-f501-49ad-8eb8-225a5811d60a' \
  --time-grain Monthly \
  --notifications "[{
    'type': 'Forecasted',
    'status': 'Active',
    'contactEmails': ['your-email@example.com'],
    'threshold': 100,
    'operator': 'GreaterThan'
  }]"
```

---

## When Cloud Pays for Itself

**Break-even analysis**:

Starting point: 1000 simulations × 5 min = 10.4 hours wall-time

| Scenario | Local Cost | Cloud Cost | Break-Even |
|----------|-----------|-----------|-----------|
| Run once (no parallelism) | $0.10 | $0.66 | Never (6.6x costlier) |
| Run 2x per day | $0.20 | $0.66 | After 6.6 days |
| Run 10x per day | $1.00 | $6.60 | After 7 days |
| Parameter sweep (1000 configs × 100 cells) | $10 | $60 | After 1 week |
| **100+ hour total execution** | $0.10 | $6.60 | Cloud wins at >100 hrs |

**Practical**: If you run simulations regularly (daily), cloud becomes cheaper around week 2. For one-off research, always choose local.

---

## Cost Optimization Strategies

### Strategy 1: Use Spot VMs (80-90% Discount)

```bash
# In Azure Batch pool creation
--enable-auto-scale true \
--auto-scale-formula '$TargetLowPriorityNodes = $PendingTasks' \
--target-low-priority-nodes 100  # Use Spot instead of dedicated
```

**Impact**: $0.25/hr → $0.03/hr per node

### Strategy 2: Result Compression (10x Savings)

```python
# Before: 50 MB result uploaded
result_json = json.dumps(population_outcome)  # 50 MB

# After: 5 MB compressed
import gzip
compressed = gzip.compress(result_json.encode(), compresslevel=9)  # 5 MB
```

**Impact**: Bandwidth $0.12/GB → $0.012/GB

### Strategy 3: Cache Locally (Avoid Recomputation)

```python
# Check cache before running
if config_hash in cache:
    return cache[config_hash]  # Free

# Only compute if new
result = run_simulation(config)
cache[config_hash] = result
```

**Impact**: 70-80% cache hit rate on repeated sweeps = 70% cost reduction

### Strategy 4: Off-Peak Scheduling (Batch flexibility)

Run parameter sweeps during off-peak hours (evenings, weekends) when Spot prices are lowest.

**Impact**: Additional 10-20% Spot discount during low-demand hours

---

## Your Decision Rules (Hardcoded)

Add these to `orchestration/router.py`:

```python
class CostRules:
    # Thresholds
    LOCAL_MAX_HOURS = 1.0           # Never run >1 hour locally
    CLOUD_MIN_HOURS = 10.0          # Always cloud for >10 hours
    CLOUD_SPOT_DISCOUNT = 0.85      # Assume 85% savings with Spot

    # Budget guards
    MAX_SPEND_PER_JOB = 5.0         # Abort if >$5 per job
    DAILY_BUDGET = 10.0             # Alert if >$10 per day
    MONTHLY_BUDGET = 50.0           # Alert if >$50 per month

    # Heuristics
    COST_PER_LOCAL_JOB = 0.0001     # $0.0001 per job
    COST_PER_CLOUD_JOB = 0.66      # $0.66 per job (Spot)

    @staticmethod
    def estimate_cost(backend: str, duration_hours: float) -> float:
        if backend == "local":
            return duration_hours * 0.001
        elif backend == "cloud":
            return duration_hours * 0.0625  # $0.0625/hr Spot
        else:
            return 0.0
```

---

## Monitoring Your Spend

### Daily Check

```bash
# See recent costs
az costmanagement query \
  --scope "/subscriptions/e71e065e-f501-49ad-8eb8-225a5811d60a" \
  --timeframe "Last7Days" \
  --type "Usage"
```

### Monthly Statement

```bash
# Get detailed invoice
az billing invoice list \
  --subscription "e71e065e-f501-49ad-8eb8-225a5811d60a" \
  --query "[0]" | jq '{name, status, dueDate, totalCharges}'
```

### Application Insights Dashboard

```kusto
customEvents
| where name == 'job_completed'
| extend cost = todouble(customDimensions.cost_dollars)
| summarize TotalSpend = sum(cost), JobCount = dcount(*)
  by bin(timestamp, 1d)
| render timechart
```

---

## Cost Guardrails (Prevent Accidents)

**Scenario**: User accidentally submits 100K-job parameter sweep to cloud

**Prevention**:

```python
# In orchestration/router.py
def submit_with_guardrail(config, backend):
    estimated_cost = CostRules.estimate_cost(backend, config.estimated_hours)

    if estimated_cost > CostRules.MAX_SPEND_PER_JOB:
        raise CostLimitError(
            f"Estimated cost ${estimated_cost:.2f} exceeds limit ${CostRules.MAX_SPEND_PER_JOB}. "
            f"Run locally instead? Or adjust parameters."
        )

    return submit(config, backend)
```

---

## References

**Azure Pricing**:
- [Batch Pricing Calculator](https://azure.microsoft.com/en-us/pricing/calculator/)
- [Batch Spot VMs (80-90% discount)](https://learn.microsoft.com/en-us/azure/batch/batch-spot-vms)
- [Bandwidth Pricing](https://azure.microsoft.com/en-us/pricing/details/bandwidth/)

**Cost Management**:
- [Azure Cost Management + Billing](https://learn.microsoft.com/en-us/azure/cost-management-billing/)
- [Set Budget Alerts](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

**Apple Silicon Performance**:
- [M-series Chip Specifications](https://support.apple.com/en-us/102894)
- [Energy Efficiency](https://www.anandtech.com/show/16252/the-apple-m1-reviewed)
