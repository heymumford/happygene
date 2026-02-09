# Roadmap: happygene

Strategic plan for happygene development across 12 months.

**Current Version**: v0.1.0 (Phase 1 MVP - COMPLETE)
**Timeline**: Weeks 1-52 (Feb 2026 - Feb 2027)
**Maintainer**: Eric Mumford (@heymumford)

---

## Phase 1: MVP (COMPLETE ✅)

**Weeks 1-12 | Shipped v0.1.0**

**Goal**: Establish core simulation framework with basic models and comprehensive testing.

### Deliverables (All Complete)
- ✅ `SimulationModel` base class and `GeneNetwork` implementation
- ✅ Three expression models: `ConstantExpression`, `LinearExpression`, `HillExpression`
- ✅ Two selection models: `ProportionalSelection`, `ThresholdSelection`
- ✅ `PointMutation` model with variable rates and magnitudes
- ✅ `DataCollector` with multi-level data collection (model, individual, gene)
- ✅ Two example scripts: `simple_duplication.py`, `regulatory_network.py`
- ✅ 110+ tests with 97%+ coverage
- ✅ Sphinx documentation with API reference and tutorials
- ✅ GitHub Actions CI/CD (Python 3.12 + 3.13 matrix)
- ✅ Governance document and contribution guidelines

### Outcome
- Framework ready for basic simulations
- Community can understand and extend architecture
- Foundation for Phase 2 features

---

## Phase 2: Gene Regulatory Networks (Weeks 13-26)

**Goal**: Add multi-gene regulatory interactions and advanced modeling.

### Q2 Deliverables (Estimated)

**Weeks 13-16: Gene Regulation Subsystem**
- Gene-to-gene regulatory interactions (activation, repression)
- Regulatory network representation (adjacency matrix)
- Composite expression models (combines TF input from multiple genes)
- Regulatory circuit detection (feedback loops, feedforward)
- Example: *Repressilator circuit* (3-gene oscillator)

**Weeks 17-20: Benchmarking & Performance**
- Performance benchmarks: 10k individuals, 100 genes, 1k generations
- Memory usage profiling and optimization
- Cache-friendly data structures for expression computation
- Parallelization exploration (NumPy broadcasting, optional Numba)
- Benchmark results documented in `docs/benchmarks/`

**Weeks 21-26: Advanced Selection Models**
- Sexual/asexual reproduction options
- Epistatic fitness (gene-gene interactions)
- Multi-objective selection (Pareto fitness)
- Fitness landscape visualization
- Example: *Divergent selection* with multiple fitness objectives

### Target Metrics
- v0.2.0 release
- 150+ tests (3x current)
- <500ms for 1k generation / 100 individuals / 50 genes
- 3+ external contributor PRs merged

---

## Phase 3: Integration & Visualization (Weeks 27-39)

**Goal**: Connect to ecosystem tools and provide rich visualization.

### Q3 Deliverables (Estimated)

**Weeks 27-30: Mesa Integration (Optional)**
- Adapt GeneNetwork to Mesa `Agent` + `Model` base classes
- Grid-based spatial simulations (optional)
- Visualization with Mesa's browser interface
- Rationale: Larger community (110+ contributors vs. our 0)

**Weeks 31-34: Solara Web Dashboard (Optional)**
- Interactive simulation parameter tuning
- Real-time fitness/expression plots
- Export simulation snapshots
- Tech: Python Solara + Plotly

**Weeks 35-39: Format Support**
- SBML export (Systems Biology Markup Language)
- YAML configuration files
- JSON for simulation snapshots + metadata
- Example: *Import BioModels SBML, simulate, export results*

### Target Metrics
- v0.3.0 release
- 200+ tests
- 5+ example notebooks
- 1k+ GitHub stars (reach goal)

---

## Phase 4: Publication & Maturity (Weeks 40-52)

**Goal**: Publish academic paper and stabilize API.

### Q4 Deliverables (Estimated)

**Weeks 40-44: Academic Paper**
- *"happygene: A Python Framework for Gene Network Evolution"*
- Methodology, examples, validation against theory
- Performance benchmarks vs. COPASI
- Submission target: JOSS (Journal of Open Source Software)

**Weeks 45-48: Stability & Polish**
- Semantic versioning finalized
- Deprecation policy documented
- Breaking change process established
- Full type hints (mypy strict mode)
- Comprehensive error messages

