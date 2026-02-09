# Task Plan: Phase 3 (BLUE) - Sensitivity Analysis Documentation & Optimization

## Goal
Complete Phase 3 (BLUE) with comprehensive documentation, production examples, and performance optimization for sensitivity analysis module.

## Branch
`feature/phase-3-blue` in worktree `../.worktrees/phase-3-blue`

## Phases
- [x] Phase 1: Design - Approach & Documentation Strategy (COMPLETE)
- [ ] Phase 2: Plan - Implementation roadmap with exact tasks
- [ ] Phase 3: Execute - Documentation, examples, optimization (14 tasks)
- [ ] Phase 4: Ship - PR creation and merge

## Deliverables

### Documentation (Primary)
- [ ] API Reference: All 7 analysis modules with docstring examples
- [ ] User Guide: "Getting Started with Sensitivity Analysis"
- [ ] Tutorial: End-to-end analysis workflow (Sobol → Morris → Response Surface)
- [ ] Architecture: Design decisions, module boundaries, extensibility

### Examples (Secondary)
- [ ] Basic: Simple parameter sweep with Sobol analysis
- [ ] Advanced: Full pipeline with all 4 analyzers
- [ ] Integration: Combined with gene network model

### Optimization (Tertiary)
- [ ] Coverage tests: Bring untested modules to >80% coverage
- [ ] Performance: Profile and optimize hot paths
- [ ] Type hints: Complete mypy compliance
- [ ] Benchmarks: Publish scaling results

## Key Questions
1. Which analysis modules need user-facing examples first? (Sobol/Morris likely, Response Surface secondary)
2. Should examples be runnable notebooks or Python scripts?
3. What's the performance target? (Keep current benchmarks or improve?)

## Decisions Made

### Design Phase (COMPLETE)
- **Documentation Strategy:** Hybrid approach (API reference + 2-3 production examples) - balances velocity with value
- **Coverage Target:** 75%+ for high-risk modules only (sobol, morris, response, output, correlation) - cost-efficient risk reduction
- **Example Format:** Python scripts (not notebooks) - simpler maintenance, auto-testable, no kernel management
- **Dependency Fix:** Response.py has StandardScaler instantiation bug (line 40) - must fix in Task 1

### Context (from Phase 2 GREEN)
- Phase 2 complete: 7 modules, 1,524 LOC, all 37/37 tests passing
- Coverage status: response (0%), output (0%), correlation (0%), morris (19%), sobol (24%)
- Current overall coverage: 53% - acceptable for framework, high-risk modules need testing

## Errors Encountered
- None yet (Phase 3 just starting)

## Implementation Plan Outline

**14 Tasks across 4 phases:**

1. **Pre-requisite:** Install sklearn + statsmodels
2. **Task 1:** Fix response.py StandardScaler bug
3. **Task 2:** Extend conftest.py fixtures (sobol_batch_results, morris_batch_results, output_dir)
4. **Tasks 3-5:** test_sobol.py (constructor, analyze, rank, interactions) → 85%+ coverage
5. **Task 6:** test_morris.py (full suite) → 85%+ coverage
6. **Task 7:** test_correlation.py (full suite) → 85%+ coverage
7. **Task 8:** test_response.py (full suite, depends on Task 1) → 85%+ coverage
8. **Task 9:** test_output.py (full suite) → 90%+ coverage
9. **Task 10:** Module docstring examples (executable doctests)
10. **Task 11:** Example script - Sobol sensitivity analysis
11. **Task 12:** Example script - Morris screening
12. **Task 13:** Update __init__.py exports, final coverage verification
13. **Task 14:** Full quality gate (tests, lint, coverage)

**Parallelizable:** Tasks 3-9 after Task 2 (fixtures). Tasks 11-12 run parallel.

## Status
**IN PROGRESS** - Phase 1 (Design) ✓ COMPLETE. Moving to Phase 2 (Planning)

## Execution Efficiency (will fill at end)
- Tool calls: TBD
- Redundant calls: 0 target
- Backtracking: 0 target
- Efficiency: ≥90% target
