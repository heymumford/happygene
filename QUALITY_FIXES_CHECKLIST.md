# Code Quality Fixes Checklist

Quick reference for implementation order. Check off as you go.

## Critical Fixes (10 minutes)

- [ ] **response.py:40** - Add sklearn imports at module top
  ```python
  from sklearn.preprocessing import StandardScaler
  from sklearn.linear_model import LinearRegression
  from sklearn.ensemble import RandomForestRegressor
  from sklearn.metrics import mean_absolute_error, mean_squared_error
  ```

- [ ] **model.py:114** - Replace string type check with isinstance()
  ```python
  # OLD: if type(self.selection_model).__name__ == 'ProportionalSelection'
  # NEW: if isinstance(self.selection_model, ProportionalSelection)
  ```
  Note: May need to import ProportionalSelection from selection.py

- [ ] **Auto-fix imports** (Ruff I001, F401)
  ```bash
  uv run python -m ruff check happygene/ --fix
  ```
  Fixes 31/36 violations automatically

- [ ] **sobol.py:138** - Remove unused variable
  ```python
  # DELETE: X = batch_results[param_cols].values
  # KEEP:  Y = batch_results[output_col].values
  ```

## High-Impact Refactoring (40 minutes)

- [ ] **regulatory_network.py** - Extract _build_digraph() helper
  - Lines 184-199 duplicate lines 201-230
  - Create new method to reduce duplication
  - Estimated: 10 min

- [ ] **response.py** - Extract _build_feature_matrix() helper
  - Lines 76-84, 121-128, 163-170 are duplicated
  - Create new method to consolidate logic
  - Estimated: 15 min

- [ ] **_internal.py + sobol.py + morris.py** - Move bounds extraction
  - Extract _get_bounds_from_results to shared utility
  - Remove duplicate implementations
  - Estimated: 15 min

## Quality Improvements (40 minutes)

- [ ] **model.py:88** - Replace hasattr() with Protocol/isinstance()
  - Remove duck typing, add type safety
  - Use RegulatoryExpressionModel protocol
  - Estimated: 20 min

- [ ] **batch.py:242** - Remove test pollution (mock detection)
  - Replace hasattr(model, '_is_mock') with dependency injection
  - Estimated: 20 min

## Cosmetic Fixes (5 minutes)

- [ ] **batch.py:212,259** - Fix line length violations (E501)
  ```python
  # Line 212: Split output_cols assignment
  # Line 259: Split survival calculation
  ```

## Verification

After each fix:
```bash
# Run unit tests
uv run pytest tests/ -xvs

# Run linter
uv run python -m ruff check happygene/

# Check specific files
uv run python -m ruff check happygene/model.py
uv run python -m ruff check happygene/analysis/response.py
```

## Progress Tracking

| Phase | Target | Completed | Status |
|-------|--------|-----------|--------|
| Critical | 10 min | | [ ] |
| High-Impact | 40 min | | [ ] |
| Quality | 40 min | | [ ] |
| Cosmetic | 5 min | | [ ] |
| **TOTAL** | **95 min** | | [ ] |

---

## Notes

- All auto-fixes are "safe" according to Ruff (no behavior change)
- Refactoring recommendations are tested against current code structure
- Import fixes handle both relative and absolute imports correctly
- No breaking changes to public APIs planned
