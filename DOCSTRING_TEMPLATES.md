# Docstring Templates & Examples

**For All Tiers**: Start with NumPy docstring format (established in CONTRIBUTING.md)

**For Tier 1-2 Only**: Add Intent section (machine-readable contract for agents)

---

## Python: Tier 1 (Critical)

### Module Header

```python
"""Gene entity implementations.

# Module Classification
Tier: CRITICAL
Coverage Target: 100%

Rationale:
This module defines Gene and Individual, core domain entities. Bugs here
affect all downstream computations; data integrity is paramount. Every
code path must be tested to prevent silent failures.

Status: STABLE (no planned changes)
"""
```

### Class Docstring (Tier 1)

```python
class Gene:
    """Represents a single gene with expression level.

    # Intent (Machine-Readable Contract for Agents)
    Purpose: Store gene identity and current expression level
    Invariant: expression_level always >= 0 (biological reality)
    Mutation contract: Expression level is updated; name is immutable
    Side effects: None (value object)
    Error handling: Negative expression_level is clamped to 0 (no exceptions)

    Domain:
    - name: str, non-empty, unique identifier
    - expression_level: float >= 0 (any non-negative value)

    Boundary cases to test:
    - name="" → ValueError (empty not allowed?)
    - expression_level=-5.0 → clamped to 0.0
    - expression_level=float('inf') → acceptable
    - expression_level=0.0 → valid (no expression)

    # API Surface (Human-Readable)
    Parameters
    ----------
    name : str
        Gene identifier (e.g., "BRCA1", "TP53")
    expression_level : float
        Current transcription rate (clamped to [0, inf))

    Attributes
    ----------
    name : str
        Immutable gene identifier
    expression_level : float
        Current expression level (always >= 0)

    Raises
    ------
    ValueError
        If name is empty or None

    Examples
    --------
    >>> gene = Gene("BRCA1", 0.5)
    >>> gene.expression_level
    0.5

    >>> gene = Gene("TP53", -0.2)  # Negative clamped to 0
    >>> gene.expression_level
    0.0
    """

    __slots__ = ('name', '_expression_level')

    def __init__(self, name: str, expression_level: float):
        if not name:
            raise ValueError("Gene name must be non-empty string")
        self.name: str = name
        self._expression_level: float = max(0.0, expression_level)

    @property
    def expression_level(self) -> float:
        """Current expression level (always >= 0)."""
        return self._expression_level
```

### Method Docstring (Tier 1)

```python
def collect(self, individual: Individual, generation: int) -> None:
    """Record individual state at current generation.

    # Intent (Machine-Readable Contract for Agents)
    Purpose: Append Individual snapshot to collection
    Preconditions:
    - individual is valid Individual instance with genes
    - generation >= 0
    - All genes have valid expression_level

    Postconditions:
    - One row appended to internal DataFrame
    - DataFrame shape[0] increases by 1
    - Data is immutable after collection (no retroactive edits)

    Mutation contract:
    - Mutates internal state (self._data)
    - Does not mutate input Individual
    - Caller retains ownership of Individual

    Side effects:
    - DataFrame memory increases
    - May trigger garbage collection if memory high

    Error handling:
    - Raises ValueError if Individual malformed
    - Raises TypeError if generation not int
    - Does NOT raise if generation < 0 (clamps to 0)

    Boundary cases to test:
    - generation=0 → valid (start of simulation)
    - generation=-1 → clamps to 0
    - generation=999999 → valid (large number)
    - individual with 0 genes → valid (empty genome)
    - individual with 1000 genes → valid (large genome)
    - repeated call with same generation → appends multiple rows (allowed)

    # API Surface (Human-Readable)
    Parameters
    ----------
    individual : Individual
        Individual to record (non-null, must have genes attribute)
    generation : int
        Generation number (>= 0, will be clamped if negative)

    Returns
    -------
    None
        Data is stored internally; no return value

    Raises
    ------
    ValueError
        If Individual lacks required attributes (genes, fitness)
    TypeError
        If generation is not int
    MemoryError
        If DataFrame grows beyond available memory

    Examples
    --------
    >>> collector = DataCollector()
    >>> ind = Individual([Gene("A", 0.5)])
    >>> collector.collect(ind, generation=0)
    >>> collector.collect(ind, generation=1)
    >>> len(collector.data)
    2
    """
    # Implementation...
    pass
```

