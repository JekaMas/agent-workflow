# IO, Network, And System Techniques

Use this reference only when traces, syscall counts, CPU profiles, or kernel
evidence show copies, crossings, polling, page faults, or placement dominate.
Use the diagnostics
[kernel and IO analysis](../../golang-performance-diagnostics/references/kernel-and-io-analysis.md)
before selecting a system mechanism.

Primary references: [`io.Copy`](https://pkg.go.dev/io#Copy),
[`net.Buffers`](https://pkg.go.dev/net#Buffers),
[runtime netpoll](https://go.dev/src/runtime/netpoll.go),
[`cmd/cgo`](https://pkg.go.dev/cmd/cgo),
[`x/sys/unix`](https://pkg.go.dev/golang.org/x/sys/unix), and Linux
[NUMA policy](https://docs.kernel.org/admin-guide/mm/numa_memory_policy.html).

- [`io.Copy` and zero-copy fast paths](#iocopy-and-zero-copy-fast-paths)
- [Vectored and batched IO](#vectored-and-batched-io)
- [Runtime network poller](#runtime-network-poller)
- [Memory-mapped IO](#memory-mapped-io)
- [Raw syscalls and cgo](#raw-syscalls-and-cgo)
- [NUMA and process placement](#numa-and-process-placement)
- [Acceptance matrix](#acceptance-matrix)

## `io.Copy` And Zero-Copy Fast Paths

Start with `io.Copy`: it can use source `WriterTo` or destination `ReaderFrom`
and platform-specific file/network paths. Wrappers can accidentally hide these
interfaces and force user-space copy loops.

Candidates:

- preserve `WriterTo`/`ReaderFrom` through wrappers;
- remove intermediate `[]byte` aggregation when streaming semantics permit;
- compare standard `io.Copy`, specialized splice/sendfile paths already exposed
  by the standard library, and the existing implementation;
- keep protocol transforms, hashing, encryption, cancellation, and accounting
  when they are required; a zero-copy path cannot silently skip them.

Measure bytes copied, syscalls, CPU, throughput, latency, allocations, and
short/error/cancellation behavior. A kernel fast path that wins file transfer
may not apply after TLS or application transformation.

## Vectored And Batched IO

Use `net.Buffers` or supported scatter/gather APIs when headers and payloads are
already separate and concatenation/crossing cost is measured. For packet-heavy
workloads, evaluate platform batch APIs through maintained standard or
`x/net`/`x/sys` surfaces before custom assembly/syscalls.

Benchmark:

- item count and bytes per item from 1 through production batch and maximum;
- syscall count, bytes, tails/partial writes, backpressure, and error position;
- batching delay versus throughput and p95/p99 latency;
- buffer ownership, reuse, and cancellation/deadline behavior;
- supported OS/architecture matrix.

Batching is rejected when it violates latency, ordering, fairness, memory
bounds, or cancellation even if syscall count falls.

## Runtime Network Poller

Standard `net` types integrate nonblocking descriptors, deadlines, and goroutine
parking with the runtime poller. Profile TLS, protocol parsing, copying, and
application work before treating netpoll as the owner.

Raw descriptors or wrappers must preserve nonblocking behavior, readiness,
deadline, close/unblock, and cancellation contracts. A blocking syscall can tie
up an M and change scheduler saturation. Required proof combines trace `net` /
`syscall` views, goroutine state, syscall counts, and end-to-end load behavior.

## Memory-Mapped IO

Consider mmap for read-mostly large files, immutable indexes, or random access
when page-cache integration and copy removal are measured owners.

The cost moves rather than disappears: page faults, RSS, virtual address space,
mapping lifetime, truncation faults, and unmap safety sit outside ordinary Go
heap metrics. Compare mmap with sequential/random `ReadAt`, buffered reads, and
OS readahead at realistic file and working-set sizes.

Required tests cover empty/short files, truncation/invalidation, offset bounds,
concurrent readers, close/unmap ownership, faults/errors, and data lifetime.
Report major/minor faults, RSS, page-cache state, latency distribution, CPU, and
Go heap together.

## Raw Syscalls And cgo

Prefer standard library or `golang.org/x/sys/unix` over the frozen `syscall`
package for new Unix-specific work. Raw syscalls are justified by missing
functionality or a measured crossing/copy owner, not by avoiding an ordinary Go
wrapper without evidence.

For cgo, batch crossings, pass flat buffers, avoid inner-loop C-to-Go callbacks,
and use documented pointer/lifetime mechanisms. `noescape`, `nocallback`,
`runtime.Pinner`, and `runtime/cgo.Handle` are contracts whose misuse can cause
memory corruption; apply only with exact call behavior and version support.

Compare pure Go, per-item crossing, and batched crossing after each major Go
upgrade because baseline cgo/runtime costs change. Include call count, copied
bytes, callback behavior, blocked-M/scheduler effects, race/checkptr tests, and
every deployment platform/compiler.

## NUMA And Process Placement

Do not assume goroutines remain on one CPU or NUMA node. Prefer operational
process partitioning, cpusets/cgroups, and first-touch ownership on multi-socket
hosts when counters prove remote-memory or migration cost.

Per-thread memory policy combined with migrating goroutines is high risk. Use
`runtime.LockOSThread` only when the OS/native contract requires it or for a
controlled experiment. Measure local/remote accesses when available,
throughput, p95/p99, migrations, scheduler freedom, failover, and behavior on
single-node hosts. A fleet-specific placement win must not become an implicit
portable default.

## Acceptance Matrix

| Technique | Exact evidence | Protected behavior | Reject when |
|---|---|---|---|
| `io.Copy` fast path | copies/syscalls/CPU | transform, accounting, cancellation | wrapper semantics hide/skip work |
| Vectored/batch IO | syscalls and batch crossover | ordering, latency, partial IO | queue/delay/memory bound regresses |
| Raw poll/syscall | trace/kernel owner | nonblocking, deadline, close | M blocks or portability expands |
| mmap | faults/RSS/copy owner | lifetime, truncation, consistency | page-fault/RSS tail is worse |
| cgo batch | crossing owner | pointer/callback contract | pure Go or small batch wins |
| NUMA placement | remote-memory evidence | deployment/failover policy | no stable ownership or fleet support |

Remove rejected implementations. Rollback is a source/config revert, not a
silent runtime fallback that keeps two unmeasured IO paths alive.
