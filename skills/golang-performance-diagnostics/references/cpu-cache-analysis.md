# CPU Cache Analysis

Use this reference when the performance question concerns cache misses,
working-set size, locality, memory layout, pointer chasing, or false sharing.
Do not diagnose cache behavior from `ns/op` or source layout alone.

Contents: evidence classes, host/cache context, Linux `perf`, macOS Instruments,
normalization, working-set crossovers, layout hypotheses, false sharing, and
acceptance.

## Evidence Classes

Prefer evidence in this order:

1. hardware performance counters for the exact benchmark process;
2. cache-counter sampling tied to named symbols;
3. controlled working-set crossover benchmarks when counters are unavailable;
4. layout and access-order inspection as hypothesis support only.

`pprof` identifies sampled CPU owners but does not measure cache hits or misses.
A slower large working set is consistent with cache pressure, but it is not a
measured miss count.

## Baseline Context

Record:

- CPU model, OS, architecture, Go version, benchmark binary hash;
- cache line and L1/L2/L3 sizes when the platform exposes them;
- benchmark command, `GOMAXPROCS`, count, benchtime, element count, element
  size, bytes visited, and access order;
- allocations and GC activity during the measured section;
- counter names, support status, multiplex/running percentage, and raw output.

Examples:

```bash
# Linux
lscpu --caches

# macOS; unavailable cache levels may return an error and must be reported as
# unknown rather than assumed.
sysctl -n hw.cachelinesize hw.l1dcachesize hw.l2cachesize hw.l3cachesize
```

## Linux `perf`

Compile the benchmark once so `perf` observes a stable process:

```bash
go test -c -o "$ART/pkg.test" ./path/to/pkg
perf list cache > "$ART/perf_cache_events.txt"
perf stat -x, -r 5 \
  -e cycles,instructions,cache-references,cache-misses \
  -e L1-dcache-loads,L1-dcache-load-misses \
  -e LLC-loads,LLC-load-misses \
  -- "$ART/pkg.test" -test.run '^$' -test.bench '^BenchmarkHot$' \
  -test.benchtime=5s -test.count=1 \
  > "$ART/benchmark_stdout.txt" 2> "$ART/perf_stat.csv"
```

Event aliases vary by CPU, kernel, virtualization, and hybrid core. Use only
events reported by `perf list`; record `<not supported>`, `<not counted>`, and
the time-running percentage. Reduce multiplexing by collecting fewer events per
run. Pinning to one CPU can reduce migration noise when repository and host
policy allow it:

```bash
taskset -c 2 perf stat ...
```

To attribute misses after aggregate counters establish a problem:

```bash
perf record -e cache-misses:u -g -- "$ART/pkg.test" \
  -test.run '^$' -test.bench '^BenchmarkHot$' -test.benchtime=10s
perf report --stdio > "$ART/cache_miss_report.txt"
```

## macOS Instruments CPU Counters

First prove the template exists:

```bash
xcrun xctrace list templates > "$ART/xctrace_templates.txt"
rg -n '^CPU Counters$' "$ART/xctrace_templates.txt"
```

Then launch the compiled benchmark under that template:

```bash
go test -c -o "$ART/pkg.test" ./path/to/pkg
xcrun xctrace record --template 'CPU Counters' \
  --output "$ART/cache.trace" --time-limit 20s --no-prompt \
  --launch -- "$ART/pkg.test" -test.run '^$' \
  -test.bench '^BenchmarkHot$' -test.benchtime=10s -test.count=1
xcrun xctrace export --input "$ART/cache.trace" --toc \
  > "$ART/cache_trace_toc.xml"
```

Counter names and export schemas vary by Xcode and Apple CPU. Preserve the
`.trace`, export only focused tables that the trace exposes, and state when the
result required Instruments inspection. Inspect the TOC before using a trace:
the stock CLI template can record with an empty `pmc-events` selection when no
counters were configured in Instruments. An empty selection is unavailable
evidence, not a zero miss count. Do not translate an unavailable Apple counter
into a Linux event name or claim a miss rate from Time Profiler data.

On heterogeneous Apple CPUs, also record per-performance-level cache sizes
when available; the generic `hw.l1dcachesize` / `hw.l2cachesize` values can
describe efficiency cores rather than the cores that execute a sustained
benchmark:

```bash
sysctl -a | rg 'hw\.perflevel[0-9]+\.(name|l1dcachesize|l2cachesize|cpusperl2)'
```

## Normalization And Interpretation

Report raw counts plus normalized metrics:

