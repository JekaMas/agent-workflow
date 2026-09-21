# Shared assurance routing

## Purpose

Define reusable review modes, configured provider execution and truthful assurance boundaries independently of consumer-specific proof generators, targets and campaigns.

## Requirements

### Requirement: Scoped review modes

The workflow SHALL route specification/evidence-plan review, implementation/evidence review and feedback resolution through the existing verification procedure, preserving the current task and authority.

#### Scenario: Review before implementation exists
- **WHEN** consequential requirements need review before code exists
- **THEN** the reviewer examines intent, missing cases and oracles without requiring an implementation result or creating another task list

#### Scenario: Findings during implementation
- **WHEN** a material in-scope finding has actionable evidence
- **THEN** authorized repair and affected revalidation continue in the same change, while unresolved decisions remain explicit

### Requirement: Qualified configured model review

A configured API model client SHALL select explicit reviewed inputs, endpoint/protocol and model, read its key from a named environment variable, preserve source/configuration identity and final output without credentials or hidden reasoning, and never equate model output with proof or task completion. It SHALL support DeepSeek, Claude, OpenAI/Codex API models and GLM through their selected API protocols.

#### Scenario: Missing configured execution path
- **WHEN** credentials, the selected endpoint or the requested model are unavailable
- **THEN** the command records a non-success outcome without exposing the key, retrying automatically or switching providers

#### Scenario: Incomplete or stale evidence
- **WHEN** input exceeds the declared context allowance, source changes, generation is incomplete or output is malformed
- **THEN** the result remains non-success and the initial diagnostics are retained without silent truncation or retry

### Requirement: Distinct assurance claims

Each investigated review/reasoning/proof path SHALL record applicability, selected candidate, invocation, execution status, assumptions and limitations separately. A required unavailable proof SHALL remain blocked; ordinary tests or model agreement SHALL NOT substitute for it.

#### Scenario: Specialist integration is unjustified or unavailable
- **WHEN** a verifier lacks an installed qualified path or the actual target needs substantial correspondence work
- **THEN** record the exact target and missing prerequisite or deferral reason without claiming implementation proof or installing an unrelated catalog

### Requirement: Workflow maintenance entrypoint

The repository SHALL provide an on-demand maintenance guide mapping workflow
structure to canonical source owners and meaningful validation, discoverable as
a Codex skill and a Claude command. It SHALL distinguish shared and consumer
sources, native OpenSpec and project operations, runtime plugins and repository
configuration, and historical evidence from current setup.

#### Scenario: Agent changes a workflow component
- **WHEN** the requested deliverable changes instructions, skills, prompts, OpenSpec integration or verification tooling
- **THEN** route to workflow-maintenance and the relevant ownership/validation sections without preloading unrelated product procedures

#### Scenario: Shared procedure needs repair
- **WHEN** the affected owner lives in the shared workflow source
- **THEN** edit and validate that canonical source, update and validate the consumer pin, and retain the user's publication boundary
