# HappyGene Architecture

**Principle**: Separation of concerns, dependency isolation, testability-first.

## System Design (C4 Lens)

### Context
```
┌─────────────────────────────────────────────────────────────────┐
│ HappyGene: Interdependent DNA Repair Simulations               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Users (Researchers)                                           │
│      │                                                          │
│      ├─→ macOS UI (SwiftUI)          [Phase 2]                 │
│      ├─→ CLI (Python Click)                                    │
│      └─→ MCP (Claude agentic)                                  │
│      │                                                          │
│      ▼                                                          │
│  ┌──────────────────────────────────┐                          │
│  │  HappyGene Engine                │                          │
│  │ (Python 3.12, TDD)               │                          │
│  ├──────────────────────────────────┤                          │
│  │ • Domain models (Pydantic)       │                          │
│  │ • Simulation pipeline            │                          │
│  │ • Plugin system                  │                          │
│  │ • I/O (HDF5, SBML)               │                          │
│  └──────────────────────────────────┘                          │
│      │                               │                         │
│      ├─→ Knowledge graph             ├─→ Compute (local/cloud)│
│      │   (PubMed sync)               │   (Azure AKS)          │
│      │                               │                         │
│      ▼                               ▼                         │
│  Literature DB              Results archival (S3/PostgreSQL)   │
│  (Last 20 per node)                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Container (Modular Monolith)

```
HappyGene (single Python package)
├── engine/
│   ├── domain/          # Immutable data boundaries
│   ├── simulator/       # Pure functions (input → output)
│   ├── plugins/         # Strategy pattern (pathways, models)
│   └── io/             # Serialization (HDF5, SBML, JSON)
│
├── cli/                # Click CLI (entry point for batch jobs)
├── mcp/                # FastMCP server (Claude integration)
├── knowledge_graph/    # Live literature topology
└── tests/             # All test modes (unit, integration, chaos)
```

### Components (Detailed)

#### 1. Domain Model (Immutable Boundaries)

```python
# engine/domain/damage.py
@dataclass(frozen=True)
class DamageProfile:
    """Immutable damage state at simulation start."""
    lesions: List[Lesion]
    dna_length: int
    ploidy: int
    cell_cycle_phase: CellCyclePhase
    created_at: datetime

# engine/domain/repair.py
@dataclass(frozen=True)
class RepairOutcome:
    """Immutable kinetics result."""
    pathway: str  # "NHEJ", "HR", "BER", etc.
    completion_time: float
    success: bool
    repaired_lesions: int
    unrepaired_lesions: int

# engine/domain/fate.py
@dataclass(frozen=True)
class CellFate:
    """Immutable cell outcome."""
    state: FateState  # ALIVE, APOPTOTIC, SENESCENT, etc.
    reason: str
    probability: float
```

**Key principle**: Domain objects are frozen dataclasses. No mutations across scales.

#### 2. Simulator Pipeline (Pure Functions)

```python
# engine/simulator/damage_inducer.py
def damage_inducer(config: DamageConfig) -> DamageProfile:
    """DamageConfig → DamageProfile"""
    # Deterministic: same config + same seed = same damage
    # Testable: no side effects, no I/O
    pass

# engine/simulator/repair_engine.py
def repair_simulator(damage: DamageProfile,
                     pathway: str,
                     time_hours: float) -> RepairOutcome:
    """DamageProfile → RepairOutcome (ODE solver)"""
    # Input: frozen dataclass
    # Output: frozen dataclass
    # No state mutation between calls
    pass

# engine/simulator/fate_decider.py
def fate_decider(outcome: RepairOutcome,
                 cell_state: CellState) -> CellFate:
    """RepairOutcome → CellFate (stochastic decision)"""
    # Input: frozen dataclass
    # Output: frozen dataclass
    # Probability-based but deterministic given seed
    pass
```

**Key principle**: Each scale is a pure function. Tests are trivial (assert output).

#### 3. Plugin System (Entry-Point Plugins)

```
engine/plugins/
├── pathways/
│   ├── nhej.py        # NHEJ pathway ODE definition
│   ├── hr.py          # HR pathway ODE definition
│   └── __init__.py    # Registry: {"NHEJ": NHEJPathway, "HR": HRPathway}
│
└── models/
    ├── kinetic_nhej.py
    ├── kinetic_hr.py
    └── __init__.py
