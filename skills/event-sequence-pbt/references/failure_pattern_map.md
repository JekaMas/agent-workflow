# Failure Pattern Map

Use this file to convert past or expected incidents into generic
event-sequence properties. Keep the generated tests domain-specific, but keep
the pattern name generic.

| # | Failure pattern | Event sequence to generate | Properties |
|---|---|---|---|
| 1 | Live external IO in a block/local boundary increases step latency | open work exists -> local boundary runs -> external fake is slow | P02, P13, P16 |
| 2 | Per-tick polling of open work creates latency proportional to active work | many open identities -> tick repeats -> dependency responds slowly | P17, P18, P30 |
| 3 | Broad list endpoint is called every tick instead of targeted/bounded work | two or more active identities -> tick -> list-all fake called | P17, P20, P30 |
| 4 | Credential or secret-provider failure spams calls/logs | auth dependency fails repeatedly -> retry windows advance | P18, P19, P22, P23 |
| 5 | Stream/session creation failure loops without bounded reconnect policy | create session fails -> time advances -> retry attempts | P18, P20, P22 |
| 6 | Private event decode/apply failure is swallowed | malformed external event arrives -> handler returns error | P10, P25, P31 |
| 7 | Fallback masks the primary failure path | stream gap occurs -> fallback succeeds -> no trace of gap/error remains | P25, P26, P31 |
| 8 | Process-local cache is treated as canonical truth | cache contains stale open state -> durable result says terminal | P03, P07, P24 |
| 9 | Terminal result arrives late but is never projected | accepted request -> terminal external result -> many ticks | P07, P11, P31 |
| 10 | Submission/acceptance is confused with completion | create request accepted -> no terminal result -> UI/projection checks status | P03, P04, P07 |
| 11 | Optional debug/file side effect aborts critical path | critical command succeeds -> optional side effect fails | P10, P27, P32 |
| 12 | Migration/startup work gives no progress or blocks indefinitely | large retained state -> migration batches -> failure/restart | P12, P19, P24, P30 |
| 13 | Mixed storage access paths corrupt or hide state under restart | writer commits -> alternate reader observes while restarting | P03, P24, P33 |
| 14 | Concurrent map/state access races under peer/worker activity | two workers process related events -> interleaved reads/writes | P06, P29 |
| 15 | Freshness uses the wrong clock/domain | external snapshot update -> local tick advances -> freshness check runs | P03, P10, P25 |
| 16 | Indicator price/metric is used as executable bound | quote signal exists -> execution command generated | P10, P32 |
| 17 | Lifecycle cardinality is conflated with execution policy | one-shot lifecycle event -> order/command policy selected | P10, P32 |
| 18 | Sentinel/normalization ambiguity changes status meaning | empty/sentinel identity/status arrives -> normalization path runs | P05, P10, P33 |
| 19 | Speculative result becomes visible before commit | speculative read returns -> commit aborts -> next tick observes state | P03, P04, P05 |
| 20 | Post-terminal balance/status refresh performs live IO in local projection | terminal result committed -> local projection runs -> balance fake slow | P02, P13, P26 |

## How To Use

1. Pick the failure pattern closest to the risk.
2. Rewrite the event sequence in the feature's domain vocabulary.
3. Add counters and logical latency to every fake named by the pattern.
4. Assert the listed properties after every event.
5. Add a minimized regression sequence if the property finds a real bug.

## Example Conversion

Pattern 4 becomes a domain-specific generator like:

```text
credential_provider_unavailable
command_needs_credentials
time_advances_less_than_backoff
retry_attempted
time_advances_to_backoff
retry_attempted
credential_provider_recovers
retry_succeeds
```

Assertions:

```text
calls_per_window <= configured_limit
logs_per_window <= configured_limit
backoff_until never moves backwards under failures
success resets the failure circuit only after an accepted response
```