- cache miss rate = misses / references, only when both events are compatible;
- cache hits = references - misses and hit rate = 1 - miss rate, only when the
  events cover the same cache level, access class, privilege scope, and time;
- misses/op = misses / completed benchmark iterations;
- misses/element or misses/byte for scans;
- cycles/op and instructions/op;
- IPC = instructions / cycles;
- `ns/op`, `B/op`, and `allocs/op` from the same workload.

Low miss rate can still mean many misses on a high-volume path. High miss rate
can be harmless on a tiny path. Evaluate cycles and end-to-end latency with the
counter delta. Counter totals include runtime, GC, setup, and benchmark harness
work unless the tool and benchmark isolate them.

Compare hit/miss changes with instructions and bytes visited. A compact
representation can reduce misses while adding decode instructions; a lookup
table can remove arithmetic while displacing hotter data; a slice can shrink an
inline row while adding allocation, indirection, and GC scan work. Keep the
complete public operation as the acceptance row.

## Working-Set Crossover Benchmark

When counters are unavailable, vary the data footprint around measured cache
sizes. Use powers of two and boundary-adjacent sizes rather than one small and
one huge case.

Required shapes:

- sequential and precomputed pseudo-random access;
- hot-field-only and all-field scans;
- one pass and repeated passes;
- element counts spanning below L1, between L1/L2, between L2/L3, and above the
  last-level cache;
- single-thread and representative concurrent access where applicable.

Keep index generation and cache-thrashing setup outside timed work. Report
`ns/element` and effective bytes visited. A latency step near a cache-size
boundary is proxy evidence; label it `working-set crossover`, not `cache miss`.

Use separate cold and warm experiments only when both model real behavior.
Artificial cache flushing answers a cold-access question; it does not predict a
steady-state hot loop. For repeated access, report reuse distance and number of
passes so a cache-hit claim is reproducible.

## Layout And Access Hypotheses

Calculate the hot footprint:

```text
hot bytes = element size * elements visited per operation
```

Then identify which bytes are actually read. Candidate changes include:

- split cold payloads from frequently scanned metadata;
- use structure-of-arrays when a loop reads one or two fields;
- preserve contiguous value storage when the whole record is consumed;
- reorder work to reuse recently loaded data;
- precompute compact indexes for repeated lookup;
- batch adjacent operations without changing ordering or cancellation.

A pointer or slice can shrink the scanned element while adding heap objects,
indirection, GC scanning, and random loads. Measure the complete lifecycle. The
Ardan Labs cache case is useful because a large inline cold array dominated a
hot metadata scan; it is not a general rule that slices beat arrays.

When testing several layout candidates, start each from the same baseline and
then combine only orthogonal winners. Reordering fields, splitting hot/cold
data, changing AoS/SoA, batching, and prefetching can compete for the same cache
effect. Use the combination and regression protocol in
[the optimization experiment framework](../../golang-optimization/references/experiment-framework.md).

## False Sharing

Suspect false sharing only when multiple cores write independent fields that
occupy the same cache line and throughput degrades with concurrency. Required
evidence:

- single-thread versus multi-thread scaling;
- per-worker or per-shard access ownership;
- hardware counters or a repeatable padding experiment;
- `-race` plus correctness tests;
- measured struct/array footprint after padding.

On supported Linux hosts, `perf c2c record` / `perf c2c report` can help
attribute cache-line sharing. Record CPU/kernel support, permissions, lost or
unsupported events, and the exact symbol/address mapping. A padding experiment
plus throughput alone is proxy evidence when cache-to-cache counters are
unavailable; label it accordingly.

Do not hardcode 64-byte padding without recording the release architecture's
cache-line size. Padding increases working-set size and can make read-heavy or
large-array workloads worse.

## Acceptance Gate

Keep a locality change only when:

- the same public benchmark improves statistically;
- allocations, retained heap, and GC do not regress beyond an accepted trade;
- counter evidence improves, or the working-set crossover and access model
  jointly support the explanation;
- behavior, ordering, ownership, and canonical representation remain unchanged;
- small and large workloads are both reported;
- rejected layout variants are removed.

Also reject a layout candidate when it improves one working-set size but moves
the production crossover below the normal footprint, when reduced cache misses
are offset by more cycles, or when padding/code/data tables increase the
complete process footprint enough to regress another protected path.

The source material motivating this workflow is Ardan Labs'
[“Getting Friendly With CPU Caches”](https://www.ardanlabs.com/blog/2023/07/getting-friendly-with-cpu-caches.html);
use its measure-first approach, not its specific array-to-slice transformation
as a default prescription.
