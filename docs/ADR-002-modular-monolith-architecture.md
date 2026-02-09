# ADR-002: Modular Monolith Architecture (Not Microservices)

**Status**: DECIDED (2026-02-08)
**Context**: Multi-scale DNA repair simulation with tight data coupling between scales

## Problem

Scales (damage → kinetics → fate) are sequential with shared state. Must choose deployment model balancing modularity, testability, and operational simplicity.

## Candidates

1. **Monolith** — Single process, all scales in one codebase
2. **Modular monolith** — Single process, clean boundaries between scales
3. **Microservices** — Separate services per scale (damage svc, kinetics svc, fate svc)
4. **Serverless** — AWS Lambda per scale (cost-optimized)

## Decision

**Use modular monolith** with entry-point plugins.

### Rationale

**Why NOT microservices**: Network latency exceeds simulation time. IPC overhead for (100 cells × 1000 ODE integrations) > sequential execution. Data serialization/deserialization dominates.

**Why NOT serverless**: Cold start overhead, state management complexity, billing unpredictable for parameter sweeps.

**Why modular monolith**:
- Single Python process (no IPC latency)
- Clean separation: damage, simulator, fate are pure functions
- Plugin system (add NHEJ/HR/BER without core changes)
- Easy testing (unit → integration → chaos)
- Reproducible (no network timeouts, deterministic)

### Architecture

```
Engine (Python package)
├── domain/          # Immutable data (frozen dataclasses)
│   ├── damage.py
│   ├── repair.py
│   └── fate.py
├── simulator/       # Pure functions (input → output)
│   ├── damage_inducer.py       # DamageConfig → DamageProfile
│   ├── repair_engine.py        # DamageProfile → RepairOutcome
│   └── fate_decider.py         # RepairOutcome → CellFate
├── plugins/         # Strategy pattern (zero core changes)
│   ├── pathways/
│   │   ├── nhej.py
│   │   ├── hr.py
│   │   └── __init__.py
│   └── models/
└── io/              # Serialization (HDF5, SBML, JSON)
```

### Dependency Graph (No Cycles)

```
plugins ──→ domain
            ↑
simulator ──┤
            │
           io
```

Pure functions enable:
- Trivial testing (assert output)
- Parallel execution (1000 independent simulations)
- Reproducibility (same input → same output)

## Extension Points (Cost to Add)

| Extension | Effort | How |
|-----------|--------|-----|
| New repair pathway (e.g., MMR) | 4 hours | Add `plugins/pathways/mmr.py` + register |
| New damage type (e.g., interstrand crosslink) | 2-4 hours | Update damage inducer |
| New cell fate (e.g., autophagy) | 1-2 hours | Update fate decider |
| New ODE solver | 2-4 hours | Swap `scipy.integrate.solve_ivp` → assimulo |

**No core changes required for new pathways** (entry-point plugins pattern).

## Scaling Strategy

| Scale | Model | Performance |
|-------|-------|-------------|
| Single cell | Sequential | ~1 ms (simple kinetics) |
| Population (100 cells) | Vectorized NumPy | ~10-100 ms |
| Parameter sweep (1000 configs) | Embarrassingly parallel (multiprocessing/Dask) | ~1-5 min (8-core) |
| Large sweep (100K+ configs) | Cloud (Azure Batch/AKS) | User controls orchestration |

**Local stays local** by default. Cloud is opt-in.

## Testing Strategy

| Level | Approach | Cost |
|-------|----------|------|
| Unit | Pure functions (assert output) | ~5 min |
| Integration | Multi-component (damage → kinetics → fate) | ~10-30 min |
| Chaos | Fault injection (timeouts, corruptions) | ~1-5 min |
| COPASI validation | SBML round-trip (cross-tool) | ~5-10 min |

## Constraints

- **Python 3.12+** (dataclasses, type hints)
- **No async I/O** (simulation is CPU-bound, not I/O-bound)
- **No databases** at Phase 1 (results to HDF5; PostgreSQL in Phase 2 if needed)
- **No message queues** (no service-to-service communication)

## Phase 2: macOS UI + Cloud

Phase 2 adds UI and cloud orchestration:

```
macOS UI (SwiftUI) ──→ CLI (Python Click) ──→ Engine (modular monolith)
                                          ↓
                                    Local execution
                                          │
                                          ├─→ Results → ~/Library/HappyGene/
                                          └─→ Sync to S3 (async)
```

**Still monolith** at core. UI/CLI are thin wrappers.

## References

- Martin, Robert C. "Clean Architecture" (2017) — Boundaries, plugins
- Newman, Sam. "Building Microservices" (2015) — When NOT to use microservices
- Evans, Eric. "Domain-Driven Design" (2003) — Bounded contexts, ubiquitous language
