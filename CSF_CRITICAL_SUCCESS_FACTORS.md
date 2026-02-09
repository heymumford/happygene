# Critical Success Factors (CSF): The Essentials

**Quick Reference**: 5 factors that predict 90%+ survival probability. If you only read one document, read this.

**Format**: Metric + threshold + action

---

## CSF #1: GOVERNANCE MODEL (Clear Ownership)

### Green Flag ✅
- Named BDFL (or core team with decision authority)
- Published GOVERNANCE.md explaining how decisions are made
- Succession plan documented (who takes over if you leave?)
- Decision process: RFC for major changes (open to community input)

### Yellow Flag 🟡
- BDFL exists but unclear (or multiple people claiming leadership)
- No published governance document
- Succession plan not mentioned
- Decisions made in private (community unaware)

### Red Flag ❌
- No named maintainers
- Governance document contradicts practice
- Single person controls all decisions with no consultation
- Founding team has all left; unclear who's in charge

### For HappyGene
```
Current: You (Eric) = BDFL
By month 3: Publish GOVERNANCE.md
By month 6: Recruit co-lead (explicit merge authority)
By month 12: Core team model (3+ people deciding)
```

**Effort**: 2-3 hours to publish, ongoing communication

---

## CSF #2: DOCUMENTATION (Onboarding Friction)

### Green Flag ✅
- README explains what the tool does in 30 seconds
- Installation works in <2 minutes: `pip install . && python example.py`
- 5+ realistic example notebooks (copy-paste ready)
- Full API documentation (auto-generated from docstrings)
- Troubleshooting guide (common errors + solutions)
- CONTRIBUTING.md explains how to contribute (all skill levels)

### Yellow Flag 🟡
- README exists but vague
- Installation requires manual configuration steps
- 1-2 examples; toy data only
- Partial API docs (some classes undocumented)
- No troubleshooting section
- CONTRIBUTING.md is generic

### Red Flag ❌
- No README
- Installation broken or requires complex setup
- No examples
- No API documentation
- No CONTRIBUTING.md
- Users can't get started in 30 minutes

### For HappyGene

**By month 3** (Foundation):
- README (30-second explanation)
- Installation working: `pip install -e .`
- 2 realistic examples
- 50% API documented
- CONTRIBUTING.md published

**By month 6** (Stabilization):
- README + getting started guide
- Installation: pip + conda
- 5+ examples
- 100% API documented
- Troubleshooting section (10+ common errors)

**By month 12** (Publication):
- All above +
- Video tutorials (5 min + 15 min + 30 min versions)
- Gallery of use cases
- Integration guides (interop with other tools)

**Effort**: 40-60 hours total (spread across 12 months)

---

## CSF #3: TESTING & CI/CD (Community Trust)

### Green Flag ✅
- ≥80% test coverage (enforced on PRs)
- CI/CD runs on 2+ platforms (Linux, macOS, Windows)
- Tests on 3+ Python versions (3.9, 3.10, 3.11, 3.12)
- Coverage badge in README (visible status)
- Pre-commit hooks (auto-lint: black + ruff)
- Tests run in <5 minutes (fast feedback)

### Yellow Flag 🟡
- 50-70% test coverage
- Single platform testing (Linux only)
- Single Python version
- No coverage reporting
- Manual linting (not automated)
- Tests take 15-30 minutes

### Red Flag ❌
- <50% test coverage
- Manual testing only (no CI/CD)
- Tests flake randomly
- No linting
- Tests take >1 hour
- Regressions merge undetected

### For HappyGene

**By month 1** (Launch):
- GitHub Actions workflow (2+ platforms, 4 Python versions)
- >70% coverage (enforced)
- Pre-commit hooks installed
- Passing tests <5 min

**By month 6** (Growth):
- ≥80% coverage (enforced)
- 3+ platforms (Linux, macOS, Windows)
- Nightly runs (catch dependency breaks)
- Coverage badge in README

**By month 12** (Publication):
- ≥85% coverage
- Advanced CI/CD (security scanning, performance benchmarks)
- Codecov integration (track coverage over time)

**Effort**: 5 hours setup; <1 hour/month maintenance

---

## CSF #4: COMMUNITY GROWTH (More Hands)

### Green Flag ✅
- 5+ active contributors (issues/PRs each month)
- <48 hour first response on issues/PRs
- Public contributor list (celebrate in README)
- Multiple contribution tiers (docs, tests, code; not just code)
- "Good-first-issue" labels (5-10 items for newcomers)
- Regular recognition (thank publicly in releases)

### Yellow Flag 🟡
- 2-4 active contributors
- 2-7 day response time
- Contributor list exists but outdated
- Only code contributions accepted
- <3 good-first-issues
- Minimal public recognition

