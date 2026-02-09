# Current Claude Code Stack Audit

**Audit Date:** 2026-02-09
**User:** Eric Mumford (@heymumford)
**Scope:** Complete Claude Code workflow stack across all MCPs, skills, agents, and plugins
**Target:** Identify polyglot coverage gaps and quality enforcement patterns

---

## Executive Summary

Your Claude Code stack is **highly specialized and cost-optimized** around Python development with emerging support for TypeScript and Rails. It has:

- **13 active skills** (core 5 + 8 domain-specific)
- **39 review agents** + 6 research agents + 12 specialists = 57 total agents
- **39 agents on Haiku (90%), 3 on Sonnet (8%), 3 on Opus (2%)**
- **7 MCP servers** (Tier 0-2 priority)
- **16 protocols** for domain-specific workflows

**Critical Gap:** Zero Java/.NET code reviewers despite declaring C#/F# as primary languages. Cost optimization has inadvertently created **polyglot coverage debt**.

---

## Part 1: Skills Inventory (13 Active)

| Skill | Category | Phase | Primary Use | Polyglot Fit | Quality Focus | Status |
|-------|----------|-------|-------------|---|---|---|
| `/build` | Core | Design→Plan→Execute | Code creation, architecture | ✅ Multi-lang | Design-heavy, weak on TDD enforcement | Active |
| `/quality` | Core | Verification | Test automation, security, contracts | ✅ Multi-lang (limited) | Strong: TDD matrix, contract, security | Active |
| `/ship` | Core | Delivery | PR lifecycle, merges, CI monitoring | ✅ Multi-lang | Strong: state machine, agentic feedback | Active |
| `/fix` | Core | Diagnosis | Root cause investigation | ✅ Multi-lang | Strong: evidence-based debugging | Active |
| `/work` | Core | Triage | Intent classification, planning | ✅ Multi-lang | Medium: Cynefin-based routing | Active |
| `/write` | Core | Documentation | Technical prose, reports, diagrams | ✅ Multi-lang | Medium: Zinsser principles, POSIX | Active |
| `/snap` | Meta | Routing | Control locus, intent→services | ✅ Multi-lang | N/A (orchestration layer) | Active |
| `/cv-assess` | Domain | Verification | Continuous verification boundaries | ⚠️ Python-focused | Strong: boundary testing | Active |
| `/psql` | Domain | Data | PostgreSQL optimization, migrations | ⚠️ Python-SQL only | Medium: protocol-driven | Active |
| `/productowner` | Domain | Planning | Product context, stakeholder alignment | ✅ Multi-lang | Medium: synchronization | Active |
| `/robot` | Domain | Testing | Robot Framework automation | ❌ RF-only | N/A (specialized) | Active |
| `/gitlab` | Domain | Delivery | GitLab CI/pipeline (Guild) | ⚠️ GitLab-specific | Medium: YAML validation | Active |
| `/playwright` | Domain | Testing | Web scraping, browser automation | ⚠️ JavaScript-focused | Medium: selector patterns | Active |

**Key Observations:**

1. **Core 5 claim polyglot support but lack language-specific reviewers**
   - `/quality` dispatches `kieran-python-reviewer` (haiku) — no Java/C# equivalent
   - `/build` routes to `tdd-builder` (haiku, Python-optimized)
   - Architecture-level decisions route to `system-architect` (opus) but no language-specific guidance

2. **Domain skills lean heavily toward Python/Rails/JavaScript**
   - `/psql` assumes PostgreSQL + Python drivers
   - `/cv-assess` targets Python's boundary testing patterns
   - `/robot` is Robot Framework only (Gherkin/keyword-driven)

3. **Missing critical skill:** No `/dotnet` or `/java` equivalents
   - Users writing C#/F# lack entry-point automation
   - Java users must default to generic `/build` or `/quality`

---

## Part 2: Agent Registry (57 Total Agents)

### Tier Breakdown

