---
name: conflict-resolution
description: Resolve merge, rebase or cherry-pick conflicts while preserving both sides’ intended behavior.
---

# Semantic conflict resolution

Use for an actual conflict or an explicitly requested resolution plan. Inspect Git state and preserve unrelated work; do not reset, stash or discard it. Conflict resolution does not authorize starting a merge/rebase, changing accepted contracts, continuing an operation, publishing or force-pushing beyond the task.

## Side definitions


Define the sides for the current operation before editing:

Record the semantic source branches/commits and their exact revisions separately
from Git's conflict-side labels. Inspect the operation and index stages before
choosing a side:

- During a merge or cherry-pick, `ours` (stage 2) is the current receiving side
  and `theirs` (stage 3) is the incoming side.
- During a rebase, `ours` (stage 2) is the upstream plus commits already replayed;
  `theirs` (stage 3) is the work being replayed. Do not equate `ours` with the
  original feature branch.
- `base` is the stage-1 ancestor for the conflicted path; verify it rather than
  assuming the operation's branch merge base is the file's exact three-way base.

Use exact commit and stage identities in behavior comparisons. Do not hard-code
branch names or choose `--ours`/`--theirs` from a conversational side label.

## Resolve by behavior

Inventory unresolved paths with `git status --short` and `git diff --name-only --diff-filter=U`. Group interacting conflicts by behavior/owner. Inspect stage blobs, relevant tests/contracts, introducing history and each side's changes from the actual base. Record intended behavior from both sides, explicit removals and how the result combines or supersedes them.

Resolve dependencies in a useful order; no fixed top-down file sequence. Do not pick a whole side without evidence that it subsumes the other intent. For generated artifacts resolve canonical inputs first, regenerate through the existing command and inspect semantic output. Do not hand-edit generated output to conceal disagreement.

Run focused checks for both retained behaviors and their interactions, plus applicable diff/generated-source checks. Missing prerequisites and unresolved product choices remain explicit blockers; continue independent authorized conflicts. Full-stack execution and protected mutations follow consumer authority, never this skill. Before authorized continuation inspect the staged resolution and remaining conflicts; do not hide discarded behavior behind syntactic conflict removal.

Report resolved families, behavior decisions and supporting history/tests, observed results, remaining conflicts and exact unblock actions. Return to the same implementation/review flow; clean conflict markers alone are not task completion.
