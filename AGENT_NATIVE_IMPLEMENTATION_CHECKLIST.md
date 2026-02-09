# Agent-Native Development Implementation Checklist

**Status**: Ready to implement (reference DEBATE_ITERATION_3_AgentNative.md for full rationale)

**Timeline**: Phased implementation across Phase 2

---

## Phase 1: Audit & Measurement (Weeks 1-2)

- [ ] **Classify existing modules by tier**
  - [ ] Review all Python files in `happygene/`
  - [ ] Classify each as Tier 1, 2, 3, or 4
  - [ ] Document classification in file headers (see template below)
  - [ ] Create mapping: `TIER_CLASSIFICATION.md`

- [ ] **Run coverage audit by tier**
  - [ ] Execute: `pytest --cov=happygene --cov-report=json`
  - [ ] Run: `python scripts/check_coverage_by_tier.py`
  - [ ] Generate report: `COVERAGE_AUDIT_PHASE1.md`
  - [ ] Identify gaps:
    - [ ] Tier 1 files below 100%?
    - [ ] Tier 2 files below 90%?
    - [ ] Tier 3 files below 70%?

- [ ] **Document current docstring coverage**
  - [ ] Scan for existing Intent sections in docstrings
  - [ ] Identify Tier 1-2 functions lacking Intent
  - [ ] Create remediation list: `DOCSTRING_GAPS.md`

---

## Phase 2: CI/CD Implementation (Weeks 3-4)

- [ ] **Implement tier-based coverage checking**
  - [ ] Add `scripts/check_coverage_by_tier.py` (already done ✓)
  - [ ] Test script locally:
    ```bash
    pytest --cov=happygene --cov-report=json
    python scripts/check_coverage_by_tier.py
    ```
  - [ ] Verify output format matches expected

- [ ] **Update GitHub Actions workflow**
  - [ ] Edit `.github/workflows/test.yml`
  - [ ] Add step: Call `scripts/check_coverage_by_tier.py`
  - [ ] Set exit code handling: fail if script returns non-zero
  - [ ] Test on feature branch:
    ```bash
    git checkout -b feature/tier-coverage-gates
    # Make a small coverage gap to test
    git push -u origin feature/tier-coverage-gates
    # Verify GitHub Actions fails appropriately
    ```

- [ ] **Implement docstring validation (optional Phase 2b)**
  - [ ] Create `scripts/check_docstring_intent.py`
  - [ ] Scan for "# Intent" section in Tier 1-2 functions
  - [ ] Add GitHub Actions step for docstring check
  - [ ] Make non-blocking (warning only) for Phase 2

- [ ] **Update CONTRIBUTING.md**
  - [ ] Add section: "Coverage Requirements by Tier"
  - [ ] Add section: "Docstring Standards"
  - [ ] Include examples (Python, Java, .NET)
  - [ ] Link to `DEBATE_ITERATION_3_AgentNative.md`

---

## Phase 3: Docstring Enhancement (Weeks 5-8)

- [ ] **Add Intent sections to Tier 1 modules**
  - [ ] `datacollector.py`:
    - [ ] Class docstring: Add Intent section
    - [ ] `collect()` method: Add Intent section
    - [ ] All other public methods: Add Intent sections
  - [ ] `regulatory_network.py`:
    - [ ] Class docstring: Add Intent section
    - [ ] All public methods: Add Intent sections
  - [ ] `entities.py` (Gene, Individual):
    - [ ] Class docstrings: Add Intent sections
    - [ ] All public methods: Add Intent sections

- [ ] **Add Intent sections to Tier 2 modules**
  - [ ] `expression.py`:
    - [ ] ExpressionModel base class: Add Intent
    - [ ] All concrete implementations: Add Intent
    - [ ] Boundary case documentation
  - [ ] `selection.py`:
    - [ ] SelectionModel base class: Add Intent
    - [ ] All concrete implementations: Add Intent
  - [ ] `mutation.py`:
    - [ ] MutationModel base class: Add Intent
    - [ ] All concrete implementations: Add Intent

- [ ] **Create docstring templates**
  - [ ] Python (NumPy + Intent): `DOCSTRING_TEMPLATES.md`
  - [ ] Java (JavaDoc + Intent): `DOCSTRING_TEMPLATES.md`
  - [ ] C# (XMLDoc + Intent): `DOCSTRING_TEMPLATES.md`
  - [ ] Add examples for each tier

---

## Phase 4: Empirical Risk Modeling (Weeks 5-8, parallel)

