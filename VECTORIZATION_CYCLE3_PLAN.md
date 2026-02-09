# Vectorization Extensions - Selection & Update Phases (Cycle 3)

## Goal
Extend NumPy vectorization beyond expression phase to selection and update phases via batch fitness computation methods.

## Current State
- Expression phase: Fully vectorized with `expr_matrix` (n_individuals × n_genes)
- Selection phase: Partially vectorized only for ProportionalSelection (type check in model.py:114)
- Update phase: Nested loops assigning expression values from matrix to Individual objects

## Implementation Plan

### Phase 1: Add Batch Methods to SelectionModel Subclasses (TDD)
1. [  ] **ProportionalSelection.compute_fitness_batch**
   - Test: Verify batch output matches per-individual compute_fitness
   - Implementation: `np.mean(expr_matrix, axis=1)`

2. [  ] **ThresholdSelection.compute_fitness_batch**
   - Test: Verify batch output matches per-individual compute_fitness
   - Implementation: `(np.mean(expr_matrix, axis=1) >= self.threshold).astype(float)`

3. [  ] **EpistaticFitness.compute_fitness_batch**
   - Test: Verify batch output matches per-individual compute_fitness
   - Implementation: Vectorized epistatic computation

4. [  ] **MultiObjectiveSelection.compute_fitness_batch**
   - Test: Verify batch output matches per-individual compute_fitness
   - Implementation: `expr_matrix @ self.objective_weights / sum(weights)`

### Phase 2: Refactor model.py to Use Batch Methods
1. [  ] Replace type-check branching (model.py:114-124)
2. [  ] Call `selection_model.compute_fitness_batch(expr_matrix)` for all types
3. [  ] Single loop assigns fitness values to individuals

### Phase 3: Testing & Verification
1. [  ] All tests pass (current 211+)
2. [  ] No regressions in behavior
3. [  ] Batch methods produce numerically identical results
4. [  ] Benchmark before/after on 5k×100×100

### Phase 4: Commit & Report
- Commit with performance metrics
- Document phase breakdown improvement

## Success Criteria
- All new compute_fitness_batch methods produce identical results
- Selection phase time reduced by >=5%
- Overall step time reduced by >=2%
- All 211+ tests pass
- Zero regressions

## Files to Modify
- `/Users/vorthruna/ProjectsWATTS/happygene/happygene/selection.py` - Add batch methods
- `/Users/vorthruna/ProjectsWATTS/happygene/happygene/model.py` - Use batch methods in step()
- `/Users/vorthruna/ProjectsWATTS/happygene/tests/test_selection.py` - Add batch comparison tests

## Status
**IN PROGRESS** - Starting Phase 1: TDD for batch methods
