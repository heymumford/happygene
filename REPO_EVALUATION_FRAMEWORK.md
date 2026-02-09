# Repository Evaluation Framework for Biology/Simulation Tools

**Purpose**: Systematic assessment of open-source biology and simulation projects for maturity, sustainability, and adoption potential.

**Applies to**: Mesa, Snakemake, Nextflow, Bioconda packages, Bioconductor packages, and similar scientific software.

---

## Quick Assessment: 5-Minute Screening

Visit the GitHub repo homepage and answer:

| Question | Green ✓ | Yellow ? | Red ✗ | Notes |
|----------|---------|---------|-------|-------|
| **README exists and is current?** | Clear; updated <6mo | Exists; unclear scope | Missing/outdated | First signal of maintenance |
| **Last commit was when?** | <1 month | 1-3 months | >6 months | Indicates activity level |
| **Releases labeled + documented?** | ≥2 per year with notes | Irregular; sparse notes | None or ancient | Signals stability guarantees |
| **Test coverage visible?** | Badge ≥80% | Badge <80% | No badge | CI/CD signals |
| **Contributing guide exists?** | Detailed; recent | Vague; outdated | Missing | Signals openness to contributors |
| **Is there a license?** | OSI-approved (MIT/Apache2) | Permissive but niche | Proprietary/unclear | Legal clarity |

**Scoring**: 6/6 green = **highly viable**; 4-5 green = **investigate further**; <4 green = **consider alternatives**.

---

## Comprehensive Assessment: 1-Hour Deep Dive

### SECTION 1: ACTIVITY & MAINTENANCE (GitHub Metrics)

**Data Source**: GitHub Insights tab + `git log` analysis

#### 1.1 Commit Frequency & Patterns

```bash
# Clone repo; run these commands:
git log --all --oneline --since="1 year ago" | wc -l  # Total commits in 12mo
git log --all --oneline --since="6 months ago" | wc -l # Recent activity
```

| Metric | Healthy | At Risk | Dead |
|--------|---------|---------|------|
| Commits (12 months) | ≥50 | 20-50 | <20 |
| Commits (6 months) | ≥25 | 10-25 | <10 |
| **Trend** | Steady or growing | Declining | Flat or abandoned |

**Interpretation**:
- Growth = active development or bug fixes
- Flat + old commits = legacy mode (stable but no longer evolving)
- Decline + recent commits = refactoring or major restructuring (check PRs)

---

#### 1.2 Pull Request Health

**GitHub Insights → Pull Requests**:

| Metric | Healthy | At Risk | Dead |
|--------|---------|---------|------|
| PRs merged (last 3 months) | ≥10 | 3-9 | <3 |
| Avg time to merge (days) | <30 | 30-90 | >90 |
| Open PR backlog | <20 | 20-50 | >50 |
| Stale PRs (>3 months old, unmerged) | <10% | 10-30% | >30% |

**How to calculate**:
1. Go to `repo/pulls?q=is:pr+is:closed+merged`
2. Filter to last 3 months
3. Count merged PRs
4. For time-to-merge: sample 10 recent PRs, check created → merged dates

**Red Flag**: 50+ open PRs with none merged in 3 months = bottleneck in review.

---

#### 1.3 Issue Responsiveness

**GitHub Insights → Issues**:

| Metric | Healthy | At Risk | Dead |
|--------|---------|---------|------|
| Avg response time (hours) | <24 | 24-72 | >72 |
| Issues closed (last 3 months) | ≥15 | 5-15 | <5 |
| Open issue backlog | <50 | 50-150 | >150 |
| % issues marked `wontfix` (recent) | <5% | 5-15% | >15% |

**How to check**:
1. Go to `repo/issues?q=is:issue+is:closed`
2. Filter to last 3 months
3. Random sample: pick 5 issues, check "created" → "closed" timestamps
4. Look at `labels` for `wontfix`, `duplicate`, `stale`

**Red Flag**: High `wontfix` without resolution = maintainer has stopped triaging.

---

#### 1.4 Contributor Diversity

**GitHub Insights → Contributors**:

| Metric | Healthy | At Risk | Dead |
|--------|---------|---------|------|
| Unique contributors (12mo) | ≥5 | 2-4 | ≤1 |
| % commits by top contributor | <50% | 50-80% | >80% |
| New contributors (12mo) | ≥2 | 0-1 | 0 |

**Why This Matters**: "Bus factor = 1" (only maintainer knows code) → high abandonment risk if they leave.

**How to check**:
```bash
git shortlog -sne | head -10  # Top contributors
git log --all --since="1 year ago" --pretty="%an" | sort -u | wc -l  # Unique contributors
```

---

