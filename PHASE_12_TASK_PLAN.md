# Task Plan: Phase 12 - Sensitivity Analysis Module

## Goal
Enable researchers to perform global sensitivity analysis (Sobol indices, Morris screening) and parameter interaction analysis using HappyGene simulations. Produce publication-ready outputs with reproducible seeds.

## Branch
`feature/phase-12-sensitivity` in worktree `../.worktrees/phase-12-sensitivity`

## Phases

### Phase 1: RED - Test-First Specification
- [ ] Create test structure: tests/analysis/ with conftest.py
- [ ] Write contract tests for BatchSimulator (sample generation, batch execution)
- [ ] Write contract tests for SobolAnalyzer (index computation, bounds validation)
- [ ] Write contract tests for MorrisAnalyzer (screening indices)
- [ ] Write property-based tests (deterministic seeds, reproducibility)
- [ ] Write chaos tests (invalid inputs, edge cases)
- [ ] Write performance benchmarks (scaling with n_samples)
- [ ] Status: 40+ failing tests defined, architecture clear

### Phase 2: GREEN - Implementation
- [ ] Implement happygene/analysis/_internal.py (SeedManager, validators, utilities)
- [ ] Implement happygene/analysis/batch.py (BatchSimulator core)
- [ ] Implement happygene/analysis/sobol.py (SobolAnalyzer wrapper)
- [ ] Implement happygene/analysis/morris.py (MorrisAnalyzer)
- [ ] Implement happygene/analysis/correlation.py (CorrelationAnalyzer)
- [ ] Implement happygene/analysis/response.py (ResponseSurfaceModel)
- [ ] Implement happygene/analysis/output.py (OutputExporter - plots, CSV, JSON)
- [ ] All tests passing (153 existing + 40+ new = 190+ total)
- [ ] Status: All RED tests passing, full implementation complete

### Phase 3: BLUE - Polish & Documentation
- [ ] Refactor for clarity (docstrings, type hints, logging)
- [ ] Create researcher-focused quick-start guide (docs/analysis_quick_start.md)
- [ ] Create API reference (docs/analysis_api_reference.md)
- [ ] Add Jupyter notebook example: 06_global_sensitivity.ipynb
- [ ] Update mkdocs.yml to include analysis documentation
- [ ] Performance optimization pass
- [ ] Coverage verification (maintain 80%+ coverage)
- [ ] Status: Production-ready analysis module with examples

### Phase 4: Verification
- [ ] All tests pass (190+ tests)
- [ ] Code coverage ≥ 80%
- [ ] Example notebook executes without errors
- [ ] Publication-ready plots generate successfully
- [ ] Documentation links work and are searchable
- [ ] Release: v0.3.0 with sensitivity analysis features

## Key Deliverables

### Module Files
- `happygene/analysis/__init__.py` - Public API exports
- `happygene/analysis/_internal.py` - Shared utilities
- `happygene/analysis/batch.py` - BatchSimulator (core)
- `happygene/analysis/sobol.py` - Global sensitivity via Sobol indices
- `happygene/analysis/morris.py` - Fast screening via Morris
- `happygene/analysis/correlation.py` - Parameter interactions
- `happygene/analysis/response.py` - Surrogate models
- `happygene/analysis/output.py` - Publication-ready exports

### Test Files
- `tests/analysis/__init__.py`
- `tests/analysis/conftest.py` - Fixtures (sim_factory, param_space, samples)
- `tests/analysis/test_batch.py` - Contract + property + chaos + perf tests
- `tests/analysis/test_sobol.py` - Sobol-specific tests
- `tests/analysis/test_morris.py` - Morris screening tests
- `tests/analysis/test_correlation.py` - Interaction tests
- `tests/analysis/test_response.py` - Surrogate model tests
- `tests/analysis/test_output.py` - Export format tests

### Documentation
- `docs/analysis_quick_start.md` - 10-minute researcher guide
- `docs/analysis_api_reference.md` - Full API documentation
- `docs/examples/06_global_sensitivity.ipynb` - Jupyter notebook example
- Updated `mkdocs.yml` with analysis section

## Test Plan Summary

**Contract Tests (SALib Integration)**
- BatchSimulator creation and sample generation
- Sobol indices shape, bounds, total-effects ≥ main-effects property
- Morris indices validity
- Output DataFrame structure and row counts

**Property-Based Tests (Reproducibility)**
- Same seed → identical samples (Sobol, Morris)
- Same seed → identical batch outputs
- Seed parameter coverage (0 to 2^31-1)

**Chaos Tests (Error Resilience)**
- Empty param_space rejection
- Invalid bounds (low ≥ high) rejection
- Zero generations handling
- Constant output (variance=0) handling
- NaN values rejection
- Single parameter sweep (dimension=1)
- High-dimensional space (15+ params)
- Multiple outputs handling

**Performance Benchmarks**
- Linear scaling with n_samples (10 → 100 → 1000)
- Sobol computation <1s for 512 samples
- Morris fast: ~5x fewer samples than Sobol

## Success Criteria
- [ ] 40+ new tests all passing
- [ ] 190+ total tests (existing 153 + new 40+)
- [ ] Code coverage ≥ 80%
- [ ] BatchSimulator API clean and intuitive
- [ ] Sobol/Morris indices validated against SALib reference
- [ ] Publication-ready plots (tornado, scatter, heatmap, network)
- [ ] Reproducible outputs (seed tracking, metadata)
- [ ] Example notebook runs without errors
- [ ] Documentation searchable and complete

## Decisions Made
(To be filled)

## Errors Encountered
(To be filled)

## Status
**Starting Phase 1 (RED)** - Test-first specification
