# Portable project workflow

For everyday use, start with [the quickstart](quickstart.md).

Read applicable project instructions and `.agents/workflow-project.json`. The
project pin owns shared procedures. The profile records actual roots and conventions;
it does not authorize installation, services or external access.

Use the installed OpenSpec schema and native instructions. Proposal expresses
intent; specs require observable behavior and rejection cases; design records
choices, dependencies and evidence; tasks.md is the only task list. Detail the next
useful increment, revise within intent, and continue authorized implementation,
inspection, repair and revalidation. Shared openspec-delivery owns completion. Use docs/operations.md from this
package for operation-specific loading; all operation adapters and full OpenSpec
rules are rendered from the same canonical templates.

Operation skills in `.agents/skills/openspec-*` and Claude opsx commands route here.
`check workflow` runs the shared mechanics plus bootstrap ownership check;
`check spec <change>` validates exact artifacts; `check ready <change>` additionally
requires completed tasks. Neither structural readiness nor a green review is DONE.
Select product checks from the actual project instructions, manifests and profile.
Native language commands are supported; Make and a universal tool version are not
required. Preserve execution records, selected cases, relevant configurations and
failures in the change. Review-only scope does not permit tracked-file repair.

Load generic sdd-go/sdd-rust only when local language skills do not already supply
adequate guidance. Property, fuzz, concurrency, simulation, proof and performance
routes are conditional; do not run a catalog merely because it is available.

## Sync and archive

Sync is optional before archive: it merges selected delta requirements into main
specs without closing the change. Archive can synchronize directly or follow an
already validated sync. Inspect exact selected roots and changes, preserve unrelated
specs, and run strict validation for every affected main spec after either path.
A meaningful Purpose must satisfy the installed validator; a placeholder or too-short
Purpose can leave strict validation failing even when archive exits successfully.
Repair the resulting spec and revalidate before reporting closure.

Archive only completed, authorized work. For bulk requests assess each selected
change separately and preserve unselected or incomplete work. Readiness checks do
not authorize archive; archive does not authorize publication or deployment. New
material intent belongs in a separate change.

## Exact local check commands

Run from the consumer root; select a new output directory for each run:

- `workflow`: run every applicable consumer check below and retain each exit;
  failure of one does not become a pass because a later command succeeds:
  1. `python3 -B .agents/workflow/scripts/bootstrap.py status --repo .` for managed adopters; custom adapters use their documented state/pin check.
  2. `python3 -B .agents/workflow/scripts/skill_packages.py --root . --policy .agents/skill-policy.json validate`.
  3. `python3 -B .agents/workflow/scripts/workflow_publication.py --root . --policy .agents/publication-policy.json`.
  4. `python3 -B .agents/workflow/scripts/check_opsx_routes.py --root .`.
  5. `make -C .agents/workflow check` for shared mechanics.
  Inspect and stage the intended new setup sources before publication validation;
  an untracked/ignored active source is a failure, not a setup pass. The generated
  policy files keep consumer choices explicit. Existing custom consumers may use
  equivalent wrappers, but must retain packaging and publication checks. These
  checks do not establish product behavior or selected artifact validity.
- `spec <change>`: `python3 -B .agents/workflow/scripts/local_verify.py openspec
  --cwd . --change <change> --scope openspec --require-project-guidance
  --output-dir <evidence-directory>`.
- `ready <change>`: the same command with `--require-tasks-complete`.
- Language/assurance: inspect project commands and actual tool configuration first;
  the shared runner's pinned lint version is optional. Use the project's supported
  native route if it differs, retain its output and do not mislabel an unsupported
  adapter as a pass. Proof routes also require the project's actual source-bound
  target; the bootstrap does not copy Smart Example proof targets into a new repo.

## Conditional specialists

Use event-sequence-pbt for stateful retry, recovery, ordering or concurrency
properties in any language. Its generic model/oracle/replay procedure is shared;
framework recipes load separately and have explicit capability limits.
For Go hangs select golang-testing. For Go performance questions select
golang-performance-diagnostics, then golang-optimization once measurements
justify a change. These skills return results to the same OpenSpec change.
Project adapters and Claude commands are generated according to the tracked
profile; canonical skill bodies live under this pin's skills directory.

## Shared and project responsibilities

Generic operation/rule, delivery, review/testing/repair, debugging, conflict, language
and maintenance procedures live in this package. Project profiles/adapters own
commands, toolchain support, domain knowledge, operational gates and concrete proof
targets. Use docs/adoption.md for detection, safe existing-setup migration and updates.
Generic validator code accepts project policy; packaging budgets and campaign
requirements do not become universal defaults. New reusable workflow requirements
and changes belong in this package's openspec tree.

Use [native CLI usage](native-openspec.md) for artifact commands and [local adapter limits](local-checks.md) when selecting runner checks.
