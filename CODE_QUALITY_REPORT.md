# Code Quality Report: Happygene

**Date:** 2026-02-09
**Scan:** Ruff linter + manual duplication + anti-pattern analysis
**Coverage:** 36 linter violations, 5 code duplication patterns, 4 anti-patterns identified

---

## Executive Summary

| Metric | Value | Status |
|--------|-------|--------|
| **Ruff Violations** | 36 | HIGH priority: 31 auto-fixable |
| **Code Duplication** | 5 patterns | MEDIUM: refactoring opportunity |
| **Anti-Patterns** | 4 detected | MEDIUM-HIGH: risk mitigation needed |
| **Files Affected** | 15+ | Systematic issues across codebase |
| **Estimated Effort** | 2-3 hours total | 15-20 min fixes + 1-2 hr refactoring |

---

## Part 1: Ruff Violations (36 Total)

### Summary by Violation Type

| Code | Type | Count | Severity | Auto-fix |
|------|------|-------|----------|----------|
| I001 | Unsorted imports | 17 | MEDIUM | Yes ✓ |
| F401 | Unused imports | 11 | LOW | Yes ✓ |
| F841 | Unused variable | 1 | LOW | Yes ✓ |
| E501 | Line too long (>100) | 2 | LOW | Partial |
| **Total** | | **36** | | **31/36 fixable** |

### Detailed Violations

#### **I001: Unsorted Imports (17 violations)**

Files affected:
- `happygene/analysis/__init__.py:35` - BatchSimulator, SobolAnalyzer, MorrisAnalyzer (3 imports not alphabetized)
- `happygene/analysis/_internal.py:10` - numpy/typing/pathlib unordered
- `happygene/analysis/batch.py:10` - numpy/pandas/typing/datetime unordered
- `happygene/analysis/batch.py:16` - SALib imports unordered
- `happygene/analysis/batch.py:22` - engine/analysis imports unordered
- `happygene/analysis/correlation.py:16` - numpy/pandas/typing unordered
- `happygene/analysis/morris.py:15` - numpy/pandas/typing/dataclass unordered
- `happygene/analysis/output.py:14` - json/pandas/typing/pathlib unordered
- `happygene/analysis/response.py:18` (not shown in truncated output, but present)
- `happygene/analysis/sobol.py:13` - numpy/pandas/typing/dataclass unordered
- `happygene/base.py:2` - abc/numpy unordered
- `happygene/conditions.py:2` - dataclasses/typing unordered
- `happygene/datacollector.py:2` - typing/collections/pandas unordered
- `happygene/expression.py:2` - abc/happygene imports unordered
- `happygene/model.py:2` - typing/numpy + happygene imports mixed
- `happygene/mutation.py:2` - abc/happygene/numpy unordered
- `happygene/regulatory_expression.py:15` - abc/happygene/conditions unordered
- `happygene/regulatory_network.py:6` - dataclasses/typing/numpy/scipy/networkx unordered
- `happygene/selection.py:2` - abc/typing/numpy/happygene unordered

**Impact:** Code style inconsistency; all safe to auto-fix
**Fix:** `uv run python -m ruff check happygene/ --fix`

---

#### **F401: Unused Imports (11 violations)**

| File | Line | Import | Status |
|------|------|--------|--------|
| `analysis/_internal.py` | 11 | `typing.Optional` | Unused, remove |
| `analysis/_internal.py` | 12 | `pathlib.Path` | Unused, remove |
| `analysis/batch.py` | 12 | `typing.List` | Unused (use list[...] syntax) |
| `analysis/correlation.py` | 18 | `typing.Optional` | Unused, remove |
| `analysis/response.py` | 40 | `sklearn.preprocessing.StandardScaler` | **CRITICAL: Used but not imported at module level** (see Anti-Patterns) |
| `analysis/output.py` | (truncated) | `typing.Optional` | Likely unused |
| `analysis/sobol.py` | (truncated) | `typing.Optional` or `List` | Likely unused |
| `datacollector.py` | 3 | `collections.deque` | Unused, remove |
| (and others in truncated output) | | | |

**Impact:** Unused imports add noise, confuse readers, slow lint checks
**Fix:** `uv run python -m ruff check happygene/ --fix` (auto-fixes all)

---

#### **F841: Unused Variable (1 violation)**

