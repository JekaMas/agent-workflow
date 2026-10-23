# OpenSpec 1.14.3 qualification — 2026-10-23

## Scope and baseline

The global npm installation changed from `@fission-ai/openspec@1.13.1` to exact
`1.14.3`; both `openspec --version` and `npm ls -g` confirm it. Node v22.22.0
satisfies the package's Node >=20.19.0 requirement.

Source starts at current main `3a2ccce`, with parser dependency PR #16 at
`9e0891e`. Its complete-stdout repair is preserved rather than reimplemented.
The upgrade branch has no consumer product modifications.

Before source changes, native `openspec validate --all --strict --json
--no-interactive` selected eight items and failed two: overlong execution-stop
and evidence-graph requirement bodies. After the documented format repairs it
selected nine items (including this change), passed all nine, and reported no
issues. This is structural spec validation, not implementation acceptance.
No requirement, field or scenario was removed to obtain that result.

## Validation contract

`verification.json` owns two requirements, four properties, eleven exact case
edges and three deduplicated commands. Its commands cover the complete adapter,
graph/discovery, native OpenSpec and bootstrap suites, including legacy negative
and large-artifact cases. Source fingerprints were stabilized once after the
implementation batch. The older evidence-graph manifest records its actual R1
format/scenario and test-source invalidations; old receipts are not refreshed.

The required Make check set is inspected with `make -n check`. Reconcile its
commands with the graph observations and execute only uncovered groups. The
aggregate Make recipe otherwise repeats the adapter tests through workflow-tests
and the older change DAG. User instructions require retaining still-valid greens
rather than rerunning them merely to obtain another aggregate command exit.

Native all-item strict validation is already green on its unchanged semantic
inputs. Python syntax inspection covers all five changed Python files. Diff
whitespace inspection passed after removing one trailing blank line.

## Results

Implementation and acceptance executions are pending at this checkpoint. Tasks
remain unchecked until exact observed cases and the clean-state gate pass.

## Inspection and rollout limits

Self-review checks the exact version refusal, warning preservation, concrete
artifact/symlink containment guidance, exact source checkbox guidance, removal
provenance, sync blocking and generated-route drift. Rendered guidance tests
establish distribution and content, not autonomous-agent adherence. Native
fixtures establish disposable spec-driven mechanics, not product behavior.

Semantic Context and JetBrains-index discovery were unavailable for this exact
worktree; discovery.json records the actual status diagnostics and bounded source
reads. No index, IDE project, model call, product archive or external runtime was
created for this qualification.

Global personal workflow source and product consumer pins retain their existing
revisions. Those pinned runners still require their own version qualification and
rollout; installing the new CLI alone does not update them. Review and publish the
shared patch before migrating consumers. The existing product task 4.5 remains
open and this qualification does not claim its acceptance.
