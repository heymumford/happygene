# Stack Audit Quick Reference

**Audit Date:** 2026-02-09 | **Full Report:** CURRENT_STACK_AUDIT.md

---

## Skills Cheat Sheet (13 Total)

```
CORE LAYER (5 skills)
├─ /snap        [Meta]        Classify intent → route to agents/MCPs/skills
├─ /build       [Create]      Design → Plan → Execute (TDD gate missing)
├─ /quality     [Verify]      Test automation, contracts, security (Java/C# reviewers missing)
├─ /ship        [Deliver]     PR lifecycle → merge → deploy
└─ /fix         [Diagnose]    Root cause investigation (test diagnose missing)

FOUNDATIONAL (2 skills)
├─ /work        [Triage]      Complexity classification, planning infrastructure
└─ /write       [Document]    Technical prose, reports, diagrams (✅ No gaps)

DOMAIN SPECIALISTS (6 skills)
├─ /cv-assess   [Test]        Boundary testing (Python-biased, needs xUnit/NUnit/Jest)
├─ /psql        [Data]        PostgreSQL optimization (Python-driver-biased)
├─ /productowner [Plan]       Stakeholder alignment (✅ No gaps)
├─ /robot       [Test]        Robot Framework automation (RF-only, OK)
├─ /gitlab      [Deliver]     GitLab CI/pipeline (GitLab-specific, OK)
└─ /playwright  [Test]        Web scraping, browser automation (JS-focused, OK)
```

---

## Agent Registry at a Glance (57 Total)

### Tier Distribution
- **Tier 0 (Haiku, $0.05 avg):** 39 agents (90%)
- **Tier 1 (Sonnet, $2.25 avg):** 3 agents (8%)
- **Tier 2 (Opus, $3.00 avg):** 3 agents (2%)

### Review Agents by Language

**Python (Full Coverage ✅)**
- `kieran-python-reviewer` — Haiku (TDD, naming, async, typing)

**TypeScript (Good Coverage ✅)**
- `kieran-typescript-reviewer` — Haiku (typing, async, imports)

**Rails/Ruby (Good Coverage ✅)**
- `kieran-rails-reviewer` — Haiku (conventions, ActiveRecord, DSL)

**Java (NO COVERAGE ❌)**
- [Agent needed: kieran-java-reviewer]
- Would cover: Spring, dependency injection, OOP, naming

**C#/.NET (NO COVERAGE ❌)**
- [Agent needed: kieran-csharp-reviewer]
- Would cover: async/await, LINQ, Entity Framework, naming

### Specialist Review Agents (Good Polyglot Coverage)

| Agent | Model | Applies to |
|-------|-------|-----------|
| `pattern-recognition-specialist` | haiku | All (design patterns) |
| `security-sentinel` | haiku | All (OWASP) |
| `performance-oracle` | haiku | All (bottlenecks) |
| `code-simplicity-reviewer` | haiku | All (YAGNI) |
| `architecture-strategist` | sonnet | All (SOLID, boundaries) |
| `dhh-rails-reviewer` | sonnet | Rails only |

### Specialist Agents (Deep Expertise)

| Agent | Model | Focus | Gap |
|-------|-------|-------|-----|
| `security-reviewer` | opus | Proactive scanning (Python-biased, declares Python/FastAPI) |
| `tdd-builder` | haiku | TDD implementation (Python-default via uv run) |
| `tdd-verification-tester` | haiku | Test matrix design (polyglot-capable) |
| `system-architect` | opus | System design, SOLID (✅ polyglot) |

### Research Agents (All Polyglot-Capable ✅)

- `framework-docs-researcher` (haiku)
- `best-practices-researcher` (haiku)
- `git-history-analyzer` (haiku)
- `repo-research-analyst` (haiku)
- Built-in: `Explore` (haiku), `general-purpose` (haiku)

---

## MCP Coverage (7 Connected)

| MCP | Tier | Purpose | Polyglot |
|-----|------|---------|----------|
| `brave-search` | 0 | Web search (50 req/sec) | ✅ Universal |
| `memory` | 0 | Knowledge graph | ✅ Universal |
| `sequential-thinking` | 0 | DeepSeek R1 reasoning | ✅ Universal |
| `context7` | 1 | Library docs lookup (100+ frameworks) | ✅ Universal |
| `postgres` | 1 | PostgreSQL operations | ⚠️ SQL-agnostic, Python-driver-biased |
| `jira-guild` | 2 | Guild Jira (tickets, sprints) | ✅ Universal |
| `confluence-guild` | 2 | Confluence wiki | ✅ Universal |