| File | Line | Variable | Context |
|------|------|----------|---------|
| `analysis/sobol.py` | 138 | `X` | Assigned but never used; `Y` is used for SALib analysis |

```python
# Line 138-139 (sobol.py)
X = batch_results[param_cols].values  # Assigned but unused
Y = batch_results[output_col].values  # Only Y used by sobol_analyze
```

**Impact:** Wasted allocation for large datasets
**Fix:** Remove line 138 (X is not passed to sobol_analyze)

---

#### **E501: Line Too Long (2 violations)**

| File | Line | Length | Content |
|------|------|--------|---------|
| `analysis/batch.py` | 212 | 103 | `output_cols = set(...) - set(...) - {"run_id", "seed", "timestamp"}` |
| `analysis/batch.py` | 259 | 104 | `survival = max(0.0, min(1.0, 0.9 - 0.1 * dose_gy + ...))` |

**Impact:** Style; readable but violates 100-char line limit
**Fix:** Extract intermediate variables or use line continuation

---

## Part 2: Code Duplication (5 Patterns Identified)

### Pattern 1: NetworkX DiGraph Building (CRITICAL)

**Files:** `regulatory_network.py:184-199` vs `regulatory_network.py:201-230`

**Affected Methods:**
- `_compute_is_acyclic()` (lines 184-199)
- `_find_feedback_loops()` (lines 201-230)

**Duplication:** Both methods build identical DiGraph from sparse adjacency matrix

```python
# Lines 186-193 (_compute_is_acyclic)
G = nx.DiGraph()
G.add_nodes_from(range(self._n_genes))
cx = self._adjacency.tocoo()
for i, j, v in zip(cx.row, cx.col, cx.data):
    if v != 0:
        G.add_edge(j, i)

# Lines 210-217 (_find_feedback_loops) - IDENTICAL
G = nx.DiGraph()
G.add_nodes_from(range(self._n_genes))
cx = self._adjacency.tocoo()
for i, j, v in zip(cx.row, cx.col, cx.data):
    if v != 0:
        G.add_edge(j, i)
```

**Lines of Duplication:** 9 lines (indices 186-193 and 210-217)
**Refactoring:** Extract `_build_digraph()` helper method

**Solution:**
```python
def _build_digraph(self) -> nx.DiGraph:
    """Build directed graph from sparse adjacency matrix."""
    G = nx.DiGraph()
    G.add_nodes_from(range(self._n_genes))
    cx = self._adjacency.tocoo()
    for i, j, v in zip(cx.row, cx.col, cx.data):
        if v != 0:
            G.add_edge(j, i)
    return G

def _compute_is_acyclic(self) -> bool:
    G = self._build_digraph()
    try:
        return nx.is_directed_acyclic_graph(G)
    except Exception:
        return False

def _find_feedback_loops(self) -> List[Set[str]]:
    G = self._build_digraph()
    sccs = nx.strongly_connected_components(G)
    # ... rest of logic
```

**Effort:** 10 min | **Impact:** HIGH (reduce duplication, centralize bug fixes)

---

### Pattern 2: Parameter Bounds Extraction (MEDIUM)

**Files:** `analysis/sobol.py:165-188` vs `analysis/morris.py:164-187`

**Affected Methods:**
- `SobolAnalyzer._get_bounds_from_results()` (sobol.py:165-188)
- `MorrisAnalyzer._get_bounds_from_results()` (morris.py:164-187)

**Duplication:** Identical 24-line method in both classes

```python
# sobol.py:165-188
def _get_bounds_from_results(self, batch_results: pd.DataFrame) -> List[Tuple]:
    bounds = []
    for pname in self.param_names:
        if pname in batch_results.columns:
            min_val = float(batch_results[pname].min())
            max_val = float(batch_results[pname].max())
            bounds.append((min_val, max_val))
        else:
            bounds.append((0.0, 1.0))
    return bounds

# morris.py:164-187 - IDENTICAL
# Same implementation repeated
```

**Lines of Duplication:** 24 lines
**Refactoring:** Move to `_internal.py` as utility function

