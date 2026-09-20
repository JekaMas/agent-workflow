# Optimization Decision Playbook

Use this reference when the agent needs a concrete choice algorithm, not another
list of tools. Start from the target metric, choose one gate below, patch one
hypothesis, and prove it with correctness tests plus `benchstat` or profiles.

Contents: goal sizing, workflow, data/index changes, algorithm changes,
benchmark input design, allocation/GC changes, compiler/runtime changes,
standard-library hot-path choices, concurrency, and service-level decisions.

## Goal Sizing

Decision:

- `5-20%`: implementation cleanup, allocation reduction, call-count reduction,
  narrower stdlib APIs, or compiler-friendly source shape can be enough.
- `2x`: start with doing less work, representation changes, indexing,
  batching, or algorithm changes.
- `10x`: start with algorithm, IO, storage, cross-service, or system-design
  changes. Micro-tuning is unlikely to be the owner.

Required context:

```text
Goal: p99 320ms -> <100ms at 250k req/s.
Protected behavior: canonical receipt bytes and deterministic order.
Evidence: CPU 45%, trace sync/net wait high, CPU profile does not explain wall.
Next gate: service/concurrency, not CPU microbenchmark.
```

## Baseline Workflow

Algorithm:

1. Write the protected behavior and correctness tests.
2. Capture Go version, package, benchmark regex, input shape, `-count`,
   `-benchtime`, `GOOS`, `GOARCH`, `GOMAXPROCS`, and artifacts.
3. Make one hypothesis: allocation churn, retained heap, CPU loop, lock wait,
   scheduler wait, IO wait, algorithmic growth, or representation mismatch.
4. Patch only that hypothesis.
5. Compare with `benchstat`; use profile diffs when location matters.
6. Revert neutral/noisy/negative patches unless they are required for clarity or
   correctness and the user accepts the tradeoff.

Minimal benchmark:

```go
var sink int

func BenchmarkLookup(b *testing.B) {
	data := buildRepresentativeInput()
	b.ReportAllocs()
	for b.Loop() {
		sink = lookup(data, "target")
	}
}
```

```bash
go test ./pkg -run '^$' -bench '^BenchmarkLookup$' -benchmem -count=10 > old.txt
go test ./pkg -run '^$' -bench '^BenchmarkLookup$' -benchmem -count=10 > new.txt
benchstat old.txt new.txt
```

## Data and Index Changes

Use when repeated work answers the same question: lookup by ID, membership,
length, parsing, formatting, aggregation, or secondary-key search.

Gate:

- Read/query count is high enough to pay for memory and update cost.
- Update, invalidation, and determinism rules are explicit.
- Benchmarks include read/write mix, not read-only happy path.

Index shape:

```go
type Orders struct {
	rows []Order
	byID map[string]int
}

func NewOrders(rows []Order) *Orders {
	idx := make(map[string]int, len(rows))
	for i := range rows {
		idx[rows[i].ID] = i
	}
	return &Orders{rows: rows, byID: idx}
}

func (o *Orders) ByID(id string) (Order, bool) {
	i, ok := o.byID[id]
	if !ok {
		return Order{}, false
	}
	return o.rows[i], true
}
```

Measure: `sec/op` by query/update ratio, `B/op`, `allocs/op`, retained heap, and
cache hit/miss ratio if applicable.

## Algorithm Changes

Use when runtime grows poorly across realistic sizes or profiles point at
search, sort, matching, routing, or lookup loops.

Gate:

- Benchmark several real sizes and distributions.
- Include build/index/sort cost as well as query cost.
- Keep a small/large polyalgorithm only when the threshold is measured.

Variable-size benchmark:

```go
func BenchmarkContains(b *testing.B) {
	for _, n := range []int{8, 32, 128, 1024} {
		b.Run(fmt.Sprintf("n=%d", n), func(b *testing.B) {
			xs := makeInput(n)
			b.ReportAllocs()
			for b.Loop() {
				_ = contains(xs, xs[n/2])
			}
		})
	}
}
```

Decision rule:

```text
linear scan wins for n<=16 in this package benchmark
binary/search/index wins above that
threshold is tested and named in code comments
```

## Benchmark Input Design

Use when a benchmark might be overfit.

Checklist:

