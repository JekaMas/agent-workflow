# Maintain shared workflow defaults

Keep generic procedures in shared skills/docs, global entrypoints in defaults,
installer mechanics in scripts/bootstrap.py and repo generation in its repo_files
function. Client discovery metadata and scripts are portable; project APIs, domain
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
