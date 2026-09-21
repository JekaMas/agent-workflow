# Maintain shared workflow defaults

Keep generic procedures in shared skills/docs, global entrypoints in defaults,
installer mechanics in scripts/bootstrap.py and repo generation in its repo_files
function using the canonical integration renderer. Client discovery metadata and scripts are portable; project APIs, domain
constraints, actual manifests, product test selection and proof targets stay local.
Do not copy an entire product skill into personal scope merely to reuse a paragraph.

Personal defaults route to the repository first. Default availability must not
shadow same-named project skills or silently switch a pin. Preserve exact user
requirements, review-only scope, actual approval boundaries and independent-work
continuation. Tool/delegation preferences are conditional and subordinate to user
and runtime policy. No hard-coded model, role, developer checkout or CURRENT ledger.

For a shared behavior change, inspect the existing delivery/verification owners,
make the minimal canonical edit, qualify relevant positive and negative fixtures,
then test at least one consumer. Installer changes need no-write preview, idempotency,
conflict/edited-file handling, backup/restore inspection, exact pin and upgrade tests.
New project operations need both clients wired. Artifact changes need actual emitted
OpenSpec guidance, not YAML parsing alone. Report UI/agent evaluation gaps.

Validate shared make check; use scripts/rehearse_flow.py only for a relevant native
flow experiment. Compare controlled tasks with fixed source, model/tool settings
and budgets for outcome/defect/reading/cost claims. Scripted same-session pilots
establish mechanics and limits, not independent model quality or universal speedups.
Publish only under current authority and push shared source before consumer pins.
Do not place private repository reports, credentials or personal backup contents
in this public package. Setup/update/rollback instructions are in docs/adoption.md.

Verify tracked source with scripts/audit_sources.py --path <source-root>; add
--personal and --workspace <workspace-root> for installed routing. It resolves
symlinks and checks Git tracking/ignore rules. Backups and caches are not active
instruction owners and remain outside this source inventory.

## Specialist ownership

Shared skills own Go hang diagnostics, performance diagnostics/optimization and
language-independent event-sequence testing. Retain their conditional reference
routing and cross-skill links. The Go diagnostics/optimization pair ships together.
Language examples are adapters, not universal framework requirements. Changes to
specialist distribution need fresh-clone resolution checks for both client routes,
language selection, unmanaged collisions and upgrades. Existing product commands,
approvals, test sets and domain oracles remain in consumer adapters.

OpenSpec operation semantics and artifact rules have one owner:
`scripts/integration_templates/`. `scripts/integration.py` renders both new and
existing consumers. Never maintain a richer separate set in a product repository.
`docs/operations.md` owns the operation loading map; project guides supply local
commands, references and knowledge. Check all 14 paths with
`scripts/check_opsx_routes.py --root <consumer>` and run native instruction tests.
Migration reports stay in the affected consumer's change record as evidence,
not as another authoritative execution procedure.

Sync/archive/bulk-archive share `integration_templates/spec-validation.md`;
the renderer includes it in each required entrypoint. Keep this single source
instead of copying the strict-main-spec procedure between templates. Native
`test_full_lifecycle.py` fixtures exercise direct archive, prior sync, modified
requirements, selected bulk closure, invalid-main repair and incomplete-task
refusal in disposable repositories. Never run these closure experiments against
consumer changes. Generated output equality is intentional, not another owner.

## Specification and engineering ownership

The shared `openspec/specs/portable-workflow/spec.md` owns reusable adoption and
integration requirements. Start generic workflow changes in this repository's
`openspec/changes/`; keep consumer rollout tasks and historical evidence in the
affected consumer. File count in a historical change is not a count of active
custom procedures. Do not export private captures into this public package.

`verification-design/references/` owns portable behavior boundaries, isolation,
properties, scheduling, risk selection, architecture/resource inspection and
substitution claims. `sdd-go/references/` and `sdd-rust/references/` own conditional
language guidance. Consumer adapters retain domain errors, signing, exact commands,
toolchains, approval policies and campaign obligations. Update the shared body
and pinned consumer together; do not create a second canonical copy.

This repository's own OpenSpec config uses `openspec/workflow-profile.json` and
`integration.render_config`; its paths resolve directly to this source checkout.
Re-render that config when rules/profile changes and run `make check`. Consumer
rendering continues to use its `.agents/workflow-project.json` profile.

Shared main specs also own `adaptive-development-workflow` (planning through completion) and `assurance-routing` (review modes/provider controls/claim limits). Consumer E2E lane contracts and native proof-generator acceptance remain local.

For instruction/KB ownership changes use [knowledge maintenance](knowledge-maintenance.md). Shared hypothesis-debugging and conflict-resolution own general procedures; consumers keep operational sources and protected contracts. Generic provider setup is in [model review](model-review.md).

Shared `skill_packages.py` owns packaging and explicit workspace-link operations;
`workflow_publication.py` owns consumer-index/pin checks. Consumers provide policy
JSON and thin wrappers. `audit_sources.py` remains the separate resolved Git-owner
audit, including personal links; these checks establish different boundaries.
Bootstrap owns manifest discovery and reviewed migration snapshots. Never treat
plan hashes as semantic review or authority. Skill/source tests must retain
missing/ignored/stale failures and policy separation.

`policies/` owns reusable optional conventions selected explicitly by a consumer. Explicit-authority, exhaustive-investigation and coordinated-review retain their original safeguards, but are not new default approval/index/delegation requirements for every repository. Never infer selection or permission from their presence.

For extraction reviews, compare the source commit, shared replacement and retained
consumer adapter together. Separate exact moves/minor adaptations from changes to
coverage units, mandatory assertions, activation, approval or stopping behavior.
Requested feature additions are not evidence of relocation equivalence. Record
unavailable pre-extraction source as a provenance gap, not a preservation pass.
