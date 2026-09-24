Read `openspec instructions apply --change <name> --json` and its resolved context files. Select the next useful increment, implement, inspect, repair and revalidate. Replan within intent when evidence changes approach. Check tasks only against actual outcomes. Continue until one of the three stop conditions below holds; artifact all_done is not product DONE.

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
- Apply continues until one of exactly three conditions holds, and no others:
  (1) a direct contradiction inside the specification or requirements; (2) a
  spec/artifact state that cannot be repaired in scope; (3) an absolute need for
  a user decision that the artifacts cannot answer (missing authority, mutually
  exclusive requirements, or a protected/external operation). An agent turn
  boundary, a compacted or restarted thread, a long run, or an unfinished
  increment is none of these: resume from the change's recorded checkpoint and
  keep applying in the next turn, reporting progress rather than declaring a
  stop.
- Your own context, working memory or effort is never a blocker and never a
  reason to defer, hand off, pause or ask for a decision answered by the spec,
  design or tasks. When those already state the behaviour and its tests, implement
  them; do not substitute a plan, a proposal or a partial landing for the work.
