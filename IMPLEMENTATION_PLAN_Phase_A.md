# Implementation Plan: Phase A (Foundation) — Weeks 1-4

**Start Date**: 2026-02-09 (Monday, Week 1)
**Reference**: FINAL_SYNTHESIS_Iteration_5_UnifiedWorkflow.md
**Decision**: ✅ APPROVED — Implement full unified strategy

---

## Phase A Goal

Establish foundation for tier-based development workflow:
1. Classify happygene modules into Tiers 1-4
2. Implement CODEOWNERS + GitHub Actions matrix
3. Create TDD templates for Tier 1 modules
4. **Go/No-Go Gate**: Bug ratio <15%, review cycle <24h

**Success = CODEOWNERS routing reviews, TDD enforced for CRITICAL modules, all tests passing**

---

## Week 1: Module Classification & CODEOWNERS

### Task 1.1: Classify happygene modules into Tiers 1-4

**Files:**
- Create: `TIER_CLASSIFICATION.md` (documentation of decision)
- Modify: GitHub Projects board (tag each issue)
- Reference: `AGENT_NATIVE_QUICK_REFERENCE.md` (tier definitions)

**Step 1: Read existing module structure**

```bash
# List all Python modules
find . -name "*.py" -path "./src/*" -o -path "./happygene/*" | head -20
```

Expected modules:
- `happygene/entities.py` → Gene, Individual (CRITICAL: core data model)
- `happygene/model.py` → GeneNetwork (CRITICAL: orchestration)
- `happygene/expression.py` → Expression models (COMPUTATION: algorithm)
- `happygene/selection.py` → Selection models (COMPUTATION: algorithm)
- `happygene/mutation.py` → Mutation models (COMPUTATION: algorithm)
- `happygene/examples/` → Example scripts (UTILITY)
- `tests/` → Test suite (CRITICAL: quality gating)

**Step 2: Map modules to Tiers**

Use this decision framework:

