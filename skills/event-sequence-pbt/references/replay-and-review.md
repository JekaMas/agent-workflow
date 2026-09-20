# Replay And Review

## Contents

- [Sequence execution](#sequence-execution)
- [Scenario replay](#scenario-replay)
- [Review checklist](#review-checklist)

## Sequence execution

```text
initialize independent model and SUT adapter
for each generated domain event:
    apply to model and SUT through the selected boundary
    compare state projections, outcomes and forbidden effects
    record disposition and replay context
minimize any failure while preserving its causal or rejection contract
```

## Scenario Replay

A failing run must be reproducible without rerunning the generator blindly.
Failure output should include:

```text
seed
event_count
failing_event_index
full or minimized event sequence
dependency states at failure
logical time at failure
model state summary
SUT state summary
counters and logical latency summary
```

The minimized event sequence should become a regression test when it describes a
real bug.

## Review Checklist

Reject the PBT if:

- properties are vague or missing;
- events are implementation mutations instead of things that happened;
- dependencies are implicit or undocumented;
- invalid event ordering is not generated or checked;
- fakes lack counters/logical latency;
- a claimed deterministic model test performs uncontrolled real IO, sleeps, or
  depends on wall-clock time; qualify real integration behavior separately;
- assertions only happen at the end;
- generated events bypass the boundary under test;
- failure output cannot replay the scenario.
