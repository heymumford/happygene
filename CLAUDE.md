# HappyGene Project Configuration

## Vision
Interdependent, parameterized simulations modeling DNA repair mechanisms at multi-scale (molecular → cellular → population). Extract principles from peer-reviewed literature, build production-grade biocomputation platform with macOS UI, cloud-local orchestration, and live literature knowledge graph.

## Directory Structure

See `docs/ARCHITECTURE.md` for complete separation-of-concerns design.

**Quick Reference:**
- `engine/` — Core simulation engine (Python, TDD, testable)
- `cli/` — Command-line interface (entry point for batches)
- `mcp/` — Claude MCP server (6 core tools for agentic orchestration)
- `macos/` — Native macOS UI (SwiftUI, Intel + Apple Silicon)
- `knowledge_graph/` — Live literature graph (PubMed + dependency traversal)
- `docs/` — Architecture, quickstart, deployment
- `changelog/` — Industry-standard changelog (machine + human readable)

## Development Workflow

### Test-First (TDD)
```bash
# Before implementing: write failing tests
make test

# Implement to make tests pass
make build

# Refactor with confidence
make test
```

### Building
```bash
just run <config.yaml>      # Via justfile
make run CONFIG=<config>    # Via Makefile
uv run happygene run <config>  # Direct (Python 3.12+)
```

### Validation
```bash
make validate               # Schema validation
make sbml-export           # COPASI round-trip check
make chaos-test            # Fault injection tests
```

## Technology Stack

### Phase 1 (MVP, 8 weeks)
- **Engine**: Python 3.12, NumPy, SciPy (ODE), Pydantic (config)
- **CLI**: Click or Typer
- **Tests**: pytest, hypothesis (property-based), chaos patterns
- **Deployment**: pip package, Docker

### Phase 2 (Graphics + macOS)
- **macOS UI**: SwiftUI + Foundation
- **Graphics**: Canvas/Metal for real-time visualization
- **Cloud-Local**: Azure AKS + local orchestration

### Phase 3 (Advanced)
- **Literature**: PubMed E-utilities with live sync
- **Optimization**: Numba JIT, Julia ODE bridge (diffeqpy)
- **Performance**: Gillespie algorithm for kinetics

## Key Decisions

| Decision | Rationale | Date |
|----------|-----------|------|
| Python primary | OpenMM native, MCP integration, Jupyter ecosystem | 2026-02-08 |
| Modular monolith | Sequential scales (damage → kinetics → fate); no microservices | 2026-02-08 |
| Entry-point plugins | Zero core changes to add new repair pathways | 2026-02-08 |
| YAML + Pydantic config | Git-tracked reproducibility, parameter overrides | 2026-02-08 |
| SciPy ODE (Phase 1) | Proven, publication-ready; Gillespie/assimulo in Phase 2 if needed | 2026-02-08 |
| Adversarial design | Local compute primary, cloud as hedge; simplify before scaling | 2026-02-08 |

## Testing Philosophy

**Multi-level validation required** (≥2 data types simultaneously):
- **Unit**: Pure functions vs analytical solutions
- **Kinetic**: ODE solver vs published γ-H2AX data
- **System**: Survival curves vs clonogenic assays
- **Chaos**: Fault injection (timeouts, corruptions, intermittent failures)
- **Cross-tool**: SBML round-trip with COPASI

## Naming Conventions

- **Damage models**: `*DamageProfile` (e.g., `RadiationDamageProfile`)
- **Repair pathways**: `*RepairSimulator` (e.g., `NHEJRepairSimulator`)
- **Fate decisions**: `*FateDecider` (e.g., `ApoptosisDecider`)
- **Tests**: `test_*_property.py` (property-based), `test_*_chaos.py` (chaos), `test_*_contract.py` (API contracts)

## Credentials & Secrets

- **Location**: `~/.env` ONLY (single source of truth)
- **Never**: `.env.example`, `.env.template`, or project-level .env files
- **PubMed API key** (if rate-limiting needed): stored in `~/.env` as `PUBMED_API_KEY`

## CI/CD Gates

1. Lint (ruff)
2. Type check (mypy)
3. Fast tests (unit)
4. Slow tests (integration + chaos)
5. Coverage (threshold: 75%)
6. SBML validation (round-trip)
7. Deploy

## Documentation Requirements

- `docs/QUICK_START.md` — 5-minute tutorial (keep fresh)
- `docs/ARCHITECTURE.md` — System design (this is law)
- `docs/SIMULATION_DESIGN.md` — Add new repair pathway (template + example)
- `docs/KNOWLEDGE_GRAPH.md` — Literature topology (PubMed binding protocol)
- `CHANGELOG.md` — Industry standard (entries on every commit)

## When to Ask Questions

- ✓ Architectural trade-offs (local vs cloud, Swift vs Electron)
- ✓ Repair pathway design (NHEJ vs HR scope)
- ✓ Literature curation strategy (automated vs manual)
- ✗ Credentials (use ~/.env)
- ✗ Documentation theater (only essential files)
- ✗ Time estimates (focus on what, not how long)

---

**Status**: Repository structure initialized (2026-02-08). Ready for Phase 3 (narrow technology choices) and Phase 4 (MVP implementation).
