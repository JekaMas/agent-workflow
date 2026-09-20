# Portable project workflow

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

For archive/sync, inspect delta/main requirements, preserve unrelated changes and
validate affected main specs strictly. A new capability needs a meaningful Purpose;
archive-generated placeholders are not acceptance. Publication/deployment require
current authority. New material intent belongs in a separate change.

## Exact local check commands

Run from the consumer root; select a new output directory for each run:

- `workflow`: `python3 -B .agents/workflow/scripts/bootstrap.py status --repo .`,
  then `python3 .agents/workflow/scripts/check_opsx_routes.py --root .` and
  `make -C .agents/workflow check`. Preserve either failure. Shared mechanics
  use their own fixtures; this is not product or consumer artifact validation.
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
