# Contributing to Happy Gene

Thanks for your interest in contributing! This project follows strict public-domain OSS practices.

## Code Standards

### Commits

All commits must use **Conventional Commits** format with evidence requirements:

```
type(scope): description

Body: [Evidence of correctness]
```

**Valid types:**
- `feat`: New feature
- `fix`: Bug fix
- `test`: Test additions/modifications
- `docs`: Documentation
- `refactor`: Code restructuring (no behavior change)
- `perf`: Performance improvements
- `ci`: CI/CD pipeline changes

**Example:**
```
feat(io): Add SBML export with COPASI round-trip validation

All 14 tests passing (97/97 suite). Coverage 77% (target 75%).
- export_to_sbml() generates Level 3 v2 XML with all damage types
- Import preserves dose_gy and population_size (round-trip fidelity)
- Robust namespace handling for element finding
```

### Code Style

- **Python 3.12+** syntax
- **Type hints everywhere** — mypy strict mode
- **NumPy docstrings** for all functions/classes
- **100 character line length**
- **Black formatting** + isort imports

**Type hints example:**
```python
def export_to_sbml(
    config: HappyGeneConfig,
    damage_profile: DamageProfile,
    output_path: Union[str, Path]
) -> Path:
    """Export simulation configuration to SBML.

    Args:
        config: HappyGeneConfig with kinetics and output settings
        damage_profile: DamageProfile with lesions and metadata
        output_path: Path to write SBML XML file

    Returns:
        Path to created SBML file

    Raises:
        ValueError: If config/profile invalid
        IOError: If file write fails
    """
```

## Testing

**Coverage requirement: 75%+**

Test file structure:
```
tests/unit/                    # Pure function tests (no I/O)
tests/integration/             # Multi-component tests
engine/tests/                  # Domain-specific tests
```

### Test Execution

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=engine --cov-report=html

# Run specific test file
pytest tests/unit/test_sbml_export.py

# Run by marker
pytest -m unit
pytest -m integration
```

### Test Markers

- `@pytest.mark.unit` — Pure functions, no I/O
- `@pytest.mark.integration` — Multi-component, may use files
- `@pytest.mark.validation` — Cross-system validation (SBML round-trip)
- `@pytest.mark.chaos` — Fault injection tests

### Test Requirements

Every test must verify behavior, not just code paths:

✅ **Good**:
```python
def test_export_preserves_dose_gy():
    """SBML export round-trip preserves dose_gy metadata."""
    original_dose = 3.5
    profile = DamageProfile(..., dose_gy=original_dose, ...)

    export_to_sbml(config, profile, path)
    restored_profile, _ = import_from_sbml(path)

    assert restored_profile.dose_gy == original_dose
```

❌ **Bad**:
```python
def test_export_calls_write():
    """Test that export_to_sbml calls write."""
    with patch('builtins.open'):
        export_to_sbml(config, profile, path)  # Proves nothing
```

## Branch Workflow

1. **Create feature branch** from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/DESCRIPTION
   ```

2. **Make changes** with frequent commits:
   ```bash
   git add engine/io/sbml_export.py
   git commit -m "feat(io): Add SBML export function

   Generates Level 3 v2 XML compatible with COPASI.
   Test: test_sbml_export_creates_valid_file passing."
   ```

3. **Push and create PR**:
   ```bash
   git push origin feature/DESCRIPTION
   # Create PR in GitHub UI
   ```

4. **Address review feedback** with new commits (don't rebase):
   ```bash
   git commit -m "test(io): Add unicode preservation test for species IDs"
   ```

5. **Merge** only after approval and CI passes

## Pull Request Checklist

Before creating a PR, verify:

- [ ] All tests pass (`pytest`)
- [ ] Coverage ≥ 75% (`pytest --cov=engine --cov-report=term-missing`)
- [ ] Type hints complete (`mypy engine`)
- [ ] Code formatted (`black . && isort .`)
- [ ] Commit messages follow Conventional Commits
- [ ] Documentation updated (docstrings, README, CHANGELOG)
- [ ] No debug prints or commented code

## Documentation

### Docstrings

Use NumPy style for all functions, classes, and modules:

```python
def validate_sbml(sbml_path: Union[str, Path]) -> bool:
    """Validate SBML document structure and content.

    Checks well-formedness (valid XML), schema compliance (SBML Level 3
    Version 2), required elements, and numerical consistency.

    Parameters
    ----------
    sbml_path : Union[str, Path]
        Path to SBML XML file

    Returns
    -------
    bool
        True if valid, False otherwise

    Raises
    ------
    FileNotFoundError
        If file doesn't exist
    ValueError
        If validation fails with details

    Examples
    --------
    >>> validate_sbml("model.xml")
    True
    """
```

### Changelog

Update [CHANGELOG.md](CHANGELOG.md) under "Unreleased" section:

```markdown
## Unreleased

### Added
- SBML export/import for COPASI round-trip validation (99% fidelity)
- 14 new SBML module tests (all passing)

### Fixed
- Namespace handling in XML element discovery

### Changed
- Added libsbml and lxml to optional dependencies
```

## Questions?

- Open a [GitHub Discussion](https://github.com/heymumford/happygene/discussions)
- Check [existing issues](https://github.com/heymumford/happygene/issues)
- Email: eric@heymumford.com

## License

By contributing, you agree that your contributions are licensed under GPL-3.0-or-later.