---

## Python: Tier 2 (Computation)

### Class Docstring (Tier 2)

```python
class LinearExpression(ExpressionModel):
    """Linear gene expression model: E = slope × tf + intercept.

    # Intent (for agents)
    Purpose: Compute linear response to transcription factor
    Formula: E(tf) = max(0, slope × tf + intercept)
    Domain:
    - slope: any real number (positive = activation, negative = repression)
    - intercept: [0, ∞) (basal expression when tf=0)
    - tf: [0, 1] (transcription factor concentration, normalized)

    Range: E(tf) ∈ [0, ∞)
    Invariant: Expression always non-negative (biological reality)

    Boundary cases:
    - slope=0: returns intercept (constant expression)
    - slope<0, tf>0: can return 0 if formula < 0 (clamping)
    - tf=0: returns max(0, intercept) (basal level)
    - intercept=0: returns max(0, slope × tf)

    # API Surface (Human-Readable)
    Parameters
    ----------
    slope : float
        Sensitivity to transcription factor (can be negative)
    intercept : float
        Basal expression level when tf=0. Must be >= 0.

    Attributes
    ----------
    slope : float
        Sensitivity coefficient
    intercept : float
        Basal expression level

    Raises
    ------
    ValueError
        If intercept < 0

    Examples
    --------
    >>> expr = LinearExpression(slope=1.0, intercept=0.2)
    >>> expr.compute(Conditions(tf_concentration=0.5))
    0.7  # 1.0 * 0.5 + 0.2

    >>> expr = LinearExpression(slope=-1.0, intercept=0.3)
    >>> expr.compute(Conditions(tf_concentration=0.5))
    0.0  # max(0, -1.0 * 0.5 + 0.3) = max(0, -0.2)
    """

    def __init__(self, slope: float, intercept: float):
        if intercept < 0.0:
            raise ValueError(f"intercept must be >= 0, got {intercept}")
        self.slope: float = slope
        self.intercept: float = intercept

    def compute(self, conditions: Conditions) -> float:
        """Compute linear expression.

        # Intent
        Formula: E = max(0, slope × tf_concentration + intercept)
        Result clamped to [0, ∞)
        Boundary cases: See class docstring

        # API Surface
        Parameters
        ----------
        conditions : Conditions
            Environmental conditions with tf_concentration [0, 1]

        Returns
        -------
        float
            Expression level, always >= 0

        Examples
        --------
        >>> m = LinearExpression(slope=2.0, intercept=0.1)
        >>> m.compute(Conditions(tf_concentration=0.5))
        1.1  # 2.0 * 0.5 + 0.1
        """
        result = self.slope * conditions.tf_concentration + self.intercept
        return max(0.0, result)
```

### Function Docstring (Tier 2)

```python
def proportional_selection(individuals: List[Individual]) -> None:
    """Apply fitness-proportional selection to population.

    # Intent
    Purpose: Reduce population to fittest individuals based on fitness values
    Algorithm: Roulette wheel selection (fitness-proportional)
    Preconditions:
    - All individuals have fitness >= 0
    - Population non-empty

    Postconditions:
    - Population size unchanged
    - Only fittest individuals survive
    - Selection is stochastic (random variation)

    Domain:
    - individuals: list of Individual with .fitness attribute
    - fitness values: [0, inf)

    Boundary cases:
    - All fitness=0 → equal probability of survival
    - One fitness >> others → dominates (99%+ survive)
    - fitness sum overflow → may cause numerical issues

    # API Surface
    Parameters
    ----------
    individuals : List[Individual]
        Population to select (non-empty, all have .fitness)

    Returns
    -------
    None
        Modifies individuals in-place (removes unfit)

    Raises
    ------
    ValueError
        If population empty
    ValueError
        If any fitness < 0

    Examples
    --------
    >>> inds = [Individual(...), Individual(...)]
    >>> inds[0].fitness = 0.1
    >>> inds[1].fitness = 0.9
    >>> proportional_selection(inds)
    >>> # inds[1] more likely to survive
    """
    # Implementation...
    pass
```

