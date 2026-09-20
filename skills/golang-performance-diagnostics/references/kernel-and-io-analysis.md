# Kernel And IO Analysis

Use this reference when Go CPU profiles do not explain wall time or the
hypothesis concerns syscalls, network polling, page faults, block IO, cgroup
throttling, kernel CPU, retransmissions, or off-CPU delay.

Primary references: [Go execution traces](https://go.dev/blog/execution-traces-2024),
[`go tool trace`](https://pkg.go.dev/cmd/trace), Linux
[`perf` security and access](https://docs.kernel.org/admin-guide/perf-security.html),
and the kernel [BPF documentation](https://docs.kernel.org/bpf/).

- [Evidence order](#evidence-order)
- [Go trace and syscall counts](#go-trace-and-syscall-counts)
- [Kernel and eBPF evidence](#kernel-and-ebpf-evidence)
- [Page cache, mmap, and faults](#page-cache-mmap-and-faults)
- [Correlation and acceptance](#correlation-and-acceptance)

## Evidence Order

1. Use Go CPU, block/mutex, goroutine, and execution-trace evidence to classify
   CPU, scheduler, sync, syscall, network, and GC time.
2. Count the boundary: calls, bytes, rows/packets, partial operations, and
   batching shape.
3. Use OS-native tools for process/syscall/page-fault/network evidence.
4. Escalate to eBPF only when the unresolved owner is in kernel/off-CPU space
   and host policy permits it.
5. Correlate by process/thread, pprof labels/trace regions, workload phase, or a
   bounded time window. Do not join unbounded raw event streams after capture.

## Go Trace And Syscall Counts

Use trace-derived profiles for scheduler, synchronization, syscall, and network
waiting, then inspect the named owner:

```bash
go test ./path/to/pkg -run '^$' -bench '^BenchmarkTarget$' \
  -trace "$ART/trace.out"
go tool trace -pprof=sched "$ART/trace.out" > "$ART/sched.pprof"
go tool trace -pprof=sync "$ART/trace.out" > "$ART/sync.pprof"
go tool trace -pprof=syscall "$ART/trace.out" > "$ART/syscall.pprof"
go tool trace -pprof=net "$ART/trace.out" > "$ART/net.pprof"
```

Instrument or use platform tools to count `read`, `write`, `readv`, `writev`,
`sendmsg`, `recvmsg`, polling, open/close, mmap/munmap, and bytes transferred for
the exact workload. A lower syscall count is not sufficient if batches increase
latency, memory, retries, or partial-write complexity.

## Kernel And eBPF Evidence

Use Linux `perf`, tracepoints, or approved eBPF tooling for questions such as:

- off-CPU stacks and wakeup latency;
- syscall latency distributions;
- scheduler migrations and cgroup throttling;
- page faults and block IO;
- TCP retransmissions, drops, and network queueing;
- kernel CPU, locks, or allocation outside Go frames.

Record kernel version, privileges/capabilities, tool and program version,
filters, sampling rate, lost events, map/ring-buffer drops, attachment points,
and overhead. eBPF verifier acceptance proves safety constraints, not low
measurement overhead or correct interpretation.

Prefer process/cgroup/PID and event filters at collection time. Save raw binary
artifacts outside agent context and review bounded summaries. If production
policy forbids eBPF or PMU access, mark kernel attribution unavailable and use
trace/counter proxies without relabeling them as direct evidence.

## Page Cache, mmap, And Faults

For file/mmap questions record:

- major/minor faults, RSS, mapped bytes, Go heap, and page-cache state;
- sequential/random access, file size, reuse, and warm/cold policy;
- bytes copied and syscalls for the read-based control;
- truncation, invalidation, unmap, and lifetime behavior;
- latency distributions, not only throughput.

Do not force global cache drops on a shared host. A deliberate cold-cache
experiment needs isolated host approval and is separate from steady-state
production behavior.

## Correlation And Acceptance

Kernel evidence authorizes a Go/system change only when it correlates with the
same workload and time phase. Required report:

| Question | Evidence |
|---|---|
| Where did wall time go? | Go trace/profile plus kernel/off-CPU summary |
| How often is boundary crossed? | instrumented calls, syscalls, bytes/items |
| Does candidate remove owner? | before/after normalized kernel and Go evidence |
| Did cost move? | CPU, scheduler, faults, RSS, queueing, retransmit, tail latency |
| Is evidence trustworthy? | filters, lost events, multiplex/overhead, host policy |

Reject a candidate when kernel activity falls but application tail latency,
correctness, cancellation, memory bounds, or portability regress.
