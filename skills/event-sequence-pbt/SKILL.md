---
name: event-sequence-pbt
description: Design or review stateful sequence properties for retries, recovery and concurrency with independent oracles and replay.
---

# Event-Sequence PBT

This procedure is language-independent. Follow the selected repository workflow
and use its existing property framework. Read `references/language-adapters.md`
when mapping generation, shrinking and replay to a language. No framework install
or mandatory manifest follows from selecting this skill.

## Definitions

**Event**: a domain occurrence that happens at a boundary or as a result of time
passing. An event is not a direct mutation of implementation state.

**Context**: the current modeled world before an event: known entities, current
phase, ownership, logical time, available budgets, dependency health, and
visibility/finality state.

**Dependency**: a causal prerequisite for an event to be valid. Dependencies may
be satisfied or intentionally unsatisfied to test rejection behavior.

**Model/oracle**: a small deterministic reference state machine that applies
events and records expected state, expected calls, rejected invalid events, and
forbidden effects.

**SUT handler**: the code path or seam being tested. It receives the same events
or resulting calls as the model.

**Fake**: a stateful dependency substitute controlled by generated events. It
records calls, logical latency, failures, cancellation, and forbidden calls.

**Mock**: a stricter assertion surface for expected/forbidden calls. Prefer
stateful fakes for event-sequence PBT; use mocks mainly for hard "must not call"
guards.

**Logical time**: model time advanced by events. Use it for deterministic model
properties. Real I/O and scheduling need separately identified integration evidence.

## Core Rule

Generate events in the domain sense: "what happened".

Good events:

```text
request accepted
commit succeeds
commit aborts
network response arrives
dependency times out
stream disconnects
retry budget exhausted
deadline reached
result finalized
next tick observes committed result
```

Bad events:

```text
set cache field to X
insert storage row directly
toggle fresh flag
set retry counter to 3
```

Rows, caches, reducer states, retry counters, projections, and indexes are
derived state. Tests may assert them, but generators should not produce them as
primary events.

Drive the SUT only through its public or test seam. Apply every event to the
model and SUT, assert after every step, and use generated causal events instead
of mutating private setup state. Keep the deterministic model harness free of sleeps and uncontrolled time or
randomness. If the SUT requires real I/O or scheduling, record that boundary and
its replay limits; do not present model determinism as operational evidence.

A required event class counts only when its production-boundary contract is
actually exercised. Declare a typed event disposition before implementation:

- `applied`: the production boundary was reached and the expected mutation was
  committed;
- `observed_no_mutation`: the production boundary was reached and the expected
  idempotent, read, or rejected outcome plus forbidden mutations were asserted;
- `skipped_precondition`: the boundary was not exercised.

The first two dispositions are effective coverage when required by the event
contract. A skipped precondition is never coverage. A label, counter increment,
test-local toggle, or early return does not prove an event. Generate causal
prerequisites and require every declared disposition in the event contract at
least once per run. Use directed witnesses within the run for rare required
cases; do not replace per-run coverage with totals pooled across runs. If invalid placement is part of the property, invoke the
production boundary and assert `observed_no_mutation` instead of silently
skipping it. Do not use one boolean such as `changed` as the sole coverage
classification because it conflates a verified rejection with an unexercised
event.

## Topic Router

Load only the files selected by the current test risk:

- `references/event-modeling.md`: event contracts and types, dependency classes,
  context recognition, and separate model/SUT handlers.
- `references/property_catalog.md`: falsifiable property templates for latency,
  call amplification, retry storms, resilience, robustness, idempotency,
  causality, isolation, and observability.
- `references/property_discovery.md`: steps and rules for finding positive and
  negative properties, including security, liveness, fairness, and system
  resilience properties.
- `references/failure_pattern_map.md`: common incident patterns generalized into
  event-sequence properties and counter assertions.
- `references/fakes-and-generators.md`: event-controlled fakes, counters,
  logical latency, and model-aware generator design.
- `references/language-adapters.md`: language/framework selection and replay limits.
- `references/examples.md`: illustrative Go/Rapid snippets for event definitions, handlers,
  counting fakes, generators, assertions, and replayable failures.
