# Finding Positive And Negative Properties

Use this before writing generators. The goal is to produce falsifiable
properties from contracts, interfaces, dependencies, and operational risks.

## Contents

- [Definitions](#definitions)
- [Discovery steps](#discovery-steps)
- [Positive property rules](#positive-property-rules)
- [Negative property rules](#negative-property-rules)
- [Security property checklist](#security-property-checklist)
- [Liveness property checklist](#liveness-property-checklist)
- [Derivation heuristics](#derivation-heuristics)
- [Deriving properties](#deriving-properties)
- [Organizing property checks](#organizing-property-checks)
- [Quality gate](#quality-gate)

## Definitions

**Positive property**: required behavior under valid inputs and fair conditions.
It proves the system can make intended progress or produce the intended effect.

**Negative property**: forbidden behavior under invalid, adversarial, stale,
duplicated, failed, reordered, or overloaded events. It proves the system avoids
unsafe effects.

**Safety property**: "nothing bad happens." Example: unauthorized input never
changes protected state.

**Liveness property**: "something good eventually happens" under stated
fairness assumptions. Example: a queued command eventually reaches terminal
state if dependencies eventually succeed and budgets remain available.

**Fairness assumption**: the explicit condition under which liveness is
expected. Never assert liveness without naming dependency recovery, scheduler
ticks, retry budget, and visibility/commit requirements.

## Discovery Steps

1. **Name the boundary.**
   Define the exact method, handler, loop, transaction, queue, worker, or
   protocol boundary under test. List what it may read, write, call, emit, and
   block on.

2. **List observable outcomes.**
   Include state changes, emitted commands, committed rows, returned values,
   metrics, logs, retries, cancellations, and external calls. Properties should
   assert observable outcomes, not private implementation details.

3. **List actors and authority.**
   Identify users, workers, schedulers, peers, dependencies, operators, and
   attackers. For each actor, write what they are allowed and forbidden to do.

4. **List identities and ownership.**
   Define the stable identity for every command/result/entity. Add collision,
   duplicate, wrong-owner, wrong-epoch, and unrelated-identity events.

5. **Sketch the state machine.**
   Write states, terminal states, allowed transitions, forbidden transitions,
   duplicate handling, and stale-event handling. Terminal and authority rules
   usually become negative properties.

6. **Write positive happy-path properties.**
   For each valid command path, state what should eventually happen under fair
   dependency behavior. Include progress deadlines or logical step bounds when
   available.

7. **Invert every precondition into a negative property.**
   For each required dependency, generate the event before the dependency is
   satisfied and assert rejection/no-op/queued-for-later behavior.

8. **Add security properties.**
   Check authorization, authentication, integrity, replay, downgrade,
   confidentiality, isolation, and denial-of-service resistance. Security
   properties are usually negative properties with adversarial event sequences.

9. **Add liveness properties.**
   Define the fair scheduler/dependency assumptions and the progress bound. Add
   separate negative properties for unfair conditions, such as dependency never
   recovers or retry budget is exhausted.

10. **Add resilience and operations properties.**
    Include call budgets, latency bounds, retry/backoff, circuit breaker,
    restart recovery, queue growth, log spam, lock safety, and slow dependency
    isolation.

11. **Define counters and logical latency.**
    Every property involving calls, retries, logs, queues, locks, or latency
    needs fake counters and logical time. Do not depend on wall-clock sleeps.

12. **Define replay evidence.**
    Decide what must be printed on failure: seed, event index, minimized
    sequence, dependency state, model state, SUT state, counters, and logical
    time.

## Positive Property Rules

- Positive properties require valid preconditions and fair dependency behavior.
- Positive properties must name the target effect and visibility boundary.
- Positive properties must not rely on real time; use logical ticks/deadlines.
- Positive properties should include progress bounds when the contract has a
  budget, timeout, block count, retry count, or queue depth.
- A positive property is incomplete if it cannot explain why progress is allowed
  in the generated context.

Template:

```text
Given valid authority, existing identity, committed prerequisite state, and
dependency eventually returns success within budget,
When the generated event sequence includes command -> commit -> delivery ticks,
Then the model and SUT eventually expose terminal success,
And calls/logs/latency stay within declared bounds.
```

## Negative Property Rules

- For every positive precondition, generate at least one sequence where it is
  missing, stale, wrong-owner, duplicated, reordered, or invalid.
- Negative properties must assert both protected state and side effects.
- Negative properties should count forbidden calls, forbidden writes, and
  forbidden logs/metrics when relevant.
- Negative properties must include malformed and semantically invalid inputs.
- A negative property is weak if it only checks returned error and not state,
  calls, queues, metrics, or leakage.

Template:

```text
Given missing authority or stale identity,
When the dependency/result/command event arrives,
Then protected state is unchanged,
And no external command is sent,
And the rejection is counted once with bounded logging.
```

## Security Property Checklist

Turn each row into positive and negative event sequences.

| Area | Positive property | Negative property |
|---|---|---|
| Authorization | Authorized actor can perform allowed action | Unauthorized actor cannot mutate state or trigger external effects |
| Authentication | Valid credential/session is accepted | Missing, expired, malformed, or wrong-epoch credential is rejected |
| Integrity | Signed/hashed/versioned payload applies only if exact | Tampered, downgraded, or mismatched payload is rejected |
| Replay | Duplicate idempotent event is harmless | Replayed old event cannot re-execute side effects |
| Isolation | Actor/entity affects only owned scope | Cross-identity event cannot mutate unrelated state |
| Confidentiality | Error/log exposes only safe metadata | Secrets, payloads, tokens, keys, or private data never appear in logs/errors |
| Availability | Valid workload stays within budgets | Invalid/failing workload cannot create call, log, queue, memory, or lock spam |
| Ordering | Event applies after required predecessor | Out-of-order event cannot create early visibility or unsafe transition |

Security events to generate:

```text
wrong_actor
wrong_owner
wrong_identity
wrong_epoch
wrong_version
replayed_result
tampered_payload
missing_signature
expired_credential
oversized_payload
malformed_payload
dependency_error_with_secret_text
```

## Liveness Property Checklist

Liveness must always state fairness. Use both positive and negative variants.

Positive liveness:

```text
Given work is accepted, scheduler ticks continue, dependency eventually
recovers, retry budget remains, and no terminal failure occurs,
Then the work eventually reaches visible completed/failed/expired state within
the modeled bound.
```

Negative liveness / bounded non-progress:

```text
Given dependency never recovers or retry budget is exhausted,
Then the system does not spin forever,
And calls, retries, queue growth, logs, and latency remain bounded,
And the stalled state is observable.
```

Liveness rules:

- Do not assert "eventually" without a scheduler/tick event.
- Do not assert "eventually" without a dependency recovery or timeout event.
- Define the maximum logical steps, retries, or deadline.
- If progress can be blocked forever by an external dependency, the real
  property is bounded non-progress plus observability.
- Under repeated failure, the system should become more conservative, not more
  aggressive.

## Derivation Heuristics

Use these prompts while reviewing an interface:

```text
What must already be true?
What if that is false?
What must eventually happen?
What can never happen?
What if the event is duplicated?
What if it arrives before commit/finalization?
What if it arrives after terminal state?
What if it belongs to another identity?
What if the dependency is slow, failing, or recovers?
What if the process restarts after each step?
What if the actor is unauthorized?
What if the payload is old, downgraded, malformed, or oversized?
What calls are allowed, and how many?
What latency is allowed, and why?
What state/log/metric proves the system is stuck but safe?
```

## Deriving Properties

Properties come from interface contracts, guarantees, expectations, and
dependency interactions.

Use this mapping:

```text
"must not call X"                  -> forbidden-call counter stays zero
"only after commit/finalization"   -> causality/visibility property
"idempotent"                       -> duplicate event leaves core state equal
"bounded"                          -> call/retry/latency/concurrency budget
"eventually"                       -> progress under fair valid events
"terminal"                         -> monotonicity/no regression
"isolated by identity"             -> unrelated events do not mutate target
"retry with backoff"               -> no tight loop; next attempt after time
"context deadline respected"       -> operation stops at logical deadline
"auth/ownership required"          -> unauthorized event rejected
"local only"                       -> external fake call count remains zero
"cache is optimization"            -> restart with empty cache preserves correctness
```

Every property should name:

```text
Given:
When:
Then:
Forbidden:
Counters:
```

## Organizing Property Checks

Each accepted property must have one named check owner: either a single
function or a small checker type with `Check(...)`. The checker owns the state it
needs and has an explicit comment naming the property, positive behavior,
negative/forbidden behavior, and counters/latency/state inspected. Do not hide
many properties inside one large assertion helper.

For larger property catalogs, keep the test entrypoint/model lean and put each
property checker/holder in its own focused file. Prefer a separate package for
pure model/PBT tests when the test does not need production unexported state.

## Quality Gate

Reject the property set if:

- it has only happy paths;
- it has only safety and no liveness/progress under fair conditions;
- it has liveness but no fairness assumptions;
- it checks return values but not side effects;
- it checks state but not dependency call counters;
- it ignores unauthorized, stale, duplicate, malformed, or reordered events;
- it lacks latency/call-budget properties for external dependencies;
- failure output cannot replay the exact sequence.