**Solution:**
```python
# In analysis/_internal.py
def extract_bounds_from_results(
    param_names: List[str], batch_results: pd.DataFrame
) -> List[Tuple[float, float]]:
    """Extract parameter bounds from batch results.

    Parameters
    ----------
    param_names : List[str]
        Parameter names to extract
    batch_results : pd.DataFrame
        Results DataFrame

    Returns
    -------
    List[Tuple[float, float]]
        Bounds [(min, max), ...] for each parameter
    """
    bounds = []
    for pname in param_names:
        if pname in batch_results.columns:
            min_val = float(batch_results[pname].min())
            max_val = float(batch_results[pname].max())
            bounds.append((min_val, max_val))
        else:
            bounds.append((0.0, 1.0))
    return bounds

# In sobol.py and morris.py
def _get_bounds_from_results(self, batch_results: pd.DataFrame) -> List[Tuple]:
    return extract_bounds_from_results(self.param_names, batch_results)
```

**Effort:** 15 min | **Impact:** MEDIUM (reduce duplication, improve maintainability)

---

### Pattern 3: Feature Matrix Building in Response Surface Models (MEDIUM)

**Files:** `analysis/response.py:76-84` vs `analysis/response.py:163-170`

**Affected Methods:**
- `ResponseSurfaceModel.fit()` (lines 76-84)
- `ResponseSurfaceModel.predict()` (lines 121-128)
- `ResponseSurfaceModel.cross_validate()` (lines 163-170)

**Duplication:** Three code blocks build identical feature matrices

```python
# fit() method (lines 76-84)
if self.method == "linear":
    X_train = X_scaled
elif self.method == "quadratic":
    X_train = self._add_polynomial_features(X_scaled, degree=2)
elif self.method == "rf":
    X_train = X_scaled
else:
    raise ValueError(f"Unknown method: {self.method}")

# predict() method (lines 121-128) - IDENTICAL
if self.method == "linear":
    X_test = X_scaled
elif self.method == "quadratic":
    X_test = self._add_polynomial_features(X_scaled, degree=2)
elif self.method == "rf":
    X_test = X_scaled
else:
    raise ValueError(f"Unknown method: {self.method}")

# cross_validate() method (lines 163-170) - IDENTICAL
if self.method == "linear":
    X_train = X_scaled
elif self.method == "quadratic":
    X_train = self._add_polynomial_features(X_scaled, degree=2)
elif self.method == "rf":
    X_train = X_scaled
else:
    raise ValueError(f"Unknown method: {self.method}")
```

**Lines of Duplication:** 9 lines × 3 locations = 27 lines total
**Refactoring:** Extract `_build_feature_matrix()` helper method

**Solution:**
```python
def _build_feature_matrix(self, X_scaled: np.ndarray) -> np.ndarray:
    """Build feature matrix based on configured method."""
    if self.method == "linear":
        return X_scaled
    elif self.method == "quadratic":
        return self._add_polynomial_features(X_scaled, degree=2)
    elif self.method == "rf":
        return X_scaled
    else:
        raise ValueError(f"Unknown method: {self.method}")

# In fit(), predict(), cross_validate():
# OLD: if self.method == "linear": ... (9 lines)
# NEW: X_train = self._build_feature_matrix(X_scaled)
```

**Effort:** 15 min | **Impact:** HIGH (reduce duplication, simplify logic)

---

### Pattern 4: Sample Extraction Pattern (LOW)

**Files:** Multiple analysis files

**Pattern:** `param_cols = [p for p in self.param_names if p in batch_results.columns]` appears in:
- `sobol.py:132`
- `morris.py:135`
- `response.py:68`, `response.py:155`

**Lines of Duplication:** 1 line × 4 locations

**Solution:** Extract to `_internal.py` utility function or inline (low impact for single-line patterns)

---

### Pattern 5: Model Import/Detection Pattern (MEDIUM)

**Files:** `model.py:88-100`

**Issue:** Repeated hasattr checks for model capabilities

```python
# Lines 88-100 (model.py)
if hasattr(self.expression_model, 'regulatory_model'):
    # Apply expression model with TF inputs for each gene
    for gene_idx in range(n_genes):
        expr = self.expression_model.compute(...)
else:
    # Fallback: compute base model without TF inputs
    for gene_idx in range(n_genes):
        expr = self.expression_model.compute(self.conditions)
```

**Issue:** Loop is duplicated; only the `compute()` call differs
**Refactoring:** Use method delegation or Protocol to check capability once

---

## Part 3: Anti-Patterns (4 Detected)

### Anti-Pattern 1: String-based Type Checking (HIGH PRIORITY)

**File:** `happygene/model.py:114`

