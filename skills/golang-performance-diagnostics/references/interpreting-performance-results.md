# Interpreting Go Performance Results

Use this reference to read test, benchmark, profile, compiler, runtime, PMU,
database, and kernel output and to reason about A/B differences. Preserve raw
outputs; summaries are derived evidence, not replacements.

- [A/B contract](#ab-contract)
- [Decision classes](#decision-classes)
- [Tests and fuzzing](#tests-and-fuzzing)
- [Go benchmark output](#go-benchmark-output)
- [`benchstat`](#benchstat)
- [Profiles](#profiles)
- [Execution traces](#execution-traces)
- [Compiler and machine code](#compiler-and-machine-code)
- [Hardware counters](#hardware-counters)
- [Runtime metrics and GC](#runtime-metrics-and-gc)
- [Database, IO, and kernel counters](#database-io-and-kernel-counters)
- [Diff reasoning checklist](#diff-reasoning-checklist)

## A/B Contract

`A` is the baseline and `B` is one candidate. Record revision, Go version,
GOOS/GOARCH, CPU, power/governor state, `GOMAXPROCS`, command, fixture hash,
timed boundary, and repetitions. Build stable benchmark binaries where setup
or compile variation matters. Alternate or randomize A/B run order when drift
is plausible.

Use direction-aware improvement:

```text
lower-is-better improvement = (A - B) / A * 100
higher-is-better improvement = (B - A) / A * 100
```

Always show raw A and B values beside percentages. Percentages hide absolute
cost, and ratios become misleading near zero. For exact counters such as
DB calls, rows, syscalls, or wire bytes, report integer deltas too. Treat
allocation counts as exact only when the operation and harness make them
deterministic; benchmark `allocs/op` and `B/op` are reported per-operation
averages.

## Decision Classes

| Observation | Interpretation | Decision |
|---|---|---|
| Correctness or exact resource gate fails | Invalid candidate | Revert; speed is irrelevant |
| Samples overlap/no significant difference | Insufficient evidence of change | Normal; keep baseline unless another exact objective improved |
| Statistically credible but below practical threshold | Real but not worth its cost | Normal; keep simpler implementation |
| Practical primary win, predicted owner falls, protected rows pass | Causal useful improvement | Good; test combinations and full matrix |
| Kernel wins but public path does not | Wrapper/other owner dominates or workload mismatch | Do not ship on kernel evidence alone |
| Primary metric wins but another layer grows by similar amount | Cost moved, not removed | Reject or investigate ownership boundary |
| Large win and profile owner disappears | Bottleneck moved | Reprofile; compare absolute samples before further work |
| Result depends on one order, host, distribution, or warm state | Confounded or overfit | Expand/repair experiment |

Statistical significance answers whether a difference is distinguishable under
the experiment. Practical significance answers whether the difference matters.
Both are required for a timing-based `good` result.

## Tests And Fuzzing

`PASS` proves only the assertions exercised. It does not prove faster code.
Read failures from the first causal assertion or panic, not the final package
summary. For table/property tests, record the exact input and invariant.

- `go test -race`: a race report invalidates concurrency optimization; read the
  conflicting access stacks and creation stacks.
- Fuzzing: distinguish a newly discovered failing input from corpus replay.
  Preserve the minimal reproducer and run it as a deterministic regression.
- Timeouts/deadlocks: capture goroutine stacks and ownership state; increasing
  a timeout is not a performance fix.
- Flaky pass/fail: rerun enough to identify rate and environmental correlation;
  do not classify one passing rerun as green evidence.

## Go Benchmark Output

Typical columns:

```text
BenchmarkDecode-12  25000000  47.2 ns/op  0 B/op  0 allocs/op
```

- suffix `-12` is the effective parallelism/CPU setting reported for the run,
  not a batch size;
- iteration count shows how many timed operations ran;
- `ns/op` is lower-is-better latency per benchmark operation;
- throughput metrics such as `MB/s` are higher-is-better;
- `B/op` and `allocs/op` cover Go heap allocations attributed inside the timed
  benchmark, not stack use, mmap RSS, C allocation, setup excluded by timer
  control, or retained memory;
- custom metrics are meaningful only after reading how the benchmark calls
  `ReportMetric` and what one operation represents.

Check that fixtures, conversion, random generation, verification, transaction
creation, and teardown are either intentionally included or explicitly outside
the timed boundary. Use `b.ReportAllocs()`/`-benchmem`, stable sinks, and enough
benchtime. One benchmark line is a sample, not an A/B conclusion.

## `benchstat`

Read each row as baseline distribution, candidate distribution, percent delta,
and the configured statistical test/confidence result. Then ask:

1. Is lower or higher better for this metric?
2. Is the comparison marked statistically distinguishable?
3. Does the interval/direction remain stable across repetitions?
4. Does the effect exceed the declared practical threshold?
5. Does the geomean summarize comparable rows, or hide a critical regression?

`~` or an equivalent no-significant-change marker means the experiment did not
establish a timing change. It does not prove equality. A small p-value does not
prove practical value or causality. Never average unrelated benchmark rows or
accept a favorable geomean when a protected common, wide, error, cold, or
concurrent row regresses beyond budget.

## Profiles

Select the correct sample index before reading percentages:

| Profile | Read as |
|---|---|
| CPU | Sampled on-CPU execution, not complete wall time |
| `alloc_space` | Bytes allocated over the captured interval |
| `alloc_objects` | Number of allocated objects |
| `inuse_space` | Sampled live bytes at capture |
| `inuse_objects` | Sampled live object count |
| Mutex | Delay attributed to lock-holder unlock stacks |
| Block | Time blocked on synchronization operations |

In pprof, `flat` is cost charged directly to a function and `cum` includes its
callees. High cumulative/low flat means the function routes to expensive work;
optimizing its own instructions may not help. Focused edge/caller-callee views
explain ownership better than top tables alone.

For A/B diff profiles, positive and negative samples show where measured cost
grew or fell according to profile order. Verify the base/candidate order and
sample type before interpreting signs. Compare absolute sample totals too: a
larger percentage can result from total work shrinking elsewhere.

## Execution Traces

Use traces for chronology and latency that CPU profiles cannot explain:
runnable delay, processor utilization, goroutine states, syscalls, network
wait, synchronization, GC, tasks, and regions.

Read a trace by locating the user-visible slow interval, separating running,
runnable, blocked, syscall/network, GC, and idle time, then following the
goroutine/task ownership chain. A high goroutine count is not itself bad;
unbounded growth, long runnable queues, leaks, or delayed cancellation are.
Compare equivalent load intervals, not trace-wide percentages from different
traffic shapes.

## Compiler And Machine Code

- Escape output: distinguish `can inline` from an actual `inlining call` at the
  caller. Read `moved to heap` together with the reason/data-flow chain.
- BCE output: reported remaining checks identify candidates. Absence of a line
  is support evidence, not final proof; inspect the linked code and benchmark.
- SSA: inspect the relevant phase and function, not a full dump by eye. Look for
  checks, conversions, duplicated work, phi values, and lowered operations.
- Assembly/objdump: compare linked target functions for calls, frame size,
  spills/reloads, bounds-panic calls, write barriers, branches, vector/scalar
  instructions, and code bytes.

Compiler diagnostics are explanations, not wins. An inlined or check-free
function can regress through code growth, register pressure, or changed layout.

## Hardware Counters

Normalize counters per operation or fixed workload. Read at least task-clock,
cycles, instructions, branches, branch misses, cache references/misses, faults,
context switches, and migrations when available.

- lower cycles with similar instructions suggests better stalls/locality;
- lower instructions with similar cycles may expose a memory or front-end owner;
- lower miss percentage can still be worse if total references/instructions grow;
- IPC is descriptive, not an objective by itself;
- branch-miss reduction is useful only when cycles/public time also improve;
- multiplexed counters need the tool's scaled counts and running percentage;
  heavily multiplexed or unavailable events weaken the conclusion.

Use `perf stat` A/B on the same binary workload and `perf record/report`,
annotate, or `perf c2c` to attribute an observed difference. PMU event names and
semantics are CPU-specific; record the host model and event mapping.

## Runtime Metrics And GC

Read only metrics present in `runtime/metrics.All()` for the active toolchain.
Counters need interval deltas; gauges need synchronized snapshots; histogram
buckets need distribution-aware comparison.

Correlate allocation rate, live heap, scan work, GC cycles, assists, pauses,
goroutine/scheduler state, and memory limit with application throughput and
p95/p99. A lower Go heap is not automatically good if GC CPU, RSS, mmap/C
memory, or tails rise. Compare equal traffic and warmup phases.

## Database, IO, And Kernel Counters

Instrument exact calls, cursor operations, rows examined/returned, bytes,
syscalls, batches, copies, faults, and retries. Report both count per operation
and scale slope at realistic retained history/input sizes.

- exact key read should remain constant with unrelated database growth;
- bounded range read should scale with requested/returned bound, not total DB;
- fewer calls with more rows per call may be a win or a hidden scan;
- fewer syscalls can lose when batching delay or copied bytes grows;
- lower Go CPU with higher off-CPU/kernel delay is a cost shift;
- eBPF/perf data must report filters, lost events, multiplexing, and collection
  overhead.

Code review can predict complexity but does not measure calls or rows. Use
instrumented evidence and maximum-retention fixtures.

## Diff Reasoning Checklist

For every A/B report, answer:

1. What changed in source, binary, environment, and workload?
2. Which metric is primary, which direction is better, and what is the practical
   threshold?
3. Is the result statistically distinguishable and stable across order/runs?
4. Did the diagnostic owner move as predicted?
5. Did public-path gain plausibly capture the kernel/owner reduction?
6. Which exact counters changed: allocations, bytes, calls, rows, syscalls,
   wire/code size, objects, goroutines?
7. Which noisy metrics changed: latency, throughput, cycles, misses, GC,
   scheduler, build time?
8. Did a protected minority, error, cold, wide, concurrent, architecture, or
   holdout row regress?
9. Was work removed, or moved to setup, caller, kernel, C, mmap, cache warmup,
   another goroutine, or another lifecycle stage?
10. Is the candidate simpler than equally effective alternatives, and can it be
    rolled back by reverting one selected change?

Classify the result only after all ten answers are explicit.
