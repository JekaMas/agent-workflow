# Proposal

## Why

The installed OpenSpec CLI is now 1.14.3, but the shared runner accepts only
1.13.1. New strict warnings also reject two existing requirement bodies, and our
custom operation templates need the upstream safeguards that native regeneration
would otherwise supply.

## What Changes

- **BREAKING**: qualify the runner against exact OpenSpec 1.14.3 in place of 1.13.1;
  continue refusing unqualified versions.
- Exercise native strict warnings, metadata and exact task locations in disposable
  fixtures, preserving failure, empty-selection and incomplete-task behavior.
- Preserve every existing obligation while shortening the two overlong requirement
  bodies; move case-field detail into its existing coverage scenario.
- Teach shared authoring operations to resolve output paths inside the selected
  change, apply to check the native task location, and verify to recover removed
  requirement text before judging implementation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `portable-workflow`: qualify current native compatibility and preserve the
  safety checks in the canonical rendered operation procedures.

The existing adaptive-development requirement and active evidence-graph delta
receive formatting repairs only; their obligations and scenarios are preserved.

## Impact

Shared runner, native disposable fixtures, integration templates/renderer,
compatibility documentation and the two affected specification sources. The
existing full-stdout parser repair in PR #16 is a dependency, not reimplemented
here. Consumer pins, global workflow instructions and product changes are outside
this patch; the requested local OpenSpec CLI upgrade is already installed.
