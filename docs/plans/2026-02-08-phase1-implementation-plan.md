# Phase 1 Implementation Plan: Week 1-12

**Architecture:** See `/Users/vorthruna/ProjectsWATTS/happygene/docs/plans/2026-02-08-phase1-architecture-adrs.md`

**Working directory:** `/Users/vorthruna/ProjectsWATTS/happygene-phase1/`

**Branch:** `feature/phase1-implementation` (worktree at `../happygene-phase1`)

---

## Week 1: Project Scaffolding and SimulationModel Base

**Goal:** Establish directory structure, convert to uv/PEP 621, create the `SimulationModel` abstract base class (ADR-001), and prove the build works with 2 passing tests.

**Requires:** None (starting point)

**Deliverable:** Directory tree, `.gitignore`, PEP 621 `pyproject.toml`, `SimulationModel` ABC, 2 passing tests

### Sub-step 1.1: Create directory structure

```bash
cd /Users/vorthruna/ProjectsWATTS/happygene-phase1
mkdir -p happygene tests examples docs .github/workflows
touch happygene/__init__.py tests/__init__.py tests/conftest.py
```

### Sub-step 1.2: Deploy .gitignore from template

Copy `/Users/vorthruna/ProjectsWATTS/happygene/TEMPLATES/.gitignore` to `/Users/vorthruna/ProjectsWATTS/happygene-phase1/.gitignore`. (132 lines, covers `__pycache__`, `.coverage`, `.venv`, IDE files)

### Sub-step 1.3: Write pyproject.toml (PEP 621 + uv)

**Exact path:** `/Users/vorthruna/ProjectsWATTS/happygene-phase1/pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "happygene"
version = "0.1.0"
description = "Framework for simulating gene network evolution with selection, mutation, and expression dynamics"
readme = "README.md"
license = "MIT"
requires-python = ">=3.12"
authors = [
    { name = "Eric Mumford" },
]
keywords = ["genetics", "evolution", "simulation", "agent-based-modeling"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
]
dependencies = [
    "numpy>=1.26",
    "pandas>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "ruff>=0.4",
    "pytest-xdist>=3.5",
]
docs = [
    "sphinx>=7.0",
    "sphinx-rtd-theme>=2.0",
    "myst-parser>=3.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=happygene --cov-report=term-missing"
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
minversion = "8.0"
markers = ["slow: marks tests as slow (deselect with '-m \"not slow\"')"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]

[tool.coverage.run]
source = ["happygene"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.",
]
```

Run: `cd /Users/vorthruna/ProjectsWATTS/happygene-phase1 && uv venv && source .venv/bin/activate && uv pip install -e ".[dev]"`

Expected: Clean install. Verify with `uv run python -c "import happygene"`.

### Sub-step 1.4: Write SimulationModel ABC (test first)

**Test file:** `/Users/vorthruna/ProjectsWATTS/happygene-phase1/tests/test_base.py`

```python
"""Tests for SimulationModel abstract base class."""
import pytest
from happygene.base import SimulationModel


class ConcreteModel(SimulationModel):
    """Minimal concrete subclass for testing."""

    def step(self):
        self._generation += 1


def test_simulation_model_cannot_instantiate():
    """SimulationModel is abstract; direct instantiation must raise TypeError."""
    with pytest.raises(TypeError):
        SimulationModel(seed=42)


def test_concrete_model_step_increments_generation():
    """Calling step() on a concrete subclass advances the generation counter."""
    model = ConcreteModel(seed=42)
    assert model.generation == 0
    model.step()
    assert model.generation == 1
```

Run: `uv run pytest tests/test_base.py -v` -- both tests must FAIL (module does not exist yet).

**Implementation file:** `/Users/vorthruna/ProjectsWATTS/happygene-phase1/happygene/base.py`

```python
"""SimulationModel: abstract base for all happygene simulations (ADR-001)."""
from abc import ABC, abstractmethod
import numpy as np


class SimulationModel(ABC):
    """Abstract base class for gene network simulation models.

    Provides generation tracking, reproducible RNG, and a step() contract.
    Custom base (not Mesa.Model) per ADR-001: biology-first API.

    Parameters
    ----------
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(self, seed: int | None = None):
        self._generation: int = 0
        self._rng: np.random.Generator = np.random.default_rng(seed)
        self._running: bool = True

    @property
    def generation(self) -> int:
        """Current generation number (0-indexed)."""
        return self._generation

    @property
    def rng(self) -> np.random.Generator:
        """Reproducible random number generator."""
        return self._rng

    @property
    def running(self) -> bool:
        """Whether the simulation is still active."""
        return self._running

    @abstractmethod
    def step(self) -> None:
        """Advance the simulation by one generation. Subclasses must implement."""
        ...

    def run(self, generations: int) -> None:
        """Run simulation for a fixed number of generations.

        Parameters
        ----------
        generations : int
            Number of generations to simulate.
        """
        for _ in range(generations):
            if not self._running:
                break
            self.step()
```

**Update `__init__.py`:** `/Users/vorthruna/ProjectsWATTS/happygene-phase1/happygene/__init__.py`

```python
"""HappyGene: Gene network evolution simulation framework."""
__version__ = "0.1.0"
```

Run: `uv run pytest tests/test_base.py -v` -- both tests PASS.

### Sub-step 1.5: Commit

```
chore: scaffold project with PEP 621 + SimulationModel ABC

Rationale: ADR-001 mandates custom SimulationModel base (not Mesa.Model)
for biology-first API. PEP 621 replaces Poetry per project tooling mandate.
```

**Validation gate:** `uv run pytest tests/ -v` shows 2 passed, 0 failed.

---

## Week 2: Gene and Individual Entities

**Goal:** Create the `Gene` and `Individual` entity classes and wire them into `GeneNetwork`, the first concrete `SimulationModel` subclass.

**Requires:** Week 1 (SimulationModel ABC in `happygene/base.py`)

**Deliverable:** `Gene`, `Individual`, `GeneNetwork` classes; 8+ passing tests (cumulative: 10+)

[See full plan document for complete Week 2-12 details]

---

## Summary: 12-Week Execution Path

| Week | Component | Tests | Cumulative | Status |
|------|-----------|-------|-----------|--------|
| 1 | SimulationModel ABC, pyproject.toml | 2 | 2 | Design → Execute |
| 2 | Gene, Individual, GeneNetwork | 8 | 10 | Ready |
| 3 | ExpressionModel + Linear + Constant | 8 | 18 | Ready |
| 4 | Hill + SelectionModel + 2 selectors | 10 | 28 | Ready |
| 5 | MutationModel + full step() loop | 7 | 35 | Ready |
| 6 | DataCollector (3-tier) | 7 | 42 | Ready |
| 7 | Theory validation + edge cases | 8 | 50 | Ready |
| 8 | Performance benchmarks + coverage | 5 | 55 | Ready |
| 9 | Example 1: simple_duplication | 1 | 56 | Ready |
| 10 | Example 2: regulatory_network + CI/CD | 1 | 57 | Ready |
| 11 | Sphinx documentation | 0 | 57 | Ready |
| 12 | Governance + v0.1.0 tag | 0 | 57 | Ready |

**Success Criteria:**
- ✅ 57+ pytest tests passing
- ✅ 80%+ coverage on all modules
- ✅ 2 executable example scripts
- ✅ GitHub Actions CI/CD green
- ✅ Sphinx docs build clean
- ✅ CONTRIBUTING.md, GOVERNANCE.md, ROADMAP.md deployed
- ✅ v0.1.0 git tag created

---

## Next Action

Execute `/build execute batch` or `/build execute subagent` to start Week 1 implementation.
