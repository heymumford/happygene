# Agent-Native Development: Quick Reference

**Decision**: Adopt TEAM C (Risk-Stratified) approach with empirical refinement

**Effective**: Phase 2 (starting Week 1)

---

## Coverage Requirements by Tier

| Tier | Name | Coverage | Examples | Rationale |
|---|---|---|---|---|
| **Tier 1** | Critical | **100%** | DataCollector, RegulatoryNetwork, Gene, Individual | Data integrity; silent failures = invalid results |
| **Tier 2** | Computation | **90%** | Expression, Selection, Mutation models | Math correctness; users validate output |
| **Tier 3** | Utility | **70%** | Analysis tools, batch processing, helpers | Localized bugs; user validation sufficient |
| **Tier 4** | Legacy | **50%** | Deprecated code, pending refactor | Will be removed; don't invest |

---

## Docstring Standards

### Python (All Tiers Use NumPy Base)

**Tier 1-2: NumPy + Intent Section (Required)**

```python
def critical_function(data: Data) -> Result:
    """One-line summary.

    # Intent (for agents)
    Purpose: What this does
    Formula: E = max(0, slope × tf + intercept) [if mathematical]
    Domain: Valid inputs
    Range: Output range
    Invariants: What must be true
    Boundary cases: [case] → [result]
    Error contract: What exceptions raised

    # API Surface
    Parameters
    ----------
    data : Data
        Description

    Returns
    -------
    Result
        Description

    Raises
    ------
    ValueError: If [condition]
    """
```

**Tier 3: NumPy Only**

```python
def utility_function(x: float) -> float:
    """Clamp value to [0, 1].

    Parameters
    ----------
    x : float
        Input value

    Returns
    -------
    float
        Clamped value
    """
```

---

### Java (Phase 3+)

**Tier 1-2: JavaDoc + Intent Section**

```java
/**
 * Critical function with Intent section.
 *
 * // Intent (for agents)
 * Purpose: What this does
 * Formula: [if mathematical]
 * Domain: Valid inputs
 * Range: Output range
 *
 * @param data Input data (non-null)
 * @return Result (non-null)
 * @throws IllegalArgumentException if preconditions violated
 */
public Result criticalFunction(Data data) {
    if (data == null) throw new IllegalArgumentException("data must be non-null");
    // ...
}
```

---

### C# (Phase 3+)

**Tier 1-2: XMLDoc + Intent Section**

```csharp
/// <summary>
/// Critical function with Intent section.
///
/// // Intent (for agents)
/// Purpose: What this does
/// Formula: [if mathematical]
/// Domain: Valid inputs
/// Range: Output range
/// </summary>
/// <param name="data">Input data (non-null)</param>
/// <returns>Result (non-null)</returns>
/// <exception cref="ArgumentNullException">if data is null</exception>
public Result CriticalFunction(Data data) {
    if (data == null) throw new ArgumentNullException(nameof(data));
    // ...
}
```

---

## CI/CD Enforcement

**GitHub Actions** (Automatic on every push):

```yaml
- name: Enforce tier-based coverage
  run: python scripts/check_coverage_by_tier.py
  # Fails if:
  # - Tier 1 < 100%
  # - Tier 2 < 90%
  # - Tier 3 < 70%
```

**Local Testing** (Before push):

```bash
# Run tests with coverage
pytest --cov=happygene --cov-report=json

# Check tier compliance
python scripts/check_coverage_by_tier.py
```

---

## Module Classification (Phase 1 Result)

### Tier 1: Critical (100%)
- `datacollector.py` — Data integrity critical
- `regulatory_network.py` — Reproducibility critical
- `entities.py` (Gene, Individual) — Domain model
- `base.py` — Simulation foundation

### Tier 2: Computation (90%)
- `expression.py` — LinearExpression, Hill, Constant
- `selection.py` — Proportional, Threshold, Epistatic
- `mutation.py` — PointMutation, Duplication, Conversion
- `conditions.py` — Environmental state
- `regulatory_expression.py` — Composite models

### Tier 3: Utility (70%)
- `analysis/` — Statistical utilities (correlation, morris, sobol, batch)
- `model.py` — GeneNetwork orchestration (mostly)

### Tier 4: Legacy (50%)
- Deprecated modules (if any; currently none)

---

## For Agent Prompts

When requesting code generation, include:

