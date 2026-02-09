# Governance Model: happygene

This document describes the governance structure, decision-making process, and contributor tiers for the happygene project.

## Core Principle

**happygene is a BDFL (Benevolent Dictator for Life) project** with a clear path for community leadership.

The BDFL retains final decision authority on:
- Architectural decisions (module structure, dependencies)
- API stability and breaking changes
- Release cycles and versioning
- Project direction and strategic priorities

However, day-to-day decisions are made collaboratively with community input.

## BDFL Role

**Current BDFL:** Eric Mumford (@heymumford)

The BDFL:
- Makes final decisions on design conflicts
- Stewards the project roadmap
- Manages releases and versioning
- Evaluates major contributions
- Can delegate authority to Core Contributors

## Contributor Tiers

### Tier 1: Users
- Read access to repository
- Can open issues and discussions
- Can submit pull requests
- Expected: Follow code standards and testing requirements

**Responsibilities:**
- Report bugs with reproducible examples
- Propose features with clear use cases
- Test new releases and report issues

### Tier 2: Contributors
- Submit pull requests that are reviewed and merged
- Contribute examples, documentation, or bug fixes
- Engage in discussions and peer review

**Criteria for elevation to Contributor:**
- 2+ merged pull requests
- Demonstrates understanding of code style and testing standards
- Participates respectfully in discussions

**Privileges:**
- Direct push to feature branches (no forced push to main)
- Can be assigned issues
- Invited to contributor discussions

**Responsibilities:**
- Follow Conventional Commits format
- Maintain test coverage ≥ 75%
- Update documentation for user-facing changes
- Review and provide feedback on peer PRs

### Tier 3: Core Contributors
- Merge authority (can merge reviewed PRs)
- Can push directly to main (release branches)
- Participate in architectural decisions
- Maintain specific modules or subsystems

**Criteria for elevation to Core Contributor:**
- 5+ merged PRs with consistent quality
- Demonstrated expertise in one or more modules
- Mentors other contributors
- Active over 3+ months

**Privileges:**
- Can merge approved PRs
- Can propose breaking changes (with BDFL approval)
- Can lead design discussions
- Credited in releases

**Responsibilities:**
- Ensure code reviews meet quality standards
- Mentor new contributors
- Maintain assigned modules (tests, documentation, performance)
- Participate in release planning
- Keep documentation current

### Tier 4: BDFL
- Final decision authority
- Can override contributor decisions (with transparency)
- Sets project direction and priorities
- Manages releases

## Decision-Making Process

### Minor Decisions (Bug fixes, docs, test additions)
- Any contributor can propose
- Needs 1 approval from Core Contributor
- Can merge after 24h with no objections

### Moderate Decisions (New features, API additions)
- Needs discussion in issue/PR
- Needs 2 approvals (≥1 Core Contributor)
- Needs 48h review window
- BDFL may weigh in if design impact is significant

### Major Decisions (Breaking changes, architecture)
- Must have GitHub issue for discussion
- Needs formal RFC (Request for Comments)
- Needs 2+ Core Contributor approvals
- BDFL approval required
- 1 week discussion window minimum

### Reversions
- Any Core Contributor can revert a commit if:
  - Tests fail on main
  - Security issue is discovered
  - Breaking change not approved
- Must post explanation in PR

## Code Review Standards

### All PRs must have:

**1. Tests**
- New features: ≥80% coverage of new code
- Bug fixes: Tests for the specific bug
- Existing coverage must not decrease

**2. Documentation**
- Docstrings for all public functions/classes
- Examples for complex features
- CHANGELOG.md updated

**3. Commits**
- Conventional Commits format
- Clear commit messages with rationale
- Reasonable commit size (not 1 commit for 10 files)

### Review Checklist

- [ ] Tests pass (CI green)
- [ ] Coverage requirements met
- [ ] Code style consistent (black, isort)
- [ ] No debug code or commented logic
- [ ] Docstrings complete
- [ ] CHANGELOG updated (if user-facing)
- [ ] No breaking changes without issue discussion
- [ ] Performance impact acceptable (benchmarks if relevant)

## Release Process

### Version Format
happygene uses semantic versioning: `MAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes or major features (e.g., new expression model)
- `MINOR`: Backward-compatible features (e.g., new method)
- `PATCH`: Bug fixes, documentation, internal improvements

### Release Cycle
- **Target**: 1-2 releases per month during active development
- **Schedule**: No fixed release dates; driven by feature readiness
- **Branch**: Releases from `main` branch

### Release Checklist

1. **Prepare release candidate:**
   - Update CHANGELOG.md
   - Verify all tests pass
   - Verify coverage ≥ 95%
   - Update version in pyproject.toml

2. **Tag and build:**
   - `git tag -a v0.X.X -m "Release v0.X.X"`
   - `git push origin v0.X.X`

3. **Publish:**
   - Build: `python -m build`
   - Upload: `twine upload dist/*`

4. **Announce:**
   - GitHub releases page
   - Project announcement (if major feature)

## Conflict Resolution

### Issue Resolution Path

1. **Discussion**: Open GitHub issue with specific concern
2. **Proposal**: Suggest solution with rationale
3. **Review**: Core Contributors provide feedback
4. **Decision**: BDFL makes final call if unresolved after 1 week
5. **Implementation**: Clear next steps documented

### Code Conflict
- If reviewers disagree on code style/design:
  - Document both positions in issue
  - Provide RFC if complex
  - BDFL makes final decision
  - Decision documented for future reference

### Community Conduct
- Be respectful and assume good intent
- Focus on technical merit, not personal opinions
- Disagreement on technical issues is healthy
- See CODE_OF_CONDUCT.md for conduct standards

## Transparency

### Decision Log
- All major decisions documented in GitHub issues
- RFCs filed for significant changes
- CHANGELOG.md updated after each release

### Public Communications
- Roadmap published in ROADMAP.md
- Monthly status updates (if active development)
- GitHub Discussions for feature requests

## Amendment Process

This governance document can be amended by:

1. **Proposal**: File issue with proposed change and rationale
2. **Discussion**: Minimum 1 week feedback window
3. **Vote**: Core Contributors vote (simple majority)
4. **Approval**: BDFL approval required
5. **Documentation**: Updated governance document in repository

## Transition Plan

If BDFL is unavailable (6+ months inactive):

1. **Core Contributors** nominate replacement BDFL
2. **Community vote**: All Contributors eligible to vote
3. **Super-majority required**: 2/3 of active Contributors
4. **Announcement**: Transition documented in README and GOVERNANCE

---

**Effective date**: 2026-02-08
**Last updated**: 2026-02-08
**BDFL**: Eric Mumford (@heymumford)
