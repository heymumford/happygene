# Happy Gene

[![Tests](https://github.com/heymumford/happygene/actions/workflows/test.yml/badge.svg)](https://github.com/heymumford/happygene/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-77%25-green)](https://github.com/heymumford/happygene)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0--or--later-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)

Interdependent, parameterized simulations modeling DNA repair mechanisms at multi-scale.

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/heymumford/happygene
cd happygene

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Basic Usage

```python
from engine.domain.models import DamageProfile, Lesion, DamageType, CellCyclePhase
from engine.domain.config import HappyGeneConfig, KineticsConfig, SolverMethod
from engine.io.sbml_export import export_to_sbml

# Create damage profile
lesion = Lesion(position_bp=1000, damage_type=DamageType.DSB, time_seconds=0.0, severity=1.0)
damage_profile = DamageProfile(
    lesions=(lesion,),
    dose_gy=3.0,
    population_size=100,
    cell_cycle_phase=CellCyclePhase.G1
)

# Configure kinetics
kinetics = KineticsConfig(method=SolverMethod.BDF, rtol=1e-6, atol=1e-9, max_step=1.0)
config = HappyGeneConfig(kinetics=kinetics)

# Export to SBML for COPASI validation
output_path = export_to_sbml(config, damage_profile, "model.xml")
```

## Documentation

- [📖 Full Documentation](https://heymumford.github.io/happygene) — Getting started, tutorials, API reference, and examples
- [🔧 Contributing Guide](CONTRIBUTING.md) — How to contribute
- [📝 Changelog](CHANGELOG.md) — Version history

## Features

- **Multi-scale DNA repair modeling** — Cell cycle phase integration
- **Parameterized damage profiles** — 7 damage types × 8 repair pathways
- **SBML export/import** — COPASI round-trip validation with < 0.1% RMSE
- **Chaos engineering tests** — 22 fault injection tests verifying resilience
- **Contract testing** — API validation across multiple test maturity levels

## Architecture

```
engine/
├── domain/          # Core domain models (immutable frozen dataclasses)
├── kinetics/        # ODE solver integration (scipy.integrate.solve_ivp)
├── io/              # I/O subsystem (SBML export/import/validation)
└── tests/           # Unit, integration, chaos, validation tests

cli/                 # Command-line interface
docs/                # Documentation and design decisions
```

## Requirements

- **Python 3.12+**
- **Dependencies**: numpy, scipy, pydantic, click, h5py, attrs, python-dateutil
- **Optional**: python-libsbml (SBML I/O), scikit-learn, SALib (sensitivity analysis)

## Testing

```bash
# All tests (97 tests, 77% coverage)
pytest

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# With coverage report
pytest --cov=engine --cov-report=html
```

## License

This project is licensed under the GNU General Public License v3.0 or later. See [LICENSE](LICENSE) for details.

**Author:** Eric C. Mumford <eric@heymumford.com>

## Citation

If you use Happy Gene in research, please cite:

```bibtex
@software{mumford2024happygene,
  title = {Happy Gene: Multi-scale DNA Repair Simulation},
  author = {Mumford, Eric C.},
  url = {https://github.com/heymumford/happygene},
  year = {2024},
  license = {GPL-3.0-or-later}
}
```

## Status

- **Latest Version**: 0.1.0
- **Test Coverage**: 80.54% (target: 75%)
- **Tests Passing**: 153/153 ✓
- **CI/CD**: GitHub Actions (pytest + type checking)
