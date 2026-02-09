# Decision Framework: Polyglot Quality Gate Selection

## Quick Decision Tree

```
START: Do you have polyglot code in one repository?
├─ NO → Use current Python-only gate, revisit when you add Java/C#
└─ YES → Continue

Have you built abstraction layers before?
├─ NO → Go with Team B (Language-Specific) or Team A (Unified)
└─ YES → Consider Team C (Abstraction)

Team size?
├─ <5 people → Team A (Unified, simplest)
├─ 5-10 people → Team B (Language-Specific, most natural)
└─ 10+ people → Team C (Abstraction, scales best)

Time to implement?
├─ Need it in <1 day? → Team A
├─ Have 3 days? → Team B
└─ Have 2 days and want future-proof? → Team C

Done: Follow the implementation guide for your chosen team.
```

## Risk Assessment

### Team A (Unified Gate) - Risk Level: MEDIUM

**Red flags (avoid if any of these apply):**
- You anticipate >4 languages (gate becomes unmaintainable)
- Your team has 10+ developers (coordination overhead)
- Java/C# CI runners are slow (will block Python devs waiting)
- You have different quality expectations per language (coverage ≥80% Python, ≥70% Java)

**Green flags (ideal if all apply):**
- <5 developers
- Similar CI runtime across languages (all ~3-5 minutes)
- Unified quality standards (80% coverage for all)
- Want to ship this week

**Mitigation (if you choose Team A anyway):**
- Implement per-language configuration overrides (allow Python 80%, Java 75%)
- Plan for refactoring to Team C when you hit 4 languages
- Add detailed per-language failure reporting to hide complexity

---

### Team B (Language-Specific) - Risk Level: LOW

**Red flags (avoid if any apply):**
- You have >10 developers (ops burden of 3 separate gates)
- You want developers to move between Python/Java/C# freely (context-switching cost)
- You care about operational simplicity (3 alerts = high alert fatigue)
- You want a single "is this deployable?" answer (not "Python ✓, Java ✗, C# ✓")