- `references/rapid_recipes.md`: rapid-specific recipes for choosing between
  `MakeCustom`, explicit generators, `Repeat`, state-machine actions, fakes,
  failure replay, and fuzz handoff.
- `references/replay-and-review.md`: full-loop skeleton, failure evidence,
  deterministic regression handoff, and final review rejection criteria.

Every reference is directly routed here. Do not bulk-load them or introduce a
reference-to-reference loading chain.

## PBT Workflow

1. Map changed behavior to affected properties, event changes and selected
   evidence. Record the focused command and broader required scope/owner when
   applicable. Store this in the selected OpenSpec change's specs/design or linked evidence,
   referenced from its authoritative tasks; otherwise use current task evidence.
   Historical PLAN records remain inputs, not another task list.
2. Define properties first. Resolve ambiguity from requirements and owners; ask
   only for consequential decisions while continuing independent authorized work.
3. Define the event vocabulary.
4. Define dependencies, invalid-event behavior, and required typed event
   dispositions for each event.
5. Trace important model facts to independent expectations and SUT observations.
   For complex models, a compact table can use:
   `required fact | independent model field | model transition | SUT observation |
   comparison | forbidden SUT-derived expectation`. Every required checkpoint,
   generation, write-count, demand, retention, cache, identity, timestamp, and
   lifecycle fact needs an explained independent comparison when applicable.
6. Build the reference model/oracle. Do not derive expected values from SUT
   flags, helper results, counters, generation tokens, or storage reads.
7. Build fakes with counters and logical latency.
8. Generate deterministic event sequences with the affected language's existing
   property mechanism. Select language details through
   `references/language-adapters.md`; framework capabilities are not assumed.
9. Apply every event to model and SUT.
10. Assert properties after every event, not only at the end.
11. On failure, report seed, event index, minimized event sequence, model state,
   SUT state, counters, logical time, and dependency chain.

Create a new event only for a new reachable domain occurrence or a changed
causal/rejection contract. Create or amend a property only for a changed
invariant, fairness assumption, bound, ordering rule, liveness expectation, or
forbidden effect. Do not add an event merely because implementation gains a
field, helper, cache, row, or internal state transition.

Run the smallest affected property selector during implementation. Broaden checks
when shared event vocabulary, oracle, harness or production semantics invalidate
other evidence. Keep required checks distinct from optional exploratory campaigns.
A short suite that skips a required property does not satisfy it; retain a documented
local selection and report actual execution, failure, skip and replay evidence.

The focused PBT must programmatically assert its typed-disposition matrix and
independent model coverage: every required fact maps to an independent model
field/transition, an actual SUT observation and a comparison. A compact in-memory
map or existing harness assertions are sufficient; no new manifest is required.
Do not start the full PBT while a required disposition is zero, a required event
is covered only by `skipped_precondition`, or a required model fact lacks an
independent oracle. Repair the harness and rerun the focused selector first.
Retain the observed assertions and replay evidence in the current change.
Isolate measurement-sensitive checks from competing load and retain minimized
regressions rather than repeatedly rerunning an unchanged expensive campaign.

## Closure Gate

Do not accept the PBT until:

- positive properties name their fairness assumptions and negative properties
  cover missing, stale, unauthorized, duplicate, malformed, and reordered input;
- event dependencies and invalid-event behavior are explicit;
- in each run, every required event class has every nonzero `applied` or
  `observed_no_mutation` disposition named by its declared contract;
  `skipped_precondition`, silent no-op events, and test-local state substitution
  do not satisfy the matrix;
- evidence maps every required fact to a model
  field and transition, a production observation, and a comparison without a
  SUT-derived oracle;
- fakes prove call, retry, log, queue, lock, and logical-latency bounds without
  real IO, sleeps, or wall-clock time;
- the model and SUT are compared after every event through the boundary under
  test; and
- a failure is replayable from its seed and minimized event sequence, with a
  deterministic regression test retained for every confirmed bug.

For changes to existing state/property suites, use `references/change-impact.md` to map invalidated coverage and its verification owner.
