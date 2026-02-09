# Phase 2 Architecture: Four ADRs

## ADR-004: RegulatoryNetwork Representation Strategy

**Status:** Proposed

**Context:**
Phase 2 requires multi-gene regulatory interactions. Three options emerged:
- **Option A**: Static adjacency matrix (sparse, numpy-backed), evaluated once at initialization
- **Option B**: Dynamic gene product concentrations tracked per-generation (more realistic, O(n) memory per gen)
- **Option C**: Hybrid—cached adjacency, lazy evaluation on mutation

Phase 1 introduced immutable Gene/Individual objects, validated early. This suggests static representation.

**Decision:**
Option A — Static sparse adjacency matrix (scipy.sparse CSR format), immutable post-initialization.

**Rationale:**
1. Consistency with Phase 1 early-validation pattern (catch topology errors before 10k-generation runs)
2. Memory efficiency: sparse matrix for typical networks (10% density = 100× compression vs. dense)
3. Performance: regulatory inputs computed as single matrix-vector multiply per generation (O(nnz) ≈ O(n) for sparse networks)
4. Biology accuracy: Most real networks stable over 1000 generations; mutation model handles structural change
5. Student accessibility: Clear separation between network topology (fixed) and dynamics (expression changes)

**Alternatives Considered:**
- **Option B (Dynamic tracking)**: +Realistic, -O(n) memory per gen (100 indiv × 100 genes × 1000 gen = 10M floats), slows expression calculation by 2-3×, overkill for Phase 2 scope
- **Option C (Hybrid)**: +Handles mutations, -Adds complexity (when to invalidate cache?), deferred to Phase 3

**Consequences:**
- (+) Fast expression computation (single sparse matrix op), low memory overhead, matches Phase 1 immutability philosophy
- (+) Adjacency matrix easily inspectable/debuggable (can be printed as dense for small networks)
- (-) Structural mutations (gene duplication, deletion) require rebuilding matrix (Phase 3: handle via mutation model)
- (-) Cannot model real-time rewiring (e.g., drugs affecting TF levels); acceptable for Phase 2
- Risk: Users assume adjacency changes mid-simulation; mitigation: document as immutable, add validation in constructor

---

## ADR-005: Composite Expression Model Pipeline

**Status:** Proposed

**Context:**
Phase 1 expression models (Linear, Hill, Constant) compute single-gene levels from environmental conditions. Phase 2 must combine regulatory inputs (from other genes) with base models. Three options:

- **Option A**: Regulatory inputs injected as additional parameters to base expression model
- **Option B**: CompositeExpressionModel wraps base model + regulatory overlay (composition pattern)
- **Option C**: Gene-level expression calculated via TF binding independently of base model

**Decision:**
Option B — CompositeExpressionModel composition pattern.

**Rationale:**
1. Separation of concerns: base model (what gene would express if isolated) + regulatory input (how other genes modify it)
2. Inheritance-based extensibility: users subclass CompositeExpressionModel for custom regulatory logic
3. Composability: arbitrary nesting (Hill(Linear(...))) similar to functional composition; students understand function composition
4. Consistency with Phase 1: users already extend ExpressionModel via inheritance
5. Testability: base and regulatory layers independently testable

**Alternatives Considered:**
- **Option A (Parameter injection)**: +Simpler, -breaks Phase 1 API (expression_model.compute(conditions) would need new signature), -regulatory logic hidden in base model, -hard to debug
- **Option C (Independent calculation)**: +Biologically flexible, -disconnects from base model semantics (what does "linear" mean without baseline?), -no reuse of Phase 1 models

**Consequences:**
- (+) Base expression models (Linear, Hill) reusable unchanged; CompositeExpressionModel adds ~50-100 lines
- (+) Regulatory logic inspectable (`model.base_model`, `model.regulatory_model`)
- (+) Composable: Hill(Linear(...)) works naturally
- (-) Additional indirection (~10% slowdown per call); mitigated by vectorization
- (-) Users must learn composition pattern (5-line example suffices)
- Risk: Composition overhead at 10k scale; mitigation: vectorize at GeneNetwork level, not model level