### SECTION 2: QUALITY & RELIABILITY (Code Standards)

**Data Source**: GitHub repo `/tests`, `/docs`, `README.md`, GitHub Actions tab

#### 2.1 Testing & Coverage

```bash
# Look for evidence of testing:
ls -la | grep -E "(test|spec|pytest|tox)"
find . -name "*.yml" -path "*/.github/workflows/*" | head -5
```

| Aspect | Good | Needs Work | Poor |
|--------|------|-----------|------|
| **Test coverage** | ≥80% reported | 50-80% | <50% or no badge |
| **CI/CD** | GitHub Actions + other platform | GitHub Actions only | None visible |
| **Test framework** | pytest/unittest with clear organization | Ad-hoc tests | No tests |
| **Coverage reporting** | Codecov/Coveralls integrated | Manual reports | None |

**Specific checks**:
- [ ] Find `.github/workflows/*.yml` files
- [ ] Check for `pytest`, `coverage`, `codecov` mentions
- [ ] Look at README for coverage badge
- [ ] Sample 3 test files; verify they're not trivial (e.g., `assert True`)

**Example of Good Setup**:
```yaml
# .github/workflows/test.yml exists; includes:
- runs-on: ubuntu-latest, macos-latest, windows-latest
- python-version: 3.9, 3.10, 3.11, 3.12
- pytest tests/ --cov=mymodule --cov-report=xml
- codecov token setup
```

---

#### 2.2 Code Quality Tooling

Check `requirements-dev.txt` or `pyproject.toml` for:

| Tool | Purpose | Signal |
|------|---------|--------|
| `black`, `isort` | Code formatting | Standardized style |
| `flake8`, `pylint` | Linting | Code quality enforcement |
| `mypy`, `pyright` | Type checking | Reduced runtime errors |
| `pre-commit` | Automation | Prevents bad commits |
| `sphinx`, `mkdocs` | Docs generation | Professional documentation |

**Green flag**: If `pyproject.toml` has `[tool.pytest]`, `[tool.black]`, `[tool.mypy]` sections configured.

---

#### 2.3 Dependency Management

```bash
# Check for dependency bloat:
cat requirements.txt | wc -l  # How many dependencies?
cat setup.py | grep "install_requires"
```

| Pattern | Assessment |
|---------|-----------|
| <10 core dependencies | Lightweight; easy to install |
| 10-30 dependencies | Normal for scientific tools |
| >50 dependencies | Complex; harder to debug conflicts |
| Pinned versions (>=X.Y, ==X.Y.Z) | Reproducible installations |
| Unpinned versions (>=X, >) | Permissive; may break users |

**For biology tools**: Expect dependencies on numpy, scipy, pandas. More than that signals potential bloat.

---

### SECTION 3: DOCUMENTATION & USABILITY

**Data Source**: `/docs`, `/examples`, `README.md`, online docs (ReadTheDocs, etc.)

#### 3.1 Documentation Structure

Visit the project's documentation site (usually `project.readthedocs.io` or `/docs` in repo):

| Element | Present | Comprehensive | Missing |
|---------|---------|---------------|---------|
| **Getting started** | ✓ | 10-min guide works as written | Only API reference |
| **Installation** | ✓ | Multiple methods (pip/conda/source) | Single method; unclear steps |
| **API reference** | ✓ | Auto-generated from code | Hand-written; incomplete |
| **Tutorials/vignettes** | ✓ | ≥3 realistic examples; runnable | None or toy examples |
| **FAQ** | ✓ | Addresses common errors | None |
| **Troubleshooting** | ✓ | "This error means..." + solution | None |

**Critical for biology**: At least 3 example notebooks/vignettes using real (or realistic) data.

#### 3.2 Example Gallery & Community

Check `/examples`, `/docs/examples`, `/notebooks` directories:

| Quality | Assessment |
|---------|-----------|
| ✓ 5+ runnable notebooks with real data | Excellent; users can copy-paste |
| ✓ 2-4 examples; focused on core features | Good foundation |
| ? 1-2 toy examples; synthetic data only | Shows usage; lacks realism |
| ✗ No examples or pseudocode only | High friction for adoption |

**Check for community examples**:
- GitHub "Issues" or "Discussions" with contributed workflows
- External blog posts linking to the tool
- Example GitHub repos using the tool

**Red flag**: Zero external examples in year 1 = possibly not discoverable.

---

#### 3.3 Citation & Academic Credibility

Check README and `/docs`:

| Presence | Signal |
|----------|--------|
| ✓ DOI badge + link to JOSS paper | Published; citable; peer-reviewed |
| ✓ `CITATION.cff` or `CITATION.md` with BibTeX | Easy to cite; discoverable |
| ? Paper reference (pre-print or submitted) | In progress; some validation |
| ? Funding acknowledgment | Grants or industry backing |
| ✗ No publication; no citation guidance | Not yet established; emerging |

