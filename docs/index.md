# HappyGene Documentation

## Overview

HappyGene is a multi-scale DNA repair simulation engine that models the interdependent mechanisms of DNA damage recognition, repair pathway activation, and kinetic resolution. Designed for research and publication.

**Quick Links**:
- [Getting Started](getting-started.md) - Installation and first steps (5 min)
- [User Guide](user-guide.md) - Comprehensive usage documentation
- [API Reference](api-reference.md) - Complete function and class reference
- [Tutorials](tutorials/) - Step-by-step workflows
- [Examples](examples/) - Jupyter notebooks with runnable code

## Key Features

- **Multi-scale Simulation**: Atomic-level damage lesions to cellular repair kinetics
- **COPASI Compatible**: Export/import SBML Level 3 for interoperability
- **Batch Processing**: Run simulations at scale with statistical aggregation
- **Interactive Visualization**: Plotly-based dashboards and publication-ready plots
- **Publication Ready**: 80%+ test coverage, GPL-3.0 licensed, reproducible

## Installation

```bash
pip install happygene
```

## Quick Start

```python
from engine.simulator.runner import SimulationRunner
from engine.domain.config import HappyGeneConfig, DamageProfile, KineticsConfig

# Configure simulation
config = HappyGeneConfig(
    damage_profile=DamageProfile(dose_gy=3.0, population_size=1000),
    kinetics=KineticsConfig(...)
)

# Run simulation
runner = SimulationRunner(config)
results = runner.run()
print(f"Repairs: {results['final_repair_count']}")
```

## Documentation Structure

### For Users
- [Getting Started](getting-started.md) - New users start here
- [User Guide](user-guide.md) - Detailed usage patterns
- [API Reference](api-reference.md) - Function and class documentation

### For Researchers
- [Tutorials](tutorials/) - Domain-specific workflows
- [Examples](examples/) - Jupyter notebooks with analysis
- [COPASI Integration](tutorials/copasi-workflow.md) - Interoperability guide

### For Developers
- [Contributing](../CONTRIBUTING.md) - Development guidelines
- [Architecture](architecture.md) - System design and patterns
- [Testing](testing.md) - Test strategy and coverage

## Examples

### Basic Simulation
```python
results = runner.run()  # Single simulation
```

### Batch Processing
```python
batch_results = batch_simulator.run_batch(num_runs=100)
stats = BatchSimulator.compute_statistics(batch_results)
```

### Visualization
```python
dashboard = create_dashboard(batch_results)
dashboard.save_html("results.html")
```

### COPASI Export
```python
from engine.io.sbml_export import export_to_sbml
export_to_sbml(config, "simulation.xml")
```

## Support

- **Issues**: [GitHub Issues](https://github.com/heymumford/happygene/issues)
- **Discussions**: [GitHub Discussions](https://github.com/heymumford/happygene/discussions)
- **Email**: eric@heymumford.com

## License

GNU General Public License v3.0 or later. See [LICENSE](../LICENSE) for details.

Copyright © 2026 Eric C. Mumford
