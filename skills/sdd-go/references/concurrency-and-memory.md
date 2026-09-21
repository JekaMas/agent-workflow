# Concurrency And Memory

Load this reference whenever Go code starts goroutines, uses channels/locks,
depends on cancellation/timing, retains buffers, or changes resource ownership.

## Goroutine Contract

Every goroutine needs:

- one owner;
- a start point and exit condition;
- a stop/cancel signal;
- a join/wait path;
- bounded work and backlog behavior.

Do not fire-and-forget, spawn unbounded request goroutines, or hide goroutines
inside helpers without returning a lifecycle handle.

## Queues And Cancellation

- Bound worker count and queue capacity.
- Define overflow/backpressure behavior.
- On cancellation, specify whether queued work drains or is discarded.
- Every potentially blocking loop/send/receive needs a cancellation path.
- Use `context` for cancellation/deadlines, not as an untyped value bag.
- Prefer `errgroup.WithContext` plus a bounded worker design when it matches the
  ownership contract.

## Timing

- Correctness must not assume scheduler fairness or prompt execution.
- Do not use `time.Sleep` to coordinate correctness.
- Use injected clocks, controlled channels, or explicit events in tests.
- Timeouts may guard/fail a test; they must not be what makes it pass.

## Termination Tests

Cover relevant cases:

- cancellation during active work;
- cancellation with backlog;
- stalled downstream;
- queue overflow/backpressure;
- join completion and resource closure.

Route a suspected live deadlock or test timeout to `golang-testing` for stack
capture before changing code.

## Memory And Resources

- Treat goroutine leaks as memory leaks.
- Avoid retaining large backing arrays through small subslices or closures.
- Prefer immutable value messages; protect shared pointer state explicitly.
- Close files, bodies, connections, timers, and other owned resources.
- Preallocate only when size is known and the code remains clear.
- Do not add pooling, caches, weak references, unsafe access, atomics, sharding,
  or runtime/scheduler tuning without evidence. Start with
  `golang-performance-diagnostics`.
- Never make correctness depend on GC, cleanup timing, or weak reachability.