---

## Python: Tier 3 (Utility)

### Function Docstring (Tier 3)

```python
def spearman_correlation(param_df: pd.DataFrame, output_df: pd.DataFrame) -> pd.DataFrame:
    """Compute Spearman rank correlation between parameters and outputs.

    Rank-based correlation (non-parametric) is more robust to outliers
    than Pearson correlation.

    Parameters
    ----------
    param_df : pd.DataFrame
        Parameter sweep results (columns = parameters, rows = trials)
    output_df : pd.DataFrame
        Simulation outputs (columns = metrics, rows = trials)

    Returns
    -------
    pd.DataFrame
        Correlation matrix with shape (n_params, n_outputs)
        Values in [-1, 1]; includes p-values

    Raises
    ------
    ValueError
        If DataFrames have different number of rows
    ValueError
        If DataFrames have non-numeric columns

    Examples
    --------
    >>> params = pd.DataFrame({'slope': [1, 2, 3], 'intercept': [0, 0.5, 1]})
    >>> outputs = pd.DataFrame({'expression': [0.5, 1.5, 2.5]})
    >>> corr = spearman_correlation(params, outputs)
    >>> corr.shape
    (2, 1)  # 2 params × 1 output
    """
    # Implementation...
    pass

def _clamp_to_bounds(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    """Clamp value to [lower, upper] range.

    Parameters
    ----------
    value : float
        Input value
    lower : float, optional
        Lower bound (default: 0.0)
    upper : float, optional
        Upper bound (default: 1.0)

    Returns
    -------
    float
        Value clamped to [lower, upper]
    """
    return max(lower, min(upper, value))
```

---

## Java: Tier 1 (Critical)

### Class Docstring (Tier 1)

```java
/**
 * Represents a single gene with expression level.
 *
 * // Intent (Machine-Readable Contract for Agents)
 * Purpose: Store gene identity and expression state
 * Invariant: expression_level always >= 0 (biological reality)
 * Mutation: expression_level updated; name immutable
 * Error handling: Negative levels clamped to 0; no exceptions
 *
 * Domain:
 * - name: non-null, non-empty string (e.g., "BRCA1")
 * - expression_level: float >= 0
 *
 * Boundary cases to test:
 * - name=null → NullPointerException
 * - name="" → IllegalArgumentException
 * - expression_level=-5.0 → clamped to 0.0
 * - expression_level=Float.POSITIVE_INFINITY → valid
 *
 * @author happygene team
 */
public class Gene {
    private final String name;
    private float expressionLevel;

    /**
     * Initialize a gene with name and expression level.
     *
     * // Intent
     * Precondition: name non-null and non-empty
     * Postcondition: Gene created; expression_level >= 0
     * Side effects: None
     * Error handling: Throws if name invalid; clamps expression_level
     *
     * @param name Gene identifier (non-null, non-empty)
     * @param expressionLevel Current transcription rate (clamped to >= 0)
     * @throws NullPointerException if name is null
     * @throws IllegalArgumentException if name is empty
     */
    public Gene(String name, float expressionLevel) {
        if (name == null) {
            throw new NullPointerException("name must be non-null");
        }
        if (name.isEmpty()) {
            throw new IllegalArgumentException("name must be non-empty");
        }
        this.name = name;
        this.expressionLevel = Math.max(0.0f, expressionLevel);
    }

    /**
     * Get current expression level.
     *
     * // Intent
     * Postcondition: Always returns value >= 0
     * Side effects: None (getter only)
     *
     * @return Expression level (always >= 0)
     */
    public float getExpressionLevel() {
        return expressionLevel;
    }

    /**
     * Set expression level (clamped to >= 0).
     *
     * // Intent
     * Precondition: None (any float accepted)
     * Postcondition: expression_level >= 0
     * Error handling: Negative values clamped; no exception
     *
     * @param level New expression level (will be clamped to >= 0)
     */
    public void setExpressionLevel(float level) {
        this.expressionLevel = Math.max(0.0f, level);
    }
}
```

### Method Docstring (Tier 1)

