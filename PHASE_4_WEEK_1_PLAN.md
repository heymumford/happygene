# Phase 4 Week 1: Domain Model + Pydantic Configs

**Goal**: Establish frozen dataclasses + Pydantic v2 schemas for DNA damage, repair mechanisms, cell fate, and configuration. TDD discipline: RED → GREEN → BLUE cycles.

**Duration**: 1 week (5 working days)

---

## Phases

- [x] Phase 1: Domain Model Architecture (design, no code) - 2026-02-08
- [x] Phase 2: RED Tests (pytest fixtures, property-based tests) - 2026-02-08
- [x] Phase 3: GREEN Implementation (dataclasses, Pydantic schemas) - 2026-02-08
- [ ] Phase 4: BLUE Refactoring (clarity, docstrings, optimization)
- [ ] Phase 5: Cross-Validation (COPASI export, round-trip fidelity)
- [ ] Phase 6: Integration (CLI config loading, error handling)

---

## Architecture (from ADRs)

### 1. Domain Model (Immutable Boundaries)

**Frozen dataclasses** for data integrity across pipeline:
- `DamageProfile`: Dose (Gy), damage type, location, time
- `RepairOutcome`: Events (NHEJ/HR/BER), timing, fidelity
- `CellFate`: Status (viable/apoptosis/senescence), markers

**Pydantic v2 schemas** for YAML/JSON config:
- `SimulationConfig`: Population, time, repair pathways
- `KineticsConfig`: Solver tolerances (rtol, atol), ODE settings
- `OutputConfig`: HDF5 structure, metadata fields

### 2. Key Invariants (Property-Based Tests)

- Damage profiles immutable after creation
- Repair outcomes chain temporally (t0 < t1 < t2)
- Cell fate deterministic given (config, seed, damage)
- YAML → Pydantic → YAML round-trip preserves all fields
- Config hash stable (same input → same hash)

### 3. Extension Points

- Damage types: enum (DSB, SSB, CrossLink, Oxidative, Depurination)
- Repair pathways: registry (NHEJ, HR, BER, NER, MMR, TLS, altEJ)
- Cell fate: extensible (can add new markers)

---

## Week 1 Breakdown

### Day 1-2: Design + RED Phase

**Deliverables:**
- Domain model class diagram (text)
- Frozen dataclass structure (no implementation)
- Pydantic schema validation rules
- pytest test suite (all failing, RED)

**Files to create:**
- `engine/domain/models.py` (skeleton, docstrings only)
- `engine/domain/config.py` (Pydantic schemas)
- `tests/unit/test_domain_models.py` (RED: 30+ tests failing)
- `tests/unit/test_config_validation.py` (RED: 20+ tests failing)

**Test Categories:**
1. Immutability: Attempt to modify frozen fields → TypeError
2. Temporal ordering: Repair events must chain t0 < t1 < t2
3. Config validation: Invalid dose_gy → validation error
4. Round-trip: YAML → Pydantic → YAML preserves data
5. Config hash: Same input → same SHA256
6. Enum validation: Damage type must be one of [DSB, SSB, ...]
7. Boundary values: dose_gy ∈ [0, 10], population ∈ [1, 1000000]
8. Special chars: Unicode in pathway names preserved

### Day 3: GREEN Phase

**Deliverables:**
- Frozen dataclasses (immutable, with type hints)
- Pydantic v2 models with validation
- All 50+ tests passing
- Config loaders (YAML → Python objects)

**Code patterns:**
```python
# engine/domain/models.py
from dataclasses import dataclass
from enum import Enum

class DamageType(str, Enum):
    DSB = "double_strand_break"
    SSB = "single_strand_break"
    # ...

@dataclass(frozen=True)  # Immutable
class DamageProfile:
    dose_gy: float
    damage_type: DamageType
    time_seconds: float
    location_nm: Optional[float]

    def __post_init__(self):
        if not (0 <= self.dose_gy <= 10):
            raise ValueError(f"dose_gy must be in [0, 10], got {self.dose_gy}")
```

```python
# engine/domain/config.py
from pydantic import BaseModel, Field, validator

class KineticsConfig(BaseModel):
    rtol: float = Field(1e-6, ge=1e-9, le=1e-3)
    atol: float = Field(1e-9, ge=1e-12, le=1e-6)
    method: str = Field("BDF", pattern="^(BDF|RK45|RK23)$")

    class Config:
        frozen = True
```

### Day 4: BLUE Phase

**Deliverables:**
- Enhanced docstrings (purpose, examples, constraints)
- Static type hints (mypy strict mode)
- Optimized validation logic
- 100% test coverage with zero violations

