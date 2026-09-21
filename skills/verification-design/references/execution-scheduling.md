## Batched Execution

Map required evidence to its owner. For several interacting or expensive test
sets, use a scheduling table only when it clarifies dependencies or isolation:

| Wave | Proof IDs | Commands/packages | Invalidated by | Parallel group | Serialization reason |
|---|---|---|---|---|---|

For a correction, start the command registry empty and rebuild it from the
current delta. Every command needs a current authorization edge: open finding,
invalidated preservation proof, mandatory final gate, or conditional recovery.
Historical registries are evidence, not execution defaults. Keep mutating repair
commands outside the normal proof list; run one only when a current diagnostic
triggers it and the task explicitly authorizes its scope.

Use these rules:

- Start with the cheapest useful discriminator when the cause or oracle is
  uncertain. Batch already-understood independent cases when that saves setup;
  do not postpone informative feedback until every case is authored.
- Combine overlapping names in one anchored package command. Launch independent commands concurrently by default when task authority, resources and
  measurement isolation permit; retain each command's bounded output and exit.
- Inspect the whole wave, classify every failure, and fix all independent
  confirmed owners before affected revalidation. Rerun a command when its inputs
  changed or a specific diagnostic/reliability question requires repetition;
  preserve the initial failure and do not retry unchanged merely to get green.
- A failure in one package does not invalidate green results from independent
  packages. Link those still-valid results in the existing change evidence.
- Run required benchmarks as a batch only after correctness and ownership are
  stable. Comparable baseline/candidate distributions, profiles, and DB-scale
  measurements remain serialized and isolated so parallel load cannot corrupt
  the comparison; unrelated non-comparative benchmark smoke commands may run
  concurrently.
- Prefer focused checks during development. Run a broader lint/build/test check
  earlier when a concrete dependency, build or integration question requires it;
  do not impose a final-only phase gate. Preserve required final aggregate checks
  and reuse results only when their relevant inputs and semantics remain valid.
- Run required properties through their selected commands. A fast suite that
  skips those properties cannot replace them; preserve both obligations when assigned.

This changes scheduling, not proof strength. Every required property and
negative case remains mandatory even when several are covered by one command.
