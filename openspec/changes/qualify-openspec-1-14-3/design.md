# Design

## Context

See proposal.md. Base: current origin/main `3a2ccce`, followed by the existing
PR #16 head `9e0891e` for its complete-stdout parser fix. Work is isolated on
`fix/openspec-1.14.3-20261023`; existing checkouts and unfinished work are preserved.
The locally installed CLI changed from 1.13.1 to user-selected 1.14.3 using npm.

## Decisions

Keep an exact adapter pin, not an untested semver range. Native temporary projects
qualify validation, guidance, task provenance and archive behavior. Unit fixtures
retain rejection of unqualified versions and malformed/large JSON. PR #16 remains
a visible dependency instead of copying its parser implementation.

The shared templates override upstream-generated skills, so refresh the specific
upstream safety semantics in the canonical templates. One included authoring
fragment covers propose, ff, continue, explore and update. Both client routes
resolve that same generated procedure. These checks prove emitted guidance and
route/drift behavior; they do not prove autonomous-agent adherence.

Strict validation on unchanged main selected eight items and failed two: the
execution-stop main requirement and the active evidence-graph requirement exceed
500 characters. Keep their obligations and all scenario identities; shorten the
first body without removing any listed condition, and move the second body's
case-field enumeration into its existing coverage scenario. Record the exact
formatting invalidation in the older change rather than pretending its historical
evidence was rerun. Historical docs/validation.md results remain historical.

## Evidence

The change-owned verification.json maps the two modified requirements to exact
native, adapter and consumer tests, including negative cases. Inspect the emitted
instructions after rendering config changes. Reconcile the required Make check
set using retained valid greens and newly affected checks, without rerunning green
tests merely for a stage/commit change. The final clean-state DAG gate is separate
from behavioral evidence.

The release review covers 1.13.2 through 1.14.3. New tool adapters, store layouts,
shell completion and custom schemas are not integrations this patch claims to
qualify. Current spec-driven artifact dependencies and closure boundaries remain.

## Rollout and limits

Commit and review shared source before changing consumer pins. Do not run native
`openspec update --force` over custom rendered adapters. The global personal
workflow release and product consumer pins need a separately reviewed rollout;
this patch does not overwrite them. Downgrade the CLI with the previous exact npm
version if a rollback is needed. No product changes are archived by qualification.

The user subsequently authorized a dedicated spec-update guide, review with
subagents, PR preparation/merge and the existing personal workflow rollout.
Keep guide ownership under docs with links to canonical procedures. Review the
parser dependency and upgrade together, then merge #16 before retargeting #17 to
main; use the reviewed exact head for each merge. Preview/apply the personal
installer only from a clean merged checkout and verify its exact release pointer,
backups and installed native compatibility. Preserve product consumer pins.