### Red Flag ❌
- 1 contributor (you only)
- >2 week response time
- No contributor list
- Contributes unwelcome (hidden barriers)
- No good-first-issues
- Contributors go unrecognized

### For HappyGene

**By month 3**:
- You + 1 active contributor
- <48 hr response SLA (strict)
- 5 good-first-issues labeled
- CONTRIBUTING.md published

**By month 6**:
- You + 2-3 active contributors
- <48 hr response (maintained)
- 10+ good-first-issues
- Featured contributor section in README

**By month 12**:
- 5+ active contributors
- <24 hr response on simple issues
- Quarterly contributor recognition posts
- Mentoring program (formal onboarding)

**Effort**: 2-3 hours/week (triage, mentoring, recognition)

---

## CSF #5: RELEASE CADENCE (Predictability)

### Green Flag ✅
- Monthly releases (even if minor version bumps)
- Release notes explaining what changed (+ linked issues)
- Changelog file (CHANGELOG.md or releases.md)
- Version numbering follows semver (major.minor.patch)
- Release on predictable schedule (first Friday of month, etc.)
- Deprecation warnings 2 releases before removal

### Yellow Flag 🟡
- Quarterly releases (4x/year)
- Release notes exist but incomplete
- Changelog updated sporadically
- Version numbering inconsistent
- Release schedule unpredictable (sometimes 2 weeks, sometimes 6 months)
- No deprecation warnings

### Red Flag ❌
- 6+ months since last release
- No release notes
- No changelog
- Arbitrary version numbers
- No predictable schedule
- Breaking changes unannounced

### For HappyGene

**By month 3**:
- Establish monthly release cycle
- Release notes (GitHub Releases page)
- Changelog (CHANGELOG.md)
- Semver versioning (0.1.0 → 0.2.0 → 0.3.0)

**By month 6**:
- Monthly releases (no exceptions)
- Detailed release notes (what changed, why, migration guide)
- Changelog automatically generated from commits
- Predictable schedule (e.g., first Friday)

**By month 12**:
- All above +
- Deprecation policy (announce removal 2 releases ahead)
- LTS (Long-Term Support) versions for production users
- Migration guides for breaking changes

**Effort**: 1 hour/month (release automation + notes)

---

## BONUS CSF: PUBLICATION (Credibility)

### Not Required for Survival, But Accelerates Growth

**Green Flag** ✅
- JOSS paper published (month 12-18)
- Pre-print on bioRxiv/arXiv (month 9-12)
- Domain journal paper (month 18+; optional)
- Papers cite your tool (proof of use)
- >100 Google Scholar cites (by year 2-3)

**Yellow Flag** 🟡
- No publication yet (month 12+)
- Pre-print exists but not submitted to JOSS
- 10-50 cites

**Red Flag** ❌
- Published in Nature without JOSS first (JOSS will reject)
- No publication or pre-print after 18 months
- Declining citation count

### For HappyGene

**Timeline**:
- Month 6-8: Write pre-print (bioRxiv)
- Month 10-12: Submit JOSS
- Month 12-14: JOSS review (4-8 weeks)
- Month 14-16: (Optional) Prepare domain journal paper
- Month 16-18: Submit domain journal

**Critical**: Submit JOSS at month 12 (not earlier; not later). Don't skip to Nature. JOSS reviewers will ask you to do JOSS anyway.

**Effort**: 40-60 hours (paper writing + community examples)

---

## QUICK ASSESSMENT: Which CSFs Are You Missing?

| CSF | Status | By When | Action |
|-----|--------|---------|--------|
| **Governance** | 🔴 Not started | Month 1 | Publish GOVERNANCE.md |
| **Documentation** | 🟡 Partial (research docs only) | Month 3 | README + 2 examples |
| **Testing & CI/CD** | 🟡 Partial (no CI) | Month 1 | GitHub Actions setup |
| **Community** | 🔴 None yet | Month 3 | CONTRIBUTING.md + good-first-issues |
| **Release Cadence** | 🔴 Not started | Month 1 | Monthly releases + CHANGELOG.md |
| **Publication** | 🟡 Research docs complete | Month 12 | JOSS submission |

**Gap Analysis**: You're missing CSF #1, #4, #5 (governance, community, releases). These are CRITICAL. Do not skip.

---

## THE 30-DAY QUICK START (Closing Gaps #1, #4, #5)

### Week 1: Governance + Release Plan
```
Mon: Write GOVERNANCE.md (who decides? how? succession?)
Tue: Publish GOVERNANCE.md on GitHub
Wed: Create CHANGELOG.md (empty template)
Thu: Plan first release (v0.1.0)
Fri: Release v0.1.0 (even if minimal)
```

### Week 2: Contribution Pathways
```
Mon: Copy CONTRIBUTING.md from Mesa
Tue: Adapt for HappyGene context
Wed: Publish CONTRIBUTING.md on GitHub
Thu: Label 5 issues as "good-first-issue"
Fri: Announce in README (link to CONTRIBUTING.md)
```

