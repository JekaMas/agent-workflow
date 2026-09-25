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

- The completion unit is the **full iteration**, not a finding, increment or
  milestone. An iteration is complete only when **every** finding in it is
  implemented, every one of its tasks is checked against implemented cases, its
  requirements carry no planned placeholders, `requirement_tests.py run
  --<iteration selection> --require-clean` reports `passed` on a committed
  revision, and the language, specification and required preservation checks pass
  on that same revision. A single finding landed, a passing focused gate, a
  committed increment or a subset of the iteration is not an iteration result and
  must not be reported as one.
- Work the iteration's findings through to that verified result in the same run:
  after each finding, continue to the next one instead of summarising. Structural
  results (`validate`, `spec-check`, `spec-ready`) never imply implementation;
  label them structural whenever you report them.
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
- Apply stops at exactly three points, and nowhere else: (1) **a spec change is
  needed** - the finding cannot be satisfied without changing the approved
  specification, so the user must decide; (2) **an absolute implementation
  blocker** the agent cannot resolve - missing authority, credentials or
  dependency, a protected/external operation, or mutually exclusive
  requirements; (3) **the iteration is finished** - 100% implemented, every
  check green, and `requirement_tests.py run --<iteration selection>
  --require-clean` passed on a committed revision. An agent turn boundary, a
  compacted or restarted thread, context exhaustion or a truncated response, a
  prediction of truncation or of any other condition here, effort, elapsed time,
  a long run, a landed milestone, or an unfinished increment is none of these.
  Checkpoint each step so a ceiling is resumable, then resume from the change's
  recorded checkpoint and keep applying; the ceiling is a reason to checkpoint
  and keep steps small, never a reason to stop.
- A finding that is aligned with the specification and needs no spec change is
  never a stop. Record it in the iteration's task list and apply it in the same
  run; do not hand findings back for a decision that the spec already answers.
- Your own context, working memory or effort is never a blocker and never a
  reason to defer, hand off, pause or ask for a decision answered by the spec,
  design or tasks. When those already state the behaviour and its tests, implement
  them; do not substitute a plan, a proposal or a partial landing for the work.
- A status report, progress update or partial-result summary is never the end of
  an operation: continue with the next authorized action and report only at the
  iteration's verified result or at one of the three stops above.
- Progress belongs in intermediate updates during the run. The operation's final
  message is what ends the agent turn, so emit it only at the iteration's verified
  result or at one of the three stops above - never as a progress report, and
  never because a finding, commit or gate just landed while iteration work
  remains.
- A real blocker means stop (1) or stop (2) above, with a recorded witness and the
  exact unblock action. Nothing else - including a hard finding, a red gate, a long
  repair or a shared/dirty checkout - qualifies; record it as a task and continue.
