# ADR-003: YAML + Pydantic Configuration (Not Flat Files)

**Status**: DECIDED (2026-02-08)
**Context**: Reproducible parameter configuration for publication-grade simulations

## Problem

Must store simulation parameters (dose, repair pathways, kinetic rates) in way that is:
- Human-readable (researchers edit by hand)
- Machine-validated (schema enforcement)
- Reproducible (Git-trackable, hash for provenance)
- Composable (configs inherit, override)

## Candidates

1. **Flat YAML** — Single config file, no validation
2. **YAML + JSON Schema** — Validation via external schema
3. **YAML + Pydantic** — Type-safe validation in code
4. **TOML** — Flat structure, good for packaging
5. **SBML** — XML standard (verbose, overkill for Phase 1)

## Decision

**Use YAML + Pydantic v2**.

### Rationale

**YAML**: Human-readable, minimal syntax, research scientists can edit without learning JSON/TOML

**Pydantic v2**:
- Type validation at parse time
- Clear error messages (researcher sees what's wrong, not cryptic JSON errors)
- Python-native (no external schema files to maintain)
- Coercion (string "2.0" → float 2.0)
- Nested models (hierarchical config)

### Configuration Structure

```yaml
# simulation_nhej_2gy.yaml
simulation:
  type: "radiation_dna_repair"
  dose_gy: 2.0
  repair_pathways:
    - NHEJ
  population_size: 1000
  time_hours: 24
  random_seed: 42

kinetics:
  solver: "BDF"
  rtol: 1.0e-6
  atol: 1.0e-9
  max_step: 1.0

output:
  format: "hdf5"
  file: "results.h5"
  include_trajectory: true
```

### Pydantic Schema

```python
from pydantic import BaseModel, Field, field_validator

class SimulationConfig(BaseModel):
    type: str = Field(..., description="Simulation type")
    dose_gy: float = Field(..., ge=0, le=10)  # 0-10 Gy
    repair_pathways: list[str] = Field(..., min_items=1)
    population_size: int = Field(default=1000, ge=1, le=100000)
    time_hours: float = Field(default=24, ge=0.1, le=168)
    random_seed: int = Field(default=None)

    @field_validator("repair_pathways")
    @classmethod
    def validate_pathways(cls, v):
        valid = {"NHEJ", "HR", "BER", "NER", "MMR", "TLS", "alt-EJ"}
        for pathway in v:
            if pathway not in valid:
                raise ValueError(f"Unknown pathway: {pathway}")
        return v

class KineticsConfig(BaseModel):
    solver: str = Field(default="BDF")
    rtol: float = Field(default=1e-6, gt=0, lt=1e-2)
    atol: float = Field(default=1e-9, gt=0, lt=1e-5)
    max_step: float = Field(default=1.0, gt=0)

class OutputConfig(BaseModel):
    format: str = Field(default="hdf5")
    file: Path
    include_trajectory: bool = Field(default=True)

class ConfigSchema(BaseModel):
    simulation: SimulationConfig
    kinetics: KineticsConfig = Field(default_factory=KineticsConfig)
    output: OutputConfig
```

### Usage

```python
import yaml
from pathlib import Path

# Load from YAML
with open("simulation_nhej_2gy.yaml") as f:
    config_dict = yaml.safe_load(f)

config = ConfigSchema(**config_dict)  # Validation happens here

# Access with type hints
print(config.simulation.dose_gy)  # IDE autocomplete works
print(config.kinetics.solver)

# Reproducibility: embed config hash + git commit in output
import hashlib
config_hash = hashlib.sha256(
    yaml.dump(config.model_dump(), sort_keys=True).encode()
).hexdigest()

print(f"Config hash: {config_hash}")  # Stored in HDF5 metadata
```

### Validation Errors (Clear Feedback)

```
$ happygene run bad_config.yaml

pydantic_core._pydantic_core.ValidationError: 1 validation error for ConfigSchema
simulation.dose_gy
  Input should be <= 10 [type=less_than_equal, input_value=25.0, input_type=float]

Expected: dose_gy between 0 and 10 Gy
```

## Phase 2: Hierarchical Configs

Phase 2 adds composition (base + overrides):

```yaml
# base_nihej.yaml
extends: "templates/standard_nhej.yaml"

simulation:
  dose_gy: 4.0  # Override
  population_size: 10000  # Override

kinetics:
  rtol: 1.0e-7  # More strict
```

Implemented via `@root_validator` or schema inheritance.

## Related Decisions

- ADR-001: ODE solver (BDF) tuneable via kinetics.solver
- ADR-002: Modular monolith (configs passed to pure functions)
- ADR-004: Git + provenance (config_hash stored in output)

## References

- Pydantic v2 documentation: https://docs.pydantic.dev/
- YAML specification: https://yaml.org/
- Configuration design patterns: McDowell, "Configuration Management Best Practices"
