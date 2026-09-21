# Portable workflow

## Purpose

Define reusable development defaults, safe adoption and pinned OpenSpec integration across repositories while preserving consumer authority and evidence requirements.

## Requirements
### Requirement: Portable defaults
Personal instructions SHALL use concise shared routing, preserve requirement integrity and repository authority, and avoid mandatory product roles, delegation or legacy checkpoints.
#### Scenario: Configured repository
- **WHEN** personal skills activate in a repository with its own workflow
- **THEN** use the repository's applicable instructions and pinned source rather than a different global implementation
#### Scenario: New repository
- **WHEN** no workflow is configured
- **THEN** offer the shared adoption path within user authority; a small edit does not require installation
### Requirement: Safe adoption and updates
The installer SHALL preview without writes, preserve existing instructions, reject conflicting/unmanaged files and edited managed content, and pin exact shared source. Global replacement SHALL retain recoverable backups.
#### Scenario: Collision or changed managed file
- **WHEN** a target exists without ownership or differs from its recorded hash
- **THEN** refuse the update without overwriting that content
#### Scenario: Repeat installation
- **WHEN** the same release is already installed without drift
- **THEN** preserve equivalent content and report the installed revision
### Requirement: Qualified consumer integration
Consumer adapters SHALL preserve actual commands, toolchains, artifact dependencies and failure semantics; selection or structural success SHALL not establish product completion.
#### Scenario: Pilot adoption
- **WHEN** a repository adopts the package
- **THEN** validate local workflow wiring and native artifact instructions while retaining domain rules and reporting unexecuted product evidence

### Requirement: Portable specialist distribution
Adopted repositories SHALL resolve specialist procedures from their own pinned shared source. Event-sequence testing SHALL be language-independent; Go diagnostic and optimization discovery SHALL follow the project language profile. Existing project skills and commands SHALL not be overwritten implicitly.
#### Scenario: Fresh Go checkout
- **WHEN** a developer clones an adopted Go repository and initializes its pinned submodule
- **THEN** Codex and Claude routes resolve the shared event-sequence and Go specialist procedures without personal configuration
#### Scenario: Other language
- **WHEN** the profile selects Rust or another language without Go
- **THEN** event-sequence testing remains available without loading Go recipes or creating Go specialist discovery routes
#### Scenario: Existing specialist owner
- **WHEN** adoption finds an unmanaged specialist entrypoint
- **THEN** it refuses the collision and preserves that source for reviewed migration

### Requirement: One canonical OpenSpec integration
All consumers SHALL use the same shared operation procedures and full artifact/apply/archive guidance. Local profiles SHALL retain project references and context. Validation SHALL reject divergence from the pinned rendered output.
#### Scenario: Existing consumer migration
- **WHEN** an existing consumer migrates its richer integration
- **THEN** preserve the action procedures for all operations, local check selection, authority and completion boundaries through shared templates and local profile references
#### Scenario: Drift
- **WHEN** a rendered adapter or config changes independently of its shared template and profile
- **THEN** integration validation fails rather than accepting a second lifecycle