**Quality gates:**
- `make lint` passes (ruff, isort)
- `make type-check` passes (mypy --strict)
- `make test` passes (pytest 50+ tests)
- Test coverage ≥ 95%

### Day 5: Cross-Validation + Integration

**Deliverables:**
- SBML export (for COPASI round-trip)
- CLI config loading integrated
- Error messages publication-grade
- All integration tests passing

**Validation:**
- Load a config from YAML
- Verify all fields present in Pydantic objects
- Export to SBML
- Load back from SBML
- Verify data fidelity <0.1% drift

---

## Key Decisions

1. **Frozen dataclasses over mutable**: Enforce immutability at boundaries, prevent accidental mutation
2. **Pydantic v2 (not dataclasses for config)**: Superior validation, JSON schema generation, round-trip serialization
3. **Enum for damage types**: Type-safe, extensible, self-documenting
4. **Property-based tests first**: Define invariants before implementation

---

## Test Structure

### tests/unit/test_domain_models.py (30 tests)

```
Immutability Tests (8)
├─ frozen_dataclass_rejects_field_mutation
├─ frozen_dataclass_hashable
├─ frozen_dataclass_comparable
└─ ...

Temporal Ordering Tests (8)
├─ repair_events_chain_temporally
├─ repair_event_with_inverted_times_rejected
├─ multiple_repair_events_maintain_order
└─ ...

Validation Tests (8)
├─ damage_type_enum_validation
├─ dose_range_validation [0, 10]
├─ population_range_validation [1, 1M]
└─ ...

Property-Based Tests (6)
├─ round_trip_serialization_fidelity
├─ config_hash_stability
├─ unicode_preservation
└─ ...
```

### tests/unit/test_config_validation.py (20 tests)

```
Pydantic Validation (10)
├─ valid_config_loads
├─ invalid_rtol_rejected
├─ missing_required_field_rejected
├─ enum_field_validation
└─ ...

YAML Loading (5)
├─ yaml_to_pydantic_round_trip
├─ special_chars_preserved
└─ ...

Config Hash (5)
├─ same_input_same_hash
├─ order_invariant_hash
└─ ...
```

---

## Acceptance Criteria

**All must pass by end of Day 5:**

- [ ] 50+ unit tests passing (0 failures, 0 skips)
- [ ] mypy --strict (0 errors)
- [ ] ruff check (0 violations)
- [ ] Coverage ≥ 95% (engine/domain/)
- [ ] SBML export round-trip <0.1% RMSE
- [ ] CLI can load YAML config
- [ ] No technical debt comments
- [ ] All docstrings complete (no empty)

---

## Errors Encountered

*To be filled as we execute*

---

## Status

**IN PROGRESS** - Phase 4 (BLUE Refactoring)

### Progress
- ✅ Phase 1-3 COMPLETE (Day 1)
  - engine/domain/models.py: 470 LOC (frozen dataclasses, 7 core types)
  - engine/domain/config.py: 280 LOC (Pydantic schemas)
  - tests/unit/test_domain_models.py: 500 LOC (40+ tests)
  - tests/unit/test_config_validation.py: 450 LOC (42+ tests)
  - **82 tests PASSING** (0 failures)
  - Type hints: 100% complete
  - Docstrings: 95% complete

### Key Achievements
- Immutability: Frozen dataclasses prevent mutation at boundaries
- Temporal ordering: Lesions/events must chain t0 < t1 < t2
- Validation: dose_gy ∈ [0,10], population ∈ [1, 1M], tolerances [1e-12, 1e-3]
- Config hashing: Deterministic SHA256 (16-char hex) for reproducibility
- Enum safety: DamageType, RepairPathway, CellFateStatus, CellCyclePhase
- Round-trip: Config.to_dict() → JSON serializable

### Technical Debt (minimal)
- Pydantic v2: Using deprecated class-based Config (5 deprecation warnings)
  - Fix: Use ConfigDict in Phase 4
- YAML loading: Placeholder NotImplementedError (Phase 5)

---

## Commands

```bash
# Run tests
make test

# Type check
make type-check

# Full quality gate
make lint && make type-check && make test

# Coverage report
pytest --cov=engine/domain tests/unit/test_domain_models.py tests/unit/test_config_validation.py
```

---

## Success Metrics

| Metric | Target | Evidence |
|--------|--------|----------|
| Test coverage (domain/) | ≥95% | pytest --cov report |
| Tests passing | 50+ | `make test` output |
| Type safety | mypy strict | mypy --strict engine/domain/ |
| Linting | 0 violations | ruff check engine/domain/ |
| Documentation | 100% complete | All docstrings present |
| SBML fidelity | <0.1% RMSE | Cross-validation test |