- common case, boundary case, worst plausible case, skewed data;
- realistic cardinality, hit ratio, miss ratio, payload size, and reuse distance;
- real traces for cache or branch behavior;
- no use of `b.N` as workload size.

Trace-shaped cache benchmark:

```go
func BenchmarkCacheTrace(b *testing.B) {
	trace := loadKeys("testdata/search_keys.txt")
	c := NewCache(1024)
	b.ReportAllocs()
	for i := 0; b.Loop(); i++ {
		_, _ = c.GetOrCompute(trace[i%len(trace)])
	}
}
```

## Allocation and GC Changes

Use when `B/op`, `allocs/op`, `alloc_space`, `alloc_objects`, `inuse_space`, or
GC assist/context proves allocation is material.

Gate:

- `alloc_space`: reduce bytes/op, copies, formatting, decoded payload churn.
- `alloc_objects`: remove tiny temporaries, boxing, closures, interface-shaped
  APIs, or reflective value churn.
- `inuse_space`: bound caches, release references, avoid backing-array pinning.
- Escape analysis is explanatory only; tie it to hot profile frames.

Caller-buffer shape:

```go
func AppendRecord(dst []byte, r Record) []byte {
	dst = strconv.AppendInt(dst, r.ID, 10)
	dst = append(dst, ',')
	dst = append(dst, r.Name...)
	return dst
}
```

Backing-array release:

```go
func keepSmallView(big []byte, lo, hi int) []byte {
	return append([]byte(nil), big[lo:hi]...)
}
```

Do not change `GOGC` or add pooling before reducing avoidable allocation and
retention.

## Runtime and Compiler Changes

Use when profiles overlap with compiler-visible costs: interface conversions,
`fmt`, reflection, bounds checks, string/byte conversions, array range copies,
or missed inlining/stack allocation.

Gate:

- Profile first, compiler diagnostics second.
- `-gcflags='all=-m=3'` explains escape/inlining.
- `-d=ssa/check_bce/debug=1` explains remaining bounds checks.
- Rebenchmark after Go upgrades if the win depends on compiler behavior.

Array range copy avoidance:

```go
func sumArray(a [1024]int) int {
	sum := 0
	for i := range a {
		sum += a[i]
	}
	return sum
}
```

Prefer clear source that helps the compiler; keep contortions only when
`benchstat` proves the win.

## Standard-Library Hot Paths

Use when a standard-library frame is hot and the current API is too general.

Rules:

- Replace `fmt` with `strconv`/append-style code in hot formatting paths.
- Use `EqualFold` instead of lowercasing both strings for comparison.
- Use reusable timers instead of `time.After` in hot loops.
- Drain and close HTTP response bodies when reuse affects latency.
- Avoid `binary.Read`/`binary.Write` reflection in hot binary protocols.

Hot formatting:

```go
buf := make([]byte, 0, 32)
buf = strconv.AppendInt(buf, id, 10)
buf = append(buf, ':')
buf = append(buf, status...)
```

## Concurrency

Use when CPU does not explain wall time or mutex/block/trace data identifies
wait owners.

Gate:

- Shorten critical sections before sharding.
- Move IO/logging/allocation outside locks.
- Bound worker counts and queues.
- Preserve owner, stop signal, join path, exit condition, cancellation, and
  drain/discard behavior.
- Changing repo coordination mechanisms requires explicit approval.

Lock-hold reduction:

```go
func (s *Store) Update(k string, v Value) {
	next := prepareValue(v)
	s.mu.Lock()
	s.rows[k] = next
	s.mu.Unlock()
}
```

Measure: `trace -pprof=sched|sync`, block/mutex profiles, goroutine count,
queue depth, throughput, and `p95`/`p99`.

## Whole-Service Decisions

Use when optimizing a service path rather than a package function.

Algorithm:

1. Split wall time into CPU, GC, lock, scheduler, syscall, network, database,
   downstream service, queueing, and load imbalance.
2. Optimize the highest owner level first.
3. Load test with realistic request rate and ramp-up/ramp-down.
4. Verify production metrics after rollout; profiles can shift with traffic.

Service packet:

```text
Traffic: 250k req/s target, 40-core host, 10 min ramp.
Symptom: p99 320ms, CPU 45%, goroutines blocked on outbound RPC.
Next evidence: distributed trace + Go trace sync/net pprof.
Not useful yet: local CPU loop microbenchmark.
```
