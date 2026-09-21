---
name: verification-design
description: Design or review consequential properties, test oracles, coverage, falsification and test-set evidence.
---

# Verification design

Read the selected requirements and actual owner/boundaries, then the relevant
section of `references/verification.md`. Match existing properties and tests before
adding coverage. Consumer policy owns protected actions and required acceptance.
Return findings/evidence to the current change; no separate task list or role is
created. Routine text edits need proportionate inspection, not a test matrix.

For specification review, implementation review or feedback resolution, use
`references/review-modes.md`. For an actual implementation-proof obligation or
proof-guided increment, use `references/implementation-proof.md`. Neither route
loads for routine text inspection.

## Conditional implementation and testing detail

- `references/behavior-and-boundaries.md`: select the actual owner/boundary and meaningful negative checks.
- `references/state-and-isolation.md`: setup, cleanup, clocks and resource isolation.
- `references/fuzz-and-properties.md`: input domains, generators and preserved counterexamples.
- `references/execution-scheduling.md`: dependent or expensive test sets; no new acceptance gate.
- `references/local-verification.md`: language, recovery, UI, concurrency and performance risk matrix.
- `references/architecture-and-contracts.md`: ownership, interactions, storage growth and resource contracts.
- `references/test-boundaries.md`: substituted-owner claims and proportionate evidence records.

Load only the reference needed by the current question. Consumer policies own
actual command selection and campaign requirements. These references are part of
the same implementation/review/repair loop; they do not impose a separate handoff.

For implementation inspection use `references/code-inspection.md`; consumer adapters supply domain contracts and exact evidence gates.
