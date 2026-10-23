# Review and rollout follow-up — 2026-10-23

The user authorized a separate spec-update guide, implementation and guide
review with subagents, preparation/merge of PR #17 and its dependency, and
updating the existing installed personal workflow. Tasks.md group 2 remains the
only checklist. Product consumer migrations are separate.

## Subagent review

The implementation/evidence reviewer inspected main through `838db02`, including
the parser dependency and actual retained observations. It confirmed the prior
171 suite outcomes, eleven current upgrade edges and sixty legacy identities,
with the documented Make and multiline-description observation limits.

It found one P2: after an earlier specs observation passes, an OSError reading a
later OpenSpec stdout artifact can leave the report marked passed. The exception
handler records only a reason. The missing guidance/task response therefore
fails open. The worker reproduced both missing-guidance and permission-denied task
paths as false greens, then repaired PR #16's artifact-read branch. The failed
step and report now record `artifact_read_failed`, preserve reason/path and return
nonzero without preview fallback. Its two new cases and four affected large-output
cases passed (6/6). The implementation reviewer rechecked the fix and results and
found no remaining blocker.

The separate guide reviewer found two P2 documentation issues: distinguish the
ADDED/main-spec 500-character warnings from inherited MODIFIED preservation, and
inspect Git diffs under the selected planning store's actual owner. The author
repaired both; reinspection against the installed 1.14.3 sources found no remaining
guide blocker. Both client entrypoint links resolve to the separate guide.

Changing that production artifact-read owner invalidates the affected wrapper
and native guidance/task observations. New regression assertions and test-source
changes invalidate their fingerprint-bound edges. Revalidate those affected
cases/closures on the stabilized fix; retain unrelated policy, source-audit,
model-review and direct archive observations unless their own inputs change.
Documentation, task progress and merge commits alone do not invalidate behavior.

## Personal-update preview refusal

The normal personal preview refused modified managed instructions. Inspection
confirmed that the installed release has two locally edited default files: one
contains personal Context guidance, the other the user's green-evidence reuse
rules. Their symlink targets still match the installer record; their content
hashes differ. The committed default bytes match the recorded hashes. This is
confirmed content drift, not a broken link or a reason to overwrite state hashes.

The exact customized files, patch, original state and symlink mappings were
captured in a private protected pre-reconciliation backup. No instruction file
or active pointer was changed by that capture. Do not publish backup contents or
machine-specific instructions with the shared source.

The proposed preservation route is a clean private local overlay commit based on
the exact reviewed merged upstream revision. It retains the two local additions
as tracked source, without pushing them publicly. Only after preservation is
verified may the old two managed files be normalized to their recorded committed
bytes and the ordinary installer preview/apply run. Any failed activation restores
the captured content, state and links. Record both the private pre-reconciliation
backup and the installer's normal rollback backup. Verify merged ancestry, clean
tracked active source, exact instruction bytes, links and native compatibility.

The preservation-plan reviewer confirmed the two local additions are appended to
unchanged committed defaults, all eleven managed links match, and the backup/
private-overlay route respects the installer's checks. Rollback must restore the
entire captured pointer/link/content/state tuple after a partial installer failure,
not only the current pointer. The standard install backup will contain normalized
old bytes; retain the separate pre-reconciliation backup of customized bytes.

## Integrated conflict resolution and revalidation

The receiving upgrade head `93f0a2c` and incoming parser repair `af8f49b` have
three interacting conflicts: test fixtures, graph bindings and appended progress
notes. Keep the upgrade's exact 1.14.3 policy plus unknown-version rejection, the
repair's missing/unreadable-artifact cases and full-artifact handling, and both
sets of progress notes. The controlled large-artifact fixture reads the selected
module version; the actual native-version gate remains an independent oracle.
An AST comparison confirms every test method from both sides survives unchanged.
The existing graph now has 62 edges; the upgrade graph includes the two explicit
read-error cases for 13 edges. Current test-source fingerprints were calculated
once after the combined source stabilized.

The changed artifact-read owner, merged version fixture and new assertions
invalidate the wrapper/native graph closure. Re-execute that complete closure on
clean integrated source. The lifecycle incomplete-task refusal also calls this
wrapper and needs an affected recheck. Other preserved policy/audit/model/direct
archive cases retain their original receipts. The appended documentation requires
link and semantic review; it does not invalidate those behavior cases.

These are subagent reviews, not claims of independent empirical or autonomous-
agent acceptance. Final merge and installed-runtime observations follow below.

## Final reviewed source and retained evidence

