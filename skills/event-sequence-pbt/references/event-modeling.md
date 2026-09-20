# Event, Dependency, And Model Design

## Contents

- [Event contract](#event-contract)
- [Event types](#event-types)
- [Dependency types](#dependency-types)
- [Context recognition](#context-recognition)
- [Model and SUT handlers](#model-and-sut-handlers)

## Event Contract

Every event kind must define:

```text
Name:
Actor/source:
Context:
Dependencies:
Payload:
Time effect:
Model transition:
SUT handler/action:
Expected dependency calls:
Forbidden side effects:
Counters/latency:
Properties touched:
```

Keep event payloads domain-level. If an event needs implementation-specific
fields, either the event is too low-level or the domain vocabulary is missing a
concept.

## Event Types

Use these categories to find missing events.

### 1. Command / Intent Events

Something requests work.

```text
user_submits_request
strategy_emits_intent
service_enqueues_command
scheduler_starts_task
worker_picks_job
```

Dependencies usually include authority, ownership, existing entity, phase, and
budget.

### 2. Transaction / Commit / Visibility Events

Something crosses a deterministic boundary.

```text
transaction_begins
commit_succeeds
commit_aborts
result_finalized
state_becomes_visible
next_tick_observes_visible_state
```

Dependencies usually include prepared input, current transaction, finalization,
and ordering.

### 3. External Dependency Events

An external service, network, DB, filesystem, clock, queue, or worker responds
or fails.

```text
dependency_available
dependency_unavailable
dependency_returns_value
dependency_returns_retryable_error
dependency_returns_fatal_error
dependency_times_out
dependency_cancels
dependency_disconnects
```

Dependencies usually include an earlier request/call and active dependency
state.

### 4. Time / Scheduler Events

Logical time moves.

```text
time_advances
deadline_reached
backoff_elapsed
rate_limit_window_resets
operation_completes_after_latency
```

Dependencies usually include scheduled deadlines, timers, or outstanding work.

### 5. Retry / Backoff / Budget Events

The system decides whether work may repeat.

```text
retry_due
retry_suppressed_by_backoff
budget_available
budget_exhausted
max_attempts_reached
```

Dependencies usually include previous failures, logical time, and configured
limits.

### 6. Concurrency / Ordering Events

Work overlaps or resolves in different orders.

```text
operation_starts
operation_completes
operation_cancelled
duplicate_event_arrives
older_event_arrives_after_newer
unrelated_entity_event_arrives
```

Dependencies usually include active operation count, identity, and isolation
rules.

### 7. Recovery / Restart Events

Process-local state is lost or rebuilt.

```text
process_restarts
cache_empty_after_restart
persistent_state_reloaded
worker_resumes
```

Dependencies usually include persisted or derivable state.

### 8. Configuration / Authority Events

Authority or configuration changes.

```text
credentials_rotated
permission_revoked
config_changed
feature_disabled
owner_changed
```

Dependencies usually include actor identity, generation/version, and ownership.

## Dependency Types

Recognize dependencies explicitly. Common dependency classes:

```text
existence:       entity/request/job exists
ordering:        event B requires event A first
state:           entity is in a specific phase/status
time:            logical_now >= deadline/backoff_until
budget:          tokens/concurrency/retry attempts available
authority:       caller/source is allowed
ownership:       actor owns the entity/session/job
visibility:      value is committed/finalized/observable
identity:        result is bound to exact request/job identity
isolation:       unrelated entity must not be affected
availability:    dependency is up/down/degraded
idempotency:     duplicate key already seen
```

For each dependency, define invalid-event behavior:

```text
reject without mutation
ignore as duplicate
record violation
schedule retry
mark stale/unknown
fail the property if SUT allowed forbidden side effect
```

## Context Recognition

Before writing generators, inspect the interfaces, services, and dependency
contracts and classify their contexts:

```text
Who can call this?
What entity identity does it act on?
What must already exist?
What phase/status is required?
Is the effect local, external, committed, visible, or speculative?
Can it block?
Can it retry?
What budget or deadline applies?
What is idempotent?
What must never happen?
```

Turn each answer into event dependencies and properties.

## Model And SUT Handlers

Use separate handlers for the model and the SUT.

Model handler:

```text
Apply(event) -> step_result
step_result:
  accepted | rejected | duplicate | violation
  disposition: applied | observed_no_mutation | skipped_precondition
  state changes
  expected calls
  expected counters
  expected emitted events/candidates
```

`accepted | rejected | duplicate | violation` is the domain result.
`applied | observed_no_mutation | skipped_precondition` is the coverage
disposition. Keep them separate: a rejected or duplicate event can be effective
`observed_no_mutation` coverage after a real boundary call, while an early skip
is not coverage.

SUT handler:

```text
Apply(event):
  drives public/test seam only
  configures fakes for dependency outcomes
  invokes the relevant method/tick/handler
  records actual state and counters
```

Do not let the test mutate private SUT internals to "make the next event work".
If setup needs state, generate the causal event that creates it.
