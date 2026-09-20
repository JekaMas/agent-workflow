# Benchmarking Recipes

Use this reference when the task is to write, run, compare, or interpret Go
benchmarks. For complete A/B and tool-output interpretation, also use
[interpreting-performance-results.md](interpreting-performance-results.md).

Contents: baseline packet, benchmark structure, variable inputs, reading output,
sanity checks, repo example, long-run hygiene, and outbound HTTP benchmarks.

## Baseline Packet

Collect this before changing code:

```bash
go version
go env GOOS GOARCH GOVERSION GOMOD GOWORK
go test ./your_package -run '^$' -bench '^BenchmarkName$' -benchmem -count=10 -benchtime=1s > old.txt
```

After the change:

```bash
go test ./your_package -run '^$' -bench '^BenchmarkName$' -benchmem -count=10 -benchtime=1s > new.txt
benchstat old.txt new.txt
```

Use `-run '^$'` to avoid running tests when only benchmarks are needed. Use
`-benchmem` by default. Use `-count` plus `benchstat` before claiming a win.

If a repo uses `go.work` and the command reports that the package is not in the
workspace, retry with `GOWORK=off` only after confirming the package is in the
current module.

Benchmark-plan gate:

- If the task requires writing new benchmarks or changing implementation
  primarily for performance, retain explicit benchmark-plan approval. Reuse
  applicable existing approval; ask only when the required plan approval is absent
  or its material scope changes.
- Start with feature-level benchmarks before microbenchmarks. Move to a
  microbenchmark after a feature-level run, profile, or production signal
  identifies a narrower bottleneck.
- Keep correctness tests independent from performance tests.

## Writing Benchmarks

Use Go 1.26 `b.Loop()` when available:

```go
func BenchmarkParseThing(b *testing.B) {
    input := loadRepresentativeInput()
    b.ReportAllocs()
    b.ResetTimer()

    for b.Loop() {
        got, err := ParseThing(input)
        if err != nil {
            b.Fatal(err)
        }
        sink = got
    }
}
```

For older-compatible code, use `for i := 0; i < b.N; i++`.

Keep setup outside the timed loop. Use a package-level sink or observable check
when needed to prevent dead-code elimination. Validate output cheaply inside the
loop only if it is part of the real workload or needed to protect correctness.
If benchmarked code needs a context, use `b.Context()` instead of
`context.Background()` so benchmark cleanup cancels owned work.

```go
func BenchmarkFetchPlan(b *testing.B) {
    client := NewClient(fakeTransport)
    b.ReportAllocs()
    for b.Loop() {
        got, err := client.FetchPlan(b.Context(), planID)
        if err != nil {
            b.Fatal(err)
        }
        sinkPlan = got
    }
}
```

## Variable Inputs

Use subbenchmarks for input sizes or distributions:

```go
func BenchmarkEncodeSizes(b *testing.B) {
    for _, size := range []int{1, 8, 64, 512, 4096} {
        input := makeInput(size)
        b.Run(fmt.Sprintf("size_%d", size), func(b *testing.B) {
            b.ReportAllocs()
            for b.Loop() {
                sinkBytes = Encode(input)
            }
        })
    }
}
```

Do not pass `b.N` as the workload size. `b.N` is the harness iteration count, not
the problem size. Use powers of two only when they model reality or expose
scaling. Include production-shaped samples where possible.

## Reading Benchmark Output

Example:

```text
BenchmarkFromDecimalSnapshotSPXDepth-10  100  102504 ns/op  85112 B/op  3202 allocs/op
```

Read it as:

- `-10`: GOMAXPROCS value used by the test binary.
- `100`: iterations actually run.
- `ns/op`: time per operation.
- `B/op`: allocated bytes per operation.
- `allocs/op`: allocation count per operation.

Time without allocation improvement can still be a win. Allocation improvement
without time improvement can still matter if GC, tail latency, or memory pressure
is the bottleneck. Always tie the metric to the original question.

## Sanity Checks

Treat benchmark numbers as suspect until these checks pass:

- If `ns/op` is near zero or below the plausible cost of the operation, assume
  the compiler optimized away the work. `0.5 ns/op` is a classic red flag. Add
  an observable result check or sink.
- If `B/op` or `allocs/op` is zero for code that must allocate, check whether
  setup accidentally happened outside the timed loop or the result was unused.
- If one benchmark input is repeated and a cache is involved, add varied inputs.
  A single hot key can turn a cache benchmark into an unrealistic 100% hit-rate
  test.
- If `benchstat` reports no significant difference, do not claim a win. Increase
  repetitions, reduce noise, or choose a larger representative benchmark.
