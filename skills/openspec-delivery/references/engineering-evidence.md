# Engineering evidence

Read for generated source, concurrent review snapshots, long-running checks or evidence checkpoints. These procedures add no authority or required parallelism.

## Review snapshots and generated outputs

Reviewers assigned concurrently must inspect the same identified semantic
snapshot. Keep that snapshot read-only until their results are collected; a
single writer consolidates overlapping changes. Explicitly isolated disjoint work
can continue. This is a consistency boundary, not a mandatory multi-reviewer phase
or permission to spawn agents. Use the shared verification-design procedure for the review/repair
loop and required evidence.

Run an affected canonical generator when its relevant inputs change or when a
required regeneration check calls for it. Reuse unchanged generated artifacts
across isolated cases. Inspect generated output against its source before relying
on it; verifier tests must not regenerate it merely to chase hashes or hide drift.
If a diagnostic or correction changes inputs, rerun the affected generator and
invalidated checks as needed.

## Evidence checkpoints

The selected OpenSpec tasks/specs/design remain current during investigation and
repair. Batch source/fixture fingerprints at useful verification, pause or handoff
boundaries; do not refresh them after every edit. Record exact relevant inputs
before citing final evidence. A later semantic change invalidates affected proof;
formatting-only changes may reuse results only after explicit dependency review.
No fixed checkpoint count, committed-tree prerequisite or upstream role handoff
applies. Continue required repair and revalidation until acceptance is satisfied.

## Operational diagnostics

- Seek status only when it can change the next action. Use native passive waits
  for running commands; do not busy-poll, duplicate monitors or use probes merely
  for reassurance. Bound waits by tool limits and the task's actual budget.
- Choose diagnostic/status timing from expected phase duration and declared
  readiness, heartbeat or timeout boundaries. Follow an applicable runbook's
  cadence. After unchanged results back off. A concrete crash, missed deadline,
  hang indication or explicit diagnostic request justifies focused inspection;
  arbitrary minimum delays must not hide actionable failure evidence.
- Routine status returns bounded completion/readiness/progress information.
  Broader logs or process evidence need a concrete diagnostic question.
- Capture noisy commands to artifacts. Do not stream unbounded raw logs into
  agent context. Inspect targeted filters, grouped summaries or small bounded
  tails, and retain relevant failed as well as successful evidence.
- Filter live sources at the source or first processing step, with a narrow time
  window and explicit patterns. Avoid broad raw log acquisition followed by
  after-the-fact filtering into a large context dump.
- Process large structured data incrementally when eager loading could exhaust
  memory. Programmatic streaming is useful; raw records are not a progress feed.
- Never put secrets or unbounded output into tasks, evidence summaries or chat.
  Link the artifact and record a concise result with its access/retention limits.