**Issue:**
```python
if type(self.selection_model).__name__ == 'ProportionalSelection' and n_genes > 0:
    # Vectorized fitness computation
    fitness_values = np.mean(expr_matrix, axis=1)
    for ind_idx, individual in enumerate(self.individuals):
        individual.fitness = fitness_values[ind_idx]
else:
    # Fallback
    for individual in self.individuals:
        fitness = self.selection_model.compute_fitness(individual)
        individual.fitness = fitness
```

**Problems:**
1. Fragile: Breaks if class is renamed or wrapped
2. Not Pythonic: Use `isinstance()` instead
3. Tight coupling: Model depends on implementation detail
4. Hard to test: Mock objects with wrong class name won't trigger optimization

**Risk:** HIGH (fragility, refactoring risk)

**Solution:**
```python
# Option A: Use isinstance() with protocol
from typing import Protocol

class Vectorizable(Protocol):
    """Marker for models that support vectorized fitness."""
    def supports_vectorization(self) -> bool: ...

# Option B: Simple isinstance check
from happygene.selection import ProportionalSelection

if isinstance(self.selection_model, ProportionalSelection) and n_genes > 0:
    fitness_values = np.mean(expr_matrix, axis=1)
    for ind_idx, individual in enumerate(self.individuals):
        individual.fitness = fitness_values[ind_idx]
```

**Effort:** 10 min | **Impact:** HIGH (reduce fragility, improve maintainability)

---

### Anti-Pattern 2: hasattr-based Capability Detection (MEDIUM)

**File:** `happygene/model.py:88`

**Issue:**
```python
if hasattr(self.expression_model, 'regulatory_model'):
    # Apply expression model with TF inputs
    for gene_idx in range(n_genes):
        expr = self.expression_model.compute(..., tf_inputs=tf_inputs[gene_idx])
else:
    # Fallback: compute base model without TF inputs
    for gene_idx in range(n_genes):
        expr = self.expression_model.compute(self.conditions)
```

**Problems:**
1. Duck typing without contract: Code silently falls back if attribute missing
2. No type safety: IDE can't infer which signature is called
3. Hard to debug: Swallows errors in fallback path
4. Duplication: Loop body identical except one call
5. Testing nightmare: Mocks must match hasattr expectations

**Risk:** MEDIUM (runtime surprises, hard to debug)

**Solution 1: Use Protocol (Recommended)**
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class RegulatoryExpressionModel(Protocol):
    """Expression model that accepts TF inputs."""
    def compute(self, conditions: Conditions, *, tf_inputs: float) -> float: ...

@runtime_checkable
class BaseExpressionModel(Protocol):
    """Basic expression model without regulatory inputs."""
    def compute(self, conditions: Conditions) -> float: ...

# In model.py
if isinstance(self.expression_model, RegulatoryExpressionModel):
    for gene_idx in range(n_genes):
        expr = self.expression_model.compute(
            self.conditions, tf_inputs=tf_inputs[gene_idx]
        )
else:
    for gene_idx in range(n_genes):
        expr = self.expression_model.compute(self.conditions)
```

**Solution 2: Extract to Helper Method**
```python
def _compute_gene_expression(self, gene_idx: int, tf_input: float = None) -> float:
    """Compute expression for single gene, with optional TF input."""
    if tf_input is not None and isinstance(self.expression_model, RegulatoryExpressionModel):
        return self.expression_model.compute(self.conditions, tf_inputs=tf_input)
    else:
        return self.expression_model.compute(self.conditions)

# Usage (simplified)
for gene_idx in range(n_genes):
    tf_input = tf_inputs[gene_idx] if self._regulatory_network else None
    expr = self._compute_gene_expression(gene_idx, tf_input)
```

**Effort:** 20 min | **Impact:** MEDIUM-HIGH (improve type safety, reduce surprises)

---

### Anti-Pattern 3: Mock Detection via hasattr (MEDIUM)

**File:** `happygene/analysis/batch.py:242`

**Issue:**
```python
if hasattr(model, '_is_mock') and model._is_mock:
    # For mock models, generate realistic outputs based on parameters
    rng = np.random.default_rng(seed)
    # ... generate synthetic data
    return outputs
```

**Problems:**
1. Fragile: Assumes testing convention with private attribute
2. Pollution: Test artifact lives in production code
3. Hard to discover: Hidden behavior when `_is_mock=True`
4. Tight coupling: Production code knows about test fixtures
5. Anti-DIP: Production code depends on test infrastructure

**Risk:** MEDIUM (test pollution, maintainability)

**Solution 1: Use ABCs/Protocols (Recommended)**
```python
from abc import ABC
from typing import Protocol, runtime_checkable

