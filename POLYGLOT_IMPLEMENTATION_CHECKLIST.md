# Polyglot Development Workflow: Implementation Checklist

**Purpose:** Step-by-step guidance for implementing best practices from best_practices_research.md

**Timeline:** 5 weeks, 8-10 hours/week

---

## Phase 1: Test Infrastructure (Week 1)

### 1.1 Python Testing Setup

- [ ] **Create benchmark tests directory**
  ```bash
  mkdir -p tests/benchmarks
  touch tests/benchmarks/__init__.py
  touch tests/benchmarks/test_expression_performance.py
  touch tests/benchmarks/test_simulation_performance.py
  ```

- [ ] **Add pytest-benchmark to dependencies**
  ```bash
  # Add to pyproject.toml [dev-dependencies]
  pytest-benchmark = "^5.1"
  ```

- [ ] **Create baseline benchmark**
  ```bash
  pytest tests/benchmarks/ --benchmark-only \
    --benchmark-save=baseline
  ```

- [ ] **Verify coverage tools installed**
  ```bash
  pip install pytest-cov coverage --quiet
  pytest tests/ --cov=happygene --cov-report=html
  ```

### 1.2 Java Testing Setup

- [ ] **Add JMH dependency to pom.xml**
  ```xml
  <dependency>
    <groupId>org.openjdk.jmh</groupId>
    <artifactId>jmh-core</artifactId>
    <version>1.37</version>
    <scope>test</scope>
  </dependency>
  ```

- [ ] **Create benchmark directory**
  ```bash
  mkdir -p benchmarks/src/jmh/java/com/happygene
  touch benchmarks/src/jmh/java/com/happygene/ExpressionBenchmark.java
  ```

- [ ] **Add JaCoCo plugin to pom.xml**
  ```xml
  <plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.11</version>
  </plugin>
  ```

- [ ] **Generate baseline coverage**
  ```bash
  mvn clean test jacoco:report
  ```

### 1.3 .NET Testing Setup

- [ ] **Add BenchmarkDotNet to .csproj**
  ```xml
  <ItemGroup>
    <PackageReference Include="BenchmarkDotNet" Version="0.13.12" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
  </ItemGroup>
  ```

- [ ] **Create benchmark project**
  ```bash
  mkdir -p benchmarks
  touch benchmarks/ExpressionBenchmarks.cs
  touch benchmarks/Program.cs
  ```

- [ ] **Generate baseline**
  ```bash
  dotnet run --configuration Release --project benchmarks/ \
    --exporters Json --resultPath results/baseline.json
  ```

### 1.4 CODEOWNERS File

- [ ] **Create CODEOWNERS in repo root**
  ```bash
  touch .github/CODEOWNERS  # GitHub
  # OR
  touch CODEOWNERS  # GitLab
  ```

- [ ] **Populate with language ownership**
  ```
  # Default reviewers
  * @primary-reviewer

  # Python-specific
  happygene/**/*.py  @python-team
  tests/unit/**/*.py  @python-team
  tests/integration/**/*.py  @python-team

  # Critical paths (2 reviewers)
  happygene/selection.py  @python-lead @python-architect
  happygene/models/expression.py  @python-lead @code-quality
  ```

- [ ] **Verify CODEOWNERS is readable**
  ```bash
  # GitHub: Test via API
  curl -H "Authorization: token $GH_TOKEN" \
    https://api.github.com/repos/user/repo/codeowners
  ```

---

## Phase 2: CI/CD Gates (Week 2)

### 2.1 GitHub Actions Setup

- [ ] **Create test workflow**
  ```bash
  mkdir -p .github/workflows
  touch .github/workflows/test.yml
  ```

- [ ] **Add polyglot test matrix**
  ```yaml
  # .github/workflows/test.yml
  name: Polyglot Tests
  on: [push, pull_request]

  jobs:
    test-python:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v4
          with:
            python-version: '3.12'
        - run: pip install -e . && pip install pytest pytest-cov -q
        - run: pytest tests/ --cov=happygene --cov-report=xml
        - uses: codecov/codecov-action@v3
          with:
            flags: python
  ```

- [ ] **Enable branch protection**
  - Navigate to Settings → Branches → main
  - Enable "Require status checks to pass before merging"
  - Enable "Require code owner reviews before merging"

### 2.2 Coverage Thresholds

- [ ] **Create coverage config** (.coveragerc or pyproject.toml)
  ```ini
  # .coveragerc
  [run]
  branch = True

  [report]
  fail_under = 80
  precision = 1
  show_missing = True
  ```

- [ ] **Add to CI** (fail job if coverage drops)
  ```yaml
  - name: Check coverage
    run: |
      pytest tests/ --cov=happygene --cov-report=term \
        --cov-fail-under=80
  ```

### 2.3 Auto-Merge Policy