### Week 3: Testing & CI/CD
```
Mon: Copy GitHub Actions template
Tue: Adapt for your repo (python versions, OS)
Wed: Trigger first CI/CD run
Thu: Fix any failures
Fri: Add coverage badge to README
```

### Week 4: Communication
```
Mon: Create METRICS.md (health report template)
Tue: Write first health report (current state)
Wed: Announce community channels (GitHub Discussions)
Thu: Send first monthly email (roadmap + next steps)
Fri: Celebrate first month complete!
```

**Total Effort**: 20-30 hours (spread across 4 weeks)

---

## RED FLAGS: When to Act (Intervention Checklist)

| Red Flag | When | Action | Deadline |
|----------|------|--------|----------|
| **No response to issues** | >1 week | Daily triage (30 min) | Immediate |
| **PR backlog growing** | >20 pending | Merge mechanically if tests pass | 1 week |
| **Contributor drop** | Only you committing | Recruit co-lead publicly | 2 weeks |
| **No release schedule** | Last release >6 months ago | Release v1.0 (even if imperfect) | 2 weeks |
| **Test coverage falling** | <70% and declining | Mandate tests for new PRs | 1 week |
| **Documentation outdated** | Docs lag code by >2 months | Assign someone to doc triage | 2 weeks |
| **Community feeling ignored** | Negative GitHub comments | Respond publicly + explain decisions | 3 days |

---

## METRICS TO TRACK (Monthly)

```markdown
## HappyGene Monthly Health Snapshot

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Issues responded to | <48 hr | 36 hr avg | ✅ Green |
| PRs merged/month | ≥2 | 4 | ✅ Green |
| Test coverage | ≥80% | 82% | ✅ Green |
| Active contributors | ≥5 | 3 | 🟡 Yellow |
| Commits/month | ≥10 | 12 | ✅ Green |
| Release on schedule | Monthly | v0.2.0 on time | ✅ Green |

**Actions**: Recruit 2 more contributors (address Yellow)
```

---

## DECISION TREE: Governance Model Choice

```
Are you solo?
├─ YES → BDFL (benevolent dictator) model
│  ├─ Recruit co-lead by month 6
│  └─ Plan transition to Core Team by month 12
│
└─ NO (have a team) → Core Team model
   └─ Formalize decision-making (RFC process)
```

**For HappyGene**: You're solo. Adopt BDFL. Recruit co-lead at month 6.

---

## FINAL CHECKLIST: Are You Ready to Launch?

- [ ] GOVERNANCE.md published (you are BDFL, succession plan clear)
- [ ] CONTRIBUTING.md published (how to contribute)
- [ ] GitHub Actions CI/CD working (test on 2+ platforms)
- [ ] Test coverage ≥70% (enforced on PRs)
- [ ] 5+ good-first-issues labeled
- [ ] CHANGELOG.md created (track releases)
- [ ] First release published (v0.1.0)
- [ ] README explains in 30 seconds what this is
- [ ] `pip install -e .` works (dev setup)
- [ ] Issues get <48 hr response (SLA tracked)

**If all checked**: Launch week 1. Your CSFs are solid.

---

## Success Probability Forecast

| Scenario | Year 1 | Year 2 | Year 3 |
|----------|--------|--------|--------|
| **Execute all 5 CSFs** | 50-60% adoption | 60-70% | 75-85% |
| **Missing CSF #1 (governance)** | 30-40% adoption | 20-30% | 10-20% |
| **Missing CSF #2 (docs)** | 20-30% adoption | 10-20% | <10% |
| **Missing CSF #3 (testing)** | 20-30% adoption | <10% | Abandoned |
| **Missing CSF #4 (community)** | 30-40% adoption | 20-30% | <10% |
| **Missing CSF #5 (releases)** | 20-30% adoption | <10% | Abandoned |

**With all 5 CSFs**: 85%+ probability of sustainability at 5 years

---

## TL;DR (Too Long; Didn't Read)

**Do these 5 things**:
1. Publish GOVERNANCE.md (you decide; succession plan)
2. Publish CONTRIBUTING.md (how to contribute)
3. GitHub Actions CI/CD + ≥80% coverage (automated trust)
4. Good-first-issues + <48 hr response (attract contributors)
5. Monthly releases + CHANGELOG.md (predictable)

**Effort**: 20-30 hours spread across month 1

**Success Probability**: 85%+ at 5 years if you do this

**Start this week**. First thing: write GOVERNANCE.md.

---

**Next Document to Read**: GOVERNANCE_AND_HEALTH_PLAYBOOK.md (full details, examples, case studies)

**Questions?** File an issue. Maintainers respond <48 hr.
