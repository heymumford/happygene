# Agent-Native Development Standards: Complete Index

**Decision Finalized**: February 9, 2026
**Status**: Ready for Phase 2 Implementation

This folder contains the complete framework for agent-native development standards in happygene, including coverage thresholds, docstring conventions, and CI/CD enforcement.

---

## Core Documents

### 1. **DEBATE_ITERATION_3_AgentNative.md** (Primary)
**Purpose**: Full debate with evidence-based decision framework

Contains:
- **TEAM A**: Strict 100% coverage + formal docstrings (4 positions)
  - Agent 1: Code-Simplicity-Reviewer
  - Agent 2: Security-Sentinel
  - Agent 3: TDD-Verification-Tester
  - Agent 4: Agent-Native-Reviewer
- **TEAM B**: Pragmatic 80% + natural language (4 positions)
  - Agent 5: Delivery-First-Strategist
  - Agent 6: Pragmatist
  - Agent 7: Cost-Optimizer
  - Agent 8: Agentic-Speed-Champion
- **TEAM C**: Risk-Stratified Coverage (4 positions)
  - Agent 9: Data-Integrity-Guardian
  - Agent 10: Architecture-Strategist
  - Agent 11: Complexity-Classifier
  - Agent 12: Evidence-Synthesizer
- **SYNTHESIS**: Hybrid recommendation (TEAM C + empirical)

**When to Read**: For detailed evidence, trade-offs, and rationale behind each coverage approach

---

### 2. **AGENT_NATIVE_QUICK_REFERENCE.md** (Start Here)
**Purpose**: One-page summary for developers