- [ ] **Enable GitHub auto-merge**
  - Settings → General → Allow auto-merge (check box)

- [ ] **Create auto-merge workflow**
  ```bash
  touch .github/workflows/auto-merge.yml
  ```

### 2.4 Language-Specific Linting

- [ ] **Python: Add ruff configuration**
  ```toml
  # pyproject.toml
  [tool.ruff]
  line-length = 100
  target-version = "py312"
  ```

- [ ] **Add ruff to CI workflow**
  ```yaml
  - name: Lint
    run: ruff check . && ruff format --check .
  ```

---

## Phase 3: Code Review Setup (Week 3)

### 3.1 CODEOWNERS Validation

- [ ] **Test CODEOWNERS syntax**
  ```bash
  # For GitHub:
  npm install -g @github/codeowners
  codeowners validate CODEOWNERS
  ```

- [ ] **Verify auto-request works**
  - Create test PR with file in owned path
  - Confirm reviewer auto-requested in PR

### 3.2 Review SLAs

- [ ] **Document review expectations** (in CONTRIBUTING.md)
  ```markdown
  # Code Review Standards

  ## SLAs
  - Standard changes: Response within 4 hours
  - Critical paths: Response within 2 hours

  ## Expectations
  - Run tests locally if changes surprise you
  - Respond to feedback within 24 hours
  ```

### 3.3 Review Comment Templates

- [ ] **Create GitHub PR template**
  ```bash
  mkdir -p .github/PULL_REQUEST_TEMPLATE
  touch .github/PULL_REQUEST_TEMPLATE/default.md
  ```

---

## Phase 4: Agent-Native Patterns (Week 4)

### 4.1 Test Template Library

- [ ] **Create template directory**
  ```bash
  mkdir -p .claude/templates/tests
  touch .claude/templates/tests/python-test-template.py
  touch .claude/templates/tests/java-test-template.java
  touch .claude/templates/tests/dotnet-test-template.cs
  ```

### 4.2 Docstring Standards

- [ ] **Create docstring guide** (.claude/AGENT_READABILITY.md)
  - Document test boundaries
  - Show coverage checklist format
  - Include integration point documentation

### 4.3 Agent Constraint Templates

- [ ] **Create feature request template** (.github/AGENT_REQUEST_TEMPLATE.md)
  - Include coverage: 100% constraint
  - Link test templates
  - Define success criteria explicitly

---

## Phase 5: Monitoring & Dashboards (Week 5)

### 5.1 Codecov Integration

- [ ] **Add codecov.yml**
  ```bash
  touch codecov.yml
  ```

  ```yaml
  # codecov.yml
  coverage:
    precision: 2
    range: [75, 100]

  threshold:
    patch: 80
    change: 10

  comment:
    layout: reach,diff,flags,tree,files
  ```

- [ ] **Enable in CI workflow**
  ```yaml
  - uses: codecov/codecov-action@v3
    with:
      files: ./coverage.xml
      fail_ci_if_error: true
  ```

### 5.2 Performance Dashboard

- [ ] **Create benchmark comparison workflow**
  ```bash
  touch .github/workflows/benchmark-report.yml
  ```

### 5.3 Incident Tracking

- [ ] **Create METRICS.md template**
  - Track incidents per 1,000 diffs
  - Monitor coverage trends
  - Record review SLA compliance

---

## Sign-Off Checklist

### By Week 1 End
- [ ] Benchmark baselines created
- [ ] CODEOWNERS file created and validated
- [ ] Coverage tools installed and working

### By Week 2 End
- [ ] CI/CD workflows running
- [ ] Branch protection enabled
- [ ] Auto-merge configured
- [ ] Coverage thresholds enforced

### By Week 3 End
- [ ] CODEOWNERS auto-requesting reviewers
- [ ] Team trained on review SLAs
- [ ] Review templates available

### By Week 4 End
- [ ] Test templates available
- [ ] Docstring standards documented
- [ ] Feature request template with coverage constraints

### By Week 5 End
- [ ] Codecov dashboard live
- [ ] Benchmark reports generating
- [ ] Weekly metrics reporting running

---

## Troubleshooting

### CODEOWNERS not requesting reviewers
```bash
# Verify format
npm install -g @github/codeowners
codeowners validate CODEOWNERS

# Restart CI: Close and reopen PR
```

### Coverage drops after merge
```bash
# Check baseline
codecov list -t $CODECOV_TOKEN

# Force re-run CI on main
git commit --allow-empty -m "ci: trigger coverage baseline"
git push origin main
```

### Auto-merge not triggering
1. Verify PR has 1 approval (CODEOWNERS)
2. Verify all status checks pass
3. Verify no merge conflicts
4. Check auto-merge is enabled in repo settings

---

**Next Steps:**
1. Start with Phase 1.1 this week
2. Report blockers daily
3. Celebrate each phase completion!
