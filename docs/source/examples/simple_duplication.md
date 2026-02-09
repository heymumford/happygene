# Example: Simple Gene Duplication

This is the minimal example demonstrating core happygene workflow.

**Files**: `examples/simple_duplication.py`

**Scenario**: 100 individuals, 10 genes, constant expression, proportional selection

## What it demonstrates

- Creating a population of individuals with genes
- Setting up expression, selection, and mutation models
- Running a simulation for multiple generations
- Collecting data at model, individual, and gene levels
- Analyzing and visualizing results

## Key features

- **Expression Model**: `ConstantExpression(level=1.0)` - all genes express at the same level
- **Selection Model**: `ProportionalSelection()` - fitness = mean expression
- **Mutation Model**: `PointMutation(rate=0.3, magnitude=0.05)` - 30% of genes mutate per generation
- **Population**: 100 individuals, 10 genes each
- **Duration**: 200 generations

## Run it

```bash
python examples/simple_duplication.py
```

## Expected output

The script will print:
- Population setup summary
- Model configuration
- Simulation progress
- Final fitness statistics
- Data collection summary
- (Optional) PNG visualization if matplotlib is installed

## Typical results

With constant expression (1.0) and proportional selection:
- Initial fitness: 1.0 (mean expression)
- Final fitness: ~1.0 (constant expression doesn't evolve)
- No selection pressure (all individuals equally fit)
- Mutation introduces noise but no directional change

## Try modifying

- `num_individuals`: Change population size (e.g., 50, 200)
- `num_genes`: Change number of genes (e.g., 5, 20)
- `initial_expression`: Change starting expression (e.g., 0.5, 2.0)
- `mutate_model`: Try `PointMutation(rate=0.1, magnitude=0.2)` for different mutation
- `select_model`: Try `ThresholdSelection(threshold=0.9)` to see selection pressure

## Next steps

After understanding this example, try:
- `examples/regulatory_network.py` - more advanced (Hill kinetics + threshold selection)
- Create your own expression model by subclassing `ExpressionModel`
- Use your own fitness function by subclassing `SelectionModel`