```

**YAML-driven**: Adding a new pathway requires:
1. Create `engine/plugins/pathways/myr.py` with ODE definition
2. Register in `__init__.py`: `PATHWAYS["MMR"] = MMRPathway`
3. Reference in config YAML: `pathways: [NHEJ, MMR]`

**Zero core changes** to simulate new repair type.

#### 4. I/O Layer (Reproducibility)

```python
# engine/io/hdf5_writer.py
class HDF5ResultWriter:
    """Deterministic output with provenance."""
    def write(self,
              results: PopulationOutcome,
              config_hash: str,
              git_commit: str,
              random_seed: int) -> Path:
        # Store: results + config_hash + git_commit + seed
        # Enables: bitwise reproducibility check
        pass

# engine/io/sbml_exporter.py
class SBMLExporter:
    """Export kinetics to SBML for COPASI validation."""
    def export(self,
               repair_outcome: RepairOutcome,
               output_path: Path) -> None:
        # Generate SBML model
        # Run in COPASI, compare trajectories
        pass
```

### Dependency Graph (No Cycles)

```
tests (top) ──→ Depend on everything
  │
  ├─→ cli ──→ Depends on [engine]
  ├─→ mcp ──→ Depends on [engine]
  ├─→ macos ──→ Depends on [engine] (via Python subprocess)
  │
  └─→ engine ──→ Depends on [domain, simulator, plugins, io]
        │
        ├─→ domain ──→ Depends on [Python stdlib + Pydantic]
        ├─→ simulator ──→ Depends on [domain, plugins, scipy]
        ├─→ plugins ──→ Depends on [domain, scipy]
        └─→ io ──→ Depends on [domain, h5py]

Principle: No circular dependencies. Build order: bottom-up.
```

## Testing Strategy: Multi-Level Validation

**Requirement**: Validate at ≥2 data types simultaneously (never one).

### Level 1: Unit Tests (Pure Functions)

```python
# engine/tests/unit/test_damage_inducer.py
def test_damage_inducer_deterministic():
    """Same config + seed = same damage."""
    config = DamageConfig(dose_gy=2.0, seed=42)
    d1 = damage_inducer(config)
    d2 = damage_inducer(config)
    assert d1 == d2

def test_damage_inducer_lesion_count():
    """Dose determines lesion count (linear regression)."""
    for dose in [0.5, 1.0, 2.0, 4.0]:
        damage = damage_inducer(DamageConfig(dose_gy=dose, seed=0))
        assert len(damage.lesions) == expected_lesion_count(dose)
```

### Level 2: Kinetic Validation (ODE vs Literature)

```python
# engine/tests/validation/test_kinetics_vs_literature.py
def test_nhej_repair_kinetics_vs_gamma_h2ax():
    """NHEJ kinetics match published γ-H2AX data (Haber 1999)."""
    # Run simulation
    outcome = repair_simulator(
        damage=synthetic_damage(10),
        pathway="NHEJ",
        time_hours=24
    )
    # Extract repair rate over time
    repair_curve = outcome.get_repair_curve()
    # Compare with published data
    rmse = calculate_rmse(repair_curve, GAMMA_H2AX_DATA)
    assert rmse < 0.05  # <5% error
```

### Level 3: System Validation (Survival Curves)

```python
# engine/tests/validation/test_survival_curve_vs_lq_model.py
def test_population_survival_vs_lq_model():
    """Population survival curve matches LQ (Linear-Quadratic) model."""
    # Simulate population at multiple doses
    for dose in [0.5, 1.0, 2.0, 4.0]:
        survivors = simulate_population_survival(
            dose_gy=dose,
            population_size=1000,
            pathways=["NHEJ"]
        )
        survival_fraction = survivors / 1000
        # Compare with LQ model prediction
        predicted = lq_model_survival(dose)
        assert abs(survival_fraction - predicted) < 0.1  # <10% error
```

### Level 4: Chaos Engineering (Fault Injection)

```python
# engine/tests/chaos/test_kinetics_under_chaos.py
def test_nhej_under_intermittent_failures():
    """ODE solver resilient to 30% intermittent timeouts."""
    with ChaosInjector(failure_rate=0.3, failure_type="timeout"):
        outcome = repair_simulator(
            damage=synthetic_damage(10),
            pathway="NHEJ",
            time_hours=24
        )
        # Even with failures, repair kinetics consistent
        assert outcome.success or outcome.retry_count > 0
        assert outcome.completion_time < 30  # Doesn't hang
