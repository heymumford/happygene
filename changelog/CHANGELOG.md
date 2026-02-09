# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository structure with separation of concerns design
- Project configuration (`CLAUDE.md`) with vision, workflow, and technology stack
- Changelog infrastructure (`.changelogrc`, this file)
- Directory organization: engine, cli, mcp, macos, knowledge_graph, docs, docker

### Planned (Phase 1 - MVP)
- Single radiation dose → NHEJ repair → cell survival curve simulation
- Python CLI with YAML config validation
- MCP server with 6 core tools for Claude integration
- SBML export for COPASI cross-validation
- 65+ unit tests (TDD discipline)

### Planned (Phase 2)
- macOS native UI (SwiftUI, Intel + Apple Silicon)
- Cloud-local orchestration (Azure AKS + local compute)
- Beautiful graphics rendering (animations, graphs)

### Planned (Phase 3)
- Live literature knowledge graph (PubMed E-utilities sync)
- R/Matlab integration layer
- Advanced optimization (Gillespie, Julia bridge)

---

## Version History

(Versions will be documented here as development progresses.)

---

## Notes for Maintainers

- All entries must include type prefix: `feat:`, `fix:`, `docs:`, etc.
- Link to related pull requests when available
- Group related changes under the same section
- Update this file with every merge to main/master
- Auto-generate with: `changelog/gen-changelog.sh --since <tag> --output CHANGELOG.md`
