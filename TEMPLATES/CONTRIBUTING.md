# Contributing to HappyGene

Thank you for your interest in contributing to HappyGene! This document outlines how to get involved, whether you're reporting bugs, suggesting features, or submitting code.

## Code of Conduct

HappyGene is committed to providing a welcoming and inspiring community for all. We expect all contributors to follow these principles:

- Be respectful and inclusive
- Assume good intent
- Focus on what's best for the community

## How Can You Contribute?

### 1. Report Bugs

Found a bug? Help us fix it!

**Before submitting:**
1. Check [existing issues](https://github.com/yourusername/happygene/issues) to avoid duplicates
2. Gather information:
   - Python version: `python --version`
   - HappyGene version: `pip show happygene`
   - OS (macOS/Linux/Windows)

**When submitting:**
```markdown
**Describe the bug**
A clear, concise description of what happened.

**Minimal reproducible example**
```python
import happygene
# Minimal code that reproduces the issue
```

**Expected behavior**
What you expected to happen.

**Environment**
- Python: 3.11
- HappyGene: 0.1.0
- OS: macOS 14.2
```

### 2. Suggest Features or Improvements

Have an idea? Open a discussion or issue!

**Good feature requests include:**
- Specific use case (what problem does it solve?)
- Why it's important to HappyGene
- Example usage or pseudocode

### 3. Submit Code (Pull Requests)

#### Getting Started

**Step 1: Fork and clone**
```bash
git clone https://github.com/yourusername/happygene.git
cd happygene
```

**Step 2: Set up development environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests to verify setup
pytest tests/
```

**Step 3: Create feature branch**
```bash
git checkout -b feature/your-feature-name
```

Use descriptive names: `feature/hill-expression-model`, `fix/gene-mutation-bug`, not `feature/stuff`.

#### Development Workflow

**Make your changes:**
- One logical change per commit
- Write tests for new features
- Update docstrings
- Follow Python style conventions (see style guide below)

**Example workflow:**
```bash
# Write test first (TDD recommended)
# Edit tests/test_my_feature.py

# Run tests to see them fail
pytest tests/test_my_feature.py

# Implement feature
# Edit happygene/my_module.py

# Run tests to see them pass
pytest tests/test_my_feature.py

# Run full test suite
pytest tests/

# Commit when tests pass
git add happygene/my_module.py tests/test_my_feature.py
git commit -m "feat: add new expression model"
```

**Style guide:**

```python
# Good: Clear variable names, docstrings
class HillExpressionModel(ExpressionModel):
    """Gene expression following Hill equation with cooperativity.

    Parameters
    ----------
    v_max : float
        Maximum expression level
    k : float
        Half-saturation constant
    n : float
        Hill coefficient (cooperativity)
    """

    def __init__(self, v_max: float, k: float, n: float):
        self.v_max = v_max
        self.k = k
        self.n = n

    def calculate_expression_level(self, gene, conditions):
        """Calculate expression level given conditions."""
        tf = conditions["tf_concentration"]
        return self.v_max * (tf ** self.n) / (self.k ** self.n + tf ** self.n)

# Bad: Unclear variable names, no docs
class HEM(EM):
    def __init__(self, vm, k, n):
        self.vm = vm
        self.k = k
        self.n = n

    def calc(self, g, c):
        return self.vm * (c["x"] ** self.n) / (self.k ** self.n + c["x"] ** self.n)
```

#### Testing Requirements

**All code changes require tests:**

```python
# tests/test_new_feature.py
import pytest
from happygene import MyNewClass

def test_basic_functionality():
    """Test basic creation and usage."""
    obj = MyNewClass(param=10)
    assert obj.param == 10

def test_edge_case():
    """Test with edge case values."""
    obj = MyNewClass(param=0)
    result = obj.compute()
    assert result >= 0

def test_integration():
    """Test integration with broader system."""
    model = GeneNetwork(n_individuals=10)
    # Your integration test
    assert model.step() is None  # Returns None (side-effect based)
```

**Run tests locally before submitting:**
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=happygene tests/

# Run specific test file
pytest tests/test_new_feature.py -v

# Run specific test
pytest tests/test_new_feature.py::test_basic_functionality -v
```

**Minimum coverage requirement:** 80% for new code

#### Commit Message Format

Follow this format:

```
<type>: <subject>

<body>

Closes: #<issue-number>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring (no behavior change)
- `test:` Test additions/fixes
- `docs:` Documentation
- `ci:` CI/CD configuration
- `chore:` Build, dependencies

**Examples:**
```
feat: add Hill cooperative binding expression model

Implements Hill equation with configurable n-tuple
cooperativity. Enables modeling of transcription factor
binding with multiple regulatory sites.

Closes: #5
```

```
fix: correct gene mutation probability calculation

Previous implementation incorrectly applied mutation
rate multiplicatively instead of additively. Now
correctly samples from binomial distribution.

Closes: #12
```

#### Submit Your PR

**Before pushing:**
```bash
# Ensure tests pass
pytest tests/

# Ensure no uncommitted changes
git status

# Push to your fork
git push origin feature/your-feature-name
```

**On GitHub:**
1. Open a pull request from your fork to `main`
2. Fill in the PR template:
   - Describe changes clearly
   - Link related issues
   - Mention if this is a breaking change

**PR checklist:**
- [ ] Tests pass locally (`pytest tests/`)
- [ ] No test regressions
- [ ] New features have tests
- [ ] Docstrings added/updated
- [ ] No __pycache__ or .coverage committed
- [ ] Commit message follows format

**What happens next:**
- Maintainers review your PR (usually within 48 hours)
- May ask for changes (don't take personally—we're improving together)
- Once approved, we merge!

## Development Tips

### Quick Commands

```bash
# Run tests and coverage
pytest --cov=happygene --cov-report=html tests/

# Check code style
black --check happygene/
ruff check happygene/

# Auto-format code
black happygene/
ruff check --fix happygene/

# Run specific test repeatedly (useful for debugging)
pytest tests/test_file.py::test_name -v -s --tb=short

# Run with print statements visible
pytest -s tests/test_file.py
```

### Environment Variables

Useful for development:

```bash
# Run tests with verbose output
export PYTEST_ADDOPTS="-v"

# Run tests in parallel (faster)
pytest -n auto tests/

# Generate HTML coverage report
pytest --cov=happygene --cov-report=html tests/
open htmlcov/index.html
```

### Debugging

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Run test to break
pytest tests/test_file.py -s

# In pdb prompt:
# n = next line
# s = step into function
# c = continue
# p variable = print variable
# h = help
```

## Types of Contributions We Need

### Good First Issues
- Documentation improvements
- Example models
- Bug fixes with clear reproduction steps
- Test additions

**Time: 1-4 hours**

### Core Contributions
- New expression/selection/mutation models
- Performance optimizations
- Test coverage improvements
- API enhancements

**Time: 4-16 hours**

### Advanced Contributions
- SBML import/export
- GPU acceleration
- Visualization tools
- ML integration

**Time: 40+ hours**

## Questions?

- **How to use HappyGene?** → [Getting Started](docs/getting_started.md)
- **How to set up dev environment?** → See "Getting Started" section above
- **Stuck on a bug?** → [Open a Discussion](https://github.com/yourusername/happygene/discussions)
- **Have a feature idea?** → [Open a Discussion](https://github.com/yourusername/happygene/discussions)

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- GitHub contributors page
- Release notes

We appreciate all contributions, whether code, documentation, bug reports, or ideas!

---

**Thank you for contributing to HappyGene!** 🧬