**For biology**: Project published in JOSS, Nature, BMC, or PLOS within 2 years of launch = more likely to be maintained.

---

### SECTION 4: ECOSYSTEM INTEGRATION & ADOPTION

#### 4.1 Package Distribution

Check which package managers list the tool:

| Platform | Command | Adoption Signal |
|----------|---------|-----------------|
| PyPI | `pip install tool` | Minimum standard |
| conda-forge | `conda install -c conda-forge tool` | ~80% of scientific Python |
| Bioconda | `conda install -c bioconda tool` | Standard for biology |
| BioPython ecosystem | Integrated API | Deep integration |
| nf-core (for workflows) | In registry | Production-ready |

**Check Bioconda status**:
```bash
# If tool is in bioconda:
conda search tool  # Shows it's available
# If NOT in bioconda but claimed to be:
# Red flag = discoverability loss
```

**Impact**: Conda users (especially on HPC clusters) are majority in biology research. Missing from conda = 60% lower adoption.

---

#### 4.2 Integration with Scientific Stack

**For Python/Pandas tools**, check if it works with:
- [ ] NumPy arrays (input/output)
- [ ] Pandas DataFrames (conversion to/from)
- [ ] Scikit-learn pipelines (if applicable)
- [ ] Matplotlib/Seaborn/Plotly (visualization)
- [ ] Jupyter notebooks (tab-complete, repr, display)

**Test in notebook**:
```python
import tool
import pandas as pd

# Load sample data
df = pd.read_csv("sample.csv")

# Use tool
result = tool.analyze(df)

# Check type and display
type(result)          # Should be intuitive (DataFrame, array, custom class)
result.describe()     # Should have __repr__ for notebooks
result.to_dataframe() # If custom class, conversion easy
```

**For simulation/workflow tools**, check if it integrates with:
- [ ] HPC job schedulers (Slurm, SGE)
- [ ] Container technologies (Docker, Singularity)
- [ ] Cloud platforms (AWS, GCP, Azure)
- [ ] Workflow platforms (Nextflow, Snakemake, CWL)

---

#### 4.3 Community & Engagement

Check for indicators of active research community:

| Signal | Source | Interpretation |
|--------|--------|-----------------|
| Slack/Discord/Matrix chat | Official channels link in README | Active community support |
| Forum posts/Biostars answers | Search tool name on Biostars.org | Real-world usage help |
| GitHub Discussions enabled | `repo/discussions` tab | Asynchronous community support |
| Twitter/social engagement | Tool maintainers post updates | Visibility |
| Conferences/workshops | Tool presentations at ISMB, Genome Informatics, etc. | Recognition |

**Quantify**:
```bash
# Biostars engagement (rough estimate):
curl -s "https://www.biostars.org/search/?q=tool+name" | grep -c "posts"
```

---

### SECTION 5: GOVERNANCE & SUSTAINABILITY

#### 5.1 Maintainer Profile

Go to repo **About** section and sample recent PRs/issues:

| Check | Indicator |
|-------|-----------|
| How many maintainers listed? | ≥2 good; 1 = bus factor risk |
| Are they active on recent issues? | Comments on issues from last month? |
| Full-time vs. volunteer? | Funding/employment stated? |
| Diversity of background? | Different organizations? |
| Response time on PRs? | Merge or reject within 2 weeks? |

**Check maintainer's other projects**:
- Are they spread thin across 20+ projects? (Red flag: might abandon this one)
- Do they maintain multiple mature projects? (Green flag: proven track record)

---

#### 5.2 Funding & Institutional Support

Check **About** + `/docs` + README for mentions of:

- [ ] NSF/NIH grants (with grant numbers)
- [ ] Industry sponsorship (company names)
- [ ] University affiliation (dept/university)
- [ ] Foundation support (Moore Foundation, CZI, etc.)

**Example (good)**:
```
# README mentions:
This project is supported by:
- NSF Grant #12345 (2024-2027)
- Wellcome Trust Open Research Fund
- University of Cambridge, Department of Genetics
```

**Red flag**: Zero funding acknowledgment + small contributor base = likely to stall.

---

#### 5.3 Roadmap & Stability

Check for **Roadmap** document or milestone planning:

| Signal | Interpretation |
|--------|-----------------|
| Published roadmap (12-month view) | Planned development; stability |
| Semantic versioning (v1.0 → v1.1 → v2.0) | Backward compatibility concerns; communication |
| Release schedule (quarterly, annual) | Predictability for users |
| Breaking change policy | "Major versions only" = stability promise |
| Deprecation warnings before removal | User-friendly changes |