```java
/**
 * Record individual state at current generation.
 *
 * // Intent (Machine-Readable Contract for Agents)
 * Purpose: Append Individual snapshot to persistent collection
 * Preconditions:
 * - individual non-null, valid Individual with genes
 * - generation >= 0
 * - All genes have valid expression_level
 *
 * Postconditions:
 * - One row appended to internal storage
 * - Data immutable after collection
 * - Individual ownership retained by caller
 *
 * Mutation contract: Mutates internal state (this.data)
 * Side effects: May trigger GC if memory high
 *
 * Error handling:
 * - Throws NullPointerException if individual null
 * - Throws IllegalArgumentException if generation < 0
 * - Never silently fails
 *
 * Boundary cases to test:
 * - generation=0 → valid (start)
 * - generation=-1 → throws IllegalArgumentException
 * - individual with 0 genes → valid
 * - individual with 1000 genes → valid
 * - repeated call with same generation → appends multiple rows
 *
 * @param individual Individual to record (non-null)
 * @param generation Generation number (>= 0)
 * @throws NullPointerException if individual is null
 * @throws IllegalArgumentException if generation < 0
 * @throws OutOfMemoryError if internal storage exhausted
 */
public void collect(Individual individual, int generation) {
    if (individual == null) {
        throw new NullPointerException("individual must be non-null");
    }
    if (generation < 0) {
        throw new IllegalArgumentException("generation must be >= 0");
    }
    // Implementation...
}
```

---

## Java: Tier 2 (Computation)

### Class Docstring (Tier 2)

```java
/**
 * Linear gene expression model: E = slope × tf + intercept.
 *
 * // Intent (for agents)
 * Purpose: Compute linear response to transcription factor
 * Formula: E(tf) = max(0, slope × tf + intercept)
 * Domain:
 * - slope: any real number
 * - intercept: [0, ∞)
 * - tf: [0, 1] (normalized)
 *
 * Range: E(tf) ∈ [0, ∞)
 * Invariant: Expression always non-negative
 *
 * Boundary cases:
 * - slope=0: returns intercept
 * - slope<0: can return 0 if result < 0
 * - tf=0: returns max(0, intercept)
 */
public class LinearExpression implements ExpressionModel {
    private double slope;
    private double intercept;

    /**
     * Initialize linear expression model.
     *
     * // Intent
     * Precondition: intercept >= 0
     * Postcondition: Model ready to compute
     * Error handling: Throws if intercept < 0
     *
     * @param slope Sensitivity coefficient
     * @param intercept Basal expression level (>= 0)
     * @throws IllegalArgumentException if intercept < 0
     */
    public LinearExpression(double slope, double intercept) {
        if (intercept < 0.0) {
            throw new IllegalArgumentException(
                "intercept must be >= 0, got " + intercept
            );
        }
        this.slope = slope;
        this.intercept = intercept;
    }

    /**
     * Compute expression given conditions.
     *
     * // Intent
     * Formula: E = max(0, slope × tf + intercept)
     * Boundary cases: See class docstring
     *
     * @param conditions Conditions with tf_concentration [0, 1]
     * @return Expression level (always >= 0)
     */
    @Override
    public double compute(Conditions conditions) {
        double result = slope * conditions.getTfConcentration() + intercept;
        return Math.max(0.0, result);
    }
}
```

---

## C#: Tier 1 (Critical)

### Class Docstring (Tier 1)