**Assessment:** No MCP gaps. All language-agnostic except postgres (Python-driver-biased).

---

## Polyglot Coverage Matrix (5 Primary Languages)

| Language | Skill | Reviewer | Test Framework | Build Tool | Pre-Push | Overall |
|----------|-------|----------|---|---|---|---|
| **Python** | ✅ /build | ✅ kieran-python | ✅ pytest | ✅ just/make/uv | ✅ Detected | 100% |
| **TypeScript** | ✅ /build | ✅ kieran-typescript | ⚠️ Jest generic | ❌ Not detected | ❌ Not detected | 60% |
| **Java** | ✅ /build | ❌ MISSING | ❌ Not detected | ❌ Not detected | ⚠️ Partial | 20% |
| **C#/.NET** | ✅ /build | ❌ MISSING | ❌ Not detected | ✅ dotnet detected | ⚠️ Partial | 20% |
| **Rails/Ruby** | ✅ /build | ✅ kieran-rails | ⚠️ RSpec generic | ❌ Not detected | ❌ Not detected | 60% |

**Summary:** Python at 100%, JavaScript/Rails at 60%, Java/C# at 20%. Pre-push hook only detects Python + .NET.

---

## Critical Gaps (By Severity)

### CRITICAL (This Week)
1. **No Java reviewer** — 0% coverage, falls back to generic (loss of Spring, DI, SOLID expertise)
2. **No C#/.NET reviewer** — 0% coverage, falls back to generic (loss of async/await, LINQ, EF expertise)

### HIGH (Next Week)
3. **TDD not enforced in /build execute** — Tests written post-code, defeats early defect detection
4. **No coverage gate in /quality** — Coverage drifts, no threshold enforcement
5. **Pre-push hook incomplete** — Only detects Python/dotnet, misses Java/Node/Go