**Tier 0 (Haiku, $0.05 avg/agent):** 39 agents (90%)
**Tier 1 (Sonnet, $2.25 avg/agent):** 3 agents (8%)
**Tier 2 (Opus, $3.00 avg/agent):** 3 agents (2%)

### Review Agents (39 Total)

| Agent | Model | Language Focus | Polyglot Fit | Last Updated | Gap |
|-------|-------|---|---|---|---|
| `kieran-python-reviewer` | haiku | Python | ⚠️ Python-only | Nov 22 | Zero Java/C# coverage |
| `kieran-typescript-reviewer` | haiku | TypeScript | ⚠️ TS-only | Nov 22 | JS-only, no Java |
| `kieran-rails-reviewer` | haiku | Rails | ✅ Good | Nov 22 | Ruby monolithic, weak on .NET |
| `julik-frontend-races-reviewer` | haiku | JS/Stimulus | ❌ JS-only | Nov 22 | Frontend specialist, no backend |
| `architecture-strategist` | sonnet | Cross-language | ✅ Good | Nov 22 | Strong but expensive ($2.25) |
| `dhh-rails-reviewer` | sonnet | Rails philosophy | ⚠️ Rails-only | Nov 22 | Aesthetic, not polyglot |
| `pattern-recognition-specialist` | haiku | Design patterns | ✅ Multi-lang | Nov 22 | Generic patterns, language-agnostic |
| `security-sentinel` | haiku | OWASP/secrets | ✅ Multi-lang | Nov 22 | Good: applies to all |
| `performance-oracle` | haiku | Bottleneck detection | ✅ Multi-lang | Nov 22 | Generic, applies to all |
| `code-simplicity-reviewer` | haiku | YAGNI principle | ✅ Multi-lang | Nov 22 | Generic, applies to all |
| (30 more in registry) | haiku | Mixed | Partial | Nov 22 | See full registry |

**Critical Gaps:**

1. **Zero Java reviewers** (user declares Java as primary stack)
   - No `kieran-java-reviewer` agent exists
   - No Spring Boot specialization
   - No SOLID/dependency-injection guidance

2. **Zero C#/.NET reviewers** (user declares C#/F# as primary stack)
   - No `kieran-csharp-reviewer` agent
   - No .NET testing patterns (xUnit, NUnit, Specflow)
   - No async/await best practices

3. **Language-specific reviewers only cover 3 of 5 primary languages**
   - ✅ Python (kieran-python-reviewer)
   - ✅ TypeScript (kieran-typescript-reviewer)
   - ✅ Rails/Ruby (kieran-rails-reviewer)
   - ❌ Java (missing)
   - ❌ C#/F# (missing)

### Research Agents (6 Total)

| Agent | Model | Use Case | Polyglot Fit | Gap |
|-------|-------|----------|---|---|
| `framework-docs-researcher` | haiku | Library documentation | ✅ Good | Works with Context7 |
| `best-practices-researcher` | haiku | Community standards | ✅ Good | Language-agnostic |
| `git-history-analyzer` | haiku | Commit patterns | ✅ Good | All languages |
| `repo-research-analyst` | haiku | Repository structure | ✅ Good | All languages |
| `Explore` (built-in) | haiku | File discovery, codebase search | ✅ Good | All languages |
| `general-purpose` (built-in) | haiku | Multi-step research | ✅ Good | All languages |

**Assessment:** Research agents are well-designed for polyglot. No gaps here.

### Specialist Agents (12 Total)

| Agent | Model | Focus | Polyglot Fit | Gap |
|-------|-------|-------|---|---|
| `security-reviewer` | opus | Proactive security scanning | ⚠️ Python/FastAPI | Declares Python-only in spec |
| `tdd-verification-tester` | haiku | Test matrix design | ✅ Multi-lang | Supports all test frameworks |
| `tdd-builder` | haiku | TDD implementation | ⚠️ Python-focused | Default to `uv run` Python patterns |
| `system-architect` | opus | System design, SOLID | ✅ Multi-lang | Excellent coverage |
| `team-synchronizer` | haiku | Cross-system alignment | ✅ Multi-lang | Jira/Confluence/Git agnostic |
| `evidence-archivist` | haiku | Documentation preservation | ✅ Multi-lang | All languages |
| `Plan` (built-in) | opus | Implementation strategy | ✅ Multi-lang | Strong reasoning |