```csharp
/// <summary>
/// Represents a single gene with expression level.
///
/// // Intent (Machine-Readable Contract for Agents)
/// Purpose: Store gene identity and expression state
/// Invariant: expression_level always >= 0 (biological reality)
/// Mutation: expression_level updated; name immutable
/// Error handling: Negative levels clamped to 0; no exceptions
///
/// Domain:
/// - name: non-null, non-empty string (e.g., "BRCA1")
/// - expression_level: double >= 0
///
/// Boundary cases to test:
/// - name=null → ArgumentNullException
/// - name="" → ArgumentException
/// - expression_level=-5.0 → clamped to 0.0
/// - expression_level=double.PositiveInfinity → valid
/// </summary>
public class Gene {
    private readonly string name;
    private double expressionLevel;

    /// <summary>
    /// Initialize a gene with name and expression level.
    ///
    /// // Intent
    /// Precondition: name non-null and non-empty
    /// Postcondition: Gene created; expression_level >= 0
    /// Side effects: None
    /// Error handling: Throws if name invalid; clamps expression_level
    /// </summary>
    /// <param name="name">Gene identifier (non-null, non-empty)</param>
    /// <param name="expressionLevel">Transcription rate (clamped to >= 0)</param>
    /// <exception cref="ArgumentNullException">if name is null</exception>
    /// <exception cref="ArgumentException">if name is empty</exception>
    public Gene(string name, double expressionLevel) {
        if (name == null) {
            throw new ArgumentNullException(nameof(name), "name must be non-null");
        }
        if (string.IsNullOrEmpty(name)) {
            throw new ArgumentException("name must be non-empty", nameof(name));
        }
        this.name = name;
        this.expressionLevel = Math.Max(0.0, expressionLevel);
    }

    /// <summary>
    /// Get current expression level.
    ///
    /// // Intent
    /// Postcondition: Always returns value >= 0
    /// Side effects: None (getter only)
    /// </summary>
    /// <returns>Expression level (always >= 0)</returns>
    public double ExpressionLevel {
        get { return expressionLevel; }
    }

    /// <summary>
    /// Set expression level (clamped to >= 0).
    ///
    /// // Intent
    /// Precondition: None (any double accepted)
    /// Postcondition: expression_level >= 0
    /// Error handling: Negative values clamped; no exception
    /// </summary>
    /// <param name="level">New expression level (clamped to >= 0)</param>
    public void SetExpressionLevel(double level) {
        this.expressionLevel = Math.Max(0.0, level);
    }
}
```

### Method Docstring (Tier 1)

```csharp
/// <summary>
/// Record individual state at current generation.
///
/// // Intent (Machine-Readable Contract for Agents)
/// Purpose: Append Individual snapshot to persistent collection
/// Preconditions:
/// - individual non-null, valid Individual with genes
/// - generation >= 0
/// - All genes have valid expression_level
///
/// Postconditions:
/// - One row appended to internal storage
/// - Data immutable after collection
/// - Individual ownership retained by caller
///
/// Mutation contract: Mutates internal state (this.data)
/// Side effects: May trigger GC if memory high
///
/// Error handling:
/// - Throws ArgumentNullException if individual null
/// - Throws ArgumentException if generation < 0
/// - Never silently fails
///
/// Boundary cases to test:
/// - generation=0 → valid (start)
/// - generation=-1 → throws ArgumentException
/// - individual with 0 genes → valid
/// - individual with 1000 genes → valid
/// </summary>
/// <param name="individual">Individual to record (non-null)</param>
/// <param name="generation">Generation number (>= 0)</param>
/// <exception cref="ArgumentNullException">if individual is null</exception>
/// <exception cref="ArgumentException">if generation < 0</exception>
/// <exception cref="OutOfMemoryException">if internal storage exhausted</exception>
public void Collect(Individual individual, int generation) {
    if (individual == null) {
        throw new ArgumentNullException(nameof(individual), "individual must be non-null");
    }
    if (generation < 0) {
        throw new ArgumentException("generation must be >= 0", nameof(generation));
    }
    // Implementation...
}
```

---

## Tips for Writing Intent Sections

1. **Formula**: Use plain text, not LaTeX
   - ✓ "E = slope × tf + intercept, clamped to [0, inf)"
   - ✗ "E = \mathbf{slope} \times \mathbf{tf} + \mathbf{intercept}"

2. **Domain/Range**: Explicit boundaries
   - ✓ "Domain: slope ∈ ℝ, intercept ∈ [0, ∞), tf ∈ [0, 1]"
   - ✗ "slope is a number"

3. **Boundary Cases**: Test scenarios, not descriptions
   - ✓ "slope=0, tf=0 → returns intercept"
   - ✗ "edge cases need to be tested"

4. **Error Handling**: Explicit contract
   - ✓ "Raises ValueError if intercept < 0; silently clamps expression_level"
   - ✗ "May throw errors"

5. **Keep It Concise**: 5-10 lines maximum
   - ✓ Focused on what agents need to know
   - ✗ Lengthy explanations (that's for humans, not Intent section)

---

**Last Updated**: February 9, 2026
**Status**: Ready to use for Phase 2 and beyond
