# Tier Classification — happygene v0.2.0

**Date**: 2026-02-09 (Phase A, Week 1)
**Purpose**: Drive TDD discipline, coverage targets, code review gates, polyglot support
**Reference**: FINAL_SYNTHESIS_Iteration_5_UnifiedWorkflow.md § Conflict Resolution Matrix

---

## Classification Framework

Each module is classified as **CRITICAL** (Tier 1), **COMPUTATION** (Tier 2), **UTILITY** (Tier 3), or **LEGACY** (Tier 4) based on **criticality**: How much does the system break if this module is wrong?

### Tier Definitions

| Tier | Name | Criteria | Examples | TDD | Coverage | Review |
|------|------|----------|----------|-----|----------|--------|
| **1** | CRITICAL | Breaks core simulation; immutable schema; data integrity | Gene, Individual, GeneNetwork, entities, persistence | ✅ YES | 100% | 1 reviewer |
| **2** | COMPUTATION | Changes affect results; fallback possible; algorithms | ExpressionModel, SelectionModel, MutationModel, analysis | ⚠️ Optional | 90% | 0-1 |
| **3** | UTILITY | Nice-to-have; examples, helpers, CLI, viz | examples/*, regulatory_*, analysis/* (exploratory) | ❌ NO | 70% | auto-merge |
| **4** | LEGACY | Unused, deprecated, candidates for removal | (none identified yet) | ❌ NO | 50% | auto-merge |

---

## Tier 1: CRITICAL

### Core Entities
#### **happygene/entities.py** — Gene, Individual
- **Rationale**: Fundamental data model. All downstream operations depend on correctness of Gene name/expression_level and Individual genes/fitness fields. Breaking here breaks the entire simulation.
- **Depends on**: Nothing (foundational)
- **Depended on by**: GeneNetwork, expression models, selection models, mutation models, regulatory network, data collector
- **Immutability**: Gene name is immutable (via `__slots__`), expression_level is read-only property. Individual genes list is mutable but should be validated.
- **TDD**: ✅ **Mandatory** — Every change must have failing test first
- **Coverage**: 100% required
- **Reviewer**: @vorthruna (team: data-model-lead)
- **Tests**: `tests/test_entities.py` (comprehensive)
- **Change frequency**: Low (schema is stable in v0.2.0)

#### **happygene/base.py** — SimulationModel
- **Rationale**: Abstract base class defining simulation contract (generation counter, step interface, seed handling). Changes here propagate to all simulation models.
- **Depends on**: Nothing
- **Depended on by**: GeneNetwork, RegulatoryNetwork, any future simulation models
- **TDD**: ✅ **Mandatory**
- **Coverage**: 100% (especially abstract methods and generation tracking)
- **Reviewer**: @vorthruna
- **Tests**: `tests/test_base.py`
- **Critical aspects**: Generation counter increment is correct, seed handling is deterministic

### Orchestration Layer
#### **happygene/model.py** — GeneNetwork
- **Rationale**: Main simulation orchestration. The `step()` method implements the life cycle (expression → selection → mutation → increment). Breaking this breaks the entire simulation fidelity.
- **Depends on**: entities, expression models, selection models, mutation models, base, regulatory_network (optional)
- **Depended on by**: All example scripts, data collector, analysis
- **Algorithm correctness**: Vectorized expression computation, fitness evaluation order, mutation application order
- **TDD**: ✅ **Mandatory** — Especially for `step()` method
- **Coverage**: 100% (critical path: step(), init, property accessors)
- **Reviewer**: @vorthruna (team: architecture-lead)
- **Tests**: `tests/test_model.py` (extensive integration tests, vectorization validation)
- **Critical aspects**: Expression matrix construction, selection probability calculation, mutation rate application

### Data Collection & Persistence
#### **happygene/datacollector.py** — DataCollector
- **Rationale**: Collects simulation trajectories. Loss of data = loss of experiment results. Breaking this means experiments produce no outputs.
- **Depends on**: entities, model
- **Depended on by**: All analysis, all examples
- **TDD**: ✅ **Mandatory**
- **Coverage**: 100% (all data collection paths, edge cases like empty population)
- **Reviewer**: @vorthruna
- **Tests**: `tests/test_datacollector.py`
- **Critical aspects**: Data integrity (no lost steps), correct indexing, reproducibility with seed

#### **happygene/conditions.py** — Conditions
- **Rationale**: Environmental parameters affecting simulation. Changes here propagate to expression models and fitness evaluation.
- **Depends on**: Nothing
- **Depended on by**: GeneNetwork, expression models, selection models
- **TDD**: ✅ **Mandatory** (if modified; currently stable)
- **Coverage**: 100%
- **Reviewer**: @vorthruna
- **Tests**: Implicitly tested via `tests/test_model.py` (conditions parameter)

### Test Infrastructure
#### **tests/test_model.py** — Integration Tests
- **Rationale**: Tests are the quality gate. If tests are wrong, everything downstream is wrong. Integration tests validate the entire life cycle.
- **Depends on**: All modules (integration test)
- **Depended on by**: CI/CD pipeline, Go/No-Go gate
- **TDD**: ✅ **Mandatory** (tests of tests, contract validation)
- **Coverage**: 100% (of integration scenarios; not individual units)
- **Reviewer**: @vorthruna (team: qa-lead)
- **Tests**: Self-referential; validated via contract testing + cross-validation with theory
- **Critical aspects**: Stochastic correctness (mean behavior matches Mendelian expectations), deterministic reproduction (seed), edge cases (empty population, single individual)

#### **tests/conftest.py** — Test Configuration
- **Rationale**: Shared fixtures and configuration. Breaking here breaks all downstream tests.
- **Depends on**: entities, expression models
- **Depended on by**: All tests
- **TDD**: ✅ **Mandatory**
- **Coverage**: 100% (all fixtures, parameterization)
- **Reviewer**: @vorthruna
- **Tests**: `tests/conftest.py` self-validation

#### **tests/test_theory.py** — Theory Validation
- **Rationale**: Validates simulation correctness against genetic theory (Hardy-Weinberg, Mendelian genetics). This is the **acceptance test** for simulation fidelity.
- **Depends on**: All modules (acceptance test)
- **Depended on by**: Publication readiness, credibility
- **TDD**: ✅ **Mandatory**
- **Coverage**: 100% (all theory scenarios: neutral evolution, selection, mutation)
- **Reviewer**: @vorthruna (team: domain-expert)
- **Tests**: Ensemble validation, Monte Carlo tests
- **Critical aspects**: Statistical correctness (p-values), convergence to theoretical expectations

---

## Tier 2: COMPUTATION

### Expression Models
#### **happygene/expression.py** — ExpressionModel, LinearExpression, HillExpression, ConstantExpression
- **Rationale**: Algorithms for computing gene expression. Correctness is important but behavior is deterministic and testable. Changes are isolated to expression computation; selection/mutation logic unaffected.
- **Depends on**: Nothing
- **Depended on by**: GeneNetwork.step(), regulatory networks
- **Algorithm correctness**: Linear: expression = slope × genotype + intercept; Hill: sigmoidal kinetics; Constant: fixed expression
- **TDD**: ⚠️ **Optional** (event-driven + integration tests sufficient)
- **Coverage**: 90% required (≥ 10% can be edge cases)
- **Reviewer**: 0-1 (optional; may auto-merge if coverage met)
- **Tests**: `tests/test_expression.py` (extensive but not 100% required)
- **Change frequency**: Moderate (new models added occasionally)
- **Vectorization**: Leverages NumPy for efficiency; must validate shape/broadcasting

#### **happygene/regulatory_expression.py** — RegulatoryExpressionModel, CompositeExpressionModel
- **Rationale**: Variants of expression models with regulation. Extension of Tier 2 computation.
- **Depends on**: expression
- **Depended on by**: GeneNetwork (optional), RegulatoryNetwork
- **TDD**: ⚠️ **Optional**
- **Coverage**: 90%
- **Reviewer**: 0-1
- **Tests**: `tests/test_regulatory_expression.py`

### Selection Models
#### **happygene/selection.py** — SelectionModel, ProportionalSelection, ThresholdSelection, SexualReproduction, AsexualReproduction, EpistaticFitness, MultiObjectiveSelection
- **Rationale**: Fitness evaluation and reproduction strategies. Changes affect phenotype distribution but recovery is possible through neutral drift. Fallback: uniform selection (all fitness = 1).
- **Depends on**: entities, mutation
- **Depended on by**: GeneNetwork.step(), examples
- **Algorithm correctness**: Proportional fitness, threshold behavior, sexual/asexual reproduction mechanics
- **TDD**: ⚠️ **Optional** (event-driven + integration tests sufficient)
- **Coverage**: 90% required
- **Reviewer**: 0-1
- **Tests**: `tests/test_selection.py` (comprehensive for each strategy)
- **Change frequency**: Low to moderate (strategies are stable; new ones added rarely)
- **Stochasticity**: Selection is stochastic; tests validate probability distributions, not exact outcomes

### Mutation Models
#### **happygene/mutation.py** — MutationModel, PointMutation
- **Rationale**: Stochastic mutation operator. Changes introduce variation but recovery is possible. Behavior is probabilistic; testability via ensemble averaging.
- **Depends on**: entities
- **Depended on by**: GeneNetwork.step(), examples
- **Algorithm correctness**: Mutation rate application, magnitude distribution, boundary handling (clamping to [0, inf))
- **TDD**: ⚠️ **Optional** (stochastic; ensemble tests more suitable than unit tests)
- **Coverage**: 90% required
- **Reviewer**: 0-1
- **Tests**: `tests/test_mutation.py` (ensemble tests, parameter sweeps)
- **Change frequency**: Low (mutations are stable)
- **Stochasticity**: Tests use seed for reproducibility but validate distributions, not exact sequences

### Analysis & Reporting
#### **happygene/analysis/** — Sobol, Morris, Correlation, Response Surface, Output
- **Rationale**: Post-simulation analysis tools. Output verification more important than process correctness. Exploratory; failures are learning opportunities.
- **Depends on**: model, entities, selection, expression (post-simulation)
- **Depended on by**: Examples, research workflows
- **TDD**: ⚠️ **Optional**
- **Coverage**: 90% required
- **Reviewer**: 0-1
- **Tests**: `tests/analysis/test_*.py` (sensitivity analysis validation)
- **Change frequency**: Moderate (new analyses added in v0.3+)
- **Critical aspects**: Numerical stability, statistical correctness of sensitivity indices

---

## Tier 3: UTILITY

### Examples
#### **happygene/examples/** or example scripts (any *.py files in examples)
- **Rationale**: Demonstrative code. Failures are learning opportunities; recovery is straightforward (re-run with corrected parameters).
- **Depends on**: All other modules (educational)
- **Depended on by**: Users, documentation
- **TDD**: ❌ **Not mandatory** (examples should be clear, not fully tested)
- **Coverage**: 60% minimum (main execution paths; edge cases optional)
- **Reviewer**: auto-merge if CI passes
- **Tests**: Implicit via `tests/test_examples.py` (example-as-test pattern)
- **Change frequency**: High (examples grow with new features)
- **Note**: Examples should be clear and executable; completeness > correctness

### Command-Line Interface (if exists)
#### **happygene/cli.py** or similar
- **Rationale**: User-facing but not critical to simulation. Correctness = usability.
- **Depends on**: model, data collector, analysis
- **Depended on by**: End users, documentation
- **TDD**: ❌ **Not mandatory**
- **Coverage**: 70% minimum
- **Reviewer**: auto-merge if CI passes
- **Tests**: Manual testing or integration tests (not full unit coverage)

### Visualization (if exists)
#### **happygene/viz.py** or similar
- **Rationale**: Aesthetic; correctness = readability & prettiness.
- **Depends on**: entities, data collector
- **Depended on by**: Notebooks, dashboards
- **TDD**: ❌ **Not mandatory**
- **Coverage**: 50% minimum (rendering is hard to test)
- **Reviewer**: auto-merge if CI passes
- **Tests**: Visual regression testing (manual), not unit tests

### Regulatory Network (Exploratory)
#### **happygene/regulatory_network.py** — RegulatoryNetwork, RegulationConnection
- **Rationale**: Gene regulatory network representation. Optional feature; fallback is no regulation (default all-zeros).
- **Depends on**: entities, expression
- **Depended on by**: GeneNetwork (optional), examples
- **TDD**: ⚠️ **Optional**
- **Coverage**: 70% (exploratory; some edge cases acceptable)
- **Reviewer**: auto-merge if CI passes
- **Tests**: `tests/test_regulatory_network.py` (exploratory)
- **Change frequency**: High (v0.2 feature; v0.3 will expand)
- **Maturity**: Experimental (not core simulation)

---

## Tier 4: LEGACY

**Currently**: None identified.

**Future candidates**:
- Old example scripts (when superseded by new ones)
- Deprecated expression/selection models
- Obsolete test files (e.g., test_edge_cases.py, test_edge_cases_v2.py if consolidated)

**Handling**:
- Move to `deprecated/` directory
- Tag with deprecation warnings
- Keep for backwards compatibility, but don't enforce TDD/coverage
- Remove in next major version (v1.0)

---

## Coverage Targets by Tier

| Tier | Module Category | Target | Enforcement | Tool |
|------|-----------------|--------|-------------|------|
| **1 (CRITICAL)** | entities, model, base, datacollector, conditions, tests | **100%** | Hard gate (CI fails if <100%) | pytest-cov + custom script |
| **2 (COMPUTATION)** | expression, selection, mutation, analysis, regulatory | **90%** | Soft gate (warning if <90%, but doesn't fail) | pytest-cov |
| **3 (UTILITY)** | examples, cli, viz, regulatory_network | **70%** | Informational (report only) | pytest-cov |
| **4 (LEGACY)** | deprecated/* | **50%** | Tracking (no enforcement) | pytest-cov |

---

## Code Review Gates by Tier

| Tier | Module | Required Reviewers | Condition | Tool |
|------|--------|-------------------|-----------|------|
| **1** | entities, model, base, datacollector, conditions | **1** | All changes | CODEOWNERS |
| **1** | tests/test_model.py, tests/test_theory.py | **1** | All changes | CODEOWNERS |
| **2** | expression, selection, mutation, analysis, regulatory | **0-1** | Auto-merge if coverage ≥90% | CODEOWNERS + CI gate |
| **3** | examples, cli, viz | **0** | Auto-merge if CI passes | CODEOWNERS + CI gate |
| **4** | deprecated/* | **0** | Auto-merge if CI passes | CODEOWNERS |

---

## TDD Discipline by Tier

| Tier | Discipline | Process |
|------|-----------|---------|
| **1 (CRITICAL)** | **Mandatory TDD** | 1. Write failing test 2. Run, verify FAIL 3. Minimal implementation 4. Run, verify PASS 5. Refactor 6. Commit with rationale |
| **2 (COMPUTATION)** | **Optional** (Event-driven OK) | 1. Design algorithm 2. Implement 3. Write tests 4. Validate coverage ≥90% 5. Commit with rationale |
| **3 (UTILITY)** | **Not required** | 1. Implement 2. Provide examples 3. Test manually or via examples 4. Commit with rationale |
| **4 (LEGACY)** | **Not required** | Minimal maintenance |

---

## Polyglot Support by Tier

| Tier | Python | Java | C# |
|------|--------|------|-----|
| **1** | ✅ Yes (TDD templates) | ✅ Yes (JUnit + TDD) | ✅ Yes (xUnit + TDD) |
| **2** | ✅ Yes (pytest) | ✅ Yes (JUnit) | ✅ Yes (xUnit) |
| **3** | ✅ Yes (optional) | ⚠️ Optional | ⚠️ Optional |
| **4** | ✅ Yes (tracking) | ⚠️ Tracking | ⚠️ Tracking |

Note: Phase A is Python-only. Phase B (Weeks 5-8) adds Java/C# abstraction layer.

---

## Decision Log

| Date | Decision | Rationale | Owner |
|------|----------|-----------|-------|
| 2026-02-09 | Gene, Individual → Tier 1 (CRITICAL) | Fundamental data model; all downstream depends on correctness | @vorthruna |
| 2026-02-09 | GeneNetwork → Tier 1 (CRITICAL) | Orchestration layer; simulation fidelity depends on step() logic | @vorthruna |
| 2026-02-09 | Expression/Selection/Mutation → Tier 2 (COMPUTATION) | Algorithm correctness matters but behavior is testable and deterministic | @vorthruna |
| 2026-02-09 | Analysis → Tier 2 or 3 (split) | Sobol/Morris: Tier 2 (numerical/statistical correctness); exploratory: Tier 3 | @vorthruna |
| 2026-02-09 | Examples → Tier 3 (UTILITY) | Demonstrative; clarity > completeness | @vorthruna |
| 2026-02-09 | RegulatoryNetwork → Tier 3 (UTILITY) | Exploratory feature (v0.2); fallback is no regulation | @vorthruna |

---

## Next Steps (Phase A, Week 1)

1. ✅ **Done**: Create this classification document
2. ⏳ **Next**: Implement CODEOWNERS file (`.github/CODEOWNERS`) using this classification
3. ⏳ **Next**: Implement GitHub Actions matrix (`.github/workflows/quality.yml`) with tier-aware coverage gates
4. ⏳ **Next**: Create TDD templates for Tier 1 modules
5. ⏳ **Next**: Extend pre-push hook for TDD validation

---

**Classification Version**: 1.0
**Last Updated**: 2026-02-09
**Next Review**: 2026-05-09 (after Phase A complete, before Phase B)

