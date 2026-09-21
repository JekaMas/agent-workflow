## MODIFIED Requirements

### Requirement: Safe adoption and updates
The installer SHALL preview without writes, preserve existing instructions, reject conflicting/unmanaged files and edited managed content unless an explicitly reviewed migration binds their current and proposed identities, and pin exact shared source. Global replacement SHALL retain recoverable backups.
#### Scenario: Collision or changed managed file
- **WHEN** a target exists without ownership or differs from its recorded hash
- **THEN** refuse the update without overwriting that content unless an explicitly selected reviewed migration matches every affected current and proposed identity
#### Scenario: Repeat installation
- **WHEN** the same release is already installed without drift
- **THEN** preserve equivalent content and report the installed revision