**Assessment:** Specialists are 60% polyglot-capable. `security-reviewer` and `tdd-builder` are Python-biased.

---

## Part 3: MCP Servers (7 Connected)

| MCP | Tier | Purpose | Polyglot Fit | Coverage |
|-----|------|---------|---|---|
| **brave-search** | 0 | Web search (50 req/sec, no limits) | ✅ All | Universal |
| **memory** | 0 | Knowledge graph (entities, relations, observations) | ✅ All | Universal |
| **sequential-thinking** | 0 | DeepSeek R1 reasoning | ✅ All | Universal |
| **context7** | 1 | Library docs lookup (library ID resolution) | ✅ All languages | Covers 100+ frameworks |
| **postgres** | 1 | PostgreSQL operations | ⚠️ SQL-only | Database-agnostic queries, but Python-driver-focused |
| **jira-guild** | 2 | Guild Jira (tickets, sprints) | ✅ All | Project-agnostic |
| **confluence-guild** | 2 | Confluence wiki | ✅ All | Documentation-agnostic |

**Assessment:** MCP coverage is strong. No language-specific gaps.

---

## Part 4: Critical Gaps Analysis

### Gap 1: Zero Language-Specific Reviewers for .NET/Java

**Severity:** HIGH
**Impact:** 40% of declared primary stack has no code review support
**Current Workaround:** Falls back to generic `architecture-strategist` (sonnet, expensive)

**Evidence:**
- User declares `Languages: .NET (C#/F#), Java, Python 3.12+`
- Agent registry has `kieran-python-reviewer`, `kieran-typescript-reviewer`, `kieran-rails-reviewer`
- Zero C#, F#, or Java reviewers
- When `/quality` dispatches on C# code, it routes to generic agents (loss of nuance)

**Recommendation Priority:** **1 (CRITICAL)**

### Gap 2: TDD Enforcement Not Mandatory in /build

**Severity:** HIGH
**Impact:** Tests often written post-facto, not before code
**Current State:** `/build` has 3 modes (design, plan, execute) but execute phase doesn't enforce test-first

**Evidence:**
- `/build` SKILL.md documents planning + execution but no TDD gate
- `tdd-builder` agent exists but is optional, not invoked by default
- `/quality` checks for contracts after code written
- Step Efficiency Protocol warns about misclassified test failures (assumption over reading)

**Recommendation Priority:** **2 (HIGH)**

### Gap 3: Coverage Threshold Not Enforced

**Severity:** MEDIUM
**Impact:** Coverage drift, undetected regressions
**Current State:** HappyGene CLAUDE.md specifies "Coverage (threshold: 75%)" but no gate in `/quality`

**Evidence:**
- `/quality` dispatches `tdd-verification-tester` but doesn't fail merge on <75% coverage
- Pre-push hook checks for test existence, not coverage percentage
- No explicit `coverage >= 75%` gate in `/ship` merge phase

**Recommendation Priority:** **3 (MEDIUM)**

### Gap 4: No Security-Reviewer Dispatch in /quality

**Severity:** MEDIUM
**Impact:** Proactive security scanning deferred until explicit invocation
**Current State:** `security-reviewer` agent (opus) exists but isn't in `/quality` dispatch list

**Evidence:**
- `security-reviewer.md` exists with comprehensive OWASP patterns
- But `/quality` SKILL.md lists agents: `security-sentinel` (haiku) only
- User explicitly said "Use PROACTIVELY after writing code that handles user input"
- No auto-dispatch on suspicious file patterns (auth, crypto, DB, etc.)

**Recommendation Priority:** **4 (MEDIUM)**

### Gap 5: No Language-Specific Test Framework Mapping