**Weeks 49-52: Community & Release**
- v1.0.0 stable API release
- Community examples (3+ from external contributors)
- Governance transition plan (if needed)
- 12-month retrospective
- Roadmap for Year 2

### Target Metrics
- v1.0.0 stable release
- 50+ downloads/month
- 2-3 citations
- 10+ external contributors

---

## Feature Requests (Backlog)

These are high-priority features not yet scheduled:

### High Priority
- **Asexual vs. sexual reproduction**: Toggle population breeding strategy
- **Environmental time-series**: Conditions change over generations
- **Synthetic lethals**: Gene-gene interactions in fitness
- **Recombination**: Genetic crossover between individuals

### Medium Priority
- **GPU acceleration**: CUDA/OpenCL for large populations
- **Stochastic expression**: Noise in gene expression
- **Epigenetics**: Heritable non-genetic variation
- **Population structure**: Subpopulations with migration

### Low Priority
- **3D visualizations**: Fitness landscape plots
- **Realtime streaming**: Live simulation data to web dashboard
- **Machine learning**: Surrogate models for fitness prediction
- **Cloud integration**: AWS Batch for large parameter sweeps

---

## Community Milestones

### 100 GitHub Stars
- Announce in /r/biology and /r/compsci
- Feature on PapersWithCode
- Target: Month 6

### 5 External Contributors
- Establish contributor tiers
- First CONTRIBUTING.md iteration
- Community acknowledgments
- Target: Month 9

### Academic Publication
- JOSS paper accepted
- Cite in README
- Add to bio.tools registry
- Target: Month 10

### 1.0.0 Release
- Semantic versioning stable
- API stability guarantee
- Governance finalized
- Target: Month 12

---

## Dependencies & Constraints

### Core Dependencies (No Change)
- **numpy** >= 1.26 (array operations)
- **pandas** >= 2.0 (data analysis)
- **Python** >= 3.12 (modern syntax)

### Optional Dependencies (Phase 2-4)
- **pytest** (testing - included in [dev])
- **sphinx** (docs - included in [docs])
- **solara** (web UI - Phase 3, optional)
- **mesa** (ABM framework - Phase 3, optional)
- **libsbml** (SBML support - Phase 3, optional)

### Non-Dependencies (Deliberate)
- **No C++ extensions**: Pure Python for accessibility
- **No machine learning**: Keep lightweight
- **No ODE solver**: Discrete generations only
- **No GUI application**: Web/CLI focus

---

## Success Criteria

### Phase 1 (ACHIEVED ✅)
- [x] 100+ tests passing
- [x] >90% coverage
- [x] 2+ examples working
- [x] Documentation builds cleanly
- [x] GitHub Actions CI passes
- [x] v0.1.0 released

### Phase 2 (Target: Week 26)
- [ ] Gene regulatory interactions implemented
- [ ] 150+ tests passing
- [ ] Performance benchmarks <500ms for standard scenario
- [ ] v0.2.0 released
- [ ] 3+ external contributors merged

### Phase 3 (Target: Week 39)
- [ ] Mesa or Solara integration working
- [ ] SBML export/import functional
- [ ] 200+ tests
- [ ] 5+ example notebooks
- [ ] v0.3.0 released

### Phase 4 (Target: Week 52)
- [ ] JOSS paper accepted
- [ ] v1.0.0 released with stable API
- [ ] 50+ downloads/month baseline
- [ ] 10+ external contributors
- [ ] Governance transitioned (if ready)

---

## How to Contribute

**Want to help with the roadmap?**

1. **Review the current phase** (Phase 1 complete, Phase 2 starting)
2. **Check CONTRIBUTING.md** for code standards
3. **Pick an issue** or propose a feature in Discussions
4. **Open a PR** with tests and documentation

**Contribution opportunities:**
- Write additional examples (any modeling scenario)
- Improve documentation (tutorials, API docs)
- Add tests for edge cases
- Optimize performance hot spots
- Create visualizations

**For larger features** (Phase 2+), please:
- Open an issue for discussion first
- Propose RFC with design
- Get BDFL/Core Contributor feedback before coding

---

## Questions?

- **Issues**: https://github.com/heymumford/happygene/issues
- **Discussions**: https://github.com/heymumford/happygene/discussions
- **Email**: eric@heymumford.com

---

**Last Updated**: 2026-02-08
**Next Review**: 2026-03-08
