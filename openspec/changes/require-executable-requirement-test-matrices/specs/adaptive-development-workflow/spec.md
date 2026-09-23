# Spec Delta

## ADDED Requirements

### Requirement: Executable requirement evidence graph
Every behavioral requirement in an OpenSpec change SHALL be pinned to a durable
evidence graph before semantic implementation. The graph SHALL connect the exact
specification requirement and scenarios to one or more falsifiable properties,
and each property to explicit positive and negative cases, exact observable test
identities, deduplicated commands, owners, oracles, substitution boundaries and
semantic invalidation dependencies.

#### Scenario: Requirement and scenario coverage is complete
- **WHEN** a change contains a behavioral requirement or scenario
- **THEN** validation requires an exact graph node pinned to the current specification fingerprint
- **AND** every scenario is covered by a property with at least one positive and one negative case

#### Scenario: Affected increment is applied or verified
- **WHEN** apply or verify selects requirements, owners or changed source paths for the current increment
- **THEN** the workflow resolves the transitive affected-case closure through reverse graph indexes
- **AND** executes every required local case in that closure exactly once through its canonical command
- **AND** confirms every exact expected test identity executed and passed

#### Scenario: Final implementation readiness is checked
- **WHEN** a change is evaluated for completion or archival readiness
- **THEN** the workflow executes every required case in the complete graph on the stabilized source
- **AND** missing, planned-only, stale, skipped, zero-selected, failed, timed-out or unauthorized cases keep readiness non-passing

#### Scenario: Specification or test source drifts
- **WHEN** a requirement, scenario, test source, command or oracle no longer matches its pinned fingerprint or invalidation dependency
- **THEN** the affected evidence is stale and must be reselected and executed
- **AND** historical green output cannot satisfy the changed node

#### Scenario: Test coverage appears duplicated
- **WHEN** two case nodes name the same property, polarity, observable and test identity
- **THEN** validation rejects the duplicate and retains one canonical case edge
- **AND** one test may support distinct properties only when each edge names its distinct observable or failure class

#### Scenario: Required evidence crosses an authority boundary
- **WHEN** a required case needs protected credentials, external mutation, deployment or unavailable infrastructure
- **THEN** the executor does not run it without authority
- **AND** records the case as blocked rather than passed or silently omitted

### Requirement: Searchable evidence ownership
The evidence graph SHALL support deterministic indexed lookup by requirement,
scenario, property, case, command, production owner and changed source path. Query
results SHALL be stable, deduplicated and suitable for both human review and
incremental test execution.

#### Scenario: A production owner changes
- **WHEN** verification queries one changed owner or source path
- **THEN** it returns the sorted unique closure of properties, cases and commands invalidated by that owner
- **AND** unrelated cases are not selected merely because they share a package or suite name

#### Scenario: Reviewer traces one specification point
- **WHEN** a reviewer queries a requirement or scenario identifier
- **THEN** the tool returns its properties, positive and negative cases, exact tests, commands and latest observed status
- **AND** a suite name or aggregate test count cannot replace those edges
