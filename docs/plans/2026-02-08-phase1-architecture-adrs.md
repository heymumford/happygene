# Phase 1 Architecture: Three ADRs

## ADR-001: GeneNetwork Base Class Strategy

**Status:** Accepted

**Context:**
GeneNetwork is the central simulation container. Options are direct Mesa inheritance vs. custom abstract base with adapter.

Mesa's coupling surface is small: `running`, `steps`, `rng`, `agents`, `step()`, `run_model()`. However, gene networks have hierarchical structure (Gene ⊂ Individual ⊂ Population) that doesn't map to Mesa's flat agent model.

**Decision:**
Option B – Custom abstract base class (`SimulationModel`) with Mesa compatibility layer via optional adapter.

**Rationale:**
1. Small coupling surface (~30 lines to replicate)
2. Biology diverges from Mesa's peer-agent model
3. Student extensibility requires clean domain API (`individuals`, `genes`, `generation`)
4. Mesa compatibility achievable without inheritance (adapter pattern)
5. Protects against Mesa version breaks (Mesa 3.x broke 2.x APIs)

**Consequences:**
- (+) Clean domain API, no Mesa version pinning, students learn biology not framework internals
- (-) Must replicate agent registry/RNG, Mesa tutorials not directly copy-pasteable, adapter maintenance
- Risk: Mesa integration deferred to Phase 2 (acceptable: Phase 1 examples use matplotlib directly)

---

## ADR-002: Data Collection Strategy

**Status:** Accepted

**Context:**
Mesa's `DataCollector` supports model-level and agent-level reporting. Gene networks need a third tier: gene-level metrics nested within individuals. Mesa has no native concept of sub-agent reporting.

Phase 1 examples require gene-level expression tracking — this is a hard requirement.

**Decision:**
Option B – Custom `DataCollector` following Mesa's interface conventions but adding gene-level reporting.

**Rationale:**
1. Three-tier data (model → individual → gene) is hard requirement
2. Mesa interface worth preserving (dictionary reporters, `collect()`, `get_*_dataframe()`)
3. Biology-specific convenience methods reduce boilerplate (built-in reporters like `mean_expression`)
4. Generation-indexed DataFrames more meaningful than step-indexed for evolutionary biology

**Consequences:**
- (+) Native three-tier collection, built-in biology reporters, Mesa-compatible interface
- (-) Must maintain custom implementation, users learn gene_reporters tier, ~150-200 lines
- Risk: Gene-level collection performance at scale (Week 7-8); mitigation: column-oriented storage, max_history parameter

---

## ADR-003: Expression Model API Design

**Status:** Accepted

**Context:**
Expression models compute gene expression levels. Options are stateless callables vs. stateful objects with parameter storage.

Phase 1 includes Linear, Hill, and Constant models. Each has parameters defining behavior.

**Decision:**
Option B – Stateful model objects with parameter storage and optional history tracking.

**Rationale:**
1. Parameters must be inspectable (`model.v_max`, `model.n`)
2. Validation belongs at construction time (catch errors before 10k-generation runs)
3. Phase 2 requires history for benchmarks/parameter sweeps
4. Object overhead negligible (200ns per creation, amortized ~0 for 5M calls)
5. Inheritance pattern already presumes classes

**Consequences:**
- (+) Parameters inspectable, early validation, clean `repr()`, serializable, consistent with extensibility pattern
- (-) Marginally more boilerplate, users must instantiate objects
- Risk: `conditions` dict too generic; mitigation: define `Conditions` dataclass with named fields (3-4 fields in Phase 1, extensible via kwargs)

---

## Integration: Unified Design Philosophy

All three decisions implement: **domain-first API with ecosystem compatibility as adapter, not requirement.**

| Principle | Manifestation |
|-----------|---|
| **Biology over framework** | Domain terms (generation, individual, gene) replace generic terms (step, agent, entity) |
| **Mesa-compatible, not Mesa-dependent** | Same patterns (reporters, DataFrames, inheritance), no import coupling |
| **Validate early, fail loud** | Parameter validation in constructors, not runtime |
| **Opt-in complexity** | History tracking off by default; gene collection optional |
| **Student-first API** | 5 imports to run; extensibility via clear subclass contracts |

---

## Flagged Implementation Risks

| Risk | Timing | Impact | Mitigation |
|------|--------|--------|---|
| Gene-level DataCollector performance | Week 7-8 (5M rows at 100 indiv × 50 genes × 1k gen) | Memory exhaustion | Column-oriented storage, max_history param, Week 6 benchmark |
| Mesa adapter not ready for Phase 1 | Week 9-12 | Users expect Mesa integration | Document explicitly in README: "Mesa integration is Phase 2"; Phase 1 examples use matplotlib |
| Expression model `conditions` dict too generic | Week 5 | Researchers expect specific parameters | Define `Conditions` dataclass with named fields (tf_concentration, etc.); extensible via kwargs |
| Inheritance depth confusion | Week 3-4 | Students subclass wrong level | Keep hierarchy ≤2 levels; test that subclassing works |
| pyproject.toml uses Poetry, CLAUDE.md mandates uv | Week 1 | Build system mismatch | Rewrite to PEP 621 with uv |
| README promises Mesa inheritance | Week 10-12 | Expectation mismatch | Revise: "follows Mesa's conventions" not "inherits from"; defer Mesa integration to Phase 2 |

---

## Implementation Sequence (12 weeks)

```
Week 1-2:  SimulationModel base + Gene + Individual + Conditions dataclass
Week 3:    ExpressionModel ABC + Linear + Hill + Constant
Week 4:    SelectionModel ABC + Proportional + Threshold
Week 5:    MutationModel ABC + point mutation
Week 6:    DataCollector (3-tier) + pandas export + performance benchmark
Week 7-8:  35+ tests (unit + integration + theory validation)
Week 9:    2 example scripts (simple_duplication, regulatory_network)
Week 10:   CI/CD + packaging (pyproject.toml PEP 621 + uv)
Week 11:   Documentation (Sphinx, API docs, getting started)
Week 12:   Polish, README, CONTRIBUTING, GOVERNANCE, v0.1.0 tag
```