**Green flags (ideal if all apply):**
- Clear language specialization (Python team, Java team, C# team)
- Each language has established community of practice (Python devs know pytest, Java devs know JUnit)
- You want to minimize initial setup complexity
- You don't need a unified quality vision

**Mitigation (if you choose Team B anyway):**
- Document shared quality standards (even if gates are language-specific)
- Create shared on-call rotation (not per-language)
- Schedule monthly cross-language code reviews

---

### Team C (Abstraction) - Risk Level: MEDIUM-HIGH (but pays off)

**Red flags (avoid if any apply):**
- Your team has no Python developers (abstraction is in Python)
- You're in crisis mode (abstraction is 2-day setup, not 1-day)
- You anticipate <2 languages (abstraction overhead not worth it)
- You don't have Go/Rust/C++ experience (abstraction patterns are unfamiliar)

**Green flags (ideal if all apply):**
- You expect to add 4+ languages later (abstraction amortizes cost)
- You have 5-20 developers (sweet spot for abstraction ROI)
- Your team is polyglot (Python + Java + C# developers who move between languages)
- You care about developer experience and ops simplicity

**Mitigation (if you choose Team C anyway):**
- Start with just Python + Java (2 languages) to validate abstraction
- Add C# later (copy-paste implementation from Java)
- Build fallback: language-specific gates if abstraction breaks
- Document abstraction patterns for future languages

---

## Decision Criteria Table

Use this to score each strategy (higher is better):

| Criterion | Weight | Team A | Team B | Team C |
|-----------|--------|--------|--------|--------|
| Setup speed (1 = slow, 10 = fast) | 20% | 10 | 5 | 7 |
| Operational simplicity (10 = simple) | 20% | 8 | 5 | 8 |
| Developer UX (10 = great) | 20% | 6 | 7 | 9 |
| Scalability (10 = great to 10+ languages) | 20% | 2 | 7 | 10 |
| Maintenance burden (10 = low) | 20% | 8 | 4 | 6 |
| **Weighted score** | | **6.8** | **5.6** | **8.0** |

**Interpretation:**
- **7-10:** Strong recommendation for this strategy
- **5-7:** Viable, but trade-offs exist
- **<5:** Risky, consider alternatives

---

## "What I Heard" Check

Before deciding, verify you understand the trade-offs:

### Team A Understanding Check
```
Q: If Python tests fail, does the Java job still run?
A: NO (fail-fast: true). Entire PR blocked immediately.

Q: Can I deploy if Python is broken but Java/C# pass?
A: NO. Single gate means all-or-nothing.

Q: Is this sustainable if I add Rust later?
A: NO. You'll refactor to Team B or C.
```

### Team B Understanding Check
```
Q: If Python tests fail but C# passes, can I merge?
A: NO. Branch protection requires ALL applicable gates to pass.

Q: Do Python and Java developers see each other's failures?
A: NO. They only see their language's gate status.

Q: Is this sustainable if I add Rust later?
A: YES. Add rust.yml, add to branch protection rule.
```

### Team C Understanding Check
```
Q: Where is the abstraction code?
A: scripts/quality_gate.py (single Python file, ~200 lines).

Q: Can I modify the abstraction if my language needs different config?
A: YES. gates.py has a QualityGate protocol; create YourLanguageGate subclass.

Q: What happens if the abstraction breaks?
A: Entire gate fails. Mitigation: keep language-specific gates as fallback in CI.
```

---

## Quick Start: Implementation Checklist

### Team A (Unified Gate)

- [ ] Modify `.github/workflows/test.yml` to add Java + C# matrix entries
- [ ] Update strategy.fail-fast = true
- [ ] Add aggregation job (verify all matrix jobs passed)
- [ ] Test locally: `act -j quality`
- [ ] Deploy to feature branch, test with sample PR
- [ ] Update branch protection: require only "aggregation job" to pass
- [ ] Document in CONTRIBUTING.md: "Quality gate = all languages pass"

**Estimated time:** 4 hours

### Team B (Language-Specific Gates)

- [ ] Create `.github/workflows/quality-python.yml` (refactor current test.yml)
- [ ] Create `.github/workflows/quality-java.yml` (new)
- [ ] Create `.github/workflows/quality-csharp.yml` (new)
- [ ] Create `.github/workflows/branch-protection.yml` (enforce all applicable gates)
- [ ] Update branch protection rules: require python-gate, java-gate, csharp-gate
- [ ] Test with 3 sample PRs (one per language)
- [ ] Document in CONTRIBUTING.md: "Each language has separate gate; all must pass"

**Estimated time:** 8 hours

### Team C (Abstraction Gate)

- [ ] Create `scripts/quality_gate.py` (copy from debate doc)
- [ ] Implement `PythonGate` class (test with pytest)
- [ ] Implement `JavaGate` class (test with maven)
- [ ] Implement `CSharpGate` class (test with dotnet)
- [ ] Create `.github/workflows/quality-gate-abstraction.yml`
- [ ] Create `scripts/aggregate_gate.py` (merge results)
- [ ] Test locally: `python scripts/quality_gate.py --language python`
- [ ] Deploy to feature branch
- [ ] Update branch protection: require only "aggregation-gate" job to pass
- [ ] Document in CONTRIBUTING.md: "Run `python scripts/quality_gate.py` locally"

**Estimated time:** 6 hours

---

## FAQ

**Q: Can I start with Team A and migrate to Team C later?**
A: Yes. Team A → Team C is a straightforward refactoring (create scripts/quality_gate.py, wrap existing jobs). Plan for 8 hours to migrate.

**Q: What if my Java tests take 10 minutes and Python tests take 1 minute?**
A: All three run in parallel. Total wall-clock time = max(10 min Java) ≈ 10 min. No penalty for speed mismatch.

**Q: Can I have different coverage thresholds per language?**
A: Team B: Yes (each language configures its own). Team A/C: Only if you add per-language tuning to abstraction/aggregation.

**Q: What if I only have Python today, but plan Java/C# eventually?**
A: Start with Team A (simple), plan migration to Team C in next quarter. Don't over-engineer for future.

**Q: Which team uses the least GitHub Actions minutes?**
A: All three use the same total minutes (parallel execution). Difference is negligible.

**Q: Can I use Sonarcloud instead of Codecov?**
A: Yes. All three teams support it. Swap `codecov/codecov-action@v4` for Sonarcloud's action.

**Q: What if a language-specific gate is consistently flaky (false positives)?**
A: Team B: easier to isolate (restart just that job). Team A/C: entire gate fails. Mitigation: add re-run logic to flaky tests.

---

## Feedback Loop

After 2 weeks with your chosen strategy, ask:

1. **Developers:** "How easy is it to understand why the gate failed?"
2. **Ops:** "How many false positives are we seeing?"
3. **Team:** "Are we confident in the quality signal?"

If you answer:
- "Easy / <1 per day / Yes" → You chose well
- "Confusing / >3 per day / No" → Reconsider your choice (migration plan below)

### Migration Path if You Choose Wrong

**Team A → Team B:** 2 hours (split test.yml into 3 files)
**Team A → Team C:** 4 hours (create abstraction, wrap existing jobs)
**Team B → Team C:** 4 hours (create abstraction, refactor 3 gates into implementations)
**Team C → Team B:** 3 hours (convert abstraction back to 3 separate workflows)

No sunk costs; you can pivot quickly.

---

## Recommendation for Happygene Specifically

**You should choose: Team C (Abstraction Gate)**

**Rationale:**
1. You declared Python + Java + C# (3 languages is abstraction's sweet spot)
2. You're planning evolutionary biology simulation (scientific code benefits from polyglot approach)
3. Your team is likely <10 developers (abstraction ROI is high)
4. You're building a framework (future contributors will appreciate unified developer experience)
5. You have 2 weeks before Phase 1 goes into production (time for 2-day setup + 2 weeks testing)

**Implementation:**
- Week 1: Set up Team C abstraction (scripts/quality_gate.py + GitHub Actions workflow)
- Week 2: Test with 10 real PRs, gather feedback
- Week 3: Document for contributors, train team
- Month 2+: Monitor for false positives, refine thresholds

**Budget:**
- Setup: $1,600 (2 days × engineer time)
- Monthly: $308 (GitHub Actions + architect oversight)
- 3-year TCO: $7,236

---

## Next Steps

1. **Read the full debate:** DEBATE_ITERATION_4_PolyglotGates.md (this document)
2. **Take the decision tree test:** Team A / B / C (above)
3. **Run the decision criteria table:** Score your priorities
4. **Check "What I Heard" understanding:** Validate your choice
5. **Pick a team:** Commit publicly to your choice
6. **Implement:** Use the quick-start checklist
7. **Retrospect:** After 2 weeks, did you choose well?

---

**Document generated:** February 9, 2026
**Last updated:** February 9, 2026
