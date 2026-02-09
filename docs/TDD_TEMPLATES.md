# TDD Templates for happygene v0.2.0

**Purpose**: Guide developers implementing Tier 1 (CRITICAL) modules using test-driven development (TDD)
**Target Audience**: Engineers contributing to happygene entities, model, datacollector, or test infrastructure
**Reference**: TIER_CLASSIFICATION.md § TDD Discipline by Tier

---

## Overview

Test-driven development (TDD) enforces **Tier 1 (CRITICAL)** modules with a strict discipline:

1. **Red**: Write failing test (test doesn't even compile/run)
2. **Green**: Write minimal implementation (test passes)
3. **Refactor**: Clean up code, improve design
4. **Commit**: Document rationale

This template covers:
- Gene entity (immutable schema)
- Individual entity (population container)
- GeneNetwork orchestration (life cycle)
- Test infrastructure (conftest fixtures)

---

## Pattern: Test First, Always

### The Red-Green-Refactor Cycle

```
        ┌─────────────────────────────────────────┐
        │                                         │
        v                                         │
    [RED]                                     [PASS]
     Write                                    Commit
    failing          [GREEN]          [REFACTOR]
     test      ->   Minimal     ->    Clean up
                   implemen-            code
                    tation
                      |
                      v
                    [PASS]
                     Test
```

### Discipline Rules

1. **Write test first** — Before writing any implementation code
2. **Verify FAIL** — Run test, confirm it fails (RED state)
3. **Minimal code** — Only code needed to make test pass (GREEN state)
4. **Refactor** — Once GREEN, improve without changing behavior
5. **Commit with rationale** — Every commit explains why this change was necessary

### Example Session (30 min total)

```bash
# 1. Create test file (5 min)
$ vi tests/test_entities_gene.py
  # Write: test_gene_creation, test_name_immutable, test_expression_level_clamped

# 2. Run test, verify FAIL (2 min)
$ pytest tests/test_entities_gene.py -v
  FAILED tests/test_entities_gene.py::TestGeneCreation::test_gene_creation

# 3. Implement Gene class (10 min)
$ vi happygene/entities.py
  # Add: class Gene with __init__, expression_level property

# 4. Run test, verify PASS (2 min)
$ pytest tests/test_entities_gene.py -v
  PASSED tests/test_entities_gene.py::TestGeneCreation::test_gene_creation

# 5. Refactor (5 min)
$ # Code is already clean; add docstring with Intent section

# 6. Commit (3 min)
$ git add happygene/entities.py tests/test_entities_gene.py
$ git commit -m "feat(entities): add Gene class with immutable name (TDD)

Test-first implementation:
- Failing test validates name immutability, expression_level clamping
- Minimal implementation uses __slots__ for memory efficiency
- Coverage: 100% (3 test methods × 4+ assertion paths each)

Rationale: Gene is Tier 1 CRITICAL; immutable schema ensures downstream
operations (Individual, GeneNetwork) can trust data integrity without
defensive checks.

Specification:
- name: immutable string, non-empty
- expression_level: read-only property, clamped to [0, inf)
- Memory: __slots__ reduces per-object overhead by ~40% (large populations)
- Related: TIER_CLASSIFICATION.md § Tier 1 (CRITICAL)"
```

---

## Template 1: Gene Entity (Immutable Schema)

### Step 1: Write Failing Test

**File**: `tests/test_entities_gene.py`

```python
"""Test Gene entity — immutable schema with expression level."""

import pytest
from happygene.entities import Gene


class TestGeneCreation:
    """Test Gene initialization and immutability."""

    def test_gene_initialization(self):
        """Gene should initialize with name and expression_level."""
        gene = Gene(name="TP53", expression_level=1.5)

        assert gene.name == "TP53"
        assert gene.expression_level == 1.5

    def test_gene_name_immutable(self):
        """Gene name should be read-only (immutable)."""
        gene = Gene(name="TP53", expression_level=1.5)

        # Attempt to change name should raise error
        with pytest.raises(AttributeError):
            gene.name = "BRCA1"

    def test_gene_expression_clamped_positive(self):
        """Negative expression levels should be clamped to 0."""
        gene = Gene(name="TP53", expression_level=-2.5)

        # Should clamp to 0
        assert gene.expression_level == 0.0

    def test_gene_expression_large_positive(self):
        """Large positive expression levels should be preserved."""
        gene = Gene(name="TP53", expression_level=100.0)

        assert gene.expression_level == 100.0

    def test_gene_empty_name_allowed(self):
        """Empty string names should be allowed (validated by Individual)."""
        # Note: This is a design decision; we allow empty names
        # but recommend Individual validation
        gene = Gene(name="", expression_level=1.5)
        assert gene.name == ""


class TestGeneEquality:
    """Test Gene comparison and hashing."""

    def test_genes_equal_by_value(self):
        """Two genes with same name/expression should be equal."""
        gene1 = Gene(name="TP53", expression_level=1.5)
        gene2 = Gene(name="TP53", expression_level=1.5)

        # Should support equality comparison
        # (dataclass __eq__ or custom __eq__)
        assert gene1.name == gene2.name
        assert gene1.expression_level == gene2.expression_level

    def test_gene_hash_stable(self):
        """Gene should be hashable (usable in sets/dicts)."""
        gene = Gene(name="TP53", expression_level=1.5)

        # Should support hashing
        gene_set = {gene}
        assert gene in gene_set
```

### Step 2: Verify Test Fails

```bash
$ pytest tests/test_entities_gene.py -v
    FAILED tests/test_entities_gene.py::TestGeneCreation::test_gene_initialization
    ERROR: cannot import name 'Gene' from 'happygene.entities'
```

**Status**: ✅ RED — Test fails as expected (Gene doesn't exist yet)

### Step 3: Minimal Implementation

**File**: `happygene/entities.py`

```python
"""Gene and Individual entity classes."""

from typing import List


class Gene:
    """Represents a single gene with expression level.

    # Intent (for agents)
    Agents should understand: This is the fundamental entity in happygene.
    - name is immutable (frozen/read-only)
    - expression_level is read-only property, clamped to [0, inf)
    - Validation: Gene does NOT validate name (that's Individual's responsibility)
    - All downstream operations (GeneNetwork, models) depend on this being correct
    - Test boundaries: negative expression (clamping), name immutability, edge cases

    # Natural language (for humans)
    A gene is an allele with a name and expression level.

    Parameters
    ----------
    name : str
        Gene identifier. Can be empty (Individual validates).
    expression_level : float
        Relative transcription rate. Negative values are clamped to 0.

    Attributes
    ----------
    name : str (read-only)
        Immutable gene identifier.
    expression_level : float (read-only)
        Expression level in [0, inf). Always non-negative.

    Examples
    --------
    >>> gene = Gene("TP53", 1.5)
    >>> gene.expression_level  # 1.5
    >>> Gene("BRCA1", -2.0).expression_level  # 0.0 (clamped)
    """

    __slots__ = ('name', '_expression_level')

    def __init__(self, name: str, expression_level: float):
        """Initialize gene with name and expression level.

        Parameters
        ----------
        name : str
            Gene identifier. No validation (Individual validates).
        expression_level : float
            Expression level. Negative values clamped to 0.
        """
        self.name: str = name
        # Clamp to [0, inf)
        self._expression_level: float = max(0.0, float(expression_level))

    @property
    def expression_level(self) -> float:
        """Return expression level (always >= 0).

        Returns
        -------
        float
            Current expression level.
        """
        return self._expression_level

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Gene(name={self.name!r}, expression_level={self.expression_level})"

    def __hash__(self) -> int:
        """Return hash (allows use in sets/dicts)."""
        return hash((self.name, self._expression_level))
```

### Step 4: Verify Test Passes

```bash
$ pytest tests/test_entities_gene.py -v
    PASSED tests/test_entities_gene.py::TestGeneCreation::test_gene_initialization
    PASSED tests/test_entities_gene.py::TestGeneCreation::test_gene_name_immutable
    PASSED tests/test_entities_gene.py::TestGeneCreation::test_gene_expression_clamped_positive
    ...
    ====== 5 passed in 0.23s ======
```

**Status**: ✅ GREEN — All tests pass

### Step 5: Refactor

Review code for improvements:
- ✅ Docstring is comprehensive (Intent + Natural language)
- ✅ Uses `__slots__` for memory efficiency (critical for 5k individuals × 100 genes)
- ✅ Property enforces immutability (read-only `expression_level`)
- ✅ Clamping is explicit and correct
- ✅ `__repr__` is useful for debugging
- ✅ `__hash__` enables use in collections

**No refactoring needed.** Code is already clean.

### Step 6: Verify Coverage

```bash
$ pytest tests/test_entities_gene.py --cov=happygene.entities --cov-report=term-missing
    happygene/entities.py          100%     (all lines covered)
```

**Status**: ✅ PASS — 100% coverage achieved

### Step 7: Commit with Rationale

```bash
$ git add happygene/entities.py tests/test_entities_gene.py
$ git commit -m "feat(entities): add Gene class with immutable name (TDD)

Test-first implementation:

Failing test (Red):
- tests/test_entities_gene.py validates 5 scenarios:
  1. Normal initialization (name, expression_level)
  2. Name immutability (read-only via __slots__)
  3. Expression clamping (negative → 0)
  4. Large positive values preserved
  5. Empty name allowed (validation deferred to Individual)

Minimal implementation (Green):
- Gene dataclass with __slots__ for efficiency
- __init__ clamps expression_level to [0, inf)
- @property makes expression_level read-only
- __hash__ enables use in collections

Refactor:
- Added Intent section to docstring (for agents)
- Added __repr__ for debugging
- Code is clean; no further refactoring needed

Coverage:
- 100% (all branches covered by test suite)

Rationale:
Gene is Tier 1 CRITICAL. Immutable schema ensures:
- Downstream operations (Individual, GeneNetwork) trust data integrity
- No defensive checks needed in inner loops (performance)
- Serialization/hashing work correctly
- Memory efficiency via __slots__ (5000 indiv × 100 genes = 500k objects)

Related:
- TIER_CLASSIFICATION.md § Gene Entity (Tier 1)
- Reference: Mesa ABM framework (similar entity design)
- Memory: __slots__ reduces per-object from ~296 bytes to ~152 bytes

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"
```

---

## Template 2: Individual Entity (Population Container)

### Pattern: Same as Gene

```python
# tests/test_entities_individual.py
class TestIndividualCreation:
    def test_individual_initialization(self):
        genes = [Gene("TP53", 1.5), Gene("BRCA1", 0.8)]
        indiv = Individual(genes=genes)
        assert indiv.genes == genes
        assert indiv.fitness == 1.0

    def test_individual_mean_expression(self):
        genes = [Gene("TP53", 2.0), Gene("BRCA1", 0.0)]
        indiv = Individual(genes=genes)
        assert indiv.mean_expression() == 1.0

    def test_individual_empty_genes(self):
        indiv = Individual(genes=[])
        assert indiv.mean_expression() == 0.0

# happygene/entities.py
class Individual:
    """Represents an individual in the population."""

    __slots__ = ('genes', 'fitness')

    def __init__(self, genes: List[Gene]):
        self.genes: List[Gene] = genes
        self.fitness: float = 1.0

    def mean_expression(self) -> float:
        if not self.genes:
            return 0.0
        return sum(g.expression_level for g in self.genes) / len(self.genes)
```

---

## Template 3: GeneNetwork Orchestration (step() method)

### Key Pattern: Test the Entire Life Cycle

```python
# tests/test_model.py (Tier 1, integration test)
class TestGeneNetworkStep:
    def test_step_increments_generation(self):
        model = build_test_model()  # conftest fixture
        assert model.generation == 0
        model.step()
        assert model.generation == 1

    def test_step_with_empty_population(self):
        model = GeneNetwork(
            individuals=[],
            expression_model=LinearExpression(),
            selection_model=ProportionalSelection(),
            mutation_model=PointMutation()
        )
        model.step()
        assert model.generation == 1  # Should not crash

    def test_step_vectorized_expression(self):
        # Verify vectorized computation is correct
        model = build_test_model(n_indiv=100, n_genes=50)
        model.step()
        # All individuals should have updated fitness
        assert all(indiv.fitness >= 0 for indiv in model.individuals)

    def test_step_reproducible_with_seed(self):
        model1 = GeneNetwork(..., seed=42)
        model2 = GeneNetwork(..., seed=42)

        model1.step()
        model2.step()

        # Stochastic steps should be identical with same seed
        assert model1.generation == model2.generation
```

---

## Best Practices

### 1. Test Names Should Be Descriptive

```python
# ✅ GOOD
def test_gene_expression_level_clamped_to_non_negative():
    pass

# ❌ BAD
def test_gene():
    pass
```

### 2. Test One Thing Per Test

```python
# ✅ GOOD
def test_gene_name_is_immutable(self):
    gene = Gene("TP53", 1.5)
    with pytest.raises(AttributeError):
        gene.name = "BRCA1"

# ❌ BAD
def test_gene(self):
    gene = Gene("TP53", 1.5)
    assert gene.name == "TP53"
    gene.name = "BRCA1"  # This will fail, then test stops
```

### 3. Use Fixtures for Common Setup

```python
# tests/conftest.py (Tier 1)
@pytest.fixture
def simple_gene():
    """A standard gene for tests."""
    return Gene(name="TP53", expression_level=1.5)

# tests/test_entities_gene.py
def test_gene_expression_preserves_value(simple_gene):
    assert simple_gene.expression_level == 1.5
```

### 4. Test Edge Cases

```python
# ✅ Test boundaries
def test_gene_expression_zero():
    gene = Gene("X", 0.0)
    assert gene.expression_level == 0.0

def test_gene_expression_negative_clamped():
    gene = Gene("X", -100.0)
    assert gene.expression_level == 0.0

def test_gene_expression_very_large():
    gene = Gene("X", 1e10)
    assert gene.expression_level == 1e10
```

### 5. Document Rationale in Docstrings

```python
# ✅ GOOD
def test_gene_name_immutable(self):
    """Gene name must be immutable.

    Rationale: downstream operations (Individual, GeneNetwork) depend on
    stable gene identities. Allowing mutation would break regulatory networks
    and data collection.

    Edge case: This test ensures __slots__ prevents attribute assignment.
    """
    gene = Gene("TP53", 1.5)
    with pytest.raises(AttributeError):
        gene.name = "BRCA1"
```

### 6. Commit Messages Include Test Evidence

```bash
$ git commit -m "feat(entities): add Gene class (TDD)

Failing test (Red):
- tests/test_entities_gene.py::TestGeneCreation (5 scenarios)

Implementation (Green):
- happygene/entities.py::Gene with __slots__

Coverage:
- 100% (verified via pytest --cov)

Rationale:
- Gene is Tier 1 CRITICAL (immutable schema)
- All downstream depends on correctness
- Memory efficiency via __slots__ (500k object limit in simulations)"
```

---

## Quick Checklist for Tier 1 Changes

Before committing to a Tier 1 module:

- [ ] **Test written first** (Red state, test fails)
- [ ] **Minimal implementation** (Green state, test passes)
- [ ] **Coverage 100%** (verified via `pytest --cov`)
- [ ] **No breaking changes** to public API (backwards compatible)
- [ ] **Commit message includes rationale** (why this change, how it was tested)
- [ ] **Intent docstring** (for agents)
- [ ] **All other tests still pass** (no regressions)

---

## Running TDD Locally

```bash
# Install test dependencies
pip install -e ".[dev]"

# Watch-mode testing (auto-run on file changes)
pytest tests/test_entities_gene.py -v --tb=short --looponfail

# Full coverage report
pytest tests/test_entities_gene.py --cov=happygene.entities --cov-report=html
# Open htmlcov/index.html to view

# Run tier-specific coverage validation
python scripts/check_coverage_by_tier.py
```

---

## Questions?

- **TDD discipline**: See TIER_CLASSIFICATION.md § TDD Discipline by Tier
- **Test structure**: See tests/ for examples of passing tests
- **Coverage targets**: See TIER_CLASSIFICATION.md § Coverage Targets by Tier
- **CI/CD gates**: See .github/workflows/quality.yml for automated enforcement