### MEDIUM (This Month)
6. **security-reviewer not auto-dispatched** — Only via explicit `/quality security`, misses suspicious patterns
7. **No contract testing guidance** — Polyglot services (Java, C#, TS) lack API boundary testing guidance

### LOW (Nice-to-Have)
8. **No test failure diagnosis** — Falls back to `/fix`, slower iteration

---

## Cost Analysis

### Current Model (Pre-Registry)
If all agents ran on Opus:
- 57 agents × $3.00/agent = $171/session
- Typical session: 9-12 agents = $27-36

### With Registry (Current)
- 39 haiku × $0.05 = $1.95
- 3 sonnet × $2.25 = $6.75
- 3 opus × $3.00 = $9.00
- Typical session: 3 haiku + 1 sonnet + 1 opus = $3.95

**Savings: 88% reduction ($27 → $3.95)**

### Proposed Changes (Minimal Cost Impact)
- Add 2 new haiku agents: +$0.10/dispatch (negligible)
- Auto-dispatch security-reviewer: +$3.00/review (new cost, ~30% of reviews)
- All other changes: Zero cost

**Impact:** Near-zero overhead for polyglot coverage + TDD enforcement.

---

## Pre-Push Quality Gate Status

### What Works ✅
```bash
# Detects project type
if [[ -f "$repo_root/justfile" ]] && [[ -f "$repo_root/pyproject.toml" ]]; then
    echo "python-just"
fi
if [[ -f "$repo_root/Makefile" ]] && [[ -f "$repo_root/pyproject.toml" ]]; then
    echo "python-make"
fi
if ls "$repo_root"/*.sln &>/dev/null; then
    echo "dotnet"
fi

# Runs appropriate test runner
just test-quick    # Python
make test-quick    # Python
dotnet test        # .NET

# Blocks push on failure, respects NO_VERIFY=1
```

### What's Missing ❌
```bash
# Doesn't detect Java
java-gradle        # gradle wrapper
java-maven         # pom.xml

# Doesn't detect JavaScript/Node
node-npm           # package.json + package-lock.json
node-yarn          # yarn.lock

# Doesn't detect Go
go-mod             # go.mod

# Doesn't enforce coverage
# (No percentage check, just test existence)

# Doesn't enforce lint/type checks
# (Just runs test runner)
```

---

## Protocols Inventory (16 Total)

### Core Protocols
- `architecture.md` — MCP servers, CLI orchestrator, personas
- `scm.md` — Git/GitHub, commit rationale, release management
- `commit-authoring.md` — Commit message structure, rationale
- `testing-standards.md` — Test markers, contract testing, pairwise
- `decision-logging.md` — ADR tracking
- `bug-template.md` — Jira bug description template
- `cortical.md` — Cortical Data OS, CLI, Bus patterns
- `opencode.md` — OpenCode CLI, multi-provider config
- `infrastructure.md` — Production deployment, Hostinger DNS

### PostgreSQL Protocols (5)
- `postgres/query-optimization.md` — EXPLAIN analysis, indexes
- `postgres/migration-workflow.md` — Safe schema evolution
- `postgres/python-drivers.md` — asyncpg, psycopg3, SQLAlchemy
- `postgres/performance-tuning.md` — Memory, monitoring
- `postgres/mcp-setup.md` — pg-aiguide, postgres-mcp-pro setup

### Missing Protocol
- `contract-testing-polyglot.md` — [NEEDS TO BE CREATED]
  Should cover: OpenAPI, gRPC, AsyncAPI, Spring Cloud Contract, Pact, Specflow

---

## Skill Dispatch Decision Trees

### /build Execute Phase (Current)
```
/build execute
└─ tdd-builder (haiku)
   └─ Execute plan (no TDD gate)
      └─ Code created or tests written?
         (Assumption: tests exist or will be written post-code)
```

### /build Execute Phase (RECOMMENDED)
```
/build execute
└─ Check: Do test files exist?
   ├─ NO: Dispatch tdd-verification-tester (haiku)
   │       └─ Design test matrix
   │       └─ Create failing tests
   │       └─ THEN dispatch tdd-builder
   └─ YES: Dispatch tdd-builder (haiku)
           └─ Execute plan (tests already written)
```

### /quality Dispatch (Current)
```
/quality dispatch
├─ security-sentinel (haiku) — OWASP baseline
├─ pattern-recognition-specialist (haiku)
├─ performance-oracle (haiku)
├─ code-simplicity-reviewer (haiku)
├─ kieran-python-reviewer (haiku) — Python only!
├─ tdd-verification-tester (haiku)
├─ data-integrity-guardian (haiku)
└─ architecture-strategist (sonnet) — Cross-cutting
```

### /quality Dispatch (RECOMMENDED)
```
/quality dispatch
├─ Detect file extension (.py, .java, .cs, .ts, .rb)
├─ Dispatch language-specific reviewer
│  ├─ .py → kieran-python-reviewer (haiku)
│  ├─ .java → kieran-java-reviewer (haiku) [NEW]
│  ├─ .cs → kieran-csharp-reviewer (haiku) [NEW]
│  ├─ .ts → kieran-typescript-reviewer (haiku)
│  ├─ .rb → kieran-rails-reviewer (haiku)
│  └─ unknown → architecture-strategist (sonnet)
├─ Pattern-match for suspicious code
│  └─ If (auth|crypto|sql|http|subprocess|upload|webhook) → security-reviewer (opus)
├─ Dispatch verification agents (all languages)
│  ├─ pattern-recognition-specialist (haiku)
│  ├─ performance-oracle (haiku)
│  ├─ code-simplicity-reviewer (haiku)
│  ├─ tdd-verification-tester (haiku)
│  └─ data-integrity-guardian (haiku)
└─ architecture-strategist (sonnet) — Cross-cutting
```

---

## Implementation Checklist (Phase 1: Critical)

### Task 1: Create Java Reviewer Agent

**File:** `/Users/vorthruna/.claude/agents/kieran-java-reviewer.md`

**Source:** Copy `kieran-python-reviewer.md`, adapt:

```markdown
---
name: kieran-java-reviewer
description: Strict Java quality standards (Spring, dependency injection, SOLID, naming conventions)
model: haiku
---

You are an expert Java code reviewer specializing in...

[Copy structure from kieran-python-reviewer, replace:]
- Python idioms → Java idioms (camelCase vs snake_case, beans vs dataclasses, etc.)
- pytest → JUnit 5, Mockito patterns
- Type hints → Type erasure, generics, wildcards
- Async patterns → CompletableFuture, Project Reactor
- SOLID principles → Spring patterns (DI containers, beans, stereotypes)
```

**Estimated effort:** 2 hours

### Task 2: Create C#/.NET Reviewer Agent

**File:** `/Users/vorthruna/.claude/agents/kieran-csharp-reviewer.md`

**Source:** Copy `kieran-python-reviewer.md`, adapt:

```markdown
---
name: kieran-csharp-reviewer
description: Strict C#/.NET quality standards (async/await, LINQ, Entity Framework, naming)
model: haiku
---

You are an expert C# code reviewer specializing in...

[Copy structure from kieran-python-reviewer, replace:]
- Python idioms → C# idioms (PascalCase, properties, LINQ, async/await)
- pytest → xUnit, NUnit patterns
- Type hints → Generic constraints, nullable reference types
- Async patterns → async/await, Task<T>, IAsyncEnumerable<T>
- ORM patterns → Entity Framework Core, LINQ queries
```

**Estimated effort:** 2 hours

### Task 3: Update model_registry.yaml

**File:** `~/.claude/model_registry.yaml`

**Add to `review_agents` section:**

```yaml
  compound-engineering:review:kieran-java-reviewer:
    model: haiku
    tier: 0
    use_case: "Strict Java quality standards (Spring, dependency injection, SOLID, naming)"

  compound-engineering:review:kieran-csharp-reviewer:
    model: haiku
    tier: 0
    use_case: "Strict C#/.NET quality standards (async/await, LINQ, Entity Framework, naming)"
```

**Estimated effort:** 30 minutes

### Task 4: Update /quality SKILL.md

**File:** `~/.claude/skills/quality/SKILL.md`

**Section to update:** "Agent Model Mapping"

**Current:**
```yaml
| `kieran-python-reviewer` | haiku | Python quality |
| `architecture-strategist` | sonnet | System boundary trade-offs |
```

**New:**
```yaml
| `kieran-python-reviewer` | haiku | Python quality |
| `kieran-java-reviewer` | haiku | Java quality |
| `kieran-csharp-reviewer` | haiku | C#/.NET quality |
| `architecture-strategist` | sonnet | System boundary trade-offs |
```

**Add language detection logic to dispatch section:**

```markdown
### Language-Specific Dispatch

Before dispatching verification agents, detect file extension:

- `.py`, `.pyw` → dispatch `kieran-python-reviewer`
- `.java` → dispatch `kieran-java-reviewer`
- `.cs`, `.fs`, `.fsx` → dispatch `kieran-csharp-reviewer`
- `.ts`, `.tsx` → dispatch `kieran-typescript-reviewer`
- `.rb` → dispatch `kieran-rails-reviewer`
- unknown → dispatch `architecture-strategist` (fallback)
```

**Estimated effort:** 1 hour

### Task 5: Test

**Files to create:**
- `/tmp/test_sample.java` (simple Spring controller)
- `/tmp/test_sample.cs` (simple ASP.NET controller)

**Test commands:**
```bash
# Manual test (if you can invoke agents directly)
/quality /tmp/test_sample.java
/quality /tmp/test_sample.cs

# Verify: Should dispatch kieran-java-reviewer and kieran-csharp-reviewer respectively
```

**Estimated effort:** 1 hour

**Phase 1 Total: 6-7 hours**

---

## Implementation Checklist (Phase 2: High Priority)

### Task 6: Enforce TDD in /build Execute

**File:** `~/.claude/skills/build/SKILL.md`

**Update execute phase to check for tests:**

```markdown
### Phase: Execute (TDD-First)

**MANDATORY:** Tests must exist before code execution.

Step 1: Check for test files
```bash
find . -name "test_*.py" -o -name "*_test.py" -o -name "tests/" | head -5
```

If NO test files found:
- GATE FAILURE: "TDD gate: Failing tests must exist before code execution"
- Dispatch: tdd-verification-tester (haiku)
  - Task: Design test matrix from requirements
  - Output: Failing tests (red phase)
- User must write tests first
- Then re-run: `/build execute`

Step 2: If test files exist or created above:
- Dispatch: tdd-builder (haiku)
- Task: Implement code to pass tests
```

**Estimated effort:** 2 hours

### Task 7: Add Coverage Gate to /quality

**File:** `~/.claude/skills/quality/SKILL.md`

**Add enforcement section:**

```markdown
### Coverage Enforcement (/quality enforce)

Runs test suite with coverage reporting and enforces threshold.

**Threshold:** 75% (HappyGene default, configurable per project)

Steps:
1. Run tests with coverage: `pytest --cov=src/ --cov-report=term-report`
2. Parse coverage output
3. Extract coverage percentage
4. Compare: coverage >= 75%
5. If below: FAIL with report
   - Current: X%
   - Target: 75%
   - Missing coverage: [files]
   - Action: Write tests for uncovered code

**Supported frameworks:**
- Python: pytest-cov
- Java: JaCoCo Maven plugin
- C#: coverlet
- TypeScript: nyc / c8
```

**Estimated effort:** 2 hours

### Task 8: Extend Pre-Push Hook for Java/Node/Go

**File:** `~/.claude/hooks/pre-push-quality-gate.sh`

**Update `detect_project_type()`:**

```bash
detect_project_type() {
    local repo_root
    repo_root="$(git rev-parse --show-toplevel)"

    # ... [existing Python checks] ...

    # Java: Maven
    if [[ -f "$repo_root/pom.xml" ]]; then
        echo "java-maven"
        return
    fi

    # Java: Gradle
    if [[ -f "$repo_root/build.gradle" ]] || [[ -f "$repo_root/build.gradle.kts" ]]; then
        echo "java-gradle"
        return
    fi

    # Node.js: npm
    if [[ -f "$repo_root/package.json" ]] && [[ -f "$repo_root/package-lock.json" ]]; then
        echo "node-npm"
        return
    fi

    # Node.js: Yarn
    if [[ -f "$repo_root/package.json" ]] && [[ -f "$repo_root/yarn.lock" ]]; then
        echo "node-yarn"
        return
    fi

    # Go: Go modules
    if [[ -f "$repo_root/go.mod" ]]; then
        echo "go-mod"
        return
    fi

    # ... [existing unknown] ...
}
```

**Add test runners:**

```bash
run_java_maven_tests() {
    log_info "Running: mvn test"
    if mvn test -q; then
        log_success "Maven tests passed"
        return 0
    else
        log_error "Maven tests failed"
        return 1
    fi
}

run_java_gradle_tests() {
    log_info "Running: gradle test"
    if gradle test -q; then
        log_success "Gradle tests passed"
        return 0
    else
        log_error "Gradle tests failed"
        return 1
    fi
}

run_node_tests() {
    log_info "Running: npm test"
    if npm test; then
        log_success "Node tests passed"
        return 0
    else
        log_error "Node tests failed"
        return 1
    fi
}

run_go_tests() {
    log_info "Running: go test ./..."
    if go test ./...; then
        log_success "Go tests passed"
        return 0
    else
        log_error "Go tests failed"
        return 1
    fi
}
```

**Estimated effort:** 3 hours

**Phase 2 Total: 7 hours**

---

## Quick Decision Guide

**Q: Should I add Java/C# reviewers if I only write Python?**
A: No. Implement only for languages you actually use.

**Q: Should coverage gate be universal (75%) or per-project?**
A: Per-project. Store threshold in CLAUDE.md or pyproject.toml.

**Q: Should security-reviewer auto-dispatch on ALL input-handling?**
A: No. Too many false positives. Start with: (auth|crypto|sql|http|subprocess).

**Q: Should /build require tests BEFORE code?**
A: YES. That's Test-Driven Development. Current assumption is post-facto.

**Q: Should pre-push hook run Java tests?**
A: YES. Hook already detects dotnet (.NET), so Java/Node/Go consistency.

---

## Document References

- **Full audit:** `CURRENT_STACK_AUDIT.md` (13,000+ words)
- **Executive summary:** `STACK_AUDIT_EXECUTIVE_SUMMARY.txt` (500+ words)
- **This file:** `STACK_AUDIT_QUICK_REFERENCE.md` (cheat sheets)
- **Original registry:** `~/.claude/model_registry.yaml`
- **Original skills:** `~/.claude/skills/{build,quality,ship,fix,work,write,snap}/SKILL.md`

---

**Generated:** 2026-02-09
**Ready for implementation:** Phase 1 (1 day), Phase 2 (1 week)
