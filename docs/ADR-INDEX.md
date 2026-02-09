# Architecture Decision Records (ADRs)

**Purpose**: Track architectural decisions, rationale, and alternatives. Ensure future maintainers understand "why", not just "what".

**Format**: [ADR 0000](https://adr.github.io/) — Status, Context, Problem, Candidates, Decision, Rationale, Testing, Related Decisions, References.

---

## Decision Index

| ADR | Title | Status | Date | Affects |
|-----|-------|--------|------|---------|
| [001](ADR-001-ode-solver-selection.md) | ODE Solver Selection (SciPy BDF) | DECIDED | 2026-02-08 | engine/simulator/ |
| [002](ADR-002-modular-monolith-architecture.md) | Modular Monolith Architecture | DECIDED | 2026-02-08 | engine/, cli/, mcp/ |
| [003](ADR-003-yaml-pydantic-configuration.md) | YAML + Pydantic Configuration | DECIDED | 2026-02-08 | engine/domain/ |
| [004](ADR-004-git-and-provenance.md) | Git + Provenance Metadata | DECIDED | 2026-02-08 | engine/io/ |
| [005](ADR-005-release-and-changelog.md) | SemVer Release + Changelog | DECIDED | 2026-02-08 | Release pipeline |
| [006](ADR-006-macos-swiftui.md) | macOS UI (SwiftUI, Phase 2) | PROPOSED | 2026-02-08 | macos/ |
| [007](ADR-007-cloud-local-orchestration.md) | Cloud-Local Orchestration (Azure Batch) | DECIDED | 2026-02-09 | engine/orchestration/ |

---

## Pending Decisions

| Candidate ADRs | Status | Target Date |
|---|---|---|
| Cloud-Local Orchestration (Azure AKS + local) | RESEARCH | 2026-02-09 |
| Python vs Electron for UI MVP | RESEARCH | 2026-02-09 |
| Knowledge Graph (PubMed sync strategy) | RESEARCH | 2026-02-10 |
| Testing Strategy (chaos + COPASI validation) | DECIDED | 2026-02-09 |

---

## Reading Guide

**By Role:**

- **Architect**: Start with 002 (modular monolith), then 001, 003, 004
- **Simulation Engineer**: Start with 001 (ODE solver), then 003 (config), 004 (provenance)
- **DevOps**: Start with 005 (release/changelog), then 004 (git/provenance)
- **macOS Developer**: Start with 006 (SwiftUI), then 002 (architecture)

**By Phase:**

- **Phase 1 (MVP)**: ADRs 001-005 (core decisions made)
- **Phase 2 (UI + Cloud)**: ADRs 006, cloud orchestration (pending)
- **Phase 3 (Literature)**: Knowledge graph strategy (pending)

---

## Decision Quality Checklist

Before committing an ADR:

- [ ] Context clearly explains the problem (not the symptom)
- [ ] ≥2 candidates seriously evaluated (not strawman)
- [ ] Decision includes rationale (trade-offs, constraints)
- [ ] Testing strategy defined (how to validate the choice)
- [ ] Related decisions documented (dependencies)
- [ ] Evidence-based (citations, benchmarks, not speculation)
- [ ] Clear "why not" for rejected candidates (prevents reversal)

---

## Updating ADRs

- **Status progression**: PROPOSED → DECIDED → SUPERSEDED → ARCHIVED
- **Never delete**: Archive with replacement rationale if reversing decision
- **Track evolution**: Link old ADR in new ADR's "Related Decisions"
- **Annual review**: Revisit Phase 1 decisions Q1 2027 (post-MVP)

---

## References

- [ADR: Lightweight Architecture Decision Records](https://adr.github.io/)
- [Documenting Architecture Decisions (Nygard, 2011)](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [Architecture Decisions: Demystifying Architecture](https://www.youtube.com/watch?v=txbS1IQvT_s)
