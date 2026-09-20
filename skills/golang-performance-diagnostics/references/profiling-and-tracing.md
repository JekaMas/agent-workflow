# Profiling, Tracing, GC, and Escape Analysis

Use this reference after a benchmark shows a performance problem and the next
question is why. For text extraction, filtering, live endpoints, and artifact
hygiene, use [text-artifacts-and-targeting.md](text-artifacts-and-targeting.md).

Contents: matrix, CPU, memory, escape analysis, trace, block/mutex, GC,
runtime metrics, labels, and one repo-derived allocation drill-down.

## Diagnostic Matrix

| Question | First tool | Read as | Response |
|---|---|---|---|
| CPU owner? | `-cpuprofile`, `pprof -top/-list` | High percentage plus target relevance. | Remove work, improve algorithm, inspect hot source. |
| Local cost or caller path? | CPU `flat` vs `cum` | High `flat`: local body burns samples. High `cum`, low `flat`: callees dominate. | Patch local body, or reduce call count/child cost. |
| Allocation churn? | `-memprofile`, `alloc_space` | Total bytes allocated, including freed bytes. | Reuse/preallocate/remove conversions. |
| Tiny-object pressure? | `alloc_objects` | Object count, boxing, small temporaries. | Remove closures/interface boxes/temporary objects. |
| Retained heap? | `inuse_space`, `inuse_objects` | Live heap at profile time. | Release references, bound caches, avoid large backing-array retention. |
| Escape reason? | `-gcflags='all=-m=2'` | Compiler hypothesis tied to hot allocation sites. | Change API/lifetime only where profiles agree. |
| GC part of latency? | `GODEBUG=gctrace=1` | Frequency, heap growth, assist pressure context. | Reduce allocation/retention before GC knobs. |
| Wall time not CPU? | `go test -trace`, trace pprof | `sched`, `sync`, `syscall`, `net` waits. | Reduce contention, fanout, syscalls, network waits. |
| Locks/channels? | `-blockprofile`, `-mutexprofile` | Delay and contended holders. | Shorten critical sections or change coordination. |
| Direction finder? | `runtime/metrics` | Runtime counters/histograms. | Capture the matching profile/trace next. |

## CPU Profiles

```bash
go test ./your_package -run '^$' -bench '^BenchmarkName$' \
  -cpuprofile=cpu.out -count=1

go tool pprof -top -nodecount=30 cpu.out
go tool pprof -top -cum -nodecount=30 cpu.out
go tool pprof -list 'FunctionName' cpu.out
```

Rules:

- A 5% frame cannot produce a 20% total win.
- High `flat` means the function body is hot.
- High `cum`, low `flat` means the function owns an expensive path.
- If runtime/GC dominates, switch to allocation evidence.
- If sample count is low, increase `-benchtime`.

## Memory and Allocation Profiles

```bash
go test ./your_package -run '^$' -bench '^BenchmarkName$' \
  -benchmem \
  -memprofile=mem.out \
  -memprofilerate=1 \
  -count=1

go tool pprof -top -sample_index=alloc_space mem.out
go tool pprof -top -sample_index=alloc_objects mem.out
go tool pprof -top -sample_index=inuse_space mem.out
go tool pprof -list 'FunctionName' -sample_index=alloc_space mem.out
```

Read:

- `alloc_space`: GC churn from total allocated bytes.
- `alloc_objects`: allocator pressure from object count.
- `inuse_space`: retained heap, leaks, caches, pinned backing arrays.
- High bytes plus high objects is a strong first target.
- High objects with low bytes points to tiny temporaries or boxing.
- High bytes with few objects points to buffers, decoded payloads, or retained
  backing arrays.

`-memprofilerate=1` records every allocation and is expensive; use it only on
narrow benchmarks.

## Escape Analysis

```bash
go build -gcflags='all=-m=2' ./your_package 2> escape.log
go test ./your_package -run '^$' -bench '^BenchmarkName$' \
  -gcflags='all=-m=2' 2> escape_test.log

rg 'your/package|escapes to heap|moved to heap|cannot inline|can inline' escape.log
```

Rules:

- `escapes to heap` means stack allocation was rejected.
- `moved to heap` points at locals forced onto heap.
- `cannot inline` can explain call overhead or missed stack allocation; it is
  not itself a regression.
- Ignore cold error-path escapes unless allocation profiles name them.
- Use escape output only where `B/op`, `allocs/op`, `alloc_space`, or
  `alloc_objects` also moved.
- The local Go 1.26.2 runtime does not support `allocfreetrace` in source; use
  `-benchmem`, memory profiles, `-memprofilerate=1`, and escape analysis.

## Trace

```bash
go test ./your_package -run '^$' -bench '^BenchmarkName$' \
  -trace=trace.out -count=1

go tool trace trace.out
go tool trace -pprof=sched trace.out > sched.pb.gz
go tool trace -pprof=sync trace.out > sync.pb.gz
go tool trace -pprof=syscall trace.out > syscall.pb.gz
go tool trace -pprof=net trace.out > net.pb.gz
go tool pprof -top -cum sched.pb.gz
```

