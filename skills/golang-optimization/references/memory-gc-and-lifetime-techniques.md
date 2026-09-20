# Memory, GC, And Lifetime Techniques

Use this reference when profiles or runtime metrics name pointer density, write
barriers, allocation shape, retained backing storage, stack growth, GC pacing,
or memory-limit pressure.

Primary references: [GC guide](https://go.dev/doc/gc-guide),
[`runtime/metrics`](https://pkg.go.dev/runtime/metrics),
[`runtime/debug` memory controls](https://pkg.go.dev/runtime/debug),
[escape analysis](https://go.dev/src/cmd/compile/internal/escape/escape.go),
[write-barrier pass](https://go.dev/src/cmd/compile/internal/ssa/writebarrier.go),
and the active [Go release notes](https://go.dev/doc/devel/release).

- [Pointer density and write barriers](#pointer-density-and-write-barriers)
- [Allocation shape and retention](#allocation-shape-and-retention)
- [GC pacing and memory limits](#gc-pacing-and-memory-limits)
- [Goroutine stack growth](#goroutine-stack-growth)
- [Arenas and experimental lifetime regions](#arenas-and-experimental-lifetime-regions)
- [Acceptance matrix](#acceptance-matrix)

## Pointer Density And Write Barriers

Pointer-rich graphs increase object count, indirection, GC scan work, and heap
pointer writes. Candidate shapes include flat value slices plus integer indexes,
hot scalar records separated from cold pointer-bearing metadata, pointer-free
scratch buffers, and immutable snapshots published as whole values.

Do not replace pointers mechanically. Value copies can increase bytes moved,
large flat arrays can retain cold data, and integer indexes add lookup and
invalidation rules. Measure:

- `/gc/scan/*`, heap objects, live bytes, GC CPU/assists, and pause/latency;
- `runtime.gcWriteBarrier*` or compiler barrier sequences in hot mutations;
- bytes visited and cache misses for graph versus flat traversal;
- update/build cost, retained capacity, and full lifecycle memory.

Batching pointer mutations can reduce repeated barrier and lock work, but must
preserve ordering, visibility, and failure semantics. An `atomic.Pointer[T]`
snapshot is appropriate only when the published object and everything reachable
from it remain immutable.

## Allocation Shape And Retention

Reducing object count can matter independently of reducing bytes. Compare
`alloc_objects`, `alloc_space`, `inuse_objects`, `inuse_space`, and GC scan work.

Candidates:

- allocate one flat backing block instead of many nodes;
- preallocate exact or bounded capacity from validated metadata;
- use owner-local scratch before `sync.Pool`;
- copy a small retained view out of a huge backing array when long-lived
  retention exceeds the copy cost;
- split common bounded stack storage from an explicit wide/heap path.

Preallocation is rejected when it systematically over-reserves memory, pins a
large backing array through a small slice, worsens RSS/GC scan cost, or moves
setup into an unmeasured phase. Pooling follows the separate runtime-technique
gate and must include miss, reset, cross-P, and retained-capacity behavior.

## GC Pacing And Memory Limits

Tune `GOGC`, `GOMEMLIMIT`, or `runtime/debug.SetMemoryLimit` only after removing
avoidable allocation and retention. These controls trade CPU, heap/RSS, GC
frequency, assists, and latency; they do not optimize an individual allocator
call.

Required experiment:

| Dimension | Cases |
|---|---|
| Traffic | idle, normal, peak, burst/recovery |
| Heap | steady state, cache warmup, maximum retained state |
| Controls | current, proposed, limit pressure, rollback/control |
| Metrics | throughput, p50/p95/p99, GC CPU, assists, cycles, heap/RSS, OOM headroom |

Use runtime metrics and GC traces as direction/effect evidence, not as a
replacement for application latency and throughput. A lower heap target can
raise CPU and tail latency; a higher target can violate container or host
memory limits.

GC implementation details are version-sensitive. Go 1.26 enables the Green Tea
collector by default; its release-note percentages are expectations for
GC-heavy programs, not a promise for a specific service. Compare the normal
toolchain build first. A toolchain opt-out such as `GOEXPERIMENT=nogreenteagc`
is a diagnostic control for that release, not a permanent production fallback.

## Goroutine Stack Growth

Goroutine stacks grow and may be copied. Large local arrays, deep recursion,
large by-value call chains, or many simultaneously live locals can turn an
allocation-saving rewrite into stack growth, copying, RSS, or scheduler cost.

Inspect:

- final stack-frame size and calls to `runtime.morestack*` in disassembly;
- stack-related CPU frames, goroutine count, and memory classes;
- one invocation and repeated steady-state behavior;
- fanout multiplied by per-goroutine stack footprint;
- panic/defer/error paths that keep large locals live.

Do not force a large object onto the stack merely to reach `0 allocs/op`.
Accept only when the public path, memory footprint, and representative
concurrency improve together.

## Arenas And Experimental Lifetime Regions

Use arenas only when the active Go toolchain documents and enables an arena
experiment and the workload has a proven region lifetime with bulk release.
Absence from the supported toolchain is an immediate rejection, not a reason to
add private runtime hooks.

Required gate:

- explicit experimental support policy and build matrix;
- no arena pointer escapes beyond the region lifetime;
- same correctness under check/race/fuzz tests supported by the experiment;
- retained heap/RSS and release latency improve versus flat allocation, owner-
  local reuse, and pooling;
- fallback means reverting the feature or build policy, not silently selecting
  a second production allocator at runtime.

Do not use arenas to hide unbounded ownership, leak-prone caches, or values that
must survive asynchronous work.

## Acceptance Matrix

| Technique | Required owner | Exact regression gates | Main rejection |
|---|---|---|---|
| Pointer-free/flat layout | scan/barrier/cache evidence | object count, bytes, canonical order | copies or retention erase gain |
| Preallocation | growth allocation owner | capacity, retained bytes | workload over-reserves |
| GC control | GC CPU/assist/limit evidence | memory limit and OOM headroom | CPU/latency trade is worse |
| Stack shaping | heap escape or frame owner | frame size, `morestack`, fanout memory | large stack/copy cost |
| Arena experiment | region-lifetime owner | support matrix and lifetime proof | unstable/absent API or escaping data |

For every accepted change, rerun allocation/heap profiles, runtime metrics,
public benchmarks or load tests, and the diagnostic that named the original
owner.
