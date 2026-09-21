# Adaptive development workflow

## Purpose

Define the reusable OpenSpec planning, execution, verification, repair and completion contracts while keeping consumer authority, commands and historical evidence with their owners.

## Requirements

### Requirement: One adaptive workflow owner
New substantial development work SHALL use the installed spec-driven OpenSpec
artifacts and a single authoritative change-owned task list. Historical campaign requirements and approvals
SHALL be preserved as work resumes in the selected OpenSpec change; retired
role procedures SHALL NOT create a second execution lifecycle.

#### Scenario: New evidence changes the approach
- **WHEN** an investigation reveals additional necessary work within the same intent
- **THEN** the agent updates the affected requirements, design and tasks coherently
- **AND** continues useful authorized work without creating a second plan lifecycle

#### Scenario: Existing product work is unrelated
- **WHEN** the workflow migration encounters active product changes
- **THEN** it preserves their artifacts and does not implement or archive their tasks

### Requirement: Adaptive increments preserve the outcome
The flow SHALL support useful implementation or uncertainty-reduction increments,
detail the next increment, and refine later work from evidence without imposing
a fixed iteration count or reducing the requested outcome.

#### Scenario: A local check fails
- **WHEN** a required check reveals a material defect within scope
- **THEN** the agent records the result, investigates, repairs and reruns affected checks
- **AND** a checkpoint or debugging report does not end the authorized task

### Requirement: Authority remains with the request
The flow SHALL preserve actual approval gates and SHALL NOT infer authority from
artifacts, checkboxes or repository instructions.

#### Scenario: Deployment needs approval
- **WHEN** local preparation is complete but deployment permission is absent
- **THEN** the agent prepares the reviewable action and asks for the exact missing approval
- **AND** reports local completion separately without executing the external action

#### Scenario: Routine authorized work remains
- **WHEN** an increment ends and the next in-scope action is clear
- **THEN** the agent proceeds without an artifact-by-artifact approval prompt

### Requirement: Local check outcomes are truthful
Required verification SHALL retain its command, working directory, scope, tool
identity, result and relevant artifacts. A missing prerequisite, failure,
unsupported configuration, timeout, unintended zero selection or skipped required
case SHALL NOT count as passing validation.

#### Scenario: OpenSpec validation selects nothing
- **WHEN** a validation command exits successfully but has no expected named result
- **THEN** the local workflow check reports non-success

#### Scenario: A selected command fails or times out
- **WHEN** the underlying check fails, cannot start or exceeds its stated budget
- **THEN** the wrapper records the failure or incomplete result and returns nonzero
- **AND** preserves bounded evidence without converting it into success

### Requirement: Completion follows requirements and evidence
DONE SHALL require the implemented outcome, matching artifacts, required passing
checks on the final relevant revision, appropriate diff/behavior inspection and
resolution of material findings. Incomplete work SHALL NOT be archived as complete.

#### Scenario: Artifacts exist but work remains
- **WHEN** OpenSpec reports complete artifacts while a required task or check remains
- **THEN** the agent continues or records the actual blocker
- **AND** neither status nor a clean review establishes DONE

#### Scenario: Required local work is complete
- **WHEN** all acceptance criteria and material findings have sufficient final evidence
- **THEN** the agent reports outcomes, evidence and accepted limitations and stops optional polishing
- **AND** distinguishes any pending external approval or deployment

### Requirement: Review and validation belong to the change
The workflow SHALL connect important requirements to actual owners and meaningful
evidence, review material changes against authority, and continue authorized
repair and affected revalidation without requiring legacy role handoffs or scores.

#### Scenario: Review finds an in-scope defect
- **WHEN** implementation review identifies a material defect or required evidence gap
- **THEN** the agent repairs or investigates within authority and revalidates affected evidence
- **AND** it distinguishes self-review from independent review and does not mark missing proof done

#### Scenario: Review-only authority
- **WHEN** the user requests review without implementation
- **THEN** the agent reports findings and proposed repairs without executing them

#### Scenario: Historical work has outstanding obligations
- **WHEN** prior PLAN/CURRENT records contain requirements relevant to the requested work
- **THEN** the agent maps those obligations and valid evidence into the selected OpenSpec change
- **AND** it uses one task list without retired role commands, templates or score tables

#### Scenario: Old role metadata remains installed outside the project
- **WHEN** a cached role plugin is visible but its repository workflow was retired
- **THEN** the agent follows the current repository's OpenSpec route
- **AND** it does not mutate global configuration or revive removed project instructions

### Requirement: Validate specification adequacy before semantic implementation
For meaningful behavior changes the flow SHALL challenge the specification against
intent and plausible faulty behavior, and SHALL link a proportionate validation
contract from existing artifacts without adding a mandatory approval or lifecycle.

#### Scenario: A plausible wrong implementation satisfies the planned tests
- **WHEN** an oracle or case set cannot distinguish an important contract violation
- **THEN** the agent strengthens the evidence plan or investigates the uncertainty before semantic implementation
- **AND** it asks only when a material intent or acceptance decision cannot be resolved responsibly

#### Scenario: Evidence identity is stale
- **WHEN** required evidence refers to source or fixture identities that no longer match
- **THEN** its validator rejects it and the agent records the gap or revalidates the affected evidence
- **AND** complete artifacts and task checkboxes cannot substitute for current required evidence