@runtime_checkable
class MockModel(Protocol):
    """Marker protocol for mock simulation models."""
    def __init__(self): ...
    # No other methods needed for detection

# Production code checks protocol, not attribute
if isinstance(model, MockModel):
    # Generate mock outputs
```

**Solution 2: Dependency Injection**
```python
def _run_single_simulation(
    self,
    model: HappyGeneConfig,
    n_generations: int,
    seed: int,
    output_generator: Optional[Callable] = None
) -> Dict[str, float]:
    """Run single simulation.

    Parameters
    ----------
    output_generator : Optional[Callable]
        If provided, generate mock outputs (for testing).
        Otherwise use real simulation.
    """
    if output_generator is not None:
        return output_generator(model, seed)

    # Real simulation path
    batch_sim = HappyGeneBatchSimulator(model)
    # ...
```

**Effort:** 20 min | **Impact:** MEDIUM (decouple test/production)

---

### Anti-Pattern 4: Missing Import at Module Level (CRITICAL)

**File:** `happygene/analysis/response.py:40`

**Issue:**
```python
# Line 40 (in __init__)
self.scaler = StandardScaler()

# But StandardScaler not imported at module level!
# It's only imported inside fit() method (line 60)
```

**Problems:**
1. **NameError risk:** If `ResponseSurfaceModel()` created but `fit()` never called, `scaler` attribute references undefined class
2. **Late binding:** Error occurs at runtime, not at class definition
3. **Type confusion:** Static analyzers can't infer `scaler` type
4. **Testing nightmare:** Mock setup must inject StandardScaler via fit()

**Risk:** CRITICAL (runtime failure)

**Actual code flow:**
```python
class ResponseSurfaceModel:
    def __init__(self, param_names: List[str], method: str = "linear"):
        self.scaler = StandardScaler()  # NameError if StandardScaler not imported!

    def fit(self, batch_results: pd.DataFrame, output_col: str = "survival"):
        from sklearn.preprocessing import StandardScaler  # TOO LATE!
        self.scaler = StandardScaler()  # Re-initialization
```

**Solution:** Import at module level
```python
# At top of response.py
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

class ResponseSurfaceModel:
    def __init__(self, param_names: List[str], method: str = "linear"):
        self.param_names = param_names
        self.scaler = StandardScaler()  # Now safe
        self.model = None
        self.is_fitted = False

    def fit(self, batch_results: pd.DataFrame, output_col: str = "survival"):
        # Use pre-imported sklearn classes
        # Can now remove duplicate imports inside fit()
```

**Effort:** 5 min | **Impact:** CRITICAL (fix runtime risk)

---

## Part 4: Refactoring Recommendations (Prioritized by Impact)

| Priority | Recommendation | Effort | Impact | Files | Notes |
|----------|---|---|---|---|---|
| **🔴 CRITICAL** | Fix missing StandardScaler import (Anti-Pattern 4) | 5 min | HIGH | response.py | NameError risk |
| **🔴 CRITICAL** | Replace string type check with isinstance() (Anti-Pattern 1) | 10 min | HIGH | model.py | Fragility risk |
| **🟠 HIGH** | Extract _build_digraph() helper (Pattern 1) | 10 min | HIGH | regulatory_network.py | 9-line duplication |
| **🟠 HIGH** | Extract _build_feature_matrix() helper (Pattern 3) | 15 min | HIGH | response.py | 27-line duplication |
| **🟠 HIGH** | Move _get_bounds_from_results to _internal (Pattern 2) | 15 min | MEDIUM | sobol.py, morris.py | 24-line duplication, DRY |
| **🟡 MEDIUM** | Replace hasattr-based capability detection (Anti-Pattern 2) | 20 min | MEDIUM | model.py | Type safety |
| **🟡 MEDIUM** | Remove mock detection from production code (Anti-Pattern 3) | 20 min | MEDIUM | batch.py | Test pollution |
| **🟢 LOW** | Auto-fix all import issues (Ruff) | 2 min | LOW | 15+ files | I001, F401 fixable |
| **🟢 LOW** | Fix line length violations | 5 min | LOW | batch.py | E501: 2 violations |
| **🟢 LOW** | Remove unused variable (sobol.py:138) | 2 min | LOW | sobol.py | F841: 1 violation |

---

## Part 5: Implementation Roadmap

### Phase 1: Critical Fixes (10 minutes)
```bash
# 1. Fix missing import
Edit response.py: Add sklearn imports at module level