The integrated source at `1e3374109011e66dfa2a087228b00023e4cb1c3d` passed the
complete 13-edge upgrade graph with `--all --require-clean`. Its receipt is
`data/checks/openspec-1143-reviewed-readfix/result.json`. The native logs report
35 consumer/bootstrap, 15 native OpenSpec and 88 unit cases passing, without
skips. All 62 legacy graph identities have exact passing observations and
matching current source fingerprints. The existing multiline-description
observer limitation still requires one unregistered unit identity to be
reconciled against its explicit native `... ok` and suite summary; no registered
edge is missing.

The one wrapper-dependent lifecycle refusal passed its affected recheck in
`data/checks/openspec-1143-reviewed-lifecycle/result.json`. The other 34
preservation cases retain their valid original observations. This accounts for
173 unique passing suite cases: 139 current executions plus 34 retained results.
The aggregate `make check` recipe was not rerun; its required set is reconciled
from these observations rather than duplicating valid greens.

The structural-guidance receipt alongside the reviewed graph covers all four
artifact and both operation guidance surfaces. It does not request or claim
completed follow-up tasks. Native strict validation freshly passes this change
and the legacy evidence-graph change; seven other unchanged item observations
remain valid, reconciling all nine native items. Source ownership passes for
199 declared source files. Conflict-resolution syntax and whitespace checks
also pass. These source/evidence inspections do not establish installed-runtime
discovery or product behavior.

The final implementation/evidence subagent reinspection found no remaining merge
blocker at that integrated source. The separate guide reinspection also found
no blocker after its two P2 repairs. Later progress-only commits preserve these
receipts and their original revisions; they do not refresh evidence fingerprints
or cause another behavior-suite run.

## Merged source and personal activation

[Parser PR #16](https://github.com/JekaMas/agent-workflow/pull/16) merged the
exact reviewed head `af8f49bb16fcb4293df2669760cc1ed17bbce39f` as
`0d159f404dd6fa4af3837367498d0605ba6ec84d`. After retargeting to main,
[upgrade/guide PR #17](https://github.com/JekaMas/agent-workflow/pull/17) merged
the exact final head `5db007119c9b8ac9208de4c0f55938a535c4913c` as
`aa105e2d150e89b89e1ea9e6d5b27c798c663fa0`. Both used merge commits and
exact-head protection, with clean mergeability and passing hosted CodeRabbit
status. GitHub records no human reviews; the subagent findings and reinspection
above are the actual source-review evidence. No administrative bypass was used.
The merged tree exactly equals the final upgrade head; only progress/evidence
documents differ from the integrated behavior-test commit.

The concrete activation helper and captured state received a read-only subagent
review before execution, with no blocker for the single-writer invocation. Its
rollback covers the captured customized files, active pointer, all eleven links
and original installer state. Rollback was inspected, not executed as a failure
experiment.

The ordinary installer preview and apply then succeeded from a clean private
overlay of merged source `aa105e2`. The active private Git revision is
`f8e7ba481bf356600925e01936d7e9f3f1ac0084`; ancestry and a clean tracked
checkout are verified. The only overlay differences are the two preserved local
default instruction files. Their content is byte-for-byte equal to the captured
customized files, all eleven managed links match, and normal installer ownership
hashes match the installed content. The private source's push URL is disabled.
The pre-reconciliation preservation packet and ordinary installer rollback backup
remain private and are both recorded in the local activation receipt. No private
instruction text, state file or backup contents are published with this change.

Activation changes the installed source owner and resolved entrypoints. Those
inputs require installed-owner/native checks; they do not invalidate the 173
retained behavior observations. The actual installed source audit passes for
199 declared source files and personal entrypoints in
`data/checks/openspec-1143-personal-source-audit.json`. Its OpenSpec wrapper also
passes this change's strict validation and all four artifact/two operation
guidance surfaces in `data/checks/openspec-1143-personal-native.json`.
`openspec --version` and the global npm inventory both report exact 1.14.3.
These observations establish installed ownership and native spec-driven
compatibility, not client-cache refresh or product-runtime acceptance.

Tasks 2.3 and 2.4 are checked only after those actual outcomes. Their changed
checkbox content requires a final completed-task gate; unchanged guidance and
behavior suites retain their prior receipts. Product consumers, their workflow
pins and their specifications remain outside this rollout. The separate
[spec-update guide](../../../docs/updating-specs.md) owns their future procedure.

The installed wrapper's final `--require-tasks-complete` gate passed after the
actual outcomes were checked: nine tasks complete, zero remaining, with strict
change validation also passing. Receipt:
`data/checks/openspec-1143-personal-completed-tasks.json`. Only task/evidence
records changed for that gate; it did not repeat the guidance or behavior suites.
The native checkbox result is reconciled with the source reviews and actual
activation observations above, rather than treated as standalone acceptance.