- If a benchmark suite compares many rows, use grouped comparison carefully;
  geometric mean can summarize a group, but individual regressions still need
  review.
- If benchmark setup directly seeds internal state to isolate a hot path,
  document why the public setup path is excessive and which correctness test
  covers the real path. Pre-seeding is a performance harness technique, not a
  substitute for behavior tests.

Use target size to choose strategy:

- `10-20%` needed: implementation cleanup, allocation reduction, and removing
  repeated work may be enough.
- `2x` needed: expect algorithm, representation, batching, or cache changes.
- `10x` needed: do not start with expression-level tricks; inspect algorithm,
  data layout, IO, system boundaries, and whether the benchmark models the real
  target.

## Repo-Derived Example

Lightweight benchmark used while drafting this skill:

```bash
mkdir -p data/logs/golang_optimization_skill/iter3
GOWORK=off go test ./application/cex/orderbooknumeric \
  -run '^$' \
  -bench '^BenchmarkFromDecimalSnapshotSPXDepth$' \
  -benchmem \
  -count=3 \
  -benchtime=100x \
  -timeout=5m \
  > data/logs/golang_optimization_skill/iter3/orderbook_bench.txt 2>&1

benchstat data/logs/golang_optimization_skill/iter3/orderbook_bench.txt
```

Observed summary on `go1.26.2 darwin/arm64`:

```text
name                            time/op
FromDecimalSnapshotSPXDepth-10   104us +- 1%

name                            alloc/op
FromDecimalSnapshotSPXDepth-10  85.1kB +- 0%

name                            allocs/op
FromDecimalSnapshotSPXDepth-10   3.20k +- 0%
```

Interpretation:

- This is enough to show the benchmark is allocation-heavy.
- It is not enough to prove an optimization. A before/after `benchstat` is still
  required after any patch.
- The next diagnostic should be allocation profiling, not random CPU tuning.
- Because `3202 allocs/op` is a large object count for one conversion, inspect
  `alloc_objects` as well as `alloc_space`.
- Because the benchmark uses a fixed 100-level SPX book, add variable-depth and
  mixed-symbol subbenchmarks before generalizing conclusions to all order books.

## Long-Run Hygiene

On an approved Linux benchmark host, consider
[`perflock`](https://pkg.go.dev/golang.org/x/perf/cmd/perflock) to reduce CPU
frequency and scheduling variance. Treat it as an environment control, not as a
substitute for repeated samples, `benchstat`, or production-path validation.
Record whether it was available and used; do not compare locked and unlocked
runs as if their environments were identical.

Treat benchmark suites, profile runs, traces, escape-analysis runs, and service
log checks as long-running or noisy unless proven small. Redirect output to
files. Inspect large files with `rg`, focused `sed` windows, pprof summaries, or
custom scripts. Do not stream broad stdout/stderr into the conversation.

The large-file rule wins over convenience. Do not start with `cat`, broad
`sed`, broad `head`/`tail`, or equivalent whole-file reads for logs, profiles,
trace-derived text, escape logs, JSON, CSV, or generated reports that may be
large. First check size or line count, run a targeted search, produce a pprof
summary, or extract a narrow window around a known match.

If benchmark inputs, logs, traces, JSON, CSV, or related artifacts exceed 1 GB,
do not load them eagerly. Use streaming/chunked processing or targeted
extraction before analysis. If existing tooling cannot process the input
incrementally, write or choose a streaming alternative first.

## Outbound HTTP Benchmarks

Do not benchmark live remote services unless the task is explicitly an
integration or load test. Prefer an existing interface seam. If no seam exists
and the code uses `http.Client`, inject a deterministic `RoundTripper` so the
benchmark measures local code rather than network variance.

```go
type roundTripFunc func(*http.Request) (*http.Response, error)

func (f roundTripFunc) RoundTrip(r *http.Request) (*http.Response, error) {
    return f(r)
}

func BenchmarkHTTPAdapter(b *testing.B) {
    client := &http.Client{Transport: roundTripFunc(func(r *http.Request) (*http.Response, error) {
        body := io.NopCloser(strings.NewReader(`{"ok":true}`))
        return &http.Response{StatusCode: http.StatusOK, Body: body}, nil
    })}
    adapter := NewAdapter(client)

    b.ReportAllocs()
    for b.Loop() {
        got, err := adapter.Call(b.Context(), request)
        if err != nil {
            b.Fatal(err)
        }
        sinkResult = got
    }
}
```

Use a real listener or external endpoint only when the benchmark question is
about actual transport behavior.
