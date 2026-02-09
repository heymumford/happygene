# Happygene Architecture: Quick Start Guide

## TL;DR

**Recommendation:** Build happygene like Mesa (Python, inheritance-based) with optional BioNetGen-style configuration.

```
happygene/
├── Core: GeneNetwork(Model), Gene, Individual
├── Extensibility: Python inheritance (ExpressionModel, SelectionModel, MutationModel)
├── Data: Mesa-style DataCollector → pandas DataFrame
├── Tests: pytest + ensemble validation + theory checks
├── Docs: Sphinx + 50+ examples + tutorials
└── Community: Low barrier (pip install), CONTRIBUTING.md, Discussions tab
```

---

## One-Page Architecture

```
┌─────────────────────────────────────────┐
│   User Code (Inheritance-Based)         │
│                                         │
│  class MyExpression(ExpressionModel)   │
│    def calculate(...): ...             │
│                                         │
│  class MySelection(SelectionModel)     │
│    def calculate_fitness(...): ...     │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│   happygene Core (Python)               │
│                                         │
│   GeneNetwork(Model)                   │
│   ├─ Gene (entity)                     │
│   ├─ Individual (population)           │
│   ├─ ExpressionModel (base class)      │
│   ├─ SelectionModel (base class)       │
│   ├─ MutationModel (base class)        │
│   └─ DataCollector (Mesa pattern)      │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│   Runtime Engine                        │
│                                         │
│   for t in range(generations):         │
│     model.step()                       │
│     collector.collect(model)           │
└────────────┬────────────────────────────┘
             │
             ↓
┌──────────────────┬──────────────────┬──────────┐
│   CSV Export     │  pandas.DataFrame│  Jupyter │
│   (reproducible) │  (analysis)      │ (plotting)
└──────────────────┴──────────────────┴──────────┘
```

---

## Phase 1 Deliverables (3 Months)

| Component | Effort | Deliverable |
|-----------|--------|------------|
| **Core Model** | 2 weeks | GeneNetwork, Gene, Individual (Mesa-compatible) |
| **Expression Models** | 1 week | Linear, Hill cooperative, Constant |
| **Selection Models** | 1 week | Proportional fitness, Threshold |
| **DataCollector** | 1 week | Mesa pattern (model + individual reporters) |
| **Tests** | 2 weeks | 35+ tests (unit + integration + theory) |
| **Documentation** | 2 weeks | Getting Started, API docs, 2 examples |
| **CI/CD** | 1 week | GitHub Actions, pytest, coverage |
| **Total** | **10 weeks** | **MVP ready for pilot use** |

---

## Why This Works (Lessons from Mesa)

| Factor | Mesa | Happygene |
|--------|------|----------|
| **Language** | Python | Python ✓ |
| **Setup** | `pip install mesa` (5 min) | `pip install happygene` (5 min) ✓ |
| **First Code** | Inherit Agent, Model | Inherit ExpressionModel, SelectionModel ✓ |
| **Data** | DataCollector → pandas | DataCollector → pandas ✓ |
| **Tests** | pytest + benchmarks | pytest + theory validation ✓ |
| **Examples** | 50+ on GitHub | 50+ on GitHub (goal) ✓ |
| **Community** | 110+ contributors | 5+ by year 1 (goal) |

---

## Success Metrics

### By Month 3 (MVP)
- ✓ pip install works
- ✓ 35+ tests passing
- ✓ Documentation complete
- ✓ 2 example models

### By Month 6 (v0.2)
- ✓ 60+ tests, < 5% regression
- ✓ First 3 external PRs merged
- ✓ 5 example models
- ✓ Benchmarks operational

### By Month 12 (v1.0)
- ✓ 100+ tests, 80%+ coverage
- ✓ PyPI package live
- ✓ 10+ example models
- ✓ 5+ community contributors
- ✓ JOSS paper submitted

---

## Critical Decisions (Already Made)

| Decision | Choice | Why |
|----------|--------|-----|
| **Language** | Python (not C++) | Low barrier = large community |
| **Extensibility** | Inheritance (not DSL) | Pythonic, flexible, no parser |
| **Data** | In-memory (not file-centric) | Fast + integrated analysis |
| **Testing** | pytest (not unittest) | Mesa standard, better fixtures |
| **Docs** | Sphinx (not custom) | Auto-generated API, industry standard |

---

## What NOT to Do

| Anti-Pattern | Why | Example |
|--------------|-----|---------|
| **C++ core** | Kills community contributions | COPASI model (small community) |
| **Required DSL** | Too many things to learn | BioNetGen model (steep curve) |
| **File-heavy I/O** | Slow iteration | COPASI model (I/O overhead) |
| **Weak testing** | Breaks credibility | No benchmarks = no trust |
| **No docs** | No adoption | Many tools fail here |

---

## First Week Checklist

- [ ] Create GitHub repository (with MIT license)
- [ ] Initialize basic project structure
- [ ] Create GeneNetwork class (inherit from nothing, don't depend on Mesa yet)
- [ ] Write first test (assert GeneNetwork.step() works)
- [ ] Create CONTRIBUTING.md (copy Mesa, adapt for genes)
- [ ] Push to GitHub, enable Actions
- [ ] Write README.md (5-minute getting started)

---

## Resources to Copy From

**Mesa (Primary Reference)**
- GitHub: https://github.com/mesa/mesa
- Pattern: Inheritance-based extensibility
- Documentation: https://mesa.readthedocs.io/
- CONTRIBUTING: https://github.com/mesa/mesa/blob/main/CONTRIBUTING.md

**COPASI (Testing Inspiration)**
- Testing: SBML compliance + stochastic validation
- Benchmarks: Performance tracking

**BioNetGen (DSL Inspiration, Optional)**
- Parser: ANTLR-based grammar
- Documentation: Reference manual approach

---

## Estimated Timeline

```
Week 1-2:    Core data structures (GeneNetwork, Gene, Individual)
Week 3:      Expression models
Week 4:      Selection models
Week 5-6:    DataCollector + testing infrastructure
Week 7-8:    Documentation + examples
Week 9-10:   CI/CD setup + launch
Month 2:     Feedback iteration + new models
Month 3:     Refinement + community building
```

---

## Community Engagement Strategy

### Day 1 (Launch)
- GitHub Discussions enabled
- README + Getting Started guide
- First issue templates

### Month 1
- Respond to ALL questions < 48 hours
- Merge first community PR
- Blog post: "Why we built happygene"

### Month 3
- 3+ external contributors
- CONTRIBUTING.md success stories
- Tutorial notebook published

### Month 6
- JOSS paper submitted
- Conference talk accepted
- 5+ community contributors

---

## One Recommendation Away

**If forced to choose ONE architectural decision:**

✓ **Python inheritance-based extensibility** (Mesa pattern)

This single decision:
- Lowers barrier from C++ to Python (10x more potential contributors)
- Makes testing trivial (introspection)
- Integrates with ML ecosystem (numpy, scikit-learn, PyTorch)
- Enables real-time Jupyter workflows
- Generates 80% of Mesa's community success

Everything else follows from this.

---

## Questions to Ask Domain Experts

Before coding Phase 1, validate assumptions with:

1. **Evolutionary biologists:** "Is gene duplication your primary simulation focus?"
2. **Systems biologists:** "Would you use gene regulatory network capabilities?"
3. **Educators:** "Would you teach happygene in classes if similar to Mesa?"
4. **ML researchers:** "Would you integrate with scikit-learn pipelines?"

---

**Status:** Ready for implementation  
**Next:** Review with domain experts, then start Phase 1  
**Reference:** See RESEARCH_SUMMARY.md for detailed roadmap
