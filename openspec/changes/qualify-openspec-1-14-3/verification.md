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
edges and three deduplicated commands. The initial acceptance commands cover the
complete adapter, graph/discovery, native OpenSpec and bootstrap suites, including
legacy negative and large-artifact cases. Source fingerprints were stabilized once after the
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

The complete qualification DAG passed all eleven edges with `--all
--require-clean` at clean implementation commit
`87d8267878583ebbd15057dad9eaeb6f6bf6f0ab`. Receipt:
`data/checks/openspec-1143-acceptance/result.json`.

| Group | Observed tests | Outcome |
| --- | ---: | --- |
| Disposable consumer/bootstrap | 35 | Passed, no skips |
| Actual native OpenSpec 1.14.3 | 15 | Passed, no skips |
| Adapter, evidence graph and discovery | 86 | Passed, no skips |
| Remaining Make preservation groups | 35 | Passed, no skips |
| Total unique suite cases | 171 | Passed |

The preservation receipt is
`data/checks/openspec-1143-preservation/result.json`. The initial unit receipt
contains passing observations for all sixty required edges of the older shared
evidence-graph change. That evidence is reconciled by exact test identity;
the older graph executor was not rerun solely to generate a second green receipt.
The aggregate `make check` command itself was not executed. Its full required
command/test set is accounted for through these receipts and the retained graph,
discovery, native and configuration checks.

Self-review found and repaired one qualification correction: the unqualified-
version unit fixture substitutes the command planner. Its metadata now discloses
that owner and the forbidden native-release claim; its command selects only the
affected test. That corrected qualification passed with `--require-clean` on
`8c3ac6901861a1a0f1e04079c20d04d77fb311ce`, in
`data/checks/openspec-1143-acceptance/qualification-correction.json`.
The original full-suite receipt is retained. Loading both receipts through the
native graph query reports all eleven cases currently `passed`, without stale or
missing evidence. See `final-coverage.json` and `reconciliation.json` alongside the
original receipt. Production/test source inputs are unchanged.

The generic unittest observer recognizes 85 of the 86 unit identities because
one pre-existing unregistered test has a two-line description. Its retained
native output explicitly names the test and reports `... ok`, and the unittest
summary reports 86/86. It is manually reconciled as passing; none of the eleven
new or sixty older graph edges is missing. Broader multiline-description parser
support is a separate pre-existing limitation, not an OpenSpec upgrade claim.

The source ownership audit passed for all 197 files in the declared source roots.
An initial audit incorrectly included the repository's ignored data/evidence
directory as source and refused those files as designed; the corrected command
selects defaults, skills, docs, scripts, policies, openspec, AGENTS.md and README.md.
No ignored evidence was staged to make the audit pass.

The final structural wrapper gate also passed with both
`--require-project-guidance` and `--require-tasks-complete`: all four artifact
guidance surfaces, both operation surfaces and all five task checkboxes were
observed on OpenSpec 1.14.3. Receipt:
`data/checks/openspec-1143-acceptance/native-readiness.json`.

## Review handoff

[Draft PR #17](https://github.com/JekaMas/agent-workflow/pull/17) is stacked on
[parser PR #16](https://github.com/JekaMas/agent-workflow/pull/16). The three
qualification commits preserve that dependency; later commits record evidence
without changing tested production or test source. Neither PR was merged by
this qualification. Consumer pins and the active personal release are unchanged.

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