```
# Coverage & Documentation Requirements

Tier: [CRITICAL | COMPUTATION | UTILITY]
Coverage target: [100% | 90% | 70%]

Docstring format: NumPy + Intent section (see DOCSTRING_TEMPLATES.md)

For Tier 1-2 code:
- Add Intent section with:
  - Purpose / Formula (if applicable)
  - Domain and Range
  - Invariants
  - Boundary cases to test
  - Error handling contract

Generate tests to achieve target coverage.
Report: % coverage achieved, uncovered lines (if any).
```

Example:
```
Generate ExpressionModel subclass for Michaelis-Menten kinetics.

Tier: COMPUTATION (target: 90% coverage)
Docstring: NumPy + Intent section
Include tests: All boundary cases (Km edge cases, substrate ranges)

Report coverage when done.
```

---

## Testing Checklist (for PRs)

Before merging any PR:

- [ ] Coverage report included (`--cov-report=term-missing`)
- [ ] Tier-based coverage met:
  - [ ] Tier 1 >= 100%
  - [ ] Tier 2 >= 90%
  - [ ] Tier 3 >= 70%
- [ ] Docstrings present:
  - [ ] Tier 1-2: Intent sections included
  - [ ] All: NumPy format
- [ ] No untested error paths (Tier 1)
- [ ] Tests include boundary cases (Tier 1-2)
- [ ] All examples still pass

---

## Key Decisions (Why This Approach)

| Question | Answer | Why |
|---|---|---|
| **100% everywhere?** | No, risk-stratified (100%/90%/70%) | 100% on critical code is worth it; 100% on utilities wastes effort |
| **Machine-readable docstrings?** | Yes, Intent sections for Tier 1-2 | Agents need explicit contracts; natural language insufficient for edge cases |
| **Test agent-generated code differently?** | Yes, higher standards | Agents miss edge cases; structured docstrings help agents self-correct |
| **Enforce at CI/CD?** | Yes, automatic checks | Manual reviews miss coverage gaps; automation is consistent |
| **How to refine thresholds?** | Empirical measurement (Phase 4) | Based on actual bugs, not theory; thresholds calibrated to measured risk |

---

## Timeline

| Phase | Weeks | Deliverable |
|---|---|---|
| **Phase 1: Audit** | 1-2 | Module classification, coverage audit, gaps identified |
| **Phase 2: CI/CD** | 3-4 | GitHub Actions enforcement, CONTRIBUTING.md updated |
| **Phase 3: Docstrings** | 5-8 | Intent sections added to Tier 1-2, templates published |
| **Phase 4: Validation** | 5-8 (parallel) | Empirical risk model implemented, Phase 2 predictions |
| **Phase 2 Execution** | 9-12 | All agent code meets tier targets, 3+ external PRs |

---

## Common Pitfalls & Solutions

| Pitfall | Solution |
|---|---|
| **"Intent sections are too verbose"** | Keep to 5-8 lines; focus on formula, domain, boundary cases |
| **"Coverage drops in refactoring"** | Acceptable; refactoring may expose untested paths (add tests for them) |
| **"Tier classification is subjective"** | Use empirical data (bug patterns) to validate; document rationale |
| **"Agents can't parse Intent sections"** | Test agent comprehension; refine format based on performance |
| **"100% coverage is impossible"** | Acceptable to exclude: `__repr__`, NotImplementedError, `if __name__` |

---

## Resources

| Document | Purpose |
|---|---|
| `DEBATE_ITERATION_3_AgentNative.md` | Full debate (12 agent positions, evidence, rationale) |
| `AGENT_NATIVE_IMPLEMENTATION_CHECKLIST.md` | Week-by-week implementation plan |
| `DOCSTRING_TEMPLATES.md` | Examples (Python, Java, C#) |
| `scripts/check_coverage_by_tier.py` | Automated enforcement script |
| `.github/workflows/test.yml` | CI/CD configuration |

---

## Questions?

**For coverage decisions**: See DEBATE_ITERATION_3_AgentNative.md, Teams A/B/C sections

**For docstring format**: See DOCSTRING_TEMPLATES.md and examples in happygene source

**For implementation**: See AGENT_NATIVE_IMPLEMENTATION_CHECKLIST.md

---

**Last Updated**: February 9, 2026
**Status**: Ready for implementation (Phase 2 kickoff)
