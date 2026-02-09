# Getting Started with happygene

This 5-minute tutorial walks you through creating your first gene network simulation.

## Installation

```bash
pip install happygene
```

## Your First Simulation

### Step 1: Create a Population

```python
from happygene.entities import Gene, Individual

# Create 100 individuals with 5 genes each
individuals = [
    Individual([Gene(f"gene_{j}", expression_level=0.5) for j in range(5)])
    for i in range(100)
]
```

### Step 2: Set Up Models

```python
from happygene.expression import ConstantExpression
from happygene.selection import ProportionalSelection
from happygene.mutation import PointMutation

# Expression: constant level (same for all genes)
expr_model = ConstantExpression(level=0.5)

# Selection: fitness = mean gene expression
select_model = ProportionalSelection()

# Mutation: 10% chance per gene, magnitude 0.05
mutate_model = PointMutation(rate=0.1, magnitude=0.05)
```

### Step 3: Create the Simulation Network

```python
from happygene.model import GeneNetwork

network = GeneNetwork(
    individuals=individuals,
    expression_model=expr_model,
    selection_model=select_model,
    mutation_model=mutate_model,
    seed=42  # For reproducible results
)
```

### Step 4: Run the Simulation

```python
# Run for 100 generations
network.run(100)
print(f"Generation: {network.generation}")
print(f"Mean fitness: {network.compute_mean_fitness():.4f}")
```

### Step 5: Collect Data

```python
from happygene.datacollector import DataCollector

# Create collector before running
collector = DataCollector(
    model_reporters={"mean_fitness": lambda m: m.compute_mean_fitness()},
    individual_reporters={"fitness": lambda ind: ind.fitness},
    gene_reporters={"expression_level": lambda gene: gene.expression_level}
)

# Collect data during simulation
network2 = GeneNetwork(
    individuals=individuals,
    expression_model=expr_model,
    selection_model=select_model,
    mutation_model=mutate_model,
    seed=42
)

for _ in range(100):
    network2.step()
    collector.collect(network2)

# Get results as pandas DataFrames
model_df = collector.get_model_dataframe()
individual_df = collector.get_individual_dataframe()
gene_df = collector.get_gene_dataframe()

print(model_df)
```

## Expression Models

happygene provides three built-in expression models:

### ConstantExpression
Always returns the same level regardless of conditions:

```python
from happygene.expression import ConstantExpression

model = ConstantExpression(level=0.5)
```

### LinearExpression
Linear response to transcription factor concentration:

```python
from happygene.expression import LinearExpression

model = LinearExpression(slope=2.0, intercept=0.1)
```

### HillExpression
Sigmoidal response with cooperative binding (realistic for regulatory genes):

```python
from happygene.expression import HillExpression

# E = v_max * tf^n / (k^n + tf^n)
model = HillExpression(v_max=1.0, k=0.5, n=2.0)  # n=2 for cooperativity
```

## Selection Models

### ProportionalSelection
Fitness equals mean gene expression (fitness = mean expression):

```python
from happygene.selection import ProportionalSelection

model = ProportionalSelection()
```

### ThresholdSelection
Binary fitness: 1.0 if mean expression > threshold, else 0.0:

```python
from happygene.selection import ThresholdSelection

model = ThresholdSelection(threshold=0.4)
```

## Mutations

### PointMutation
Random changes to gene expression levels:

```python
from happygene.mutation import PointMutation

# 10% of genes mutate per generation, magnitude 0.1 standard deviation
model = PointMutation(rate=0.1, magnitude=0.1)
```

## Environmental Conditions

Set transcription factor concentration and other conditions:

```python
from happygene.conditions import Conditions

conditions = Conditions(
    tf_concentration=0.7,  # TF level (used by expression models)
    temperature=37.0,      # Environment temp (extensible)
    nutrients=1.0          # Nutrient availability (extensible)
)

network = GeneNetwork(
    individuals=individuals,
    expression_model=expr_model,
    selection_model=select_model,
    mutation_model=mutate_model,
    conditions=conditions
)
```

## Next Steps

- **Run the full examples**: Check `examples/simple_duplication.py` and `examples/regulatory_network.py`
- **Extend the models**: Subclass `ExpressionModel`, `SelectionModel`, or `MutationModel`
- **Visualize results**: Use matplotlib to plot fitness/expression over time
- **Read the API**: See [API Reference](api.rst) for all classes and methods

## Key Concepts

**Gene**: Single locus with an expression level (0 or higher)

**Individual**: Collection of genes and a fitness value

**Population**: List of individuals in the simulation

**Generation**: One iteration of: expression → selection → mutation

**Fitness**: How well an individual survives/reproduces (computed by SelectionModel)

**Expression**: Level of each gene's transcript (computed by ExpressionModel)

**Mutation**: Random changes to expression levels each generation

## Reproducibility

Always set a seed for deterministic simulations:

```python
network = GeneNetwork(
    ...,
    seed=42
)
```

Same seed = same results across multiple runs.

## Troubleshooting

**Population not evolving?**
- Check that `SelectionModel` creates variation in fitness
- Try `ThresholdSelection` instead of `ProportionalSelection`
- Increase mutation rate

**High gene expression not increasing?**
- Expression model may be saturated (e.g., Hill kinetics with low tf_concentration)
- Check `Conditions.tf_concentration`
- Try different `v_max` or `k` values in `HillExpression`

**Simulations running slowly?**
- Reduce population size or number of genes
- Use `network.run(N)` instead of manual steps for faster execution

## Questions?

- **GitHub Issues**: https://github.com/heymumford/happygene/issues
- **Documentation**: https://happygene.readthedocs.io