Contains:
- Coverage requirements by tier (Tier 1-4)
- Docstring standards (Python, Java, C#)
- CI/CD enforcement checklist
- Module classification lookup table
- Common pitfalls & solutions

**When to Read**: Before writing code; reference during code review

---

### 3. **AGENT_NATIVE_IMPLEMENTATION_CHECKLIST.md** (For Project Manager)
**Purpose**: Week-by-week implementation plan

Contains:
- **Phase 1** (Weeks 1-2): Audit & Measurement
- **Phase 2** (Weeks 3-4): CI/CD Implementation
- **Phase 3** (Weeks 5-8): Docstring Enhancement
- **Phase 4** (Weeks 5-8, parallel): Empirical Risk Modeling
- **Phase 5** (Weeks 9-12): Phase 2 Enforcement
- **Phase 6** (Weeks 9-12): Documentation & Playbook
- Validation gates for each phase
- File templates
- Risk mitigation strategies

**When to Read**: At project kickoff; reference for tracking implementation progress

---

### 4. **DOCSTRING_TEMPLATES.md** (For Developers)
**Purpose**: Copy-paste examples for all languages and tiers

Contains:
- **Python**: Tier 1 (critical), Tier 2 (computation), Tier 3 (utility)
- **Java**: Tier 1 and Tier 2 examples
- **C#**: Tier 1 and Tier 2 examples
- **Tips** for writing Intent sections

**When to Read**: When writing docstrings; copy template, fill in details

---

## Supporting Files

### 5. **scripts/check_coverage_by_tier.py**
**Purpose**: Automated enforcement of tier-based coverage thresholds

Usage:
```bash
pytest --cov=happygene --cov-report=json
python scripts/check_coverage_by_tier.py
```

Enforces:
- Tier 1 >= 100% coverage
- Tier 2 >= 90% coverage
- Tier 3 >= 70% coverage
- Tier 4 >= 50% coverage

---

## Implementation Timeline

| Phase | Duration | Deliverable | Document |
|---|---|---|---|
| **Phase 1: Audit** | Weeks 1-2 | Module classification, coverage gaps identified | AGENT_NATIVE_IMPLEMENTATION_CHECKLIST.md |
| **Phase 2: CI/CD** | Weeks 3-4 | GitHub Actions enforcement enabled | AGENT_NATIVE_IMPLEMENTATION_CHECKLIST.md |
| **Phase 3: Docstrings** | Weeks 5-8 | Intent sections added to Tier 1-2 modules | DOCSTRING_TEMPLATES.md |
| **Phase 4: Validation** | Weeks 5-8 (parallel) | Empirical risk model implemented | DEBATE_ITERATION_3_AgentNative.md (Agent 12) |
| **Phase 2 Execution** | Weeks 9-12 | All agent code meets tier targets | AGENT_NATIVE_QUICK_REFERENCE.md |

---

## Coverage & Docstring Requirements (Summary)

### Coverage by Tier

| Tier | Target | Examples | Rationale |
|---|---|---|---|
| **1: Critical** | 100% | DataCollector, RegulatoryNetwork, Gene, Individual | Data integrity; silent failures unacceptable |
| **2: Computation** | 90% | Expression, Selection, Mutation models | Math correctness; output validation sufficient |
| **3: Utility** | 70% | Analysis, helpers, batch processing | Localized bugs; user validation catches issues |
| **4: Legacy** | 50% | Deprecated code | Will be removed |

### Docstring by Tier

| Tier | Format | Notes |
|---|---|---|
| **1-2** | NumPy + Intent | Machine-readable contract for agents |
| **3** | NumPy only | Natural language sufficient |
| **4** | Optional | Legacy code |

---

## Module Classification (Completed in Phase 1)

### Tier 1: Critical (100%)
- `datacollector.py` — Data integrity
- `regulatory_network.py` — Reproducibility
- `entities.py` — Domain model (Gene, Individual)
- `base.py` — Simulation foundation

### Tier 2: Computation (90%)
- `expression.py` — LinearExpression, Hill, Constant, Composite
- `selection.py` — Proportional, Threshold, Epistatic
- `mutation.py` — PointMutation, Duplication, Conversion
- `conditions.py` — Environmental state
- `regulatory_expression.py` — Composite models

### Tier 3: Utility (70%)
- `analysis/` — Statistical tools
- `model.py` — Orchestration (mostly)

### Tier 4: Legacy (50%)
- (Currently: none)

---

## Key Decisions (Why This Approach)

**Q: Why risk-stratified instead of 100% everywhere?**
A: 100% coverage on utility code (70% chance of bugs) is a poor investment. Better to enforce 100% on critical code (where silent failures = invalid results) and 70% on utility (where users catch bugs). See DEBATE_ITERATION_3_AgentNative.md, Team C synthesis.

**Q: Why machine-readable docstrings?**
A: Agents miss edge cases without explicit contracts. Empirical data shows agents achieve 94% test coverage with formal Intent sections vs. 62% with natural language only. See DEBATE_ITERATION_3_AgentNative.md, Agent 4.

**Q: How to enforce coverage at CI/CD?**
A: Use `scripts/check_coverage_by_tier.py` in GitHub Actions. Blocks merge if any module falls below its tier threshold. See AGENT_NATIVE_IMPLEMENTATION_CHECKLIST.md, Phase 2.

**Q: What if empirical model doesn't match predictions?**
A: Iterate. Phase 4 validates the model against actual bugs. If predictions are wrong, update tier classifications. See DEBATE_ITERATION_3_AgentNative.md, Agent 12.

---

## Quick Start (For Developers)

### Before Writing Code
1. Read: **AGENT_NATIVE_QUICK_REFERENCE.md**
2. Find your module's tier in the classification table
3. Note coverage target and docstring format

### While Writing Code
1. Copy template from: **DOCSTRING_TEMPLATES.md**
2. Fill in Intent section (Tier 1-2) or NumPy docstring (Tier 3)
3. Write tests to meet tier coverage target

### Before Submitting PR
1. Run coverage check locally:
   ```bash
   pytest --cov=happygene --cov-report=json
   python scripts/check_coverage_by_tier.py
   ```
2. Fix any failures (coverage below tier target)
3. Submit PR with coverage report

### Code Review
- Reviewer checks: Coverage report, tier compliance, docstring format
- GitHub Actions: Automatically runs tier-based coverage check

---

## For Agents (LLM-Friendly)

When generating code for happygene, include this in your prompt:

```
# Coverage & Documentation Requirements

Target Tier: [CRITICAL | COMPUTATION | UTILITY]
Coverage Target: [100% | 90% | 70%]

Docstring Format:
- NumPy style (parameters, returns, raises, examples)
- For Tier 1-2: Add Intent section with:
  - Purpose / Formula (if applicable)
  - Domain and Range
  - Invariants (what must always be true)
  - Boundary cases to test
  - Error handling contract

Generate tests to achieve coverage target.
Report: % coverage achieved, uncovered lines (if any).

Reference: /happygene/DOCSTRING_TEMPLATES.md for examples
```

Example response format:
```
Generated: LinearExpression subclass (Tier 2: COMPUTATION)
Coverage: 92% (target: 90%)
Uncovered: 1 line (error path in __init__ for edge case)
Docstring: NumPy + Intent section included

Tests:
- test_linear_expression_positive_slope()
- test_linear_expression_negative_slope()
- test_linear_expression_zero_slope()
- test_linear_expression_clamping()
- [etc.]
```

---

## Questions & Troubleshooting

### "Why is my PR blocked by coverage check?"

Check:
1. Which module? Find tier in **AGENT_NATIVE_QUICK_REFERENCE.md**
2. Current coverage? Run: `python scripts/check_coverage_by_tier.py`
3. Gap? Add tests for uncovered lines

Example:
```
$ python scripts/check_coverage_by_tier.py
✗ happygene/expression.py 88% (FAIL: need 90% for tier2)

Fix: Add 2 more test methods covering untested error paths
```

### "My docstring seems incomplete compared to examples in DOCSTRING_TEMPLATES.md"

If Tier 3 (Utility):
- NumPy docstring only; no Intent section needed

If Tier 1-2 (Critical/Computation):
- Add Intent section with: Purpose, Formula/Domain, Boundary cases
- Reference: **DOCSTRING_TEMPLATES.md**

### "I don't know what tier my module is"

Find your module name in **AGENT_NATIVE_QUICK_REFERENCE.md** lookup table.

If not listed:
- Persistence code (data I/O) → Tier 1
- Math/model code (expression, selection) → Tier 2
- Analysis/utility code → Tier 3
- Old/deprecated code → Tier 4

---

## External Resources

See **DEBATE_ITERATION_3_AgentNative.md** for:
- Industry evidence (GitHub, PwC, NASA, FDA standards)
- Language-specific patterns (Python, Java, .NET)
- Comparative analysis (TDD vs. event-driven testing)
- Cost-benefit analysis (time investment vs. risk reduction)

---

## Version History

| Version | Date | Changes |
|---|---|---|
| **1.0** | Feb 9, 2026 | Initial framework; 12-agent debate, synthesis, templates |

---

## Document Ownership & Maintenance

**Owner**: happygene project team (Phase 2 lead)

**Maintenance**:
- Update tier classifications as modules mature (Phase 3+)
- Refine coverage targets after Phase 2 based on bug data
- Add new languages (Scala, Kotlin, etc.) as adopted

**Reviews**: Quarterly (or after major architectural changes)

---

**Next Action**: Schedule Phase 1 kickoff meeting (Week 1)

**Questions?** See DEBATE_ITERATION_3_AgentNative.md (full framework) or AGENT_NATIVE_QUICK_REFERENCE.md (summary)
