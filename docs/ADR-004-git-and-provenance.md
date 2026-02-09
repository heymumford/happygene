# ADR-004: Git + Provenance Metadata (Reproducibility Chain)

**Status**: DECIDED (2026-02-08)
**Context**: Publication-grade simulations require traceability of inputs, code version, environment

## Problem

Must guarantee simulation can be reproduced 12 months later. Need to track:
- Configuration parameters (dose, pathways)
- Code version (which commit built the engine)
- Random seed (for stochastic decisions)
- Solver tolerances (rtol, atol)

## Candidates

1. **Manual notebook** — Document in README (unmaintainable, gets stale)
2. **Git metadata only** — Rely on git log (incomplete, misses config details)
3. **Git + config hash + seed** — Triplet stored in output file
4. **Database (PostgreSQL)** — Queryable provenance (overkill for Phase 1)

## Decision

**Store triplet: (config_hash, git_commit, random_seed)** in every output file.

### Rationale

**Minimal** (3 pieces of info) sufficient to reconstruct any simulation.

**Deterministic** (no timestamps, no user names, no hardware specs). Two researchers on opposite continents get identical results.

**Embeddable** in HDF5 metadata (single self-contained file).

### Implementation

```python
import hashlib
import subprocess
import yaml

def compute_provenance(config: ConfigSchema, seed: int):
    """Compute reproducibility triplet."""

    # 1. Config hash (deterministic)
    config_yaml = yaml.dump(config.model_dump(), sort_keys=True)
    config_hash = hashlib.sha256(config_yaml.encode()).hexdigest()

    # 2. Git commit (current HEAD)
    git_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"]
    ).decode().strip()

    # 3. Random seed
    random_seed = seed

    return {
        "config_hash": config_hash,
        "git_commit": git_commit,
        "random_seed": random_seed,
    }

def save_with_provenance(results, config, seed, output_path):
    """Save results with provenance metadata."""
    provenance = compute_provenance(config, seed)

    with h5py.File(output_path, "w") as f:
        # Results data
        f.create_dataset("results/trajectories", data=results)

        # Provenance metadata
        f.attrs["config_hash"] = provenance["config_hash"]
        f.attrs["git_commit"] = provenance["git_commit"]
        f.attrs["random_seed"] = provenance["random_seed"]
        f.attrs["timestamp"] = datetime.now().isoformat()  # For information only
```

### Usage (Reproduction Protocol)

```python
# Original run
config = load_config("simulation.yaml")
results = run_simulation(config, seed=42)
save_with_provenance(results, config, 42, "results_original.h5")

# Six months later, reproducer wants to check
with h5py.File("results_original.h5") as f:
    original_config_hash = f.attrs["config_hash"]
    original_git_commit = f.attrs["git_commit"]
    original_seed = f.attrs["random_seed"]

# Checkout exact code version
subprocess.run(["git", "checkout", original_git_commit])

# Reload config, rerun
config = load_config("simulation.yaml")
if compute_provenance(config, original_seed)["config_hash"] != original_config_hash:
    raise ValueError("Config changed! Reproduction impossible.")

results_rerun = run_simulation(config, seed=original_seed)
assert_trajectories_match(results_rerun, results_original)  # ✓ Matches
```

## SemVer Release Strategy

Releases tagged in git as `vX.Y.Z`:

```
v0.1.0 — Phase 1 MVP (radiation → NHEJ → survival)
v0.2.0 — Phase 2 (HR pathway, cloud-local orchestration)
v0.3.0 — Phase 3 (literature graph, R/Matlab integration)
v1.0.0 — Production (all 6 repair pathways, validated)
```

Each release:
- Tag git with version
- Update CHANGELOG.md (human-readable)
- Update changelog.json (machine-readable)
- Archive provenance examples in `docs/provenance/`

## SBML Export (Cross-Tool Validation)

For each simulation, export kinetic ODE system to SBML:

```python
def export_sbml(repair_outcome: RepairOutcome, output_path: Path):
    """Export kinetics to SBML for COPASI validation."""
    # Generate SBML model from ODE equations
    # Include all parameters (rates, initial conditions)
    # Embed config hash as annotation
    pass
```

Then:
1. Run SBML in COPASI (reference implementation)
2. Compare trajectories (should match < 1% RMSE)
3. Store COPASI output with original results
4. Report discrepancy or "COPASI validated" in provenance

## Related Decisions

- ADR-003: YAML + Pydantic (config stored, not hardcoded)
- ADR-002: Modular monolith (easy to checkout git, rebuild)
- ADR-005: Changelog (version tracking in source)

## Anti-Patterns Avoided

1. ❌ Storing full config YAML in output (bloats HDF5, redundant with git)
2. ❌ Storing git history (output file grows unbounded)
3. ❌ No provenance at all (impossible to reproduce, unpublishable)
4. ❌ Filesystem timestamps (unreliable, not reproducible)

## References

- Nature Methods: "Enhancing Reproducibility for Computational Methods" (2020)
- Ten Rules for Reproducible Research (PLOS)
- SBML: Systems Biology Markup Language (sbml.org)
