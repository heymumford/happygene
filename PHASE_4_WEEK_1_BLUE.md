# Phase 4 BLUE: Refactoring (Clarity + Type Safety)

**Goal**: Production-ready code with zero technical debt, strict typing, and clear intent.

**Quality Gates**:
- mypy --strict (0 errors)
- ruff check (0 violations, line length <100)
- Coverage ≥ 95%
- All docstrings complete and accurate
- No deprecation warnings

---

## Tasks

### 1. Fix Pydantic Deprecation Warnings

**Problem**: Using deprecated class-based `Config` instead of `ConfigDict`

**Fix**: Update all Pydantic models
```python
# Before (deprecated)
class KineticsConfig(BaseModel):
    rtol: float = ...
    class Config:
        frozen = True

# After (v2 style)
from pydantic import ConfigDict
class KineticsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    rtol: float = ...
```

**Files to update**:
- engine/domain/config.py (KineticsConfig, RepairPathwayConfig, SimulationConfig, OutputConfig, HappyGeneConfig)

### 2. Add Type Hints (mypy strict)

**Problem**: Some internal types need explicit annotations

**Fix**: Add `-> None`, `-> float`, `-> dict` return types to all methods

**Files to verify/update**:
- engine/domain/models.py: All @property methods need return types
- engine/domain/config.py: All methods need return types

### 3. Enhance Docstrings

**Missing**: Examples in docstrings for complex classes

**Fix**: Add usage examples and failure modes

### 4. Code Style (ruff)

**Check**: Line length, import ordering, naming conventions

---

## Success Criteria

- [ ] mypy --strict engine/domain/ (0 errors)
- [ ] ruff check engine/domain/ (0 violations)
- [ ] pytest (82 tests passing, 0 failures)
- [ ] Coverage ≥ 95%
- [ ] No deprecation warnings
- [ ] All docstrings complete