```

### Level 5: Cross-Tool Validation (SBML Round-Trip)

```python
# engine/tests/validation/test_sbml_round_trip.py
def test_copasi_round_trip():
    """SBML export → COPASI validation → reimport matches."""
    # Generate SBML
    sbml_path = sbml_exporter(repair_outcome, "nhej_model.xml")

    # Run in COPASI (subprocess)
    copasi_results = run_copasi(sbml_path)

    # Compare trajectories
    our_trajectory = repair_outcome.get_trajectory()
    copasi_trajectory = parse_copasi_output(copasi_results)

    rmse = calculate_rmse(our_trajectory, copasi_trajectory)
    assert rmse < 0.01  # <1% error
```

## Deployment Architecture

### Phase 1 (MVP)
```
Developer
    │
    ├─→ make test           (Local)
    ├─→ make build          (Local)
    ├─→ pip install -e .    (Local)
    └─→ happygene run config.yaml (Local)
```

### Phase 2 (macOS + Cloud)
```
macOS User
    │
    ├─→ HappyGene.app (SwiftUI)
    │       │
    │       └─→ Spawns CLI process (Python)
    │           │
    │           ├─→ Run locally (8 cores)
    │           └─→ Or submit to Azure AKS (orchestrated)
    │
    └─→ Results stored in: local ~/Library/HappyGene/results/ + S3 backup
```

### Phase 3 (Full Orchestration)
```
Claude (via MCP)
    │
    ├─→ mcp:run_simulation(config)
    ├─→ mcp:sweep(parameters, ranges)
    ├─→ mcp:sensitivity(outcome)
    └─→ mcp:hypothesis_test(treatment, control)

    Results → stored + visualized in Dashboard
```

## Technology Stack Decision Record

| Component | Technology | Rationale | Alternative | Why Not |
|-----------|-----------|-----------|-------------|---------|
| **Language** | Python 3.12 | OpenMM native, MCP integration, fast iteration | Julia | 10x faster ODE, but steeper curve; defer to Phase 2 |
| **ODE Solver** | SciPy (Phase 1) | Proven, publication-ready | assimulo, lsoda | Defer advanced solvers; benchmark in Phase 2 |
| **Config** | Pydantic + YAML | Type-safe + human-readable | TOML, JSON | YAML most readable for domain scientists |
| **Testing** | pytest + hypothesis | Industry standard, parameterization | unittest | pytest better for complex test scenarios |
| **CI/CD** | GitHub Actions | Free, GitHub-native | GitLab CI | User choice; can integrate either |
| **macOS UI** | SwiftUI | Native performance, A11y | Electron, Tauri | SwiftUI modern, but Electron faster MVP (Phase 1 CLI) |
| **Knowledge Graph** | PubMed E-utilities | Live, public API | Semantic Scholar, CrossRef | PubMed most authoritative for biology |
| **Cloud** | Azure AKS | User constraint | AWS, GCP | User specified Azure; flexibility via Terraform |

## Anti-Patterns Avoided

1. ❌ Microservices (scales are sequential; shared state coupling makes it worse)
2. ❌ Mutable domain state (bugs from out-of-order mutations)
3. ❌ Hardcoded pathways (new pathway requires core changes)
4. ❌ No cross-validation (simulation may be wrong; check vs literature + COPASI)
5. ❌ No reproducibility metadata (can't debug results from production)
6. ❌ No chaos testing (fails silently under real-world conditions)

## Next Steps

1. **Phase 3**: Narrow technology choices
   - Deep-dive ODE solvers (SciPy vs alternatives)
   - MCP FastAPI binding POC
   - macOS framework comparison (SwiftUI vs Electron)

2. **Phase 4**: MVP Implementation (8 weeks)
   - Week 1-2: Domain model
   - Week 3-4: NHEJ pathway + kinetics
   - Week 5-6: Population + cell fate
   - Week 7: MCP server + CLI
   - Week 8: I/O + SBML + hardening

3. **Phase 5**: Knowledge Graph Integration (3-4 weeks)
   - PubMed E-utilities binding
   - Node topology definition (9 components)
   - Dependency traversal validator
   - Live sync scheduler

---

**Status**: Architecture finalized. Ready for Phase 3 deep-dive decisions.
