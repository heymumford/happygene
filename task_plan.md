# Task Plan: DNA Repair Simulation Ecosystem

## Goal
Build foundational architecture for interdependent, parameterized simulations modeling DNA repair mechanisms using peer-reviewed science. Extract principles from reference materials and identify optimal programming languages and open-source tools for implementing multi-scale biological modeling (molecular dynamics → network → cellular → tissue).

## Domain Classification
**COMPLEX** (emergent properties, multi-scale integration, unknown unknowns)
- Multiple valid technology stacks
- Simulation fidelity vs. computational cost trade-offs
- Interdependencies between molecular, kinetic, and agent-based models
- Need for emergent behavior validation

## Phases

### Phase 1: Knowledge Capture & Storage ✓
- [x] Store reference paper (Understanding DNA Repair: Mechanisms, Significance, and Simulation Opportunities)
- [x] Create persistent findings catalog

### Phase 2: Iteration 1 - Foundational Research (12 agents, haiku)
- [ ] Agent 1: Framework docs research (molecular dynamics tools)
- [ ] Agent 2: Framework docs research (agent-based modeling platforms)
- [ ] Agent 3: Framework docs research (kinetic/network modeling tools)
- [ ] Agent 4: Best practices research (biological simulation standards)
- [ ] Agent 5: Best practices research (parameterized model design)
- [ ] Agent 6: Git history analysis (DNA repair simulation projects on GitHub)
- [ ] Agent 7: Repo analysis (open-source DNA/biology simulation tools)
- [ ] Agent 8: Language evaluation (simulation languages: Python, Julia, Rust, Go)
- [ ] Agent 9: API/toolchain analysis (MCP integration possibilities)
- [ ] Agent 10: DeepSeek R1 reasoning (COMPLEX domain: trade-offs summary)
- [ ] Agent 11: Performance oracle (simulation scalability requirements)
- [ ] Agent 12: Architecture strategist (system design principles)

**Status**: Ready to dispatch

### Phase 3: Iteration 2 - Narrow Choices & MVP Plan (4-6 agents)
- [ ] Deep-dive ODE solvers: SciPy vs assimulo vs lsoda (benchmark, convergence)
- [ ] MCP FastAPI binding POC (3-hour implementation)
- [ ] Phase 1 MVP scope freeze (vertical slice definition)
- [ ] Project scaffolding: pyproject.toml, directory structure, CI/CD templates

**Agents**: 4-6 (general-purpose for ODE eval, system-architect for MVP plan)
**Status**: Ready to dispatch

### Phase 4: Iteration 3 - MVP Implementation (Manual Execution)
- [ ] Execute Phase 1 MVP roadmap (8 weeks, external to agents)
  - Week 1-2: Domain model (dataclasses, Pydantic configs)
  - Week 3-4: Damage + kinetics engine (NHEJ pathway)
  - Week 5-6: Population + cell fate + pipeline
  - Week 7: MCP server + CLI
  - Week 8: IO + SBML validation + hardening

**Status**: Pending Phase 3 scope freeze

## Execution Model

| Iteration | Agents | Focus | Model |
|-----------|--------|-------|-------|
| **1** | 12 parallel | Research tools, frameworks, languages, trade-offs | All haiku (registry-compliant) |
| **2** | 6-8 sequential | Synthesize, narrow choices, justify recommendations | Mix haiku + 1 sonnet (arch strategist) |
| **3** | 4-6 sequential | Architecture, templates, first principles extraction | Haiku + opus system-architect review |

## Key Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| Use 12 agents for Iteration 1 | COMPLEX domain requires multi-angle probing before narrowing | 2026-02-08 |
| Haiku-first (registry) | 90% of agents are haiku; specialized domains (architecture, R1) use sonnet/opus | 2026-02-08 |
| File-based planning | Must survive context compaction; 3-file pattern (plan + findings + deliverable) | 2026-02-08 |

## Status

**PHASE 2 COMPLETE** ✅ - All 12 agents dispatched, synthesis merged into unified architecture
**PHASE 2b COMPLETE** ✅ - Repository structure initialized (commit: ac749d2)
**PHASE 3 IN PROGRESS** 🔄 - ODE Solver Benchmarking (started 2026-02-08)

### Phase 2 Outcome (Iteration 1)