---

## ADR-006: Circuit Detection & Tracking

**Status:** Proposed

**Context:**
Regulatory networks often contain feedback loops (oscillators, bistables) and feedforward motifs (robust switches). Phase 2 should detect these automatically for analysis. Three strategies:

- **Option A**: Static detection at initialization (O(n²) or less), stored, reused
- **Option B**: Dynamic detection per-generation (catches mutations affecting circuits)
- **Option C**: Optional detection (off by default, toggled via flag)

**Decision:**
Option A + Option C — Static detection at initialization, optional (off by default).

**Rationale:**
1. Performance: O(n²) graph analysis (100 genes ≈ 1ms) acceptable at init; 10ms per generation would miss Phase 2 performance target
2. Immutability: RegulatoryNetwork is static (ADR-004), so circuit structure fixed post-init
3. Mutations handled asynchronously: Phase 3 adds structural mutations separately; detection can re-run then
4. Opt-in reduces cognitive load: users opt into circuit detection if analyzing network structure
5. Biology: Short-term dynamics (100-1000 generations) don't change feedback structure significantly

**Alternatives Considered:**
- **Option B (Dynamic)**: +Detects mutations, -10ms per generation (1000 gen × 10M indiv = 2.7 hours overhead), incompatible with Phase 2 performance target
- **Option C only (always on)**: +Automatic, -Forces users to pay detection cost they may not use

**Consequences:**
- (+) Users who care about circuits opt-in with `detect_circuits=True` flag
- (+) Metadata stored cheaply (lists of circuit node sets, ~1KB per network)
- (+) Detection algorithm reusable for Phase 3 (mutations)
- (-) Dynamic mutations won't update circuits until re-run (document this; Phase 3 handles properly)
- (-) New type annotation: `network.circuits: List[Set[str]]`, users must learn to inspect
- Risk: Users assume circuits update dynamically; mitigation: raise if circuits stale after mutations (Phase 3)

---

## ADR-007: Performance Strategy for 10k-Individual Scaling

**Status:** Proposed

**Context:**
Phase 2 target: 10k individuals × 100 genes × 1000 generations < 5 seconds (aggressive) or < 30 seconds (conservative).

Phase 1 GeneNetwork.step() is Python loop-based (no vectorization). At 10k individuals, expression computation dominates (10^10 operations).

Vectorization depth determines feasibility: NumPy operations ~10-100× faster than Python loops.

**Decision:**
Vectorize at population level (NumPy batch operations) + sparse regulatory matrix operations. Target: 5-second goal (aggressive), with fallback to 30-second acceptable range.

**Rationale:**
1. Phase 1 sets precedent: uses np.random.Generator (NumPy), not random.Random (proof of NumPy compatibility)
2. Expression computation is embarrassingly parallel: all individuals independent in expression phase
3. Regulatory inputs are linear algebra: sparse matrix @ dense vector (scipy.sparse + NumPy = 100× speedup over Python loops)
4. Existing tools (NumPy, SciPy, Pandas) aligned with Phase 1 stack; no new dependencies
5. Batch vectorization requires modest refactor: move loops into NumPy operations

**Alternatives Considered:**
- **No vectorization (pure Python loops)**: -10 minutes per 10k-individual run, unacceptable
- **Numba JIT compilation**: +Transparent speedup, -new dependency, -compilation time overhead, -less controllable
- **GPU acceleration**: +Ultimate speedup, -overkill for Phase 2, adds CUDA/torch dependency, locks users to GPU hardware

