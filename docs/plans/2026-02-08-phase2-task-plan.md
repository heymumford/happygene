# Phase 2 Task Plan: Gene Regulatory Networks & Advanced Models

## Goal
Extend happygene with multi-gene regulatory interactions, advanced selection models, and performance optimization for 10k-individual populations.

## Complexity Classification
**COMPLICATED** — Known patterns exist (expression models, selection models), but requires new abstractions (regulatory networks, adjacency matrices, circuit detection) and significant refactoring of expression pipeline.

## Phases

### Phase 1: Design & Architecture ✅
- [x] Create Phase 2 ADRs (regulatory network strategy, composite expression models, circuit detection)
- [x] Design RegulatoryNetwork class with adjacency matrix representation
- [x] Design RegulationConnection (edge type) with interaction strengths
- [x] Plan composite expression model pipeline
- [x] Design circuit detection algorithms (feedback loops, feedforward)
- [x] Design performance benchmarking harness

**Status**: Complete — see `/Users/vorthruna/ProjectsWATTS/happygene/docs/plans/2026-02-08-phase2-architecture-adrs.md`

### Phase 2: Planning (Weeks 13-26) ✅
- [x] Create detailed Week-by-week implementation plan
- [x] Define file changes and test requirements
- [x] Identify integration points with Phase 1 code

**Status**: Complete — see `/Users/vorthruna/ProjectsWATTS/happygene/docs/plans/2026-02-08-phase2-implementation-plan.md`

### Phase 3: Implementation (Manual execution)
- [ ] Week 13-16: Gene regulation subsystem (regulatory network, composite models, circuit detection)
- [ ] Week 17-20: Benchmarking & performance optimization
- [ ] Week 21-26: Advanced selection models (sexual/asexual, epistatic fitness, multi-objective)

**Status**: Pending Phase 2 planning completion

## Key Questions (Answered in Design Phase)

1. **RegulatoryNetwork Representation**: ✅ Static adjacency matrix (scipy.sparse CSR), immutable post-init
2. **Expression Pipeline**: ✅ CompositeExpressionModel wraps base + regulatory overlay
3. **Circuit Detection**: ✅ Static detection at init, optional (off by default)
4. **Performance Targets**: ✅ Vectorize at population level, target 5s for 10k indiv × 100 genes × 1k gen
5. **Backwards Compatibility**: ✅ Phase 2 GeneNetwork accepts Phase 1 entities unchanged; RegulatoryNetwork optional

## Decisions Made

| Decision | Rationale | Date |
|----------|-----------|------|
| **ADR-004**: Static sparse adjacency | Immutable, fast (sparse matrix @), low memory, aligns with Phase 1 early validation | 2026-02-08 |
| **ADR-005**: CompositeExpressionModel | Composition pattern, inheritance-based extensibility, testable base + regulatory layers | 2026-02-08 |
| **ADR-006**: Optional circuit detection | Opt-in (off by default), static at init (fast), reusable for Phase 3 mutations | 2026-02-08 |
| **ADR-007**: NumPy vectorization | Population-level batch ops + sparse matrix ops, 100× speedup vs. Python loops | 2026-02-08 |

## Errors Encountered

(None yet)

## Status

**READY FOR EXECUTION** - Phase 1 (Design) ✅ and Phase 2 (Planning) ✅ complete

## Execution Summary

**Phase 2 Implementation Plan Ready:**
- Week 13: RegulatoryNetwork (sparse CSR adjacency, 15+ tests)
- Week 14: CompositeExpressionModel (composition pattern, 12 tests)
- Week 15: CircuitDetector (feedback loops & feedforward motifs, 10 tests)
- Week 16: GeneNetwork integration (regulatory input wiring, 10 tests)
- Week 17-20: Vectorization + benchmarking + performance validation
- Week 21-26: Advanced selection models (sexual/asexual, epistatic, multi-objective)

**Target Metrics:**
- 200+ cumulative tests (110 → 200)
- ≥95% coverage on Phase 2 code
- <5s for 10k individuals × 100 genes × 1k generations
- Phase 1 examples run unchanged

## Next Action

Run `/build execute batch` or `/build execute subagent` to start Week 13 implementation:

```bash
/build execute batch    # Automated: 3 tasks per batch, then report
/build execute subagent # Interactive: 1 task at a time with user confirmation
```
