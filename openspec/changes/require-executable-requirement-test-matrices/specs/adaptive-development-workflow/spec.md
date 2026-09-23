# Spec Delta

## ADDED Requirements

### Requirement: Executable requirement evidence graph
Every behavioral requirement in an OpenSpec change SHALL be pinned to a durable
evidence graph before semantic implementation. The graph SHALL connect the exact
specification requirement and scenarios to one or more falsifiable properties,
and each property/scenario edge to distinct positive and negative cases. Every
case SHALL name exactly one scenario fingerprint, setup, observable, red and green
expectations, exact observable test identity, deduplicated command, owner, oracle,
substitution boundary, and semantic invalidation dependencies.

#### Scenario: Requirement and scenario coverage is complete
- **WHEN** a change contains a behavioral requirement or scenario
- **THEN** validation requires an exact graph node pinned to the current specification fingerprint
- **AND** every scenario is covered by a property with at least one positive and one negative case
- **AND** one case cannot claim several scenarios through one broad observable
- **AND** one exact test reused across scenarios names a distinct scenario-specific reason on every edge
- **AND** the positive and negative edge for one property/scenario use independent exact test identities
- **AND** an implemented case's source path owns that exact test identity
- **AND** normalized IDs cannot contain surrounding whitespace
- **AND** generic setup, red, or green prose cannot substitute for a discriminating fixture and oracle

#### Scenario: Affected increment is applied or verified
- **WHEN** apply or verify selects requirements, owners or changed source paths for the current increment
- **THEN** the workflow resolves the transitive affected-case closure through reverse graph indexes
- **AND** after each edit it runs the smallest directly invalidated case set first and expands only after that set passes or exposes a dependency
- **AND** at the stable iteration boundary it executes the complete iteration case set exactly once through deduplicated canonical commands
- **AND** a prior green case is reused until one of its declared invalidation dependencies changes
- **AND** confirms every exact expected test identity executed and passed
- **AND** every requested changed path must match a property source glob or a case invalidation dependency
- **AND** a changed case dependency selects that case without broadening unrelated property selection

#### Scenario: Final implementation readiness is checked
- **WHEN** a change is evaluated for completion or archival readiness
- **THEN** the workflow executes every required case in the complete graph on the stabilized source
- **AND** missing, planned-only, stale, skipped, zero-selected, failed, timed-out or unauthorized cases keep readiness non-passing
- **AND** expected failures, unexpected successes, ignored cases and unavailable command working directories remain non-passing
- **AND** Python unittest, Go test JSON, Cargo libtest and Node TAP observers preserve exact case status
- **AND** arbitrary success markers cannot prove behavioral cases

#### Scenario: Specification or test source drifts
- **WHEN** a requirement, scenario, test source, command or oracle no longer matches its pinned fingerprint or invalidation dependency
- **THEN** the affected evidence is stale and must be reselected and executed
- **AND** historical green output cannot satisfy the changed node
- **AND** query loads compatible result artifacts and reports current passed or stale status per case

#### Scenario: Test coverage appears duplicated
- **WHEN** two case nodes name the same property, scenario, polarity, observable and test identity
- **THEN** validation rejects the duplicate and retains one canonical case edge
- **AND** one test may support distinct properties only when each edge names its distinct observable or failure class
- **AND** commands with the same execution tuple are one canonical command even when observation metadata or Go JSON spelling differs

#### Scenario: Required evidence crosses an authority boundary
- **WHEN** a required case needs protected credentials, external mutation, deployment or unavailable infrastructure
- **THEN** the executor does not run it without authority
- **AND** records the case as blocked rather than passed or silently omitted

#### Scenario: Verification execution is bounded and reproducible
- **WHEN** a selected command executes locally
- **THEN** the repository execution policy overrides manifest environment values
- **AND** command cwd, manifest path and output path remain inside the repository/change boundary
- **AND** timeout terminates the process group and retains complete stdout and stderr artifacts with byte-accurate previews
- **AND** Git lookup failure is reported as unknown provenance rather than clean provenance
- **AND** requested selectors, source/spec/dependency fingerprints and dirty state are retained in the result

#### Scenario: Delta specification contains non-behavioral history
- **WHEN** a change contains REMOVED or RENAMED requirements, fenced examples, or no ADDED/MODIFIED behavioral requirement
- **THEN** only real ADDED/MODIFIED requirement nodes participate in the graph
- **AND** a change with no such node validates as not requiring an evidence graph

### Requirement: Searchable evidence ownership
The evidence graph SHALL support deterministic indexed lookup by requirement,
scenario, property, case, command, production owner and changed source path. Query
results SHALL be stable, deduplicated and suitable for both human review and
incremental test execution.

#### Scenario: A production owner changes
- **WHEN** verification queries one changed owner or source path
- **THEN** it returns the sorted unique closure of properties, cases and commands invalidated by that owner
- **AND** unrelated cases are not selected merely because they share a package or suite name
- **AND** `*` does not cross a path separator while `**` has recursive path semantics

#### Scenario: Reviewer traces one specification point
- **WHEN** a reviewer queries a requirement or scenario identifier
- **THEN** the tool returns its properties, positive and negative cases, exact tests, commands and latest observed status
- **AND** a suite name or aggregate test count cannot replace those edges

### Requirement: Search-backed OpenSpec decisions
Explore and check operations for a behavioral property SHALL create or update a
change-owned discovery ledger before deciding whether evidence belongs to the
current change, a new change, validation only, or no change. Each review SHALL
cover the relevant property and exact test identities, classify every useful
result, and record exact-text, semantic Context, and JetBrains-index search lanes.

#### Scenario: Explore scopes a behavioral property
- **WHEN** an explore operation investigates an unfamiliar behavior, owner, sibling case or relevant test
- **THEN** it completes exact repository search and one focused semantic Context search before source conclusions
- **AND** it performs a targeted JetBrains-index symbol/reference lookup when that capability is exposed and healthy
- **AND** an unavailable semantic or IDE capability is recorded with its exact reason rather than claimed as evidence
- **AND** results are classified as change candidate, reusable unchanged, interface dependency, test proof, irrelevant with reason, or unresolved

#### Scenario: Check decides discovered coverage disposition
- **WHEN** a check operation validates selected properties or tests
- **THEN** the discovery ledger covers every selected property and exact test identity
- **AND** each review records current-change, new-change with target, validation-only, or no-change disposition and rationale
- **AND** unresolved results keep the decision explicitly uncertain rather than silently passing
