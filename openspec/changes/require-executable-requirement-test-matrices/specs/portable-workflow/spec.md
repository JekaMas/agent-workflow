# Spec Delta

## ADDED Requirements

### Requirement: Portable requirement evidence tooling
The pinned shared workflow SHALL ship a dependency-free evidence-graph validator,
query engine and executor plus rendered operation guidance. Consumer repositories
SHALL expose structural validation, affected-requirement execution and full final
execution without maintaining a second implementation.

#### Scenario: Consumer validates an active change
- **WHEN** the consumer runs its specification check
- **THEN** the shared validator checks graph completeness, exact spec pins, unique edges, command safety and source identities
- **AND** structural success does not claim that tests executed

#### Scenario: Consumer verifies an increment
- **WHEN** apply or verify names the affected requirement, owner or source selectors
- **THEN** the shared executor runs the selected graph closure and writes bounded machine-readable results
- **AND** the operation reports intended and observed exact cases separately

#### Scenario: Consumer checks final readiness
- **WHEN** the consumer runs final OpenSpec readiness
- **THEN** it validates task completion and executes the complete required evidence graph
- **AND** readiness fails if either structural or behavioral evidence is incomplete

#### Scenario: Consumer requires a newer Go toolchain
- **WHEN** the selected Go module requires a cached toolchain newer than the host installation
- **THEN** the runner uses Go's resolved toolchain with workspace disabled and dependency networking disabled
- **AND** an unavailable cached toolchain fails as a prerequisite instead of being replaced by an older forced local toolchain or downloaded silently
