# happygene

[![Tests](https://github.com/heymumford/happygene/actions/workflows/test.yml/badge.svg)](https://github.com/heymumford/happygene/actions/workflows/test.yml)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/heymumford/happygene)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![Version 0.2.0](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/heymumford/happygene/releases)

A Python-based framework for simulating gene network evolution with selection, mutation, and expression dynamics.

**happygene** is designed for evolutionary biologists and computational researchers who want to:
- Model gene expression and regulatory dynamics
- Simulate selection pressure and fitness landscapes
- Explore evolutionary trajectories with realistic genetics
- Publish reproducible simulations with full control over parameters

## Quick Start

### Installation

```bash
pip install happygene
```

### 5-Minute Example

```python
from happygene.entities import Gene, Individual
from happygene.model import GeneNetwork
from happygene.expression import HillExpression
from happygene.selection import ThresholdSelection
from happygene.mutation import PointMutation
from happygene.conditions import Conditions

# Create population: 50 individuals, 5 genes each
individuals = [
    Individual([Gene(f"gene_{j}", 0.5) for j in range(5)])
    for i in range(50)
]

# Set up models
expr_model = HillExpression(v_max=1.0, k=0.5, n=2.0)  # Hill kinetics
select_model = ThresholdSelection(threshold=0.4)       # Binary selection
mutate_model = PointMutation(rate=0.2, magnitude=0.1)  # Random variation

# Create network with environmental conditions
conditions = Conditions(tf_concentration=0.7)  # Transcription factor level
network = GeneNetwork(
    individuals=individuals,
    expression_model=expr_model,
    selection_model=select_model,
    mutation_model=mutate_model,
    conditions=conditions,
    seed=42  # Reproducible
)

# Run simulation for 150 generations
network.run(150)

# Check results
print(f"Final generation: {network.generation}")
print(f"Mean fitness: {network.compute_mean_fitness():.4f}")
```

For more examples, see `examples/simple_duplication.py` and `examples/regulatory_network.py`.

## Documentation

- **[Getting Started](https://happygene.readthedocs.io/en/latest/getting_started.html)** — Installation, basic workflow, all model types
- **[API Reference](https://happygene.readthedocs.io/en/latest/api.html)** — Full autodoc for all modules
- **[Theory](https://happygene.readthedocs.io/en/latest/theory.html)** — Mathematical background and population genetics
- **[Contributing](CONTRIBUTING.md)** — How to contribute code and ideas
- **[Governance](GOVERNANCE.md)** — Project structure and decision-making
- **[Roadmap](ROADMAP.md)** — Features planned for Phase 2-4

## Features

- **Python-first**: Pure Python (no C++ dependencies) for accessibility and extensibility
- **Modular architecture**: Subclass `ExpressionModel`, `SelectionModel`, or `MutationModel` to add custom behavior
- **Realistic gene dynamics**: Hill kinetics for sigmoidal responses, proportional/threshold/epistatic selection, point mutations
- **Gene Regulatory Networks** (v0.2.0+): Sparse adjacency matrices for multi-gene interactions with circuit detection
- **Composite Expression Models**: Base + regulatory overlay composition pattern for flexible gene regulation
- **Advanced Selection**: Sexual/asexual reproduction, epistatic fitness, multi-objective optimization
- **Multi-level data collection**: Track model (generation), individual (fitness), and gene (expression) metrics
- **Fast**: Simulates 1k generations × 100 individuals × 50 genes in <500ms
- **Reproducible**: Set seed for deterministic results across runs
- **Well-tested**: 200+ tests with 95%+ coverage (Phase 2)
- **Documented**: Comprehensive guides with tutorials and API reference

## Requirements

- **Python 3.12+** (3.13 supported)
- **numpy** >= 1.26
- **pandas** >= 2.0
- **scipy** >= 1.10 (sparse matrices for regulatory networks)
- **networkx** >= 3.0 (circuit detection)

**Optional dependencies:**
- **pytest** (for testing) — install with `pip install happygene[dev]`
- **sphinx** (for docs) — install with `pip install happygene[docs]`

## Core Concepts

### Entities
- **Gene**: Single locus with expression level (0 or higher)
- **Individual**: Collection of genes and a fitness value
- **Population**: List of individuals in simulation

### Models

**Expression Models**: Compute gene expression level given conditions
- `ConstantExpression`: Fixed level
- `LinearExpression`: Linear response to transcription factor
- `HillExpression`: Sigmoidal response with cooperative binding
- `CompositeExpressionModel` (v0.2.0+): Base + regulatory overlay with `AdditiveRegulation` or `MultiplicativeRegulation`

**Selection Models**: Compute individual fitness
- `ProportionalSelection`: Fitness = mean gene expression
- `ThresholdSelection`: Binary fitness based on threshold
- `EpistaticFitness` (v0.2.0+): Fitness with gene-gene interaction effects
- `MultiObjectiveSelection` (v0.2.0+): Weighted multi-objective fitness aggregation
- `SexualReproduction` (v0.2.0+): Genetic crossover between parents
- `AsexualReproduction` (v0.2.0+): Cloning-based reproduction

**Mutation Models**: Introduce genetic variation
- `PointMutation`: Random changes with configurable rate and magnitude

**Regulatory Networks** (v0.2.0+):
- `RegulatoryNetwork`: Sparse gene-to-gene interaction matrix with circuit detection
- `RegulationConnection`: Individual regulatory edge definition

### Simulation
- **GeneNetwork**: Main model coordinating expression → selection → mutation each generation
- **DataCollector**: Gathers metrics at model, individual, and gene levels
- **Conditions**: Environmental parameters (TF concentration, temperature, etc.)

## Usage Examples

### Basic Simulation
```python
from happygene.model import GeneNetwork
from happygene.entities import Individual, Gene

# Create population
individuals = [Individual([Gene(f"g{i}", 0.5) for i in range(10)]) for _ in range(100)]

# Run with defaults
network = GeneNetwork(individuals, ...)
network.run(100)  # 100 generations
```

### Custom Selection Pressure
```python
from happygene.selection import ThresholdSelection

# Only individuals with mean expression > 0.4 survive
select = ThresholdSelection(threshold=0.4)
```

### Environmental Conditions
```python
from happygene.conditions import Conditions

conditions = Conditions(
    tf_concentration=0.7,  # TF level drives Hill expression
    temperature=37.0,      # Extensible for custom models
    nutrients=1.0
)
```

### Data Collection
```python
from happygene.datacollector import DataCollector

collector = DataCollector(
    model_reporters={"mean_fitness": lambda m: m.compute_mean_fitness()},
    individual_reporters={"fitness": lambda ind: ind.fitness},
    gene_reporters={"expression": lambda g: g.expression_level}
)

for _ in range(100):
    network.step()
    collector.collect(network)

# Analyze results
model_df = collector.get_model_dataframe()
ind_df = collector.get_individual_dataframe()
gene_df = collector.get_gene_dataframe()
```

## Testing

```bash
# Install with dev dependencies
pip install happygene[dev]

# Run all tests (110 tests, 97% coverage)
pytest

# Run with coverage report
pytest --cov=happygene --cov-report=term-missing

# Run specific test file
pytest tests/test_model.py

# Run examples as smoke tests
pytest tests/test_examples.py
```

## Performance

Benchmarked on Intel i9, Python 3.13:

| Scenario | Time | Memory |
|----------|------|--------|
| 1k generations, 100 indiv., 10 genes | ~50ms | 5MB |
| 1k generations, 500 indiv., 50 genes | ~500ms | 25MB |
| 1k generations, 1k indiv., 100 genes | ~2.5s | 100MB |

## Architecture

```
happygene/
├── base.py              # SimulationModel abstract base
├── entities.py          # Gene and Individual classes
├── expression.py        # ExpressionModel implementations
├── selection.py         # SelectionModel implementations
├── mutation.py          # MutationModel implementations
├── model.py             # GeneNetwork (main simulation)
├── conditions.py        # Conditions dataclass
└── datacollector.py     # Data collection utilities

examples/
├── simple_duplication.py     # Basic example (constant expression)
└── regulatory_network.py     # Advanced example (Hill kinetics)

tests/
├── test_*.py            # 110+ unit and integration tests
└── test_examples.py     # Smoke tests for example scripts

docs/
├── source/conf.py       # Sphinx configuration
├── source/index.rst     # Documentation index
├── source/getting_started.md   # Tutorial
├── source/api.rst       # API reference
└── source/theory.rst    # Mathematical background
```

## Contributing

**Contributions welcome!** See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code standards (Conventional Commits, type hints, tests)
- Testing requirements (≥75% coverage)
- Pull request workflow
- Contributor tiers and progression

## License

GNU General Public License v3.0 or later. See [LICENSE](LICENSE) for details.

## Citation

If you use happygene in research, please cite:

```bibtex
@software{mumford_happygene_2026,
  author = {Mumford, Eric C.},
  title = {happygene: A Python framework for gene network evolution},
  year = {2026},
  url = {https://github.com/heymumford/happygene}
}
```

## Status

**Phase 1 (MVP)**: Complete ✅ (v0.1.0)
- Core framework, 3 expression models, 2 selection models
- 110+ tests, 97% coverage
- Sphinx documentation and GitHub Actions CI/CD

**Phase 2 (Gene Regulatory Networks)**: In development (v0.2.0)
- Multi-gene regulatory interactions
- Performance benchmarks
- Advanced selection models

See [ROADMAP.md](ROADMAP.md) for full development plan.

## Questions?

- **Documentation**: https://happygene.readthedocs.io
- **GitHub Issues**: https://github.com/heymumford/happygene/issues
- **Discussions**: https://github.com/heymumford/happygene/discussions
- **Email**: eric@heymumford.com

---

Built with ❤️ for evolutionary biologists and computational researchers.
