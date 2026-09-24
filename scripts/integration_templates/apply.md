Read `openspec instructions apply --change <name> --json` and its resolved context files. Select the next useful increment, implement, inspect, repair and revalidate. Replan within intent when evidence changes approach. Check tasks only against actual outcomes. Continue until acceptance is supported or a genuine blocker remains; artifact all_done is not product DONE.

For a behavioral change, validate its change-owned `verification.json` evidence
graph before implementation. Select the affected requirement/property/owner/path
closure for this increment. After each edit, run the smallest directly invalidated
case set first and expand only when it passes or exposes a dependency. Reuse prior
green results until a declared invalidation dependency changes. Execute the complete
iteration case set once after the implementation and artifacts stabilize. Confirm
exact observed test identities, not only command exit. Update stale pins or planned
cases honestly; do not omit a failing sibling test or claim unexecuted packages green.

Use `{{checks}}` to select and execute the existing workflow,
specification, language and assurance checks. This operation owns that execution;
the user need not invoke Make or a second skill. Run only relevant authorized checks.

Iteration completion contract (default):

- An increment is green only when every finding in its scope is implemented, its
  requirements carry implemented cases in `verification.json` with no planned
  placeholders left for those requirements, the language and specification checks
  pass on the same revision, and
  `requirement_tests.py run --<iteration selection> --require-clean` reports
  `passed` on a committed revision. Structural results (`validate`, `spec-check`,
  `spec-ready`) never imply implementation; label them structural whenever you
  report them.
- Land a finding as one unit. When its correction spans coupled edits — for
  example a publish-time change plus the transition that completes it — land all
  of them together with their red/green cases, or leave the task unchecked and
  report the finding as blocked with recorded anchors. A subset that leaves the
  new state unreachable is a regression, not progress.
- Resolve and record anchors before editing production: production owner, exact
  hook, durable lineage, evidence keys, and the finalizer or transition that
  completes the change. Do not start a production edit while those are unknown.
- Order of operations: implement -> register the implemented cases -> run the
  iteration selection (dirty is informational only) -> commit the increment ->
  run the same selection with `--require-clean` -> commit the acceptance record.
  A run artifact on a dirty or unknown revision is evidence, never acceptance.
- Check a task box only when its finding's cases are implemented and their
  commands passed in the acceptance run for that revision; otherwise leave it
  unchecked and state the blocker.
