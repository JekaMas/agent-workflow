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
fails open. This must be repaired in PR #16 before either merge. A worker owns
the focused reproduction and correction in an isolated dependency worktree.

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

The guide review and preservation-plan review are in progress. This is subagent
review, not a claim of independent empirical or autonomous-agent acceptance.