Use trace for wall-time questions: scheduler latency, goroutine blocking,
syscalls, network waits, GC timing, and goroutine bursts. Do not start with
trace for a simple allocation-heavy microbenchmark.

## Block and Mutex Profiles

```bash
go test ./your_package -run '^$' -bench '^BenchmarkName$' \
  -blockprofile=block.out \
  -mutexprofile=mutex.out \
  -count=1

go tool pprof -top -sample_index=delay block.out
go tool pprof -top -cum mutex.out
go tool pprof -list 'FunctionName' mutex.out
```

Read:

- Block profile points at where goroutines waited: channel ops, `select`,
  mutex/RWMutex locks, cond waits, wait groups.
- Mutex profile points at contended lock holders, often unlock sites.
- High count with tiny delay is weak evidence.
- Coordination changes need correctness tests for ownership, cancellation,
  bounded queues, stop/join behavior, and determinism where required.

## GC Context

```bash
GODEBUG=gctrace=1 go test ./your_package -run '^$' \
  -bench '^BenchmarkName$' -benchmem
```

Use `gctrace` to correlate allocation rate, heap growth, and GC frequency. Do
not use it alone to justify a patch.

## Runtime Metrics

Use `runtime/metrics` as a direction finder:

- `/sync/mutex/wait/total:seconds`: capture mutex/block profiles.
- `/sched/latencies:seconds`: capture trace-derived `sched`.
- `/gc/heap/tiny/allocs:objects`: inspect `alloc_objects`.
- `/cpu/classes/gc/mark/assist:cpu-seconds`: inspect allocation rate and
  pointer-heavy retention.
- `/gc/scan/*`: compare pointer-bearing scan work when the active toolchain
  exposes the relevant metric names.

Query `metrics.All()` and record the active Go version before selecting names;
metric names and semantics can change. Do not hardcode a version-specific name
into a reusable collector without a fail-closed availability check.

```go
func readSupportedPerfMetrics(wanted []string) []metrics.Sample {
	available := make(map[string]struct{}, len(metrics.All()))
	for _, description := range metrics.All() {
		available[description.Name] = struct{}{}
	}
	samples := make([]metrics.Sample, 0, len(wanted))
	for _, name := range wanted {
		if _, ok := available[name]; ok {
			samples = append(samples, metrics.Sample{Name: name})
		}
	}
	metrics.Read(samples)
	return samples
}
```

Report metrics as context for the next profile, not as final proof.

## Profile and Trace Labels

Use low-cardinality labels and trace regions when profiles need application
phases.

```go
func handle(ctx context.Context, market string) {
	labels := pprof.Labels("path", "quote", "market", market)
	pprof.Do(ctx, labels, func(ctx context.Context) {
		ctx, task := trace.NewTask(ctx, "quote")
		defer task.End()

		trace.WithRegion(ctx, "parse", parseQuote)
		trace.WithRegion(ctx, "execute", executeQuote)
	})
}
```

Do not label by user, order, request, or other high-cardinality/sensitive data.
For latency-spike capture on local Go 1.26.2, `runtime/trace.FlightRecorder`
can keep a moving recent trace window; analyze emitted traces with the normal
`go tool trace` and trace-derived pprof commands.

## Repo-Derived Allocation Drill-Down

Observed benchmark:

```text
BenchmarkFromDecimalSnapshotSPXDepth  about 104 us/op  85.1 kB/op  3.20k allocs/op
```

Targeted capture:

```bash
PKG=./application/cex/orderbooknumeric
BENCH='^BenchmarkFromDecimalSnapshotSPXDepth$'

GOWORK=off go test "$PKG" -run '^$' -bench "$BENCH" -benchmem \
  -count=1 -benchtime=100x \
  -cpuprofile=orderbook_cpu.out \
  -memprofile=orderbook_mem.out \
  -memprofilerate=1

go tool pprof -top -sample_index=alloc_space orderbook_mem.out
go tool pprof -list='orderbooknumeric\.fromDecimalLevels' \
  -sample_index=alloc_space orderbook_mem.out
```

Evidence chain:

- `fromDecimalLevels` owned about 76% cumulative `alloc_space`.
- Top allocation owners were `math/big` and `shopspring/decimal` operations:
  `nat.make`, `NewInt`, `Decimal.Mul`, `rescale`, and `NewFromString`.
- Escape output around `decimalUnitsAtScale` aligned with returned `big.Int`
  allocations.

Optimization direction: reduce decimal parsing and `big.Int` churn, cache scale
multipliers, or change representation only after token scale semantics and
service hot-path relevance are verified. Cold `fmt.Errorf` escapes are ignored
unless an error-workload profile names them.
