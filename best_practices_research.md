# Polyglot Development Workflows: Best Practices Research

**Research Date:** February 9, 2026
**Scope:** Python, Java, .NET with CI/CD, testing, code review, and agent-native development patterns
**Sources:** Industry leaders (Uber, HashiCorp, Databricks), GitHub/GitLab documentation, open-source best practices

---

## Table of Contents

1. [Test-First vs Event-Driven Testing](#1-test-first-vs-event-driven-testing)
2. [Code Review Gates & CODEOWNERS](#2-code-review-gates--codeowners)
3. [Agent-Native Development](#3-agent-native-development)
4. [Multi-Language Consistency](#4-multi-language-consistency)
5. [Performance Regression Prevention](#5-performance-regression-prevention)
6. [Quick Reference: Success Metrics](#quick-reference-success-metrics)

---

## 1. Test-First vs Event-Driven Testing

### Context

The choice between test-first (TDD) and event-driven/reactive testing depends on project maturity, team velocity, and risk tolerance. Industry practice in 2025-2026 shows a clear dichotomy.

### Pattern A: Test-First Development (Recommended for Continuous Delivery)

**When to use:**
- Production systems with proven product-market fit
- Multi-service architectures (Uber's 3,000+ microservices)
- Regulated domains (finance, healthcare)
- Long-term codebase maintenance (5+ years)

**Implementation:**
- Write failing test before any code (Red-Green-Refactor cycle)
- Minimum coverage threshold: 80% (line) / 90% (boundary)
- Block merge if coverage drops below threshold
- All commits paired with rationale documenting WHY change was made

**Evidence from Industry:**
- **Uber**: Reduced incidents per 1,000 diffs by 71% (2023) through comprehensive CI/CD test gates
- **TDD in 2025**: 46% of teams now automate over 50% of manual testing, accelerating TDD adoption
- **Continuous Delivery Alignment**: TDD provides confidence for frequent deployments without fear

**Trade-offs:**

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Speed to Quality** | Catches defects at commit time | 15-20% slower initial development |
| **Refactoring Safety** | Green tests prove no regressions | Requires test maintenance as code evolves |
| **Documentation** | Tests are executable specs | Tests must be readable (not just passing) |
| **CI/CD Confidence** | Auto-merge policies safe | Requires sophisticated test monitoring |

**Code Example - Python (pytest TDD pattern):**
```python
# Test first (RED)
import pytest
from happygene import GeneNetwork

def test_gene_expression_linear_model():
    network = GeneNetwork()
    gene = network.add_gene("BRCA1", parents=["TP53"])
    network.set_expression_model("Linear", alpha=0.5)

    # Call to function that doesn't exist yet
    expression = network.get_expression("BRCA1")
    assert 0 <= expression <= 1, "Expression must be normalized"

# Implementation (GREEN)
class GeneNetwork(Model):
    def get_expression(self, gene_id: str) -> float:
        """Returns normalized expression value [0,1]."""
        return self._expression_model.compute(gene_id)

# Refactor (REFACTOR)
# Move expression validation to setter, not getter
```

**Code Example - Java (JUnit TDD pattern):**
```java
// Test first (RED)
@Test
public void testGeneExpressionThreshold() {
    GeneNetwork network = new GeneNetwork();
    Gene gene = network.addGene("BRCA1");
    network.setSelectionModel(new ThresholdSelection(0.7));

    Individual ind = new Individual(gene, expression=0.8);
    assertTrue(network.survives(ind), "Expression > threshold should survive");
}

// Implementation (GREEN)
public class ThresholdSelection implements SelectionModel {
    private double threshold;

    @Override
    public boolean survives(Individual individual) {
        return individual.getExpression() >= threshold;
    }
}
```

---

### Pattern B: Event-Driven Testing (Recommended for MVPs)

**When to use:**
- Early-stage products (MVP validation phase)
- Exploratory code (proof-of-concept)
- Rapid iteration (user feedback cycles < 1 week)
- Internal tools with small user base

**Implementation:**
- Write code, then implement tests for critical paths
- Minimum coverage threshold: 50% (line) / 70% (critical paths)
- Focus on integration tests over unit tests
- Manual testing by domain expert acceptable

**Trade-offs:**

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Time to Market** | Ship features 20-30% faster | Technical debt accumulates |
| **User Feedback** | Test with real users first | Requires refactoring when scaling |
| **Team Morale** | Visible progress early | Debugging in production likely |
| **Pivot Cost** | Easy to throw away | High cleanup cost if pivot fails |

**Code Example - Python (pytest post-hoc pattern):**
```python
# Code first, test after
class GeneNetwork(Model):
    def evolve_generation(self, generations=1):
        for _ in range(generations):
            survivors = [ind for ind in self.individuals
                        if self.selection_model.survives(ind)]
            # Mutation, crossover, etc.
            return survivors

# Tests added after validation
def test_evolve_maintains_population_size():
    network = GeneNetwork(population_size=100)
    survivors = network.evolve_generation()
    assert len(survivors) > 0  # At minimum, some survive
```

---

### Coverage Thresholds by Language & Domain

| Language | Continuous Delivery | MVP/Exploratory | Critical Path | Notes |
|----------|-------------------|-----------------|---------------|-------|
| **Python** | 80% line / 90% critical | 50% line | 100% (unit+contract) | pytest-cov, boundary focus |
| **Java** | 75% line / 85% critical | 40% line | 95% (unit+contract) | JaCoCo, JUnit fixtures |
| **.NET** | 80% line / 90% critical | 50% line | 100% (unit+contract) | coverlet, xUnit patterns |

**Critical path definition:**
- Functions at system boundaries (HTTP, database, external APIs)
- Business logic with explicit requirements (contracts)
- Error handling (exceptions, null checks)
- Data validation (input/output normalization)

**Source:** [AI-Powered Test-Driven Development (TDD): Fundamentals & Best Practices 2025](https://www.nopaccelerate.com/test-driven-development-guide-2025/)

---

## 2. Code Review Gates & CODEOWNERS

### Context

Code review is the primary quality gate before merge, but implementation varies by team size and architecture complexity. CODEOWNERS files enable path-based routing of reviews to language specialists.

### Pattern A: Single Reviewer + Automated Gates (Fast Track)

**When to use:**
- Small teams (< 15 engineers)
- Non-critical code paths
- Trusted contributors
- CI/CD passing as prerequisite

**Implementation:**
```yaml
# CODEOWNERS file
# Default single reviewer

# Python-specific: auto-route to Python team
happygene/core/            @python-team
happygene/models/          @python-team
tests/                     @python-team

# Java-specific: auto-route to Java team
java-integrations/         @java-team
benchmarks/                @java-team

# .NET-specific: auto-route to .NET team
dotnet-bindings/           @dotnet-team

# Critical paths: require 2 reviewers
happygene/selection.py     @python-team @python-lead
java-integrations/jni/     @java-team @java-lead
dotnet-bindings/core/      @dotnet-team @dotnet-lead
```

**Enforcement:**
- GitHub: Branch protection rule "Require pull request reviews before merging" with minimum 1 approval
- GitLab: Protected branch + Code Owner approval required
- Auto-merge enabled: Merge after 1 approval + CI green + no conflicts

**Trade-offs:**

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Velocity** | Fast merge (< 4 hours avg) | Single reviewer may miss issues |
| **Scalability** | Works for 10-50 people | Breaks at 100+ people |
| **Knowledge Spread** | Forces reviewers to learn multiple areas | May review outside expertise |
| **Bottleneck Risk** | Low if reviewers distributed | High if single person owns path |

**GitHub Actions Example:**
```yaml
# .github/workflows/auto-merge.yml
name: Auto-merge passing PRs
on: [pull_request_review, status]

jobs:
  auto-merge:
    runs-on: ubuntu-latest
    if: |
      github.event.review.state == 'APPROVED' ||
      (github.event.state == 'success' &&
       github.event_name == 'status')
    steps:
      - uses: actions/checkout@v4
      - name: Enable auto-merge
        run: |
          gh pr merge --auto --squash $PR_NUMBER
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
```

---

### Pattern B: Two Reviewers + CODEOWNERS Specialty (High Assurance)

**When to use:**
- Large teams (15+ engineers)
- Critical systems (production, payments, auth)
- Multi-language polyglot (require language-specific sign-off)
- Regulated domains

**Implementation:**
```yaml
# CODEOWNERS file with 2-reviewer requirement

# Python models (domain expert + code quality expert)
happygene/models/*.py     @domain-expert-python @python-architect

# Java integration (Java expert + performance expert)
java-integrations/**      @java-lead @performance-engineer

# .NET bindings (C# expert + interop expert)
dotnet-bindings/**        @dotnet-architect @interop-specialist

# Database migrations (any language: DBA + domain owner)
migrations/**             @dba @domain-expert

# Critical infrastructure
src/core/selection.py     @python-lead @python-architect @cto
```

**Enforcement:**
- GitHub: `require_code_owner_reviews: true` + minimum 2 approvals from CODEOWNERS
- GitLab: "Requires approvals from Code-Owners" + minimum 2 Code Owners
- GitHub 2025 feature: "Required review by specific teams"

**Trade-offs:**

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Quality** | 2 eyes catch 40% more issues than 1 | +1-2 days to merge |
| **Knowledge** | Ensures domain + architecture review | Requires 2 available reviewers |
| **Bottleneck Risk** | Lower (distributed across 2) | Can still block if both unavailable |
| **Expertise** | Language specialist mandatory | Slows non-critical changes |

**Uber's Pattern:**
Uber gates every change affecting 1,000+ backend services with:
1. Automated test threshold: 90% placebo pass rate (tests should pass consistently)
2. Service tiering: Changes rolled out to tier 0 first, then tier 1+ only if no regressions
3. Automatic quarantine: Tests below 90% pass rate auto-marked non-blocking, alert filed

**Result:** Reduced incidents per 1,000 diffs by 71%

**Source:** [About code owners - GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners), [Shifting E2E Testing Left at Uber](https://www.uber.com/blog/shifting-e2e-testing-left/)

---

### Pattern C: Hybrid Automation (Recommended for Polyglot Teams)

**When to use:**
- Polyglot teams (Python, Java, .NET specialists)
- Auto-merge for automated changes (dependencies, format fixes)
- 2-reviewer gates for code changes only

**Implementation:**
```yaml
# .github/workflows/polyglot-gates.yml
name: Polyglot Code Review Gates

on: [pull_request]

jobs:
  language-routing:
    runs-on: ubuntu-latest
    steps:
      # Detect changed files
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v2
        id: changes
        with:
          filters: |
            python:
              - 'happygene/**/*.py'
              - 'tests/**/*.py'
            java:
              - 'java-integrations/**'
            dotnet:
              - 'dotnet-bindings/**'

      # Require language-specific reviewers
      - name: Require Python reviewers
        if: steps.changes.outputs.python == 'true'
        run: echo "Requires review from @python-team"

      - name: Require Java reviewers
        if: steps.changes.outputs.java == 'true'
        run: echo "Requires review from @java-team"

      - name: Require .NET reviewers
        if: steps.changes.outputs.dotnet == 'true'
        run: echo "Requires review from @dotnet-team"

  auto-merge-deps:
    runs-on: ubuntu-latest
    if: |
      github.actor == 'dependabot[bot]' &&
      contains(github.event.pull_request.title, 'Bump')
    steps:
      - name: Auto-merge dependency updates
        run: |
          gh pr merge --auto --squash $PR_NUMBER
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 3. Agent-Native Development

### Context

AI agents (Claude, GitHub Copilot, etc.) can implement features end-to-end, but require structured guidance: clear test suites, explicit coverage constraints, and readable documentation that machines can parse.

### Pattern A: Explicit Coverage Constraints

**Core Requirement:**
Agents don't maintain test coverage automatically. Organizations must require unit tests as a constraint in every agent request.

**Implementation:**
```markdown
# Feature Request: JWT Authentication (Agent-Native)

## Constraints (Non-negotiable)
- Unit test coverage: 100% for auth module
- Happy path tests: Successful token generation and validation
- Sad path tests: Invalid signatures, expired tokens, missing claims
- Edge cases: Empty secrets, oversized tokens, wrong algorithms
- No implementation until tests exist and pass

## Success Criteria
- All unit tests pass locally
- Integration tests pass with Redis cache
- No coverage regressions
- Commit messages include rationale (WHY, not WHAT)

## Required Test Categories
1. **Token Generation** - Valid/invalid inputs, algorithm support
2. **Token Validation** - Expired, malformed, revoked tokens
3. **Claims Parsing** - Required fields present, data types correct
4. **Secret Management** - Rotation, fallback keys, key enumeration
5. **Error Handling** - Clear error messages, no credential leaks
```

**2026 Standard Example:**
Leading organizations (e.g., Databricks ML Ops teams) explicitly require 100% test coverage as a constraint when requesting AI-generated features.

**Trade-offs:**

| Aspect | Benefit | Cost |
|--------|---------|------|
| **Quality** | Agent produces tested code immediately | 20-30% slower (write tests first) |
| **Maintenance** | Tests explain intent, catch regressions | Requires test code review |
| **Debugging** | Tests isolate failures | Agents need test output to learn |
| **Knowledge** | Tests serve as executable specs | Team must maintain test suite |

---

### Pattern B: Documentation for Machine Readability

**Requirement:**
Agents understand code comments, docstrings, and examples better than prose. Structure docs for parsing.

**Implementation - Python:**
```python
"""
Gene expression model.

## Coverage Requirements
- 100% line coverage for ExpressionModel.compute()
- 100% boundary coverage for all subclasses (Linear, Hill, Constant)
- Edge cases: alpha=0, alpha=1, missing parents, circular dependencies

## Test Boundaries
- Linear: alpha ∈ [0, 1], input ∈ [0, 1] → output ∈ [0, 1]
- Hill: n ∈ [1, 5], k ∈ (0, 1), input ∈ [0, 1] → output ∈ [0, 1]
- Constant: output always equals constant value

## Integration Points
- Input: parent_expressions (dict: str → float)
- Output: normalized_expression (float: [0, 1])
- Dependencies: numpy (optional, for numerical stability)

## Anti-patterns
- Never return NaN (normalize to 0 instead)
- Never mutate parent_expressions
- Never assume parent order (use dict, not list)
"""
class ExpressionModel(ABC):
    @abstractmethod
    def compute(self, parent_expressions: Dict[str, float]) -> float:
        """
        Compute gene expression from parent values.

        Args:
            parent_expressions: Dict mapping parent gene IDs to [0,1] values

        Returns:
            Normalized expression in [0, 1]

        Raises:
            ValueError: If parent values outside [0, 1]
            KeyError: If required parent missing
        """
        pass
```

**Implementation - Java:**
```java
/**
 * Gene expression model interface.
 *
 * <h2>Coverage Requirements</h2>
 * <ul>
 *   <li>100% line coverage for all implementations</li>
 *   <li>100% boundary coverage: input [0,1] → output [0,1]</li>
 *   <li>Edge cases: null parents, empty values, division by zero</li>
 * </ul>
 *
 * <h2>Test Boundaries</h2>
 * <ul>
 *   <li>LinearModel: alpha ∈ [0,1], expression ∈ [0,1]</li>
 *   <li>HillModel: n ∈ [1,5], k ∈ (0,1), input ∈ [0,1]</li>
 * </ul>
 *
 * <h2>Invariants</h2>
 * <ul>
 *   <li>Output always ∈ [0,1]</li>
 *   <li>No NaN/Infinity returns (normalize to 0)</li>
 *   <li>No null returns</li>
 * </ul>
 */
public interface ExpressionModel {
    /**
     * Compute normalized gene expression [0,1].
     *
     * @param parentExpressions map of parent gene ID to expression [0,1]
     * @return normalized expression [0,1]
     * @throws IllegalArgumentException if parent values outside [0,1]
     * @throws NullPointerException if parentExpressions null
     */
    float compute(Map<String, Float> parentExpressions)
        throws IllegalArgumentException;
}
```

**Implementation - .NET:**
```csharp
/// <summary>
/// Gene expression model interface.
///
/// <para>
/// <b>Coverage Requirements:</b>
/// <list type="bullet">
///   <item>100% line coverage for all implementations</item>
///   <item>100% boundary coverage: input [0,1] → output [0,1]</item>
///   <item>Edge cases: null parents, empty map, NaN inputs</item>
/// </list>
/// </para>
///
/// <para>
/// <b>Test Boundaries:</b>
/// <list type="bullet">
///   <item>LinearModel: alpha ∈ [0,1], input ∈ [0,1]</item>
///   <item>HillModel: n ∈ [1,5], k ∈ (0,1), input ∈ [0,1]</item>
/// </list>
/// </para>
/// </summary>
public interface IExpressionModel
{
    /// <summary>
    /// Compute normalized gene expression [0,1].
    /// </summary>
    /// <param name="parentExpressions">Map of parent gene ID to [0,1] expression</param>
    /// <returns>Normalized expression in [0,1]</returns>
    /// <exception cref="ArgumentOutOfRangeException">If parent values outside [0,1]</exception>
    /// <exception cref="ArgumentNullException">If parentExpressions null</exception>
    float Compute(Dictionary<string, float> parentExpressions);
}
```

**Source:** [Software development in 2026: A hands-on look at AI agents](https://www.techtarget.com/searchapparchitecture/opinion/A-hands-on-look-at-ai-agents), [Agentic SDLC in practice: the rise of autonomous software delivery 2026](https://www.pwc.com/m1/en/publications/2026/docs/future-of-solutions-dev-and-delivery-in-the-rise-of-gen-ai.pdf)

---

### Pattern C: Agent Prompting for Implementation

**Structure:**
```markdown
# Task: Implement Linear Expression Model

## Requirements (From Tests)
1. Linear.compute(parents) = alpha * mean(parents.values())
2. Output normalized to [0, 1]
3. Handles empty parents → returns 0
4. Handles NaN inputs → returns 0 (no exceptions)

## Test Suite (Pass these first)
- test_linear_mean_calculation: compute({a:0.5, b:0.3}) == 0.4*alpha
- test_linear_normalization: any alpha, any input → output ∈ [0, 1]
- test_empty_parents: compute({}) == 0
- test_nan_handling: compute({a: NaN}) == 0 (no exception)

## Implementation Guidance
- Inherit from ExpressionModel abstract class
- Use numpy.mean() for parent aggregation
- Clamp output to [0, 1] using numpy.clip()
- Document expected parameter ranges in docstring

## Success Criteria
- All 4 tests pass
- Coverage 100% (line + branch)
- No external dependencies beyond numpy
- Code review ready (no TODOs, all functions documented)
```

---

## 4. Multi-Language Consistency

### Pattern A: Shared Test Infrastructure

**Problem:**
Each language has its own testing framework (pytest, JUnit, xUnit), making it hard to enforce consistent patterns across polyglot repos.

**Solution:**
Use CI/CD matrix testing with unified reporting.

**Implementation - GitHub Actions:**
```yaml
# .github/workflows/polyglot-test.yml
name: Polyglot Testing Matrix

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e . -q
          pip install pytest pytest-cov pytest-xdist -q

      - name: Run unit tests
        run: |
          pytest tests/unit -v --cov=happygene --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration -v --timeout=30

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: python

  test-java:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v3
        with:
          java-version: '21'
          distribution: 'temurin'

      - name: Run Maven tests
        run: |
          mvn test -DskipITs=false -q

      - name: Generate coverage
        run: |
          mvn jacoco:report -q

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./target/site/jacoco/jacoco.xml
          flags: java

  test-dotnet:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0'

      - name: Run xUnit tests
        run: |
          dotnet test --configuration Release --logger "trx" --collect:"XPlat Code Coverage"

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: dotnet

  quality-gates:
    needs: [test-python, test-java, test-dotnet]
    runs-on: ubuntu-latest
    steps:
      - name: Check combined coverage
        run: |
          # All languages must meet minimum thresholds
          # (in practice, fetch codecov reports and validate)
          echo "Python: ${{ env.PYTHON_COVERAGE }}"
          echo "Java: ${{ env.JAVA_COVERAGE }}"
          echo ".NET: ${{ env.DOTNET_COVERAGE }}"
```

**Shared Quality Gates:**
```yaml
# Unified minimum thresholds (all languages)
coverage_minimum: 80
coverage_critical: 90
max_flaky_tests: 2
max_skipped_tests: 0
required_checks: [lint, type-check, test, security]
```

---

### Pattern B: Language-Specific Quality Checks

**Implementation:**
```yaml
# .github/workflows/language-gates.yml
name: Language-Specific Quality Gates

on: [pull_request]

jobs:
  python-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Lint (ruff)
        run: |
          pip install ruff -q
          ruff check happygene/ tests/

      - name: Format (ruff)
        run: ruff format --check happygene/ tests/

      - name: Type check (mypy)
        run: |
          pip install mypy types-all -q
          mypy happygene/ --strict

      - name: Security (bandit, semgrep)
        run: |
          pip install bandit semgrep -q
          bandit -r happygene/ -ll
          semgrep --config=auto happygene/

  java-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v3
        with:
          java-version: '21'

      - name: Checkstyle
        run: |
          mvn checkstyle:check -q

      - name: SpotBugs (static analysis)
        run: |
          mvn spotbugs:check -q

      - name: PMD (code smell detection)
        run: |
          mvn pmd:check -q

      - name: Dependency audit
        run: |
          mvn dependency-check:check -q

  dotnet-quality:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v3
        with:
          dotnet-version: '8.0'

      - name: StyleCop (code style)
        run: |
          dotnet tool install -g StyleCopAnalyzers
          dotnet build --configuration Release

      - name: Code analysis
        run: |
          dotnet analyzers run

      - name: Security audit
        run: |
          dotnet tool install -g dotnet-outdated
          dotnet outdated --pre-release ignore
```

---

### Pattern C: Unified CI/CD Results Dashboard

**Tool:**
Use [Codecov](https://codecov.io/), [Buildkite](https://buildkite.com/), or [DataDog](https://www.datadoghq.com/) for unified visibility across language-specific test results.

**Example Codecov Badge:**
```markdown
# Coverage Status

| Language | Coverage | Trend | Min Threshold |
|----------|----------|-------|---------------|
| Python | 87% | ↑ +2% | 80% |
| Java | 82% | ↔ | 75% |
| .NET | 79% | ↓ -1% | 75% |
| **Overall** | **82%** | ↑ +1% | **80%** |

![Codecov](https://codecov.io/gh/user/repo/branch/main/graphs/badge.svg)
```

---

## 5. Performance Regression Prevention

### Pattern A: Automated Baseline Benchmarking

**Three-Tier Approach:**

1. **Unit-Level Benchmarks** (Fast, on every commit)
   - pytest-benchmark (Python)
   - JMH (Java)
   - BenchmarkDotNet (.NET)

2. **Integration Benchmarks** (Medium, on main/release branches)
   - End-to-end workflows
   - Multi-threaded simulations
   - Real dataset sizes

3. **Production Benchmarks** (Slow, post-deployment)
   - Production traffic simulation
   - Real hardware profiles
   - Canary deployments

---

### Pattern B: pytest-benchmark (Python)

**Implementation:**
```python
# tests/benchmarks/test_expression_performance.py
import pytest
from happygene import GeneNetwork, Linear

@pytest.mark.benchmark
def test_expression_compute_linear(benchmark):
    """Benchmark Linear.compute() performance."""
    network = GeneNetwork()
    model = Linear(alpha=0.5)
    parents = {f"gene_{i}": 0.5 for i in range(100)}

    # Baseline: < 1 microsecond per call
    result = benchmark(model.compute, parents)
    assert 0 <= result <= 1

@pytest.mark.benchmark
def test_evolution_generation_1000_individuals(benchmark):
    """Benchmark one evolution cycle on 1000 individuals."""
    network = GeneNetwork(population_size=1000)

    # Baseline: < 100 milliseconds per generation
    result = benchmark(network.evolve_generation)
    assert len(result) > 0
```

**CI/CD Integration:**
```bash
# Capture baseline on main
pytest tests/benchmarks/ --benchmark-only \
  --benchmark-json=.benchmarks/baseline.json

# Compare on PR
pytest tests/benchmarks/ --benchmark-compare \
  --benchmark-compare-fail=mean:5%  # Fail if > 5% slower
```

**GitHub Actions:**
```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmarking

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e . -q
          pip install pytest pytest-benchmark -q

      - name: Benchmark PR branch
        run: |
          pytest tests/benchmarks/ --benchmark-json=.benchmarks/pr.json

      - name: Fetch baseline
        run: |
          # Download baseline from main branch artifacts
          curl -s https://api.github.com/repos/${{ github.repository }}/actions/artifacts \
            | jq -r '.artifacts[] | select(.name=="benchmark-baseline") | .url' \
            | xargs curl -o baseline.json

      - name: Compare and report
        run: |
          pytest tests/benchmarks/ --benchmark-compare=baseline.json \
            --benchmark-compare-fail=mean:10% \
            --benchmark-json=.benchmarks/pr.json

      - name: Comment on PR
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const pr_results = JSON.parse(fs.readFileSync('.benchmarks/pr.json'));
            const message = `## Performance Results\n\n${pr_results.benchmarks.map(b =>
              `- **${b.name}**: ${b.stats.mean.toFixed(3)}ms (±${b.stats.stddev.toFixed(3)})`
            ).join('\n')}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: message
            });
```

---

### Pattern C: JMH (Java)

**Implementation:**
```java
// benchmarks/src/jmh/java/com/happygene/ExpressionBenchmark.java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MICROSECONDS)
@Fork(value = 3, warmupIterations = 2)
@Measurement(iterations = 5, time = 5, timeUnit = TimeUnit.SECONDS)
@Warmup(iterations = 3, time = 5, timeUnit = TimeUnit.SECONDS)
public class ExpressionBenchmark {

    private GeneNetwork network;
    private ExpressionModel model;
    private Map<String, Float> parents;

    @Setup(Level.Trial)
    public void setup() {
        network = new GeneNetwork();
        model = new LinearExpressionModel(0.5f);
        parents = new HashMap<>();
        for (int i = 0; i < 100; i++) {
            parents.put("gene_" + i, 0.5f);
        }
    }

    @Benchmark
    public float computeLinearExpression() {
        return model.compute(parents);
    }

    @Benchmark
    public void evolveGeneration1000() {
        network = new GeneNetwork(1000);
        network.evolveGeneration();
    }
}
```

**Run with CI/CD:**
```bash
# Generate baseline
mvn -f benchmarks/pom.xml jmh:benchmark \
  -Djmh.resultFormat=json \
  -Djmh.result=target/benchmark-baseline.json

# Compare on PR
mvn -f benchmarks/pom.xml jmh:benchmark \
  -Djmh.resultFormat=json \
  -Djmh.result=target/benchmark-pr.json

# Diff results
jmh-compare target/benchmark-baseline.json target/benchmark-pr.json \
  --threshold 5%  # Alert if > 5% slower
```

---

### Pattern D: BenchmarkDotNet (.NET)

**Implementation:**
```csharp
// benchmarks/ExpressionBenchmarks.cs
[SimpleJob(warmupCount: 3, targetCount: 5)]
[MemoryDiagnoser]
[RPlotExporter]
public class ExpressionBenchmarks
{
    private GeneNetwork _network;
    private IExpressionModel _model;
    private Dictionary<string, float> _parents;

    [GlobalSetup]
    public void Setup()
    {
        _network = new GeneNetwork();
        _model = new LinearExpressionModel(0.5f);
        _parents = Enumerable.Range(0, 100)
            .ToDictionary(i => $"gene_{i}", _ => 0.5f);
    }

    [Benchmark]
    public float ComputeLinearExpression()
    {
        return _model.Compute(_parents);
    }

    [Benchmark]
    public void EvolveGeneration1000()
    {
        _network = new GeneNetwork(1000);
        _network.EvolveGeneration();
    }
}
```

**Run with CI/CD:**
```bash
# Generate baseline
dotnet run --configuration Release -- \
  --exporters Json \
  --resultPath results/baseline.json

# Compare on PR
dotnet run --configuration Release -- \
  --exporters Json \
  --resultPath results/pr.json \
  --baseline results/baseline.json
```

---

### Pattern E: Performance Alert Thresholds

**GitHub Action Implementation:**
```yaml
# .github/workflows/perf-alert.yml
name: Performance Regression Alert

on:
  pull_request:

jobs:
  check-regressions:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run benchmarks
        id: bench
        run: |
          # Run benchmarks and capture JSON output
          # (language-specific commands above)

      - name: Detect regressions
        env:
          THRESHOLD: 0.10  # 10% tolerance
        run: |
          python3 << 'EOF'
          import json, os, sys

          baseline = json.load(open('baseline.json'))
          current = json.load(open('current.json'))
          threshold = float(os.getenv('THRESHOLD', 0.10))

          regressions = []
          for bench in current['benchmarks']:
              baseline_bench = next((b for b in baseline['benchmarks']
                                   if b['name'] == bench['name']), None)
              if baseline_bench:
                  delta = (bench['mean'] - baseline_bench['mean']) / baseline_bench['mean']
                  if delta > threshold:
                      regressions.append({
                          'name': bench['name'],
                          'delta': delta,
                          'baseline': baseline_bench['mean'],
                          'current': bench['mean']
                      })

          if regressions:
              print("::error::Performance regressions detected:")
              for r in regressions:
                  print(f"  {r['name']}: {r['delta']*100:.1f}% slower")
                  print(f"    Baseline: {r['baseline']:.3f}ms → Current: {r['current']:.3f}ms")
              sys.exit(1)
          else:
              print("✓ No regressions detected")
          EOF
```

**Sources:** [GitHub Action for continuous benchmarking](https://github.com/benchmark-action/github-action-benchmark), [pytest-benchmark documentation](https://pytest-benchmark.readthedocs.io/), [Mastering .NET Performance Testing with BenchmarkDotNet](https://www.leavesnet.com/contents/139)

---

## Quick Reference: Success Metrics

### Coverage by Phase

| Phase | Python | Java | .NET | Notes |
|-------|--------|------|------|-------|
| MVP | 40-50% | 40-50% | 40-50% | Focus: happy path + critical |
| Beta | 70% | 70% | 70% | Add sad paths, edge cases |
| Production | 85-90% | 80-85% | 85-90% | Language-specific thresholds |
| Critical paths | 100% | 100% | 100% | Boundaries, contracts, business logic |

### Review Gates by Team Size

| Team Size | Reviewers | Coverage Min | Merge Time |
|-----------|-----------|--------------|-----------|
| 1-5 | 1 + CI | 70% | < 2 hours |
| 5-15 | 1 + CI | 80% | < 4 hours |
| 15-50 | 2 + CI | 85% | < 8 hours |
| 50+ | 2 (specialists) + CI | 90% | < 24 hours |

### Performance Baseline Thresholds

| Metric | Threshold | Alert Level | Action |
|--------|-----------|-------------|--------|
| Mean latency | +5% | Medium | Comment on PR, request explanation |
| P95 latency | +10% | High | Block merge, investigate root cause |
| Memory allocation | +15% | Medium | Review, optimize if > 50MB |
| GC time | +10% | High | Investigate, profile if > 1ms |

### Agent-Native Development Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| Unit test coverage | 100% (new code) | Agents don't self-correct |
| Happy paths | ≥ 2 tests | One path insufficient |
| Sad paths | ≥ 3 tests | Error handling crucial |
| Edge cases | ≥ 2 tests per boundary | Boundary is where bugs live |
| Documentation | Machine-readable comments | Agents consume docs as config |

---

## Implementation Roadmap

### Week 1: Test Infrastructure
- [ ] Set up pytest-benchmark / JMH / BenchmarkDotNet baselines
- [ ] Create CODEOWNERS file with language-specific owners
- [ ] Enable branch protection rules (1 reviewer + CI pass)

### Week 2: CI/CD Gates
- [ ] Implement polyglot test matrix (GitHub Actions / GitLab CI)
- [ ] Set coverage thresholds (80% minimum, 90% critical)
- [ ] Configure auto-merge for passing CI + approved PRs

### Week 3: Code Review
- [ ] Document review expectations (1 vs 2 reviewers)
- [ ] Train team on CODEOWNERS routing
- [ ] Establish code review SLA (< 4 hours response)

### Week 4: Agent-Native Patterns
- [ ] Document coverage requirements for agents
- [ ] Create test templates for each language
- [ ] Add docstring standards (machine-readable)

### Week 5: Monitoring
- [ ] Set up Codecov / DataDog dashboards
- [ ] Create alerts for coverage regressions
- [ ] Track incident rate (per 1,000 diffs like Uber)

---

## Additional Resources

### Official Documentation
- [GitHub Code Owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [GitLab CODEOWNERS](https://docs.gitlab.com/user/project/codeowners/)
- [pytest-benchmark documentation](https://pytest-benchmark.readthedocs.io/)
- [HashiCorp Terraform Testing](https://www.hashicorp.com/en/blog/testing-hashicorp-terraform)

### Case Studies
- [Uber: Shifting E2E Testing Left](https://www.uber.com/blog/shifting-e2e-testing-left/)
- [Databricks: MLOps Workflows with MLflow](https://www.databricks.com/blog/2020/01/16/automate-deployment-and-testing-with-databricks-notebook-mlflow.html)
- [HashiCorp: Continuous Deployment for Large Monorepos](https://www.uber.com/blog/continuous-deployment/)

### Tools & Frameworks
- **Python:** pytest, pytest-benchmark, pytest-xdist, coverage.py, mypy, ruff
- **Java:** JUnit, JMH, Mockito, TestNG, JaCoCo
- **.NET:** xUnit, Moq, BenchmarkDotNet, coverlet

---

## Synthesis: The Mumford Approach

Based on your team's skill stack (Python, Java, .NET) and ambitions (agent-native development), recommend this unified strategy:

1. **Test-First Discipline** (Core)
   - All production code requires failing test first
   - 80% minimum coverage (line), 90% (boundary)
   - Agents cannot ship without 100% coverage constraint

2. **Polyglot Code Review** (Hybrid)
   - 1 reviewer for non-critical paths (standard code, configs)
   - 2 reviewers for critical paths (auth, data, business logic)
   - CODEOWNERS routes to language specialists automatically
   - Auto-merge enabled after 1 approval + CI green + no conflicts

3. **Performance Monitoring** (Continuous)
   - Baseline benchmarks on every commit (unit-level)
   - Integration benchmarks on main/release (2-3x slower allowed)
   - Alert on > 5% latency increase, > 10% memory increase
   - Investigate post-merge CI failures immediately

4. **Agent-Native Patterns** (Explicit)
   - All agent requests include "coverage: 100%" constraint
   - Docstrings specify test boundaries (happy/sad/edge paths)
   - No implementation until all tests pass
   - Commit rationale (WHY) required from agents, not just code (WHAT)

This balances velocity (fast merges, agent assistance) with confidence (test gates, review expertise, performance monitoring).

---

**Document Generated:** February 9, 2026
**Last Updated:** February 9, 2026