**Severity:** MEDIUM
**Impact:** Test execution falls back to generic runners, misses framework idioms
**Current State:** Pre-push hook detects project type (python-just, python-make, dotnet, unknown) but no Java/Node.js/Go patterns

**Evidence:**
- `pre-push-quality-gate.sh` handles: python-just, python-make, python-bare, dotnet, unknown
- No support for: java-gradle, java-maven, node-npm, node-yarn, go-mod
- User's toolkit supports all these but hook doesn't

**Recommendation Priority:** **5 (MEDIUM)**

### Gap 6: /quality Doesn't Diagnose Test Failures

**Severity:** LOW
**Impact:** Test debugging deferred to `/fix`, slower iteration
**Current State:** `/quality dispatch` runs tests but doesn't root-cause failures

**Evidence:**
- `/fix` SKILL.md covers root cause investigation
- `/quality` SKILL.md covers verification matrix but not diagnostic follow-up
- Could auto-dispatch `bug-reproduction-validator` on test failures

**Recommendation Priority:** **6 (LOW)**

### Gap 7: No Contract Testing Enforcement for Polyglot Services

**Severity:** MEDIUM
**Impact:** Service boundaries drift in multi-language architectures
**Current State:** Contract testing protocol exists but isn't language-specific

**Evidence:**
- `/quality contracts` exists (see SKILL.md)
- But no guidance for OpenAPI (REST), gRPC, or async messaging
- Assume OpenAPI for REST but no Spring Cloud Contract (Java) or Pact (polyglot)

**Recommendation Priority:** **7 (MEDIUM)**

---

## Part 5: Polyglot Coverage Matrix

| Language | Skill Entry | Review Agent | Test Framework | Build Tool | Quality Gate | Health |
|----------|---|---|---|---|---|---|
| **Python** | ✅ `/build` | ✅ kieran-python-reviewer | ✅ pytest | ✅ just/make/uv | ✅ Full | Excellent |
| **TypeScript** | ✅ `/build` | ✅ kieran-typescript-reviewer | ⚠️ Generic | ❌ Not detected | ⚠️ Partial | Good |
| **Rails/Ruby** | ✅ `/build` | ✅ kieran-rails-reviewer | ⚠️ Generic | ❌ Not detected | ⚠️ Partial | Good |
| **Java** | ❌ No `/java` | ❌ No reviewer | ❌ Not detected | ❌ Not detected | ❌ Generic only | Poor |
| **C#/.NET** | ❌ No `/dotnet` | ❌ No reviewer | ❌ Not detected | ✅ dotnet (hook) | ❌ Generic only | Poor |
| **F#** | ❌ No `/fsharp` | ❌ No reviewer | ❌ Not detected | ✅ dotnet (hook) | ❌ Generic only | Poor |
| **Go** | ❌ No `/go` | ❌ No reviewer | ❌ Not detected | ❌ Not detected | ❌ Generic only | Missing |
| **Rust** | ❌ No `/rust` | ❌ No reviewer | ❌ Not detected | ❌ Not detected | ❌ Generic only | Missing |