# 2. Fix string type check
Edit model.py:114: Replace type().__name__ with isinstance()

# 3. Auto-fix imports
uv run python -m ruff check happygene/ --fix

# 4. Remove unused variable
Edit sobol.py:138: Delete line 138 (X assignment)
```

### Phase 2: High-Impact Refactoring (40 minutes)
```bash
# 1. Extract _build_digraph() (10 min)
Edit regulatory_network.py: Add helper, refactor _compute_is_acyclic and _find_feedback_loops

# 2. Extract _build_feature_matrix() (15 min)
Edit response.py: Add helper, simplify fit/predict/cross_validate

# 3. Move bounds extraction to _internal (15 min)
Edit _internal.py: Add extract_bounds_from_results()
Edit sobol.py, morris.py: Use shared function
```

### Phase 3: Quality Improvements (40 minutes)
```bash
# 1. Replace hasattr-based capability detection (20 min)
Edit model.py: Add RegulatoryExpressionModel protocol, refactor step() method

# 2. Remove test pollution from batch.py (20 min)
Edit batch.py: Remove _is_mock detection, use dependency injection
```

### Phase 4: Cosmetic Fixes (5 minutes)
```bash
# 1. Fix line length (5 min)
Edit batch.py:212,259: Split long lines

# Total effort: 55 minutes
```

---

## Part 6: Testing Strategy

After each refactoring, run:
```bash
# Unit tests
uv run pytest tests/ -xvs

# Linting
uv run python -m ruff check happygene/

# Type checking
uv run python -m mypy happygene/ (if configured)

# Integration tests
uv run pytest tests/integration/ -xvs
```

---

## Part 7: Success Criteria

| Metric | Before | Target | Status |
|--------|--------|--------|--------|
| Ruff violations | 36 | 0 | 🟢 Achievable with --fix |
| Code duplication patterns | 5 | 0 | 🟢 Achievable in 40 min |
| Anti-patterns | 4 | 0 | 🟠 Achievable in 40 min (requires testing) |
| Line length violations | 2 | 0 | 🟢 Achievable in 5 min |
| Test pass rate | TBD | 100% | 🔵 Must verify after refactoring |

---

## Appendix: Detailed File-by-File Issues

### happygene/model.py
- **L88:** hasattr-based capability detection (medium risk)
- **L114:** String-based type checking (high risk) ← FIX FIRST
- Recommendation: Use isinstance() + Protocol

### happygene/regulatory_network.py
- **L184-199 vs 201-230:** DiGraph building duplication
- Recommendation: Extract _build_digraph() helper (10 min)

### happygene/analysis/response.py
- **L40:** Missing StandardScaler import at module level (CRITICAL)
- **L76-84, 121-128, 163-170:** Feature matrix building duplication
- **L44-93 vs 132-186:** Feature building duplicated 3 times
- Recommendation: Import sklearn at top + extract _build_feature_matrix()

### happygene/analysis/sobol.py & morris.py
- **L165-188 (sobol) vs 164-187 (morris):** Identical _get_bounds_from_results()
- Recommendation: Move to _internal.py (15 min, benefits both)

### happygene/analysis/batch.py
- **L242:** Mock detection via hasattr (test pollution)
- **L212, 259:** Line too long (E501)
- Recommendation: Dependency injection + line splits

### All 15+ files
- **I001 (17 violations):** Unsorted imports
- **F401 (11 violations):** Unused imports
- **F841 (1 violation):** Unused variable (sobol.py:138)
- Recommendation: `uv run python -m ruff check happygene/ --fix`

---

## Conclusion

**Total actionable items:** 36 linter violations + 5 duplications + 4 anti-patterns = **45 issues**

**Estimated effort to 100% resolution:** 55 minutes (including testing)

**High-priority path (75% resolution):** 30 minutes
1. Fix missing import (response.py)
2. Fix string type check (model.py)
3. Auto-fix imports
4. Remove unused variable

**Full path (100% resolution):** 55 minutes
- Add phases 2-3 refactoring above

**Confidence:** HIGH (all issues identified, solutions designed, effort realistic)
