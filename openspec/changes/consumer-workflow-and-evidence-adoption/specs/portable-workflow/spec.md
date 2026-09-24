# Spec Delta

## ADDED Requirements

### Requirement: Workflow-mechanics suites resolve in their own package roots
The runner SHALL load consumer suites from the consumer root and shared suites
from the shared package, each in its own process, and SHALL report which group
failed. A consumer module that shares a name with a shared suite SHALL NOT
replace it.

#### Scenario: Consumer owns a scripts package
- **WHEN** the consumer root contains its own `scripts` package and the pinned shared package is a submodule
- **THEN** the consumer suites load from the consumer root and the shared suites load from the shared package
- **AND** the combined report names both groups' selections and totals

#### Scenario: Consumer shadows a shared suite name
- **WHEN** a consumer file has the same module name as a shared suite and would fail if it were loaded
- **THEN** the shared suite still runs from the shared package and the run passes

### Requirement: Consumers admit the evidence graph through one shared wrapper
The pinned package SHALL ship one wrapper that validates the selected change's
graph and discovery ledger, forwards selectors to the shared executor, executes
the complete graph for readiness with clean provenance, reports a consumer change
recorded before the graph as a validation-only transition gap, and refuses an
unrecorded change that has no graph.

#### Scenario: Validation delegates
- **WHEN** a change owns a graph and a discovery ledger
- **THEN** the wrapper returns the shared validator's status and then the ledger's
- **AND** an unrecorded change without a graph is refused with an explicit reason

#### Scenario: Recorded transition gap
- **WHEN** a change is listed in the consumer transition file and has no graph
- **THEN** `validate` reports `transition_gap` and passes as validation-only
- **AND** `ready` refuses it until the graph exists

#### Scenario: Selector forwarding
- **WHEN** a selector is passed to `query` or `run`
- **THEN** the shared executor receives it and returns its own record
- **AND** an unknown selector is refused rather than silently selecting nothing