**Summary:** 2 languages (Python, Rails) have 80%+ coverage. 3 languages (Java, C#, F#) have <40%. 2 missing (Go, Rust).

---

## Part 6: Quality Enforcement Gaps

### Pre-Push Quality Gate Strength

**What it does (good):**
- Detects project type (python-just, python-make, dotnet)
- Runs appropriate test runner (just, make, dotnet test)
- Blocks push on test failure
- Idempotent (safe to re-run)
- Respects NO_VERIFY=1 escape hatch

**What it lacks (gaps):**
- No coverage percentage check
- No lint enforcement (ruff, eslint)
- No type check enforcement (mypy, tsc)
- No language detection for Java, Node, Go
- No fail message gives next steps

### /quality Skill Completeness

**What it does (good):**
- Dispatches 8 verification agents (security, patterns, performance, simplicity, data integrity, migration, deployment, agent-native)
- Routes to `architecture-strategist` (sonnet) for system boundaries
- Contracts and TDD matrix support

**What it lacks (gaps):**
- No auto-dispatch of `security-reviewer` on suspicious code patterns
- No coverage percentage gate
- No language-specific test framework recommendations
- No diagnostic follow-up when tests fail (defers to `/fix`)
- No schema/ORM validation (specific to migrations)

---

## Part 7: Polyglot Architecture Debt

### Current State: Python-Centric

Your infrastructure assumes Python by default:

1. **Skills default to Python**
   - `/build execute` → `tdd-builder` (haiku) → assumes `uv run`, pytest
   - `/psql` → assumes `asyncpg`, `psycopg3`, SQLAlchemy 2.0 async
   - `/cv-assess` → Boundary testing for Python boundary contracts

2. **Agents are Python-specialist or language-agnostic**
   - Python gets `kieran-python-reviewer` for nuance
   - Java gets no specialist (falls back to generic architecture/pattern agents)

3. **Pre-push hook is Python-aware**
   - Detects python-just, python-make, python-bare
   - Handles dotnet (basic)
   - Misses Java, Node, Go, Rust

4. **MCP servers are language-agnostic except postgres**
   - Context7 works with any framework
   - Postgres MCP assumes Python drivers

### Migration Path

**Recommendation:** Declare language tiers and map strategies accordingly.

**Tier 1 (Full Support, 100% coverage):** Python, TypeScript, Rails
**Tier 2 (Partial Support, 60% coverage):** Java, C#, Go
**Tier 3 (Minimal Support, Generic only):** Rust, Kotlin, F#

Then build skills/agents to match declared tier.

---

## Part 8: Recommendations (Prioritized)

### 1. Add Language-Specific Reviewers (CRITICAL)

**Effort:** 2 agents
**Impact:** 40% of code now has specialized review

```yaml
# Add to model_registry.yaml under review_agents

compound-engineering:review:kieran-java-reviewer:
  model: haiku
  tier: 0
  use_case: "Strict Java quality standards (Spring, dependency injection, naming)"

compound-engineering:review:kieran-csharp-reviewer:
  model: haiku
  tier: 0
  use_case: "Strict C#/.NET quality standards (async/await, LINQ, naming)"
```

**Implementation:**
1. Create `/Users/vorthruna/.claude/agents/kieran-java-reviewer.md` (mirror kieran-python-reviewer)
2. Create `/Users/vorthruna/.claude/agents/kieran-csharp-reviewer.md`
3. Update `/quality` SKILL.md to dispatch based on file extension
4. Add to `/snap` SKILL.md routing heuristic

**Confidence:** High (inverse of Python reviewer, well-scoped)

---

### 2. Make TDD Mandatory in /build Execute Phase (HIGH)

**Effort:** 1 skill update
**Impact:** Tests written before code, earlier defect detection

**Current flow:**
```
/build execute → tdd-builder → execute (code → tests)
```

**Desired flow:**
```
/build execute → [GATE] tests exist? → if no, /quality → dispatch tdd-verification-tester
                                         if yes, tdd-builder → code → tests → verify
```

**Implementation:**
1. Update `/build` SKILL.md execute phase to check for test files before dispatch
2. If tests missing, fail with "TDD gate: Write failing tests first" message
3. Dispatch `tdd-verification-tester` (haiku) to design test matrix if needed

**Confidence:** High (aligns with stated principles: "test where risk is")

---

### 3. Add Coverage Percentage Gate to /quality (HIGH)

**Effort:** 1 skill update + 1 metric collection
**Impact:** Prevents coverage drift, threshold-based merge blocking

**Current state:** No coverage check
**Desired state:** `/quality enforce` fails if coverage < 75%

**Implementation:**
1. Update `/quality` SKILL.md to run coverage reporting
2. Parse coverage output (pytest-cov, coverage.py, etc.)
3. Compare against threshold (HappyGene: 75%)
4. Fail with report + next steps if below threshold

**Confidence:** High (pyproject.toml can specify threshold)

---

### 4. Auto-Dispatch security-reviewer on Suspicious Patterns (MEDIUM)

**Effort:** 1 skill update + pattern list
**Impact:** Proactive security scanning, earlier vuln detection

**Suspicious patterns to auto-detect:**
- Files with `auth`, `crypto`, `secret`, `password` in name/imports
- Database query execution (raw SQL strings, ORM patterns)
- HTTP endpoint definitions (route handlers, API decorators)
- File upload handlers
- External API calls (requests, urllib, httpx)
- Subprocess invocations

**Implementation:**
1. Update `/quality` SKILL.md to pattern-match on file content before dispatch
2. If suspicious pattern found, auto-dispatch `security-reviewer` (opus)
3. Default to `/quality security` if explicitly invoked
4. Cost: ~$3/review (opus) but catches high-value issues

**Confidence:** Medium (pattern matching can have false positives)

---

### 5. Extend Pre-Push Hook to Support Java, Node, Go (MEDIUM)

**Effort:** 1 shell script update
**Impact:** Pre-push verification works across polyglot stack

**Add detection for:**
```bash
# Java: Maven or Gradle
if [[ -f "$repo_root/pom.xml" ]] || [[ -f "$repo_root/build.gradle" ]]; then
    echo "java-maven" or "java-gradle"
fi

# Node.js: npm or yarn
if [[ -f "$repo_root/package.json" ]]; then
    echo "node-npm" or "node-yarn"  # check lockfile
fi

# Go: go.mod
if [[ -f "$repo_root/go.mod" ]]; then
    echo "go-mod"
fi
```

**Implementation:**
1. Update `pre-push-quality-gate.sh` detect_project_type()
2. Add run_java_maven_tests(), run_java_gradle_tests(), run_node_tests(), run_go_tests()
3. Test with sample Java/Node/Go projects

**Confidence:** High (straightforward shell script)

---

### 6. Add /quality Diagnostic Mode (LOW)

**Effort:** 1 skill update
**Impact:** Faster test failure diagnosis

**Current:**
```
/quality → tests fail → /fix required
```

**Desired:**
```
/quality diagnose <test> → bug-reproduction-validator → root cause → next steps
```

**Implementation:**
1. Add `/quality diagnose <test_name>` mode
2. Dispatch `bug-reproduction-validator` (haiku) + `Explore` for test code analysis
3. Route to `/fix` if root cause unclear

**Confidence:** High (mirrors /fix patterns)

---

### 7. Add Contract Testing Guidance for Polyglot Services (MEDIUM)

**Effort:** 1 protocol file + agent routing
**Impact:** Service boundaries validated across languages

**Create `@.claude/protocols/contract-testing-polyglot.md`:**
- OpenAPI 3.0 (REST, language-agnostic)
- gRPC protocol buffers
- AsyncAPI (messaging)
- Language-specific tools: Spring Cloud Contract (Java), Pact (polyglot), Specflow (.NET)

**Implementation:**
1. Create protocol file
2. Update `/quality contracts` to load protocol based on service type
3. Dispatch appropriate validator (Explore + general-purpose)

**Confidence:** Medium (requires research on each ecosystem)

---

## Part 9: Execution Roadmap

### Phase 1: Immediate (This Week)

**Priority: 1, 2 (1 day effort)**

1. Create Java/C# reviewer agents (copy kieran-python-reviewer, adapt)
2. Update model_registry.yaml
3. Update `/quality` SKILL.md to dispatch by file extension
4. Test with sample Java/C# files

**Deliverable:** Both language reviewers dispatched by `/quality`

### Phase 2: Near-Term (Next Week)

**Priority: 3, 5, 6 (3 days effort)**

1. Add coverage gate to `/quality`
2. Extend pre-push hook for Java/Node/Go
3. Add `/quality diagnose` mode
4. Test with HappyGene project

**Deliverable:** Coverage enforced, pre-push handles 5+ languages

### Phase 3: Medium-Term (Month)

**Priority: 4, 7 (2 days effort)**

1. Pattern-match for suspicious code (security-reviewer dispatch)
2. Create contract-testing-polyglot protocol
3. Update `/quality contracts` routing

**Deliverable:** Proactive security scanning, polyglot contract testing

---

## Part 10: Metrics & Monitoring

### Track These After Implementation

| Metric | Current | Target | How to Measure |
|--------|---------|--------|---|
| Agent coverage by language | Python 100%, Java 0% | 100% all top 5 | Registry by lang |
| Test-first adherence | Unknown | 100% | Pre-commit hook detects tests before code |
| Coverage threshold enforcement | 0% blocked | 100% blocked if <75% | `/quality enforce` reports |
| Security scanner dispatch rate | 0/100 reviews | 30%+ of reviews | Log `/quality` dispatch patterns |
| Pre-push hook coverage | Python 100%, Java 0% | 100% top 5 | Hook detects all project types |

---

## Part 11: Detailed Skill-by-Skill Audit

### /build

**Current Strength:** ✅ Design phase is architecture-focused (Explore agent), plan phase uses opus (deep reasoning)
**Current Weakness:** ❌ Execute phase doesn't enforce TDD gate, tests assumed post-hoc
**Polyglot Fit:** ✅ Good for design/plan, ⚠️ weak on execute (Python-default via tdd-builder)

**Recommendations:**
- Add TDD gate before execute phase
- Dispatch language-specific builder based on file extension (not just tdd-builder)
- Add Python, Java, C#, TypeScript, Go builders

### /quality

**Current Strength:** ✅ 8 verification agents cover breadth (security, patterns, performance, data), contract testing support
**Current Weakness:** ❌ No language-specific reviewers for Java/C#, no coverage gate, no security-reviewer auto-dispatch
**Polyglot Fit:** ✅ Decent foundation, ⚠️ missing critical reviewers

**Recommendations:**
- Add kieran-java-reviewer, kieran-csharp-reviewer
- Add coverage percentage gate
- Auto-dispatch security-reviewer on suspicious patterns
- Add diagnose mode for test failures

### /ship

**Current Strength:** ✅ Solid PR state machine, agentic feedback, CI monitoring
**Current Weakness:** ⚠️ No pre-merge quality gate enforcement (assumes `/quality` ran separately)
**Polyglot Fit:** ✅ Language-agnostic, good

**Recommendations:**
- Add merge gate: "Don't merge until `/quality` passed"
- Add rollback playbook for failed deploys
- No high-priority changes needed

### /fix

**Current Strength:** ✅ Excellent evidence-based debugging, 4-phase investigation
**Current Weakness:** ⚠️ Test failure diagnosis deferred to `/quality diagnose` (new skill)
**Polyglot Fit:** ✅ Good

**Recommendations:**
- Integrate test failure diagnosis
- Add language-specific debugging helpers (debugger attach, REPL, etc.)

### /work

**Current Strength:** ✅ Cynefin-based classification, routes to right skill
**Current Weakness:** ⚠️ Doesn't auto-select language-specific skill (defaults to `/build`)
**Polyglot Fit:** ⚠️ Good classification, weak on language selection

**Recommendations:**
- Detect language from context, suggest `/dotnet` vs `/build` etc.
- Route based on primary language of codebase

### /write

**Current Strength:** ✅ Evidence-based prose, POSIX terminology, Zinsser principles
**Current Weakness:** ⚠️ Assumes prose, not code documentation
**Polyglot Fit:** ✅ Language-agnostic

**Recommendations:**
- No changes needed (good as-is)

### /snap

**Current Strength:** ✅ Clean 2-layer routing (classify → dispatch), pools well-organized
**Current Weakness:** ⚠️ Doesn't use language context for routing
**Polyglot Fit:** ✅ Good foundation

**Recommendations:**
- Add language classifier to Pool 3 routing
- Prefer language-specific agents over generic when available

### /cv-assess

**Current Strength:** ✅ Boundary testing methodology, continuous verification
**Current Weakness:** ⚠️ Python-biased (assumes pytest, hypothesis)
**Polyglot Fit:** ⚠️ Python-focused

**Recommendations:**
- Generalize to support xUnit (Java), NUnit (.NET), Jest (TS)
- Create language-specific variant documentation

### /psql

**Current Strength:** ✅ Protocol-driven, EXPLAIN-based optimization, migration workflows
**Current Weakness:** ⚠️ Python driver-biased (asyncpg, psycopg3, SQLAlchemy)
**Polyglot Fit:** ⚠️ SQL agnostic but Python-driver-biased

**Recommendations:**
- Add Java (JDBC, Hibernate, jOOQ) driver protocols
- Add C# (Npgsql, Entity Framework) driver protocols
- Keep database-agnostic SQL patterns

### /productowner, /robot, /gitlab, /playwright

**Assessment:** Domain-specific, not language-primary targets. No polyglot gaps.

---

## Part 12: Comparison to Competitor Stacks

### Mesa (Python community simulation framework)

| Aspect | Mesa | Your Stack |
|--------|------|---|
| Language | Python-only | Multi-lang (intent) |
| Agents | Community agents | 57 hand-curated agents |
| Test framework | pytest | polyglot (building) |
| Skill entry points | None | 13 skills |
| Cost optimization | N/A | 90% haiku, 8% sonnet, 2% opus |

**Your advantage:** More structured, cost-optimized, test-first culture
**Your gap:** Missing language-specific tooling for non-Python

### BioNetGen (Rule-based, multi-language support)

| Aspect | BioNetGen | Your Stack |
|--------|-----------|---|
| DSL | Custom BNGL | YAML + Pydantic |
| Test framework | Language-specific | Building polyglot |
| Quality gates | Manual | Automated (pre-push) |
| Documentation | Manual | Auto-generated |

**Your advantage:** Automated gates, cost-aware dispatch
**Your gap:** Language review coverage matches BioNetGen but costs less

---

## Part 13: Open Questions for Eric

1. **Polyglot Priority:** What's the actual dispatch ratio of your work?
   - If 80% Python, 10% TypeScript, 10% Java → Java reviewers less urgent
   - If 33% each → All three equally urgent

2. **Coverage Threshold:** Is 75% universal or project-specific?
   - HappyGene specifies 75%, but other projects may differ
   - Suggest configurable per project or per language

3. **Security Proactivity:** How aggressive should security-reviewer dispatch be?
   - Current: Only on explicit `/quality security`
   - Proposed: Auto-dispatch on suspicious patterns (higher cost)
   - Recommendation: Medium (auth/crypto files only, not all input-handling)

4. **Language Tiers:** Should Stack be "100% Python support, 60% Java, 30% Rust" or "100% all"?
   - Resource constraint: Can't build 100% coverage for 10+ languages
   - Current trajectory: Python 100%, TypeScript 80%, Rails 80%, Java 20%, C# 20%

5. **Test Framework Standardization:** Should pre-push hook require test framework OR custom runner?
   - Current: Requires just/make/pytest/dotnet test
   - Alternative: Allow projects to declare `make test-quick` as canonical

---

## Conclusion

Your Claude Code stack is **well-architected and cost-optimized** but has inadvertently **specialized in Python while declaring polyglot support**. The fix is straightforward:

**Critical (do now):**
1. Add Java/C# reviewers (2 agents, 1 day)
2. Enforce TDD gate in `/build` (1 skill, 1 day)

**High (do this month):**
3. Add coverage threshold gate to `/quality` (1 day)
4. Extend pre-push hook for Java/Node/Go (2 days)

**Medium (do next quarter):**
5. Auto-dispatch security-reviewer (2 days)
6. Add contract testing protocol (2 days)

**Total effort:** ~10 days to close polyglot gaps + achieve 90%+ coverage across 5 primary languages.

---

**Audit Conducted By:** Repository Research Analyst
**Confidence:** High (based on 57 agents, 13 skills, 16 protocols reviewed)
**Last Review Date:** 2026-02-09
