# Proposal

## Why

OpenSpec currently recommends requirement-to-property test mapping but neither
requires a durable case inventory nor executes that inventory. A consumer could
therefore claim an increment green while omitting affected tests, as happened in
Smart Example's first GMX correction iteration.

## What Changes

- Require every behavioral requirement in a change delta to have a durable,
  machine-validated property map with explicit positive and negative cases.
- Require each case to name its real owner, oracle, exact observable test
  identity, command, substitution boundary, and invalidation dependencies.
- Add a portable manifest validator and executor that confirms intended test
  identities actually ran and passed; zero selection, skip, setup failure,
  timeout, missing implementation, or stale source identity remains non-passing.
- Make apply/verify execute all cases for the selected affected requirements and
  make final readiness execute the complete required manifest exactly once on
  the stabilized source.
- Preserve external authority: a protected or unavailable case remains an
  explicit blocker and is never auto-executed or converted to success.
- Stop forcing an older local Go toolchain when the consumer requires a newer
  already-resolved toolchain; offline dependency policy remains enforced.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `adaptive-development-workflow`: make requirement/property/case mapping and
  observed execution mandatory and machine-enforced for substantial behavioral
  changes.
- `portable-workflow`: ship the validator/executor through the pinned integration
  and require consumers to expose incremental and final commands.

## Impact

Affected shared sources include the verification procedure, OpenSpec operation
templates and configuration rules, the local verification runner/toolchain
environment, a new requirement-test manifest tool, its regression tests, and
consumer adoption documentation. Smart Example will update its shared pin,
commands, GMX change manifest, and stale iteration-one evidence after this source
is published.