- [ ] **Implement bug-risk scoring**
  - [ ] Create `scripts/empirical_coverage_model.py` (from Agent 12)
  - [ ] Function: `calculate_bug_risk(file_path, coverage, code_age_days)`
  - [ ] Function: `get_git_age(file_path)` using git log
  - [ ] Test with Phase 1 code:
    ```bash
    python scripts/empirical_coverage_model.py > coverage_targets.txt
    ```

- [ ] **Validate empirical model against Phase 1 bugs**
  - [ ] List all Phase 1 bugs (from git history, issues)
  - [ ] Map each bug to file + coverage at time of bug
  - [ ] Check if empirical model correctly predicted high-risk files
  - [ ] Report accuracy (target: >80%)

- [ ] **Generate Phase 2 risk predictions**
  - [ ] For each planned Phase 2 module, predict coverage requirement
  - [ ] Example: RegulatoryNetwork (new, phase 2) → Predict 100%
  - [ ] Example: BenchmarkAnalysis (new, phase 2) → Predict 80%
  - [ ] Create: `PHASE2_COVERAGE_PREDICTIONS.md`

---

## Phase 5: Phase 2 Enforcement (Weeks 9-12)

- [ ] **Apply tiers to Phase 2 code**
  - [ ] Before agent work begins, classify planned modules
  - [ ] Document tier in ticket/PR description
  - [ ] Set coverage target in PR checklist

- [ ] **Agent checklist for Phase 2**
  - [ ] Code completeness: All functions have docstrings
  - [ ] Tier 1 coverage: >= 100% (DataCollector, RegulatoryNetwork)
  - [ ] Tier 2 coverage: >= 90% (Expression, Selection, Mutation extensions)
  - [ ] Tier 3 coverage: >= 70% (Batch analysis, new utilities)
  - [ ] Intent sections: Present in Tier 1-2 docstrings

- [ ] **Code review checklist (for humans)**
  - [ ] Coverage report included in PR
  - [ ] Tier-based enforcement passed
  - [ ] Docstring Intent sections present (Tier 1-2)
  - [ ] No untested error paths in Tier 1 code
  - [ ] Test quality: Edge cases documented

---

## Phase 6: Documentation & Playbook (Weeks 9-12)

- [ ] **Create agent-native development playbook**
  - [ ] File: `AGENT_NATIVE_DEVELOPMENT_GUIDE.md`
  - [ ] Section: "Understanding Tier-Based Coverage"
  - [ ] Section: "Writing Machine-Readable Docstrings"
  - [ ] Section: "Test Generation for Agents"
  - [ ] Examples: Python, Java, .NET

- [ ] **Update project documentation**
  - [ ] README.md: Link to agent-native guide
  - [ ] CONTRIBUTING.md: Update coverage requirements
  - [ ] docs/theory.md or equivalent: Add docstring conventions
  - [ ] GOVERNANCE.md: Document tier classification process

- [ ] **Create reproducibility checklist**
  - [ ] File: `REPRODUCIBILITY_CHECKLIST.md`
  - [ ] For external contributors: what coverage to achieve
  - [ ] For academic publication: coverage report + docstring audit
  - [ ] For regulatory compliance: traceability requirements

---

## Validation Gates

### Week 2 Validation (Audit Complete)
- [ ] Coverage audit report exists: `COVERAGE_AUDIT_PHASE1.md`
- [ ] All modules classified by tier
- [ ] No Tier 1 modules below 100% (or remediation plan exists)
- [ ] Coverage report shows improvement trend

### Week 4 Validation (CI/CD Live)
- [ ] GitHub Actions: Coverage check step passes
- [ ] Test PR with coverage gap: Blocks merge as expected
- [ ] Test PR with sufficient coverage: Allows merge
- [ ] CONTRIBUTING.md updated with new requirements

### Week 8 Validation (Docstrings Complete)
- [ ] All Tier 1 modules have Intent sections
- [ ] All Tier 2 modules have Intent sections
- [ ] `DOCSTRING_TEMPLATES.md` published
- [ ] Example PRs use new docstring format

### Week 12 Validation (Phase 2 Compliant)
- [ ] Phase 2 agent-generated code: 100% Tier 1, 90% Tier 2, 70% Tier 3
- [ ] All new code includes Intent sections (Tier 1-2)
- [ ] 3+ external PRs meet coverage standards
- [ ] Empirical model accuracy > 80% (validated against bugs)

---

## File Templates

### Module Classification Header

