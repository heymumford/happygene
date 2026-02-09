# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

(No pending changes)

## [0.2.0] — 2026-02-08

### Added
- **Comprehensive Documentation Site** — MkDocs with Material theme
  - `mkdocs.yml`: Full documentation configuration
  - `docs/index.md`: Overview and navigation hub
  - `docs/getting-started.md`: 5-minute quick start guide
  - `docs/user-guide.md`: Comprehensive usage and configuration guide
  - `docs/api-reference.md`: Full API documentation with examples
  - `docs/examples/`: Navigation hub for Jupyter notebooks

- **5 Publication-Ready Jupyter Notebooks** — Complete workflow examples
  - `01_hello_world.ipynb`: Basic single simulation (5 min, beginner)
  - `02_batch_processing.ipynb`: Batch simulations & statistics (15 min, beginner-intermediate)
  - `03_visualization.ipynb`: Interactive dashboards & exports (15 min, intermediate)
  - `04_copasi_workflow.ipynb`: SBML round-trip with COPASI (20 min, advanced)
  - `05_parameter_sensitivity.ipynb`: Parameter sweeps & analysis (20 min, advanced)

- **Automated GitHub Pages Deployment** — GitHub Actions workflow
  - `.github/workflows/pages.yml`: Automatic build and deploy to gh-pages
  - Documentation automatically published to https://heymumford.github.io/happygene

- **Visualization Module** — Interactive plots and dashboards
  - `engine/visualization/plotter.py`: Time series, distributions, statistics plots
  - `engine/visualization/dashboard.py`: Multi-plot interactive layouts
  - `engine/visualization/exporter.py`: Export to HTML, PNG, PDF formats
  - 25+ visualization tests with 100% coverage

### Changed
- Updated README.md with documentation links and current metrics (153 tests, 80.54% coverage)
- Version bumped from 0.1.0-dev to 0.2.0

### Verified
- 153 tests passing (25 new visualization + 128 existing)
- Coverage: 80.54% (target: 75%, exceeded)
- All documentation links validated
- GitHub Pages deployment ready

## [0.1.0] — 2026-02-08

### Added
- **SBML Export/Import Module** — Full COPASI round-trip validation
  - `engine/io/sbml_export.py`: Export HappyGeneConfig and DamageProfile to SBML Level 3 v2
  - `engine/io/sbml_import.py`: Import SBML XML back to domain models
  - `engine/io/sbml_validator.py`: Schema validation and numerical consistency checks
  - 14 new test cases (all passing, 100% coverage on new modules)
  - Metadata preservation: dose_gy, population_size, kinetics parameters survive round-trip
  - Robust namespace handling for XML element discovery

- **Public-Domain OSS Practices**
  - `.gitignore`: Python/IDE/test artifact exclusions
  - `CONTRIBUTING.md`: Contributor workflow, code standards, testing requirements
  - `CHANGELOG.md`: Keep a Changelog format with semantic versioning
  - Expanded `README.md`: Badges, quick start, architecture, citation format
  - GitHub Actions CI/CD pipeline: Automated pytest + type checking

- **GPL-3.0 License Compliance**
  - Updated LICENSE year to 2026
  - Added GPL-3.0 copyright headers to all 17 Python source files
  - Author attribution: Eric C. Mumford

- **Release Infrastructure**
  - `.release-please-manifest.json`: Version tracking
  - `release-please-config.json`: Semantic versioning configuration
  - `.github/workflows/release-please.yml`: Automated release PR creation
  - `.github/workflows/publish.yml`: PyPI publish on git tags

### Changed
- `pyproject.toml`: Added optional dependencies for SBML I/O (`python-libsbml>=5.20`, `lxml>=4.9`)
- Enhanced `README.md` with badges, quick start guide, architecture diagram

### Fixed
- XML namespace handling in SBML import: Namespace-agnostic element finding (uses tag suffix matching)
- Round-trip fidelity: dose_gy and population_size now preserved through export/import cycle

### Verified
- 97 tests passing (14 new SBML + 83 core engine tests)
- Coverage: 77.06% (target: 75%, exceeded)
- Type hints: mypy strict mode compliant on new modules
- SBML round-trip validation: < 0.1% RMSE on all damage profiles

## [0.1.0-dev] — 2024-02-08

### Added
- Initial project structure with domain models
- DNA damage representation: 7 damage types (DSB, SSB, Crosslink, Oxidative, Depurination, Deamination, Thymine Dimer)
- Repair pathway modeling: 8 pathways (NHEJ, HR, BER, NER, MMR, TLS, Direct, Alt-EJ)
- Cell cycle phase integration (G1, S, G2/M)
- Kinetics configuration: Solver method selection (BDF, RK45, RK23)
- ODE integration via scipy.integrate.solve_ivp
- CLI framework with Click
- 83 unit + integration tests with 75%+ coverage requirement

### Testing Infrastructure
- pytest with coverage reporting
- Type checking via mypy (strict mode)
- Code formatting: black + isort
- Conventional Commits for version tracking

---

## Version Guidelines

### Semantic Versioning (MAJOR.MINOR.PATCH)

- **MAJOR**: Breaking changes to API or behavior
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes and documentation

### Release Process

1. Update `CHANGELOG.md` under new version heading
2. Update version in `pyproject.toml`
3. Tag commit: `git tag v0.1.0`
4. Push: `git push origin main --tags`
5. Create GitHub Release with CHANGELOG excerpt

### Breaking Changes

Major version bumps required for:
- Domain model structure changes (DamageProfile, Lesion, etc.)
- Repair pathway definitions
- SBML schema incompatibilities
- API signature changes in public modules

### Deprecation Policy

Deprecated features must:
1. Be documented with DeprecationWarning
2. Remain functional for ≥1 minor version
3. Have replacement documented
4. Be removed in next MAJOR version

---

## Contributors

- Eric C. Mumford (Author, @heymumford)

---

## Future Roadmap

### 0.2.0 (Q1 2024)
- CLI simulator pipeline integration
- Configuration file loading (.yaml/.json)
- Batch simulation support
- Multi-scale temporal integration

### 0.3.0 (Q2 2024)
- Sensitivity analysis module (SALib integration)
- Parameter sweep framework
- Output visualization (plotly)
- Performance optimization for large-scale simulations

### 0.4.0 (Q3 2024)
- GPU acceleration support
- Distributed simulation framework
- Advanced statistical analysis
- Publication-grade output formatting