**Example (good)**:
```
## Roadmap 2026

### v1.2 (Q2 2026)
- [ ] Performance improvements (vectorization)
- [ ] New statistical models
- **No breaking changes**

### v2.0 (Q1 2027)
- Refactor API (simplified parameter names)
- Migration guide will be provided
- Deprecation warnings in v1.2
```

---

### SECTION 6: RISK ASSESSMENT SYNTHESIS

#### 6.1 Abandonment Risk Calculator

**Score each area (1 = high risk, 5 = low risk)**:

| Area | Score | Comments |
|------|-------|----------|
| **Activity** (commits, PRs, issues) | _/5 | Recent activity |
| **Quality** (tests, CI/CD, coverage) | _/5 | Code standards |
| **Documentation** (guides, examples, API) | _/5 | Usability |
| **Community** (contributors, engagement) | _/5 | Ecosystem health |
| **Governance** (maintainers, funding, roadmap) | _/5 | Sustainability |

**Calculation**:
- **20-22**: Very low risk; established project
- **15-19**: Low risk; healthy project
- **10-14**: Medium risk; monitor quarterly
- **5-9**: High risk; may abandon soon
- **<5**: Critical; consider alternative

---

#### 6.2 Green Flags (Sustainability Likely)

- [ ] ≥3 active maintainers (bus factor > 1)
- [ ] Recent release (<3 months) with clear changelog
- [ ] ≥5 unique contributors in last 12 months
- [ ] Median PR review time <30 days
- [ ] Coverage badge ≥80%
- [ ] Clear CONTRIBUTING guidelines + good-first-issue labels
- [ ] Published in JOSS or Nature venue
- [ ] ≥100 Google Scholar citations (for mature projects)
- [ ] Listed in curated registries (BioConda, Bioconductor, nf-core)
- [ ] Community-contributed extensions/pipelines

---

#### 6.3 Red Flags (High Abandonment Risk)

- [ ] No commits in 6+ months
- [ ] Single maintainer; no activity from others
- [ ] PR backlog >50 with review time >90 days
- [ ] Test coverage <50%; CI/CD failing
- [ ] No documentation beyond API
- [ ] All recent issues closed `wontfix` or `stale`
- [ ] No published paper or funding acknowledgment
- [ ] Not packaged in conda/PyPI; manual installation only
- [ ] Major version released; then no updates for >1 year

---

## APPENDIX: Evaluation Checklists

### Rapid Assessment (5 minutes)

```markdown
## Project: [Name]
## Date: [Today]

### Quick Checks
- [ ] README current + clear
- [ ] Last commit <3 months ago
- [ ] ≥2 releases per year
- [ ] Test coverage badge ≥80%
- [ ] Contributing guide exists
- [ ] License is OSI-approved

### Decision
- [ ] GREEN: Proceed to comprehensive assessment
- [ ] YELLOW: Investigate specific concerns
- [ ] RED: Look for alternative

### Notes
[Observations]
```

### Comprehensive Assessment (1 hour)

```markdown
## Project: [Name]
## Date: [Today]
## Evaluator: [Name]

### ACTIVITY & MAINTENANCE
- [ ] Commits (12mo): ___/5
- [ ] PRs merged (3mo): ___/5
- [ ] Issue responsiveness: ___/5
- [ ] Contributor diversity: ___/5
**Subtotal: ___/20**

### QUALITY & RELIABILITY
- [ ] Testing & coverage: ___/5
- [ ] Code quality tooling: ___/5
- [ ] Dependency management: ___/5
**Subtotal: ___/15**

### DOCUMENTATION & USABILITY
- [ ] Doc structure: ___/5
- [ ] Examples/tutorials: ___/5
- [ ] Citation & academic credibility: ___/5
**Subtotal: ___/15**

### ECOSYSTEM INTEGRATION
- [ ] Package distribution: ___/5
- [ ] Scientific stack integration: ___/5
- [ ] Community engagement: ___/5
**Subtotal: ___/15**

### GOVERNANCE & SUSTAINABILITY
- [ ] Maintainer profile: ___/5
- [ ] Funding & support: ___/5
- [ ] Roadmap & stability: ___/5
**Subtotal: ___/15**

### TOTAL SCORE: ___/80

### ABANDONMENT RISK
- 70-80: Very Low Risk
- 60-69: Low Risk
- 50-59: Medium Risk
- 40-49: High Risk
- <40: Critical Risk

### RECOMMENDATION
[Green/Yellow/Red flag for adoption/integration]

### DETAILED NOTES
[Key findings, quotes from README/docs, specific evidence]
```

---

**Document Status**: Complete. Framework ready for repository audits.
