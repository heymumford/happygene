# HappyGene

A Python framework for simulating gene network evolution with selection, mutation, and expression dynamics.

HappyGene enables researchers and educators to model gene networks as agent-based systems, enabling exploration of evolutionary dynamics, regulatory mechanisms, and emergent behaviors in biological systems.

## Why HappyGene?

- **Pythonic**: Inheritance-based extensibility (like [Mesa](https://mesa.readthedocs.io/), the agent-based modeling framework)
- **Production-ready**: Comprehensive test coverage, documented, science-validated
- **Ecosystem integration**: Works with Jupyter, pandas, scikit-learn, PyTorch
- **Low barrier**: Install in minutes, first simulation in hours
- **Research-grade**: Theory validation, reproducible runs, publication-ready outputs

## Quick Start

### Installation

```bash
pip install happygene
```

### Your First Model

```python
from happygene import GeneNetwork, Individual

# Create a model with 100 individuals, 50 genes
model = GeneNetwork(n_individuals=100, n_genes=50)

# Run 100 generations
for generation in range(100):
    model.step()

# Access results
print(f"Final population fitness: {model.compute_mean_fitness():.3f}")
```

### Run Examples

```bash
python examples/simple_duplication.py
python examples/regulatory_network.py
```

## Documentation

- **[Getting Started](docs/getting_started.md)** — Installation, first model, concepts
- **[API Reference](docs/api.md)** — Core classes and methods
- **[Contributing](CONTRIBUTING.md)** — How to add features, report bugs
- **[Examples](examples/)** — Reference models (simple duplication, regulatory networks, etc.)

## Key Concepts

### GeneNetwork (Model)
The main simulation container. Inherits from Mesa's `Model` base class for compatibility.

```python
model = GeneNetwork(
    n_individuals=100,
    n_genes=50,
    expression_model="HillCooperative",
    selection_model="ProportionalFitness",
    mutation_rate=0.01
)
```

### Individual (Agent)
Represents an organism with genes. Agents maintain genotype, phenotype, and fitness.

```python
for individual in model.individuals:
    print(f"Fitness: {individual.fitness:.2f}")
    print(f"Mean expression: {individual.mean_expression():.2f}")
```

### Expression Models
Define how genes produce products (proteins, RNA). Extend `ExpressionModel` for custom behavior.

```python
from happygene import ExpressionModel

class MyExpressionModel(ExpressionModel):
    def calculate_expression_level(self, gene, conditions):
        # Your logic here
        return expression_value
```

### Selection Models
Define fitness and reproduction. Extend `SelectionModel` for custom selection pressure.

```python
from happygene import SelectionModel

class MySelectionModel(SelectionModel):
    def calculate_fitness(self, individual, environment):
        # Your fitness function
        return fitness_score
```

### Data Collection
Automatically collect metrics during simulation.

```python
from happygene import DataCollector

collector = DataCollector(
    model_reporters={
        "Mean_Fitness": lambda m: m.compute_mean_fitness(),
        "Genetic_Diversity": lambda m: m.compute_diversity(),
    },
    agent_reporters={
        "Fitness": "fitness",
        "Mean_Expression": lambda a: a.mean_expression(),
    }
)

# Collect during simulation
for generation in range(100):
    model.step()
    collector.collect(model)

# Export to pandas for analysis
df = collector.get_model_vars_dataframe()
df.plot(y="Mean_Fitness")
```

## Architecture

HappyGene is designed for extensibility and community contribution:

```
User Code (Your Models)
         ↓
Inheritance-based extensibility
(ExpressionModel, SelectionModel, MutationModel)
         ↓
GeneNetwork Core (GeneNetwork, Individual, Gene)
         ↓
Mesa Foundation (Model, Agent, Scheduler)
```

This design enables:
- **Easy customization** without modifying core code
- **Type safety** through inheritance validation
- **Composability** with Mesa ecosystem
- **Scientific reproducibility** through tracked randomness

## Testing

HappyGene uses pytest for comprehensive validation:

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=happygene tests/

# Run specific test file
pytest tests/test_expression.py -v
```

Tests validate:
- **Unit correctness**: Each model type
- **Integration**: Multi-component interactions
- **Theory**: Results match evolutionary theory (Hardy-Weinberg, etc.)

## Citation

If you use HappyGene in research, please cite:

```bibtex
@software{happygene2025,
  title={HappyGene: Gene Network Evolution Simulation Framework},
  author={Mumford, Eric},
  year={2025},
  url={https://github.com/yourusername/happygene}
}
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report bugs
- How to suggest features
- How to submit code
- Development setup

**Start here:** [Good First Issues](https://github.com/yourusername/happygene/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

## Community

- **GitHub Discussions:** Ask questions, share ideas
- **Issues:** Report bugs, request features
- **Contributing:** Join us!

## License

HappyGene is released under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

HappyGene is built on proven patterns from:
- [Mesa](https://github.com/mesa/mesa) — Agent-based modeling architecture
- [COPASI](https://github.com/copasi/COPASI) — Testing and validation discipline
- [BioNetGen](https://github.com/RuleWorld/bionetgen) — Modular extensibility

## Resources

- **Evolutionary Biology References:**
  - Hardy-Weinberg equilibrium
  - Genetic drift
  - Natural selection models

- **Similar Tools:**
  - [COPASI](http://copasi.org/) — Biochemical networks
  - [Mesa](https://mesa.readthedocs.io/) — General agent-based modeling
  - [BioNetGen](http://bionetgen.org/) — Rule-based protein networks

---

**Latest Release:** v0.1.0 (Beta)
**Python:** 3.11+
**License:** MIT

For questions or feedback, [open a discussion](https://github.com/yourusername/happygene/discussions).
