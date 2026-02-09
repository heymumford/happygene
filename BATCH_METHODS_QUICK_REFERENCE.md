# Batch Methods Quick Reference

## Using Batch Fitness Computation

### For Library Users

All `SelectionModel` subclasses now support vectorized batch fitness computation:

```python
import numpy as np
from happygene.selection import ProportionalSelection, ThresholdSelection

# Create selection model
selector = ProportionalSelection()

# Expression matrix: (n_individuals, n_genes)
expr_matrix = np.array([
    [0.5, 0.6, 0.7],  # Individual 1
    [0.2, 0.3, 0.4],  # Individual 2
    [0.8, 0.9, 0.95], # Individual 3
])

# Vectorized batch computation
fitness_values = selector.compute_fitness_batch(expr_matrix)
# Result: array([0.6, 0.3, 0.883...])
```

### Available Selection Models

| Model | Method | Signature |
|-------|--------|-----------|
| **ProportionalSelection** | Mean | `np.mean(expr_matrix, axis=1)` |
| **ThresholdSelection** | Binary | `(mean >= threshold).astype(float)` |
| **EpistaticFitness** | Epistatic | Base + interactions |
| **MultiObjectiveSelection** | Weighted | `expr_matrix @ weights / sum(weights)` |

## For Framework Developers

### Extending SelectionModel

When creating a new `SelectionModel` subclass, implement both methods:

```python
from happygene.selection import SelectionModel
import numpy as np

class MySelectionModel(SelectionModel):

    def compute_fitness(self, individual: Individual) -> float:
        """Single individual fitness (required for backward compatibility)."""
        expr = np.array([gene.expression_level for gene in individual.genes])
        # ... your logic ...
        return fitness_value

    def compute_fitness_batch(self, expr_matrix: np.ndarray) -> np.ndarray:
        """Batch fitness computation (MUST vectorize with NumPy)."""
        # expr_matrix shape: (n_individuals, n_genes)
        # Return shape: (n_individuals,)

        # Example: threshold at 0.5
        return (np.mean(expr_matrix, axis=1) >= 0.5).astype(float)
```

### Key Requirements

1. **Shape Contract:**
   - Input: `(n_individuals, n_genes)`
   - Output: `(n_individuals,)`

2. **Vectorization:**
   - Use NumPy operations (never explicit Python loops)
   - Leverage broadcasting for efficiency
   - Return `np.ndarray`, not list or scalar

3. **Edge Cases:**
   - Handle empty gene arrays: `if expr_matrix.shape[1] == 0`
   - Validate dimension matching: raise `ValueError` with context
   - Return zeros for zero-weight/zero-interaction cases

4. **Documentation:**
   - Docstring explaining the batch computation algorithm
   - Parameters: `expr_matrix: np.ndarray`
   - Returns: `np.ndarray`
   - Raises: Any `ValueError` conditions

## Examples

### Example 1: Simple Threshold

```python
def compute_fitness_batch(self, expr_matrix: np.ndarray) -> np.ndarray:
    """Binary fitness: 1.0 if mean >= threshold, else 0.0."""
    mean_expressions = np.mean(expr_matrix, axis=1)
    return (mean_expressions >= self.threshold).astype(float)
```

### Example 2: Matrix Operations

```python
def compute_fitness_batch(self, expr_matrix: np.ndarray) -> np.ndarray:
    """Fitness with pairwise interactions."""
    base = np.mean(expr_matrix, axis=1)
    interactions = (expr_matrix @ self.matrix * expr_matrix).sum(axis=1)
    return base + interactions / self.n_genes
```

### Example 3: Weighted Aggregation

```python
def compute_fitness_batch(self, expr_matrix: np.ndarray) -> np.ndarray:
    """Weighted sum of objectives."""
    if self.sum_weights > 0:
        return expr_matrix @ self.weights / self.sum_weights
    else:
        return np.zeros(expr_matrix.shape[0])
```

## Performance Tips

### Do's
- ✓ Use NumPy broadcasting: `(n, 1) * (1, m)` → `(n, m)`
- ✓ Use matrix operations: `A @ B` instead of loops
- ✓ Use axis parameter: `np.mean(arr, axis=1)`
- ✓ Validate once, compute many: pre-validate inputs before loop

### Don'ts
- ✗ Explicit Python loops over individuals
- ✗ List comprehensions for large arrays
- ✗ Creating unnecessary copies of data
- ✗ Converting between array types repeatedly

## Testing Your Implementation

```python
def test_my_selection_compute_fitness_batch(self):
    """Test batch method matches per-individual computation."""
    selector = MySelectionModel(...)

    # Create test data
    expr_matrix = np.array([[0.5, 0.6], [0.2, 0.3], ...])

    # Test batch computation
    batch_fitness = selector.compute_fitness_batch(expr_matrix)
    assert batch_fitness.shape == (len(expr_matrix),)

    # Verify equivalence to per-individual
    for i in range(len(expr_matrix)):
        genes = [Gene(f"g{j}", expr_matrix[i, j]) for j in range(2)]
        individual = Individual(genes)
        individual_fitness = selector.compute_fitness(individual)
        assert individual_fitness == pytest.approx(batch_fitness[i])
```

## Debugging

### Common Issues

**Issue: Shape mismatch**
```python
ValueError: expression matrix has 100 genes, but expected 50
```
Solution: Check that `expr_matrix.shape[1]` matches your model's gene count.

**Issue: Non-vectorized (slow)**
```python
# ✗ SLOW: Python loop
for individual in individuals:
    fitness = selector.compute_fitness_batch(expr_matrix)  # Wrong!

# ✓ FAST: Call once with whole matrix
fitness = selector.compute_fitness_batch(expr_matrix)
```

**Issue: Wrong output shape**
```python
# ✗ WRONG: Returns (n, 1) instead of (n,)
fitness = expr_matrix @ weights

# ✓ CORRECT: Flatten to 1D
fitness = (expr_matrix @ weights).flatten()
```

## Integration with GeneNetwork

The `GeneNetwork.step()` method automatically uses batch computation:

```python
# In model.py, step() does this:
expr_matrix = ...  # Computed in expression phase
fitness_values = self.selection_model.compute_fitness_batch(expr_matrix)
for ind_idx, individual in enumerate(self.individuals):
    individual.fitness = fitness_values[ind_idx]
```

**No need to change anything in your code** — just implement `compute_fitness_batch()` and it will be called automatically.

## References

- Source: `/Users/vorthruna/ProjectsWATTS/happygene/happygene/selection.py`
- Tests: `/Users/vorthruna/ProjectsWATTS/happygene/tests/test_selection.py`
- Benchmark: `/Users/vorthruna/ProjectsWATTS/happygene/benchmark_vectorization_cycle3.py`