**Agents deployed**: 12 (haiku/sonnet/opus per registry)
**Research areas**: 6 (MD tools, ABM tools, kinetics, best practices, open source, language eval, MCP integration, architecture, performance)
**Confidence**: HIGH (multiple agents converged on same recommendations: Python-first, Mesa, operator-splitting pipeline)
**Deliverables**: 40+ research documents, ~150 KB organized in `/Users/vorthruna/ProjectsWATTS/`

**Key Decisions Made**:
1. **Technology**: Python 3.12 + SciPy + Mesa (not Julia, not Rust, not Go)
2. **Architecture**: Modular monolith, entry-point plugins, operator-splitting pipeline
3. **Extensibility**: YAML-defined pathways (no core changes for new repair types)
4. **MCP Integration**: 6 core tools, FastMCP, 120x speedup on parameter sweeps
5. **Validation**: 4-tier test pyramid, COPASI cross-validation, publication-grade reproducibility

### Phase 2b Outcome (Repository Structure)

**Deliverables**:
- `CLAUDE.md` (project configuration + ADRs)
- `pyproject.toml` (PEP 518 build system)
- `Makefile` (development automation)
- `docs/ARCHITECTURE.md` (C4 design + component model + testing strategy)
- `changelog/` (industry-standard changelog infrastructure)
- `docker/` (local dev stack: sim + postgres + minio)
- 41 directory structure with `.gitkeep` files (41 files, 1,621 insertions)

**Commit**: ac749d2 - chore: initial repository structure

**Next Immediate Action**: Phase 3 (Iteration 2, Part A) - ODE Solver Benchmarking

### Execution Efficiency (Iteration 1)

| Metric | Actual | Target | Assessment |
|--------|--------|--------|-----------|
| Parallel agents (Iter 1) | 12 | ≥10 | ✅ Met (6+6 sequential batches) |
| Model breakdown | 10 haiku, 1 sonnet, 1 opus | Registry-compliant | ✅ Met (100% compliance) |
| Redundant calls | 0 | 0 | ✅ Met (pre-deduplicated) |
| Backtracking loops | 0 | ≤1 | ✅ Met (no retries needed) |
| Convergence | HIGH (all agents → same tech stack) | ✅ Excellent | ✅ Met |
| Cost estimate | ~$2.50 | <$5.00 | ✅ Met (register discipline worked) |

### Phase 3 Execution (ODE Solver Benchmarking)

**Goal**: Benchmark 4 ODE solver options for kinetics modeling. Select best-of-breed for Phase 1 MVP (SciPy as current default).

**Agents Dispatched** (2026-02-08):

| ID | Agent | Domain | Task | Status | ETA |
|----|-------|--------|------|--------|-----|
| 1 | general-purpose | ODE Solver Research | Benchmark SciPy, assimulo, lsoda, CVODE (convergence, stiffness, speed, memory) | 🔄 IN PROGRESS | 2h |
| 2 | best-practices-researcher | Scientific Computing Standards | Best practices for stiff ODE systems, Gear's method, error handling, publication standards | 🔄 IN PROGRESS | 2h |
| 3 | framework-docs-researcher | SciPy Documentation | Deep dive: RK45 vs DOPRI5, event detection, dense output, adaptive stepping | 🔄 IN PROGRESS | 1.5h |

**Evaluation Criteria**:

| Criterion | Weight | Why |
|-----------|--------|-----|
| **Convergence accuracy** | 25% | Non-negotiable for biology (must match γ-H2AX data < 5% RMSE) |
| **Stiffness handling** | 20% | Repair kinetics exhibit stiff regions (sensor adaptation vs slow repair) |
| **Speed** | 20% | Bottleneck identified as 50% of runtime; optimization critical |
| **Memory overhead** | 10% | Population simulations (1000+ cells) must fit in 8-16GB local RAM |
| **Python integration** | 15% | Must work cleanly with NumPy, Pydantic, pytest; avoid C/FORTRAN build issues |
| **Documentation quality** | 5% | Research-grade docs; academic users should understand parameters |
| **Reproducibility** | 5% | Deterministic seed handling; exact trajectory reproduction |

**Benchmark Workload**: NHEJ repair kinetics (stiff ODE system with γ-H2AX γ-foci signal as observable)

**Expected Deliverable**: Decision record + recommendation for Phase 1 MVP (likely SciPy DOPRI5, with assimulo earmarked for Phase 2 if profiling shows need)

## Errors Encountered

(None yet)

## Next Steps

1. Dispatch Iteration 1 agents (Phase 2)
2. Collect results into findings.md after each agent completes
3. Update this plan with Phase 2 status
4. Proceed to Phase 3 synthesis
