# Spec Delta

## MODIFIED Requirements

### Requirement: Qualified consumer integration
Consumer adapters SHALL preserve actual commands, toolchains, artifact dependencies and failure semantics; selection or structural success SHALL not establish product completion. An exact OpenSpec version SHALL be qualified with native fixtures before changing the supported adapter pin.

#### Scenario: Pilot adoption
- **WHEN** a repository adopts the package
- **THEN** validate local workflow wiring and native artifact instructions while retaining domain rules and reporting unexecuted product evidence
- **AND** refuse an unqualified OpenSpec version before running validation

#### Scenario: Native strict validation reports a warning
- **WHEN** the installed validator warns about an overlong requirement, text discarded by archive, or unsupported change metadata
- **THEN** strict verification fails and preserves the native finding
- **AND** lowercase `x-` metadata accepted by the qualified CLI remains accepted

### Requirement: One canonical OpenSpec integration
All consumers SHALL use the same shared operation procedures and full artifact/apply/archive guidance. Local profiles SHALL retain project references and context. Validation SHALL reject divergence from the pinned rendered output.

#### Scenario: Existing consumer migration
- **WHEN** an existing consumer migrates its richer integration
- **THEN** preserve the action procedures for all operations, local check selection, authority and completion boundaries through shared templates and local profile references
- **AND** authoring guidance checks a concrete output's canonical path inside the selected change before any write, including delegated creation and symlink escapes
- **AND** apply guidance checks the native task's source path, line and unchanged checkbox before marking it complete
- **AND** verify guidance recovers a removed requirement's original text before checking implementation and reports unavailable originals as unverified

#### Scenario: Drift
- **WHEN** a rendered adapter or config changes independently of its shared template and profile
- **THEN** integration validation fails rather than accepting a second lifecycle
