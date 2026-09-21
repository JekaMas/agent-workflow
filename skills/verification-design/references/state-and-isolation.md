# State And Isolation

Use this reference when tests seed state, share resources, start background
work, or depend on time and randomness.

## State Setup

Prefer public APIs and domain events. Direct mutation is invalid when it:

- mutates internals of the unit under test;
- bypasses the production write path in integration or E2E;
- constructs impossible business state outside a recovery or corruption test;
- leaks package, global, or persistent state across tests.

Narrow valid cases are read-only persistence verification after the public
path, deterministic seeding of a fake dependency, explicit corrupted-state
setup for repair or compatibility, and an approved performance setup that does
not replace correctness tests.

When direct setup is necessary, state briefly in the test why it is minimal,
which invariants it bypasses, and what behavior the test still proves.

## Isolation

- Give each test an isolated namespace, schema, data directory, or equivalent
  resource; otherwise provide reliable cleanup.
- Restore environment variables and mutable registries.
- Close files and clients; cancel and join background work.
- Assert cleanup on failure paths when leaked work would affect later tests.

## Determinism

- Do not depend on wall-clock timing, scheduler fairness, map iteration, or
  database enumeration order.
- Inject or control clocks where time is behavior.
- Seed randomness and retain replay data for failures.
- Prefer explicit synchronization and observable state over sleeps.

## Review Questions

- Is the seeded state possible through the production owner?
- Does setup bypass the behavior the test claims to prove?
- Can parallel or repeated execution observe residue?
- Are time, randomness, ordering, and background work controlled?
