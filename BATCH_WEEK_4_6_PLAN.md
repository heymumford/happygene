# Batch Plan: Week 4-6 Implementation

## Status
**IN PROGRESS** - Starting Task 4

## Task 4: Week 4 - HillExpression + SelectionModel ABC + Selectors
- [ ] 4.1 Write Hill expression tests
- [ ] 4.2 Implement HillExpression (Hill equation)
- [ ] 4.3 Create selection.py with SelectionModel ABC
- [ ] 4.4 Implement ProportionalSelection
- [ ] 4.5 Implement ThresholdSelection
- [ ] 4.6 Update __init__.py
- [ ] 4.7 Commit
- Target: 48+ tests passing

## Task 5: Week 5 - MutationModel + Full step() Loop
- [ ] 5.1 Write MutationModel ABC tests
- [ ] 5.2 Implement MutationModel ABC
- [ ] 5.3 Implement PointMutation
- [ ] 5.4 Add integration tests
- [ ] 5.5 Wire into GeneNetwork.step()
- [ ] 5.6 Modify GeneNetwork.__init__ to accept 3 models
- [ ] 5.7 Implement full step() loop
- [ ] 5.8 Update __init__.py
- [ ] 5.9 Commit
- Target: 55+ tests passing

## Task 6: Week 6 - DataCollector (3-Tier) + Pandas Export
- [ ] 6.1 Write DataCollector tests
- [ ] 6.2 Implement DataCollector with 3-tier reporters
- [ ] 6.3 Implement DataFrame export methods
- [ ] 6.4 Add max_history parameter
- [ ] 6.5 Test collection & accumulation
- [ ] 6.6 Update __init__.py
- [ ] 6.7 Commit
- Target: 62+ tests passing

## Decisions
- TDD strict: test first, implementation second
- Use numpy.random.Generator for all RNG
- SelectionModel and MutationModel inherit from ABC
- DataCollector follows Mesa DataCollector pattern

## Commits Log
(To be filled in as work completes)