**Consequences:**
- (+) 10k-individual runs viable in seconds (5-10s target)
- (+) Uses existing Phase 1 deps (NumPy, SciPy)
- (+) Batch operations easier to parallelize later (Phase 3: joblib, Ray)
- (-) Requires GeneNetwork refactor: replace nested Python loops with vectorized calls
- (-) Regulatory inputs stored as dense vectors during computation (memory: 10k indiv × 100 genes × 8 bytes = 8MB, acceptable)
- Risk: Vectorization introduces shape bugs (dimension mismatches); mitigation: extensive testing with varied population sizes

**Performance Targets:**

| Scenario | Target | Acceptance |
|----------|--------|-----------|
| 1k indiv × 100 genes × 1k gen (Phase 1 baseline) | < 1s | Expected |
| 10k indiv × 100 genes × 1k gen, sparse regulation (10%) | < 5s | Aggressive |
| 10k indiv × 100 genes × 1k gen, no regulation | < 5s | Aggressive |
| 10k indiv × 100 genes × 1k gen, dense regulation | < 10s | Acceptable |

Benchmark harness in examples/benchmark.py to measure.

---

## Integration Summary: Phase 2 Architecture

| Decision | Component | Consequence | Dependency |
|----------|-----------|------------|-----------|
| **ADR-004** | RegulatoryNetwork (static adjacency) | Immutable, fast regulation inputs via sparse matrix | None (scipy.sparse) |
| **ADR-005** | CompositeExpressionModel | Wraps base + regulatory; composition pattern | ADR-004 (needs regulatory inputs) |
| **ADR-006** | Circuit detection (optional) | Metadata on networks; phase-gated (off by default) | ADR-004 (needs adjacency) |
| **ADR-007** | Vectorized expression (NumPy batch) | Refactors GeneNetwork.step() loops; requires shape discipline | ADR-005 (vectorizes computation) |

**Unified Design Philosophy:**
- **Biology over Performance**: RegulatoryNetwork is immutable, not dynamically rewired (biologically accurate for 1000 generations)
- **Inheritance-based Extensibility**: CompositeExpressionModel and RegulatoryExpressionModel both inherit ABC; users extend via subclassing
- **Opt-in Complexity**: Regulatory networks optional (Phase 1 code still works), circuit detection off by default, vectorization transparent
- **Early Validation**: RegulatoryNetwork detects cycles/errors at init (fail loud philosophy)

**Backwards Compatibility:**
- Phase 1 GeneNetwork, Individual, Gene classes unchanged
- GeneNetwork optionally accepts `regulatory_network: RegulatoryNetwork | None` parameter
- When `regulatory_network=None`, expression models work as Phase 1 (falls back to Conditions only)
- Seamless upgrade: Phase 1 examples run unchanged; Phase 2 examples use regulatory networks

---

## Flagged Implementation Risks

| Risk | Timing | Impact | Mitigation |
|------|--------|--------|-----------|
| Sparse matrix shape bugs (ADR-004) | Week 13-14 | Silent failures with wrong dimension | Write 5 explicit tests: empty matrix, single gene, large networks with varying sparsity |
| CompositeExpressionModel overhead (ADR-005) | Week 15 | 10-15% slowdown if naively nested | Profile early; optimize critical path (Hill compositions) with caching |
| Circuit detection timeout (ADR-006) | Week 16 | O(n²) may timeout at 1000 genes | Benchmark at init; defer to Phase 3 if > 100ms; document expectations |
| Vectorization shape bugs (ADR-007) | Week 17-19 | Incorrect results with unusual pop sizes | Unit tests at: 1, 10, 100, 1001, 10000; shape asserts in loops |
| Immutability mutation surprise (ADR-004) | Week 21+ | Users expect networks to mutate | Document explicitly; Phase 3 adds structural mutation via new mutation model |
| Performance target miss (ADR-007) | Week 19 | 10k × 1k gen = 30+ seconds | Benchmark early (Week 13: 100 indiv, Week 15: 1k, Week 17: 10k); revisit if >10s |

---

**Status:** Design phase complete. Ready for `/build plan` to create detailed Week 13-26 implementation plan.
