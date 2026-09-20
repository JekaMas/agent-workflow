# Fakes And Generator Design

## Contents

- [Fakes and mocks](#fakes-and-mocks)
- [Generator design](#generator-design)

## Fakes And Mocks

Use fakes for dependencies that can be called by the SUT:

```text
network/API fake
clock fake
database fake
filesystem fake
queue/bus fake
credential/auth fake
worker pool fake
finalization/commit source fake
```

Each fake should record:

```text
calls by method/endpoint
logical latency by method/endpoint
active operations
cancellations
retry attempts
backoff decisions
forbidden-call attempts
direct mutation attempts
lock-held external call attempts
```

Each fake should be event-controlled:

```text
next call returns value
next call returns retryable error
next call returns fatal error
next call blocks until logical timeout
dependency unavailable
dependency recovers
```

Do not use wall-clock sleeps. Advance logical time with events.

## Generator Design

Use the affected language's existing property framework. Prefer model-aware
generators that draw both valid events and intentional invalid attempts:

```text
choices = valid_next_events(model) + invalid_attempts_to_test(model)
event = draw(choices, reproducible_random_source)
```

Keep the generation model independent of SUT state. Language-specific syntax
belongs in the selected adapter, not the oracle contract.

Generation guidelines:

- Generate identities from small pools to force collisions, duplicates, and
  unrelated-entity events.
- Generate valid events often enough to make progress.
- Generate invalid dependency orderings intentionally.
- Generate duplicates and old events.
- Generate time movement separately from dependency responses.
- Generate dependency failures and recovery.
- Keep helpers centralized and reusable.
- Print or preserve enough data to replay the exact sequence.
