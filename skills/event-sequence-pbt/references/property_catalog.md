# Event-Sequence PBT Property Catalog

Use this catalog to turn contracts and incident risks into falsifiable
properties. Keep property names stable in test names and failure output.

## Contents

- [Template](#template)
- [Core properties](#core-properties)
- [Latency and call-budget properties](#latency-and-call-budget-properties)
- [Resilience, robustness, and recovery](#resilience-robustness-and-recovery)
- [Counter assertions](#counter-assertions)

## Template

```text
Property:
Given:
When:
Then:
Forbidden:
Counters:
Latency:
Replay evidence:
```

## Core Properties

**P01 Determinism**
Given the same initial model state and event sequence, model and SUT produce the
same externally visible result every run.

**P02 Boundary Purity**
A boundary documented as local-only or deterministic-only performs zero calls to
external fakes and zero wall-clock sleeps.

**P03 Causality**
An effect is visible only after the event that makes it visible, such as commit,
finalization, delivery, or ownership transfer.

**P04 Same-Step Non-Visibility**
Results caused by the current step cannot affect that same step unless the
contract explicitly allows re-entrant visibility.

**P05 Identity Binding**
Every result, retry, cancellation, or duplicate is applied only to the exact
entity/request/job identity that caused it.

**P06 Isolation**
Events for one identity cannot mutate another identity, even when names,
versions, or correlation fields collide.

**P07 Terminal Monotonicity**
Terminal state never regresses to an open, pending, retriable, or unknown state.

**P08 Idempotent Replay**
Duplicate committed events, duplicate responses, and duplicate recovery scans do
not create extra effects.

**P09 Stale Event Rejection**
Older epochs, older versions, or older sequence numbers cannot overwrite newer
accepted state.

**P10 Invalid Event Safety**
Invalid dependency order, missing authority, missing ownership, missing entity,
or malformed payload leaves protected state unchanged and records the expected
rejection.

**P11 Progress Under Fairness**
If dependencies eventually return valid responses and budgets are not exhausted,
the modeled operation reaches the required stable state.

**P12 Bounded Non-Progress**
If progress is impossible, retries, queued work, memory, and log volume stay
within configured bounds.

## Latency And Call-Budget Properties

**P13 Latency Proportionality**
System step latency is bounded by local overhead plus the latency of calls that
are explicitly allowed for that step. If the step is local-only, external
latency contribution is zero.

**P14 Parallel Latency Bound**
For independent external calls scheduled in the same logical phase, total phase
latency is bounded by `local_overhead + max(call_latencies)` rather than the sum
of all call latencies.

**P15 Serial Latency Bound**
When calls must be serial, the number and order of serial calls is explicit and
total latency is bounded by `local_overhead + sum(approved_serial_latencies)`.

**P16 Slow Dependency Isolation**
A slow or blocked dependency for one identity does not increase latency for
unrelated identities or local-only boundaries.

**P17 Call Amplification Bound**
Calls per event, per identity, and per logical time window are bounded by a
small contract constant. The bound must be asserted with fake counters.

**P18 Failure Does Not Increase Call Rate**
Retryable failures do not cause a growing number of calls per window. Under
continued failure, call rate stays capped or decreases due to backoff/circuit
state.

**P19 No Spam Logging**
Repeated failure events increment metrics/counters but produce bounded logs,
for example first failure, state transition, and periodic summary only.

**P20 No Thundering Herd**
Recovery, restart, or dependency availability events do not release all pending
work at once unless concurrency and rate limits still hold.

**P21 Deadline Respect**
An operation with a deadline cancels or returns by the modeled deadline and
does not continue mutating state after cancellation.

**P22 Backoff Monotonicity**
Retry delays are nondecreasing or follow the documented policy until reset by a
success, explicit operator action, or new epoch.

**P23 Circuit Breaker Conservatism**
After repeated failures, the system becomes more conservative: fewer calls,
larger delay, degraded mode, or open circuit. It must not become more
aggressive.

## Resilience, Robustness, And Recovery

**P24 Restart Recovery**
After process-local state is lost, committed/persistent state reconstructs the
minimum required model without double-sending effects.

**P25 Gap Detection**
If a stream/session/worker epoch had a possible gap, affected open identities
are marked suspect or scheduled for reconciliation; they are not assumed
terminal or fresh.

**P26 Reconciliation Is Explicit**
Fallback/reconciliation work is observable and bounded. It does not silently
mask the original failed path, and terminal updates record their source.

**P27 Partial Failure Isolation**
Failure in one dependency, worker, identity, or shard does not stop unrelated
healthy work when the contract says they are independent.

**P28 Resource Cleanup**
On cancellation, timeout, restart, or terminal state, timers, leases,
in-flight operations, locks, and queued work are released or retained only if
the contract says so.

**P29 Lock Safety**
No external fake call, blocking wait, or callback into user code occurs while a
critical lock is held. Use fake hooks/counters to detect lock-held calls.

**P30 Queue Growth Bound**
Queues, pending maps, replay buffers, and dedupe sets grow as a function of
active identities or retention windows, not historical event count.

**P31 Observability Completeness**
Every rejected event, retry suppression, fallback, gap, terminal transition,
and circuit-state change increments a metric/counter with stable labels.

**P32 Antifragile Degradation**
After dependency instability, the system may do less work, reduce concurrency,
or rely on safer local state, but it must not widen authority, skip validation,
or bypass commit/visibility rules.

**P33 Compatibility Preservation**
New event handling does not reinterpret old durable state as a stronger state
than it was. Unknown legacy data remains unknown or requires explicit migration.

**P34 Bounded Replay**
Replaying the same sequence or a retained event log after restart does not
exceed idempotency, call, latency, and queue bounds.

## Counter Assertions

Every fake used by these properties should expose at least:

```go
type Counters struct {
    CallsByMethod      map[string]int
    CallsByIdentity    map[string]int
    ForbiddenCalls     int
    RetryAttempts      int
    SuppressedRetries  int
    ActiveOperations   int
    Cancelled          int
    LogsByKind         map[string]int
    LogicalLatencyByMethod map[string]Duration
    LockHeldCalls      int
}
```

Prefer assertions over comments:

```go
require.LessOrEqual(t, c.CallsByMethod["remote.read"], maxReads)
require.Zero(t, c.ForbiddenCalls)
require.LessOrEqual(t, c.LogsByKind["retry_failed"], maxRetryLogs)
require.LessOrEqual(t, phaseLatency, localOverhead+maxExternalLatency)
```