Add this to top of each file:

```python
"""Module for X functionality.

# Module Classification
Tier: [CRITICAL | STABLE | EXPERIMENTAL | LEGACY]
Coverage Target: [100% | 90% | 70% | 50%]

Rationale: [Why this tier?]
- Example: "CRITICAL because data corruption risk is high"
- Example: "EXPERIMENTAL because algorithm not yet published"
- Example: "UTILITY because users validate output"

Status: [STABLE | IN_DEVELOPMENT | DEPRECATED]
"""
```

### Function/Class Docstring (Tier 1: Critical)

```python
def critical_function(input_data: Data) -> Result:
    """One-line summary.

    # Intent (Machine-Readable Contract for Agents)
    Purpose: [What does this accomplish?]
    Preconditions: [Valid inputs?]
    Postconditions: [Guaranteed outputs?]
    Invariants: [What must always be true?]
    Side effects: [How does this modify state?]
    Error handling: [What exceptions can it raise?]

    Mutation contract: [If mutating state, how?]

    # Boundary Cases (for test generation)
    - Case 1: [Description] → [Expected result]
    - Case 2: [Description] → [Expected result]

    # API Surface (Human-Readable)
    Parameters
    ----------
    input_data : Data
        Description

    Returns
    -------
    Result
        Description

    Raises
    ------
    ValueError
        If [specific condition]

    Examples
    --------
    >>> critical_function(Data(value=5))
    Result(value=10)
    """
```

### Function Docstring (Tier 2: Computation)

```python
def compute_function(data: Data) -> float:
    """One-line summary.

    # Intent (for agents)
    Formula: [If mathematical, exact formula]
    Domain: [Valid input ranges]
    Range: [Output value range]
    Boundary cases: [Special handling?]

    # API Surface
    Parameters
    ----------
    data : Data
        Description

    Returns
    -------
    float
        Description

    Examples
    --------
    >>> compute_function(Data(x=1.0))
    0.5
    """
```

### Function Docstring (Tier 3: Utility)

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
        Value clamped to [0, 1]
    """
```

---

## Risk Mitigation

### Risk: Tier Classification is Subjective

**Mitigation**:
- Use empirical bug data to validate tier choices
- Document rationale for each tier assignment
- Review tier choices with domain experts
- Adjust tiers after Phase 2 based on actual bug patterns

### Risk: Intent Sections Become Outdated

**Mitigation**:
- Require docstring updates in every PR that changes behavior
- Add linter rule to flag mismatches (future work)
- Document in CONTRIBUTING.md: "If you change behavior, update Intent section"

### Risk: Coverage Targets are Too Strict/Loose

**Mitigation**:
- Start Phase 2 with proposed thresholds
- Track actual bug metrics vs. coverage thresholds
- Adjust thresholds after Q1 2026 (after Phase 2 feedback)
- Document decisions in ADR (Architecture Decision Record)

### Risk: Agents Struggle with Machine-Readable Docstrings

**Mitigation**:
- Start with natural language + examples
- Gradually add Intent sections for critical functions
- Test agent comprehension with Phase 2 code generation
- Refine format based on agent performance

---

## Success Criteria

| Milestone | Target | Evidence |
|---|---|---|
| **Week 2**: Audit Complete | All modules classified, gaps identified | COVERAGE_AUDIT_PHASE1.md |
| **Week 4**: CI/CD Live | GitHub Actions blocks non-compliant PRs | GitHub workflow runs pass/fail correctly |
| **Week 8**: Docstrings Complete | Tier 1-2 have Intent sections | Pull request with all Intent sections |
| **Week 12**: Phase 2 Compliant | 100% Tier 1, 90% Tier 2, 70% Tier 3 | Coverage report + external PRs meet thresholds |
| **End Phase 2**: Validated Model | Empirical risk model accuracy > 80% | Bug metrics vs. predictions comparison |

---

## Next Steps

1. **Immediate**: Review `DEBATE_ITERATION_3_AgentNative.md` for full rationale
2. **Week 1**: Schedule kickoff meeting with team
3. **Week 1**: Assign classification task (recommend: human review + empirical validation)
4. **Week 2**: Implement CI/CD gates
5. **Weeks 3-4**: Deploy to repository; validate on feature branches
6. **Weeks 5-12**: Execute Phase 2 with tier-based enforcement

---

**Document Status**: Ready for implementation (reference DEBATE_ITERATION_3_AgentNative.md)
**Last Updated**: February 9, 2026
**Owner**: happygene project team