### Requirement: Qualified feedback and retained failure evidence
The flow SHALL qualify decisive feedback against intended behavior, preserve
acceptance through repair, report observed coverage and retain material failure
provenance and replay in the existing change record.

#### Scenario: A test fails before reaching the claimed behavior
- **WHEN** a decisive test fails in setup or cannot reach its intended assertion
- **THEN** the agent classifies and repairs the harness or oracle as authorized
- **AND** it does not claim behavioral reproduction until the check is requalified

#### Scenario: A retry passes after a material failure
- **WHEN** an initial required failure is followed by a passing retry
- **THEN** both observations remain visible and the cause is investigated or left explicitly unresolved
- **AND** the passing retry alone does not establish reliable completion

### Requirement: Whole-outcome no-change completion
The flow SHALL allow evidence-backed completion without edits when the full
requested outcome already holds, and SHALL distinguish that state from partial
fixes, unexecuted checks or failure to reproduce one example.

#### Scenario: Only one of two stale identities is repaired
- **WHEN** a required manifest still contains a stale fixture after its source identity is restored
- **THEN** current-evidence validation remains non-passing
- **AND** the remaining criterion stays open until satisfied

#### Scenario: The requested outcome already holds
- **WHEN** current required evidence supports the whole outcome and relevant cases
- **THEN** the agent reports verified no-change completion without inventing implementation work

### Requirement: Proportionate test authority and property coverage
The flow SHALL map important requirements to observable properties, suitable
oracles and test types, selected sets and observed execution. It SHALL permit
ordinary authorized local fixtures and generated samples without universal
per-case approval manifests while preserving explicit campaign and external gates.

#### Scenario: Local generated cases explore an unchanged domain
- **WHEN** authorized local testing generates and shrinks samples within its stated domain and bounds
- **THEN** it proceeds without per-seed approval and retains material counterexamples and replay configuration
- **AND** it does not substitute simulated behavior for required real-boundary evidence

#### Scenario: Declared selection differs from observed execution
- **WHEN** a manifest or plan lists a required test that did not execute or was skipped
- **THEN** the corresponding property remains unsupported and completion is blocked on that required evidence
- **AND** structural manifest validity does not count as execution

#### Scenario: Similar tests protect different failure modes
- **WHEN** consolidation is proposed for tests with similar setup but different properties or counterexamples
- **THEN** every prior obligation is mapped to retained cases before removal
- **AND** unresolved coverage causes preservation rather than deletion

#### Scenario: A double bypasses the claimed owner
- **WHEN** a test substitutes the implementation whose behavior it claims to establish
- **THEN** review rejects that claim and requires suitable actual-owner evidence
- **AND** unrelated substitutions do not invalidate independently justified observations about the real owner

### Requirement: Canonical operation entrypoints
The flow SHALL provide checkout-local OpenSpec operation skills and Claude-compatible
opsx command routes, preserve client-specific invocation differences, and retain
standalone operation scope while continuing an authorized full delivery request.

#### Scenario: Workspace discovery points at another checkout
- **WHEN** an operation is invoked in this worktree
- **THEN** its canonical operation adapter and linked project instructions are resolved here
- **AND** a missing or nonlocal target is reported rather than silently substituted

#### Scenario: In-scope artifact update during delivery
- **WHEN** new evidence refines the selected change within authorized acceptance
- **THEN** affected artifacts are updated without per-artifact approval
- **AND** authorized implementation and repair continue with invalidated evidence rechecked

#### Scenario: Publication omits command files
- **WHEN** Git ignores a required local command route
- **THEN** the route check fails instead of reporting portable command availability

#### Scenario: Selected specification synchronization
- **WHEN** the caller selects one returned delta from a change with multiple deltas
- **THEN** synchronization uses the authoritative planning root and only that exact subset
- **AND** current specs rules are obtained before writes and unrelated deltas remain untouched

### Requirement: Measured conditional instruction loading
The flow SHALL record per-operation file/section and native-output sizes during
validation, distinguish them from hidden runtime/model context, and use relevant
sections without limiting necessary investigation or weakening requirements.

#### Scenario: Planning finishes without implementation authority
- **WHEN** new and fast-forward are explicitly requested as planning-only
- **THEN** native artifacts may become apply-ready while implementation tasks remain unchecked
- **AND** artifact completeness is not reported as product completion

### Requirement: Reproducible workflow publication
Required workflow instructions, skills, references, client routes and setup
commands SHALL be versioned or supplied by a recorded clean submodule pin.
The flow SHALL provide client-neutral bootstrap instructions and report required
external tool/service prerequisites without assuming a personal global setup.

#### Scenario: Workflow source exists only on one developer's machine
- **WHEN** a required source in the declared publication scope is untracked, ignored, missing or resolves outside the checkout
- **THEN** local publication validation fails and reports the path
- **AND** a force-added ignored source does not bypass that check

#### Scenario: Shared workflow differs from its recorded revision
- **WHEN** the shared source is absent, dirty or checked out at another revision
- **THEN** publication validation fails rather than claiming reproducible setup

#### Scenario: Client has no native skill or slash-command discovery
- **WHEN** a developer uses the documented client-neutral bootstrap
- **THEN** the same tracked authority, operation, language and verification routes are identified
- **AND** unsupported UI dispatch or unavailable tools remain explicit gaps