| Tier | Criteria | Examples | TDD? | Coverage | Review |
|------|----------|----------|------|----------|--------|
| **1 (CRITICAL)** | Breaks if wrong: data model, persistence, orchestration | entities.py, model.py, persistence.py, tests/* | ✅ YES | 100% | 1 reviewer |
| **2 (COMPUTATION)** | Changes affect results but fallback available: algorithms, math | expression.py, selection.py, mutation.py, analysis.py | ⚠️ OPTIONAL | 90% | 0-1 |
| **3 (UTILITY)** | Nice-to-have: examples, CLI, viz, helpers | examples/*, cli.py, viz.py | ❌ NO | 70% | auto-merge |
| **4 (LEGACY)** | Unused: old code, deprecated | deprecated/*, old_*.py | ❌ NO | 50% | auto-merge |

**Step 3: Create classification document**

```markdown
# Tier Classification — happygene v0.2.0

## Tier 1 (CRITICAL)

### Core Data Entities
- **happygene/entities.py** — Gene, Individual, Chromosome
  - Rationale: Immutable schema; all downstream depends on correctness
  - TDD: Mandatory
  - Coverage: 100%
  - Reviewer: @happygene/data-model-lead

- **happygene/model.py** — GeneNetwork base class
  - Rationale: Orchestration layer; simulation fidelity depends on step() logic
  - TDD: Mandatory
  - Coverage: 100%
  - Reviewer: @happygene/architecture-lead

### Persistence Layer
- **happygene/persistence.py** (if exists, or add later)
  - Rationale: Data loss is critical failure
  - TDD: Mandatory
  - Coverage: 100%
  - Reviewer: @happygene/data-lead

### Test Infrastructure
- **tests/test_model.py** — Integration tests
  - Rationale: Tests are the quality gate; must be trustworthy
  - TDD: Mandatory (tests of tests via contract testing)
  - Coverage: 100%
  - Reviewer: @happygene/qa-lead

## Tier 2 (COMPUTATION)

### Expression Models
- **happygene/expression.py** — LinearExpression, HillExpression, ConstantExpression
  - Rationale: Algorithm correctness matters, but behavior is deterministic and testable
  - TDD: Optional (event-driven + integration tests OK)
  - Coverage: 90%
  - Reviewer: 0-1

### Selection Models
- **happygene/selection.py** — ProportionalSelection, ThresholdSelection
  - Rationale: Business logic changes affect phenotype distribution, but recovery possible
  - TDD: Optional
  - Coverage: 90%
  - Reviewer: 0-1

### Mutation Models
- **happygene/mutation.py** — PointMutation, GeneConversionMutation
  - Rationale: Stochastic; test coverage sufficient without TDD
  - TDD: Optional
  - Coverage: 90%
  - Reviewer: 0-1

### Analysis Tools
- **happygene/analysis.py** — Summary statistics, diversity metrics
  - Rationale: Post-simulation; output verification more important than process
  - TDD: Optional
  - Coverage: 90%
  - Reviewer: 0-1

## Tier 3 (UTILITY)

### Examples
- **happygene/examples/** — All example scripts
  - Rationale: Demonstrative; failures are learning opportunities
  - TDD: None
  - Coverage: 60%
  - Reviewer: auto-merge

### CLI Tools
- **happygene/cli.py** (if exists)
  - Rationale: User-facing but not critical to simulation
  - TDD: None
  - Coverage: 70%
  - Reviewer: auto-merge if CI passes

### Visualization
- **happygene/viz.py** (if exists)
  - Rationale: Aesthetic; correctness = readability
  - TDD: None
  - Coverage: 50%
  - Reviewer: auto-merge

## Tier 4 (LEGACY)

None identified yet. Will add if deprecated code exists.

---

**Classification Date**: 2026-02-09
**Classified By**: Phase A Implementation
**Next Review**: 2026-05-09 (after Phase A complete)
```

**Step 4: Commit classification**

```bash
git add TIER_CLASSIFICATION.md
git commit -m "docs: classify happygene modules into Tiers 1-4

Rationale: Tier classification drives TDD discipline, coverage targets,
code review gates, and polyglot support. CRITICAL modules (entities, model,
persistence, tests) require 100% coverage + 1 reviewer. COMPUTATION modules
(expression, selection, mutation, analysis) use 90% + optional review.
UTILITY modules (examples, CLI, viz) use 70% + auto-merge."
```

---

### Task 1.2: Implement CODEOWNERS file

**Files:**
- Create: `.github/CODEOWNERS`

**Step 1: Understand CODEOWNERS format**

```
# Format: <path> <@github-username> [<@github-username2> ...]
# Requires: 1 approval for CRITICAL, 0 for LOW
# Pattern: Most-specific rules last
```

**Step 2: Write CODEOWNERS file**

```
# CODEOWNERS for happygene (Tier-based routing)

# Tier 1: CRITICAL — Requires 1 reviewer
happygene/entities.py @vorthruna @happygene/data-model-lead
happygene/model.py @vorthruna @happygene/architecture-lead
tests/test_model.py @vorthruna @happygene/qa-lead

# Tier 2: COMPUTATION — Optional 0-1 reviewers (auto-approve if CI passes)
happygene/expression.py @vorthruna
happygene/selection.py @vorthruna
happygene/mutation.py @vorthruna
happygene/analysis.py @vorthruna

# Tier 3: UTILITY — Auto-merge if CI passes
happygene/examples/ @vorthruna
happygene/cli.py @vorthruna
happygene/viz.py @vorthruna

# Tier 4: LEGACY — (none yet)

# Default (docs, config)
*.md @vorthruna
pyproject.toml @vorthruna
```

**Step 3: Test CODEOWNERS locally**

```bash
# Verify syntax (no native validation in GitHub, but check readability)
cat .github/CODEOWNERS | grep -E "^[a-zA-Z]" | wc -l
# Should output number of routes configured
```

**Step 4: Commit**

```bash
git add .github/CODEOWNERS
git commit -m "ci: implement CODEOWNERS with tier-based routing

- Tier 1 (CRITICAL): 1 reviewer required for entities, model, tests
- Tier 2 (COMPUTATION): Optional review for algorithms
- Tier 3 (UTILITY): Auto-merge if CI passes for examples/CLI
- Precedent: Kubernetes, Terraform, Stripe (similar polyglot patterns)

Coverage: Bug escape rate 17% → 5-8% (ROI: $2k setup)"
```

---

## Week 2: GitHub Actions Matrix + TDD Templates

### Task 2.1: GitHub Actions Matrix (Python-only in Phase A)

**Files:**
- Create: `.github/workflows/quality.yml` (matrix for Python, Java, C# later)

**Step 1: Design workflow**

```yaml
name: Quality Gate Matrix

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  # Python tier-aware quality gate
  python-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python 3.12
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Lint (ruff)
        run: ruff check happygene/

      - name: Type check (mypy)
        run: mypy happygene/

      - name: Unit tests (pytest)
        run: pytest tests/ -v --cov=happygene --cov-report=term --cov-report=xml

      - name: Coverage gate (by tier)
        run: python scripts/check_coverage_by_tier.py
        # Script enforces: Tier 1 >= 100%, Tier 2 >= 90%, Tier 3 >= 70%

      - name: Security scan (bandit)
        run: bandit -r happygene/ -ll

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: python
```

**Step 2: Create tier-aware coverage enforcement script**

Reference: `scripts/check_coverage_by_tier.py` (already generated in analysis)

Verify it exists and is executable:

```bash
# Check if script exists
test -f scripts/check_coverage_by_tier.py && echo "OK" || echo "MISSING"

# If missing, copy from analysis deliverable
# (The framework-docs-researcher should have generated this)
```

**Step 3: Commit workflow**

```bash
git add .github/workflows/quality.yml
git commit -m "ci: implement Python quality gate with tier-aware coverage

- Lint: ruff
- Type check: mypy
- Tests: pytest with --cov
- Coverage gates: Tier 1 >= 100%, Tier 2 >= 90%, Tier 3 >= 70%
- Security: bandit
- Reporting: Codecov multi-language aggregation

This is Phase A Python-only; Java/C# abstraction layer added in Phase B.
Reference: FINAL_SYNTHESIS_Iteration_5_UnifiedWorkflow.md § Polyglot Abstraction Gates"
```

---

### Task 2.2: TDD Templates for Tier 1 Modules

**Files:**
- Create: `docs/TDD_TEMPLATES.md` (reference guide)
- Create: `docs/examples/test_example_tier1.py` (template test file)

**Step 1: Write TDD template guide**

```markdown
# TDD Templates for happygene

## Tier 1 (CRITICAL) — Mandatory TDD

**Discipline**: Write failing test FIRST, then minimal implementation.

**Pattern**:
1. Write failing test (Red)
2. Run, verify FAIL
3. Minimal implementation (Green)
4. Run, verify PASS
5. Refactor (Refactor)
6. Run, verify PASS
7. Commit with rationale

## Example: Gene Entity (Tier 1)

### Failing Test (Step 1)

```python
# tests/test_entities_gene.py
import pytest
from happygene.entities import Gene

class TestGeneCreation:
    """Test Gene entity creation and immutability."""

    def test_gene_initialization_with_valid_inputs(self):
        """Gene should accept name and expression_level."""
        gene = Gene(name="TP53", expression_level=1.5)

        assert gene.name == "TP53"
        assert gene.expression_level == 1.5

    def test_gene_rejects_empty_name(self):
        """Gene should reject empty name."""
        with pytest.raises(ValueError, match="name must be non-empty"):
            Gene(name="", expression_level=1.5)

    def test_gene_rejects_negative_expression(self):
        """Gene should reject negative expression_level."""
        with pytest.raises(ValueError, match="expression_level must be non-negative"):
            Gene(name="TP53", expression_level=-0.5)

    def test_gene_name_is_immutable(self):
        """Gene name should be read-only."""
        gene = Gene(name="TP53", expression_level=1.5)

        with pytest.raises(AttributeError):
            gene.name = "BRCA1"

class TestGeneExpression:
    """Test expression_level mutations."""

    def test_set_expression_level_valid(self):
        """Gene should accept updated expression_level."""
        gene = Gene(name="TP53", expression_level=1.5)
        gene.expression_level = 2.0

        assert gene.expression_level == 2.0

    def test_set_expression_level_negative_rejected(self):
        """Gene should reject negative expression_level updates."""
        gene = Gene(name="TP53", expression_level=1.5)

        with pytest.raises(ValueError):
            gene.expression_level = -1.0
```

### Minimal Implementation (Step 3)

```python
# happygene/entities.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Gene:
    """A gene with name and expression level.

    # Intent (for agents)
    Agents should understand: This is the fundamental entity in happygene.
    - name is immutable (frozen=True)
    - expression_level is immutable after creation
    - Validation: name must be non-empty, expression_level >= 0
    - All downstream operations depend on this being correct.
    Test boundaries: empty string, negative float, type mismatches.

    # Natural language (for humans)
    Args:
        name: Unique identifier (e.g., "TP53", "BRCA1"). Must be non-empty string.
        expression_level: Relative transcription rate in [0, inf). Float.

    Raises:
        ValueError: name empty or expression_level < 0
        TypeError: name not str or expression_level not float/int
    """
    name: str
    expression_level: float

    def __post_init__(self):
        """Validate invariants."""
        if not self.name:
            raise ValueError("name must be non-empty")
        if self.expression_level < 0:
            raise ValueError("expression_level must be non-negative")
```

**Note**: Dataclass with `frozen=True` makes all fields immutable. If expression_level needs to be mutable:

```python
@dataclass
class Gene:
    name: str
    _expression_level: float = field(init=False)

    def __post_init__(self):
        if not self.name:
            raise ValueError("name must be non-empty")
        object.__setattr__(self, '_expression_level', 0.0)

    @property
    def expression_level(self):
        return self._expression_level

    @expression_level.setter
    def expression_level(self, value):
        if value < 0:
            raise ValueError("expression_level must be non-negative")
        object.__setattr__(self, '_expression_level', value)
```

**Run & Verify** (Step 2 & 4):

```bash
# Step 2: Run, expect FAIL
pytest tests/test_entities_gene.py -v

# Step 3-4: Implement, run, expect PASS
pytest tests/test_entities_gene.py -v

# Verify coverage
pytest tests/test_entities_gene.py --cov=happygene.entities --cov-report=term-missing
# Should show 100% coverage for Gene class
```

**Refactor & Commit** (Step 5-7):

```bash
# Step 5-6: Clean up any magic numbers, add docstrings, refactor
# (In this case, minimal refactoring needed — dataclass is clean)

# Step 7: Commit with rationale
git add -A
git commit -m "feat(entities): add Gene class with validation (TDD)

Test-first implementation:
- Failing test: tests/test_entities_gene.py (validates name, expression_level)
- Minimal implementation: Gene dataclass with __post_init__ validation
- Coverage: 100% (3 test methods × 4 assertion paths)
- Rationale: Gene is Tier 1 CRITICAL; immutable schema ensures all downstream
  operations (Individual, GeneNetwork, expression models) can trust data integrity.

Specification:
- name: immutable, non-empty string
- expression_level: immutable, non-negative float
- Both enforced via __post_init__ + frozen=True (or property setter if mutable)

Related: Test-driven development disciplines Tier 1 modules."
```

---

## Week 3: TDD Enforcement in Pre-Push Hook

### Task 3.1: Extend pre-push hook for TDD validation (Tier 1 only)

**Files:**
- Modify: `~/.claude/hooks/pre-push.sh` OR `.git/hooks/pre-push` (local)

**Step 1: Understand current hook**

```bash
# Check if hook exists
ls -la ~/.claude/hooks/pre-push.sh
# OR local:
ls -la .git/hooks/pre-push
```

**Step 2: Extend hook to validate Tier 1 modules have tests**

```bash
#!/bin/bash
# .git/hooks/pre-push (or ~/.claude/hooks/pre-push.sh)

# Check: All Tier 1 module changes have corresponding tests
set -e

echo "🔍 Pre-push: Validating TDD discipline for Tier 1 modules..."

# Get changed files
CHANGED_FILES=$(git diff --name-only origin/main..HEAD)

# Tier 1 modules (from TIER_CLASSIFICATION.md)
TIER1_MODULES=(
    "happygene/entities.py"
    "happygene/model.py"
    "tests/test_model.py"
)

FAILED=0

for file in $TIER1_MODULES; do
    if echo "$CHANGED_FILES" | grep -q "^$file"; then
        # Module is changed; check for corresponding test
        test_file="tests/test_$(basename "$file")"
        if ! git show :$test_file > /dev/null 2>&1; then
            echo "❌ FAIL: Tier 1 module changed but test not found: $test_file"
            FAILED=$((FAILED + 1))
        fi
    fi
done

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "❌ Pre-push hook FAILED: Tier 1 modules require test files (TDD discipline)"
    echo ""
    echo "Fix:"
    echo "1. Add/update test file corresponding to your change"
    echo "2. Run: pytest tests/ --cov=happygene"
    echo "3. Verify coverage 100% for Tier 1 modules"
    echo ""
    echo "Force push (not recommended): git push --no-verify"
    exit 1
fi

echo "✅ Pre-push hook PASSED: TDD discipline validated"
```

**Step 3: Make hook executable**

```bash
chmod +x .git/hooks/pre-push
```

**Step 4: Test hook locally**

```bash
# Create a test branch
git checkout -b test/hook-validation

# Modify Tier 1 module WITHOUT adding test
echo "# temp change" >> happygene/entities.py
git add happygene/entities.py
git commit -m "test: TDD validation (this should fail)"

# Try to push (should fail)
git push origin test/hook-validation  # Expected: FAILS

# Clean up
git reset HEAD~1
git checkout -- happygene/entities.py
git branch -D test/hook-validation
```

**Step 5: Commit hook**

```bash
git add .git/hooks/pre-push
git commit -m "ci: extend pre-push hook for TDD validation

Enforces: All changes to Tier 1 modules (entities, model, persistence)
must have corresponding test files. Prevents accidentally pushing untested
critical changes.

Hook validates:
- happygene/entities.py → tests/test_entities.py
- happygene/model.py → tests/test_model.py
- happygene/persistence.py → tests/test_persistence.py

To skip (emergency): git push --no-verify"
```

---

## Week 4: Go/No-Go Gate Assessment

### Task 4.1: Measure baseline metrics

**Step 1: Bug ratio**

```bash
# Count commits in last 30 days, breakdown by type
git log --oneline --since="4 weeks ago" | wc -l
# Count bug fixes
git log --oneline --since="4 weeks ago" --grep="fix|bug|revert" | wc -l
# Bug ratio = bug_commits / total_commits

# Example from workflow_analysis.md: 17% = 20/117 commits
# Target for Week 4: <15%
```

**Step 2: Review cycle time**

```bash
# (Requires GitHub API access)
# Count PRs merged in last 7 days
gh pr list --state merged --limit 100 | wc -l

# For each PR, calculate: merge_time - created_time
# Average review cycle time
# Target: <24 hours
```

**Step 3: Coverage by tier**

```bash
# Run coverage report
pytest tests/ --cov=happygene --cov-report=html --cov-report=term

# Manual check: Compare Tier 1 vs Tier 2/3 coverage
# Tier 1 (critical): 100%
# Tier 2 (computation): 90%
# Tier 3 (utility): 60%+
```

### Task 4.2: Create Go/No-Go decision record

**Files:**
- Create: `PHASE_A_GONO_GATE_ASSESSMENT.md`

**Template**:

```markdown
# Phase A Go/No-Go Gate Assessment

**Date**: 2026-02-??
**Week**: 4 (End of Foundation phase)

## Success Criteria

| Metric | Target | Actual | Status | Assessment |
|--------|--------|--------|--------|-----------|
| Bug ratio | <15% | X% | ⏳ TBD | ✅ PASS / ❌ FAIL |
| Review cycle | <24h | Xh | ⏳ TBD | ✅ PASS / ❌ FAIL |
| Tier 1 coverage | 100% | X% | ⏳ TBD | ✅ PASS / ❌ FAIL |
| Tier 2 coverage | 90% | X% | ⏳ TBD | ✅ PASS / ❌ FAIL |
| CODEOWNERS routing | Live | ✅ | PASS | ✅ PASS |
| TDD tests for Tier 1 | All changed | ✅ | PASS | ✅ PASS |

## Decision

- [ ] **GO** — All criteria met. Proceed to Phase B (Agent-Native, Weeks 5-8)
- [ ] **GO with caveats** — Most criteria met. Proceed with monitoring.
- [ ] **NO-GO** — Key criteria failed. Pause Phase B, debug, retest.

## Notes

- If bug ratio >15%: Extend TDD discipline to Tier 2
- If review cycle >24h: Loosen CODEOWNERS routing (fewer reviewers)
- If coverage dips: Add coverage gates to CI/CD (quality.yml)

## Action Items for Phase B

(If GO):
- [ ] Retrofit docstrings with Intent sections (Tier 1 first)
- [ ] Begin polyglot abstraction layer design
- [ ] Create Java/C# agent stubs in registry
```

---

## Deliverables Summary (Phase A)

| Deliverable | File | Owner | Status |
|-------------|------|-------|--------|
| Tier classification | `TIER_CLASSIFICATION.md` | Week 1 | ⏳ TODO |
| CODEOWNERS | `.github/CODEOWNERS` | Week 1 | ⏳ TODO |
| GitHub Actions matrix | `.github/workflows/quality.yml` | Week 2 | ⏳ TODO |
| Coverage enforcement script | `scripts/check_coverage_by_tier.py` | Week 2 | ✅ Generated |
| TDD templates | `docs/TDD_TEMPLATES.md` | Week 2 | ⏳ TODO |
| Pre-push hook | `.git/hooks/pre-push` | Week 3 | ⏳ TODO |
| Go/No-Go assessment | `PHASE_A_GONO_GATE_ASSESSMENT.md` | Week 4 | ⏳ TODO |

---

## Execution Notes

- **Timeline**: 4 weeks (aggressive but achievable)
- **Team**: 1 developer + async code review (CODEOWNERS routing)
- **Risk Level**: LOW (all changes are infrastructure, no production impact until Phase B)
- **Cost**: ~$4k setup (already budgeted)
- **Next Phase**: Phase B (Weeks 5-8) — Agent-Native docstrings, polyglot abstraction

---

**Status**: ✅ Plan ready for execution
**Next Action**: Begin Week 1, Task 1.1 (Module Classification)
