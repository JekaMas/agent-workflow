# Branching And Branchless Optimization

Use branchless techniques only after a profile identifies a hot condition and
representative inputs show that its outcome is costly or unpredictable.
Removing an `if` in source is not an optimization result.

References:

- [Branchless Programming in Go](https://codexplorer.medium.com/branchless-programming-in-go-when-every-nanosecond-counts-9912386595db)
- [CUHK branch-prediction lab](https://www.cse.cuhk.edu.hk/~ericlo/teaching/os/lab/13-Memory2/part3_1.html)
- [`segmentio/asm`](https://github.com/segmentio/asm)

Contents: evidence chain, hardware counters, assembly proof, candidate order,
`segmentio/asm` gate, interaction testing, and acceptance matrix. Use
[experiment-framework.md](experiment-framework.md) when comparing or combining
multiple branch, scalar, SWAR, SIMD, or layout candidates.

## Required Evidence Chain

1. Name the public hot path and branch-owning function from CPU/profile data.
2. Define realistic outcome distributions. Include predictable all-hit/all-miss,
   observed production ratios, 50/50 random, alternating, bursty, and sorted
   inputs when they are plausible.
3. Measure cycles, instructions, branches, and branch misses on a machine that
   exposes the hardware PMU.
4. Inspect generated assembly. An ordinary Go condition may already compile to
   `CMOV`/`CSEL`; bit arithmetic may still contain a branch.
5. Benchmark the isolated kernel and public operation with the same candidate.
6. Keep only candidates that improve the target distribution without an
   unacceptable protected-path regression.

The CUHK sorted-versus-unsorted exercise demonstrates the measurement method:
the same work and data can have very different prediction behavior after
ordering changes. It does not authorize sorting when ordering, latency, or the
sort cost differs in production. Include preprocessing and mutation costs in
the public benchmark.

## `perf stat`

Build one benchmark binary so compilation is outside the counter run:

```bash
go test -c -o "$ART/pkg.test" ./path/to/pkg
perf stat -x, -r 10 \
  -e task-clock,cycles,instructions,branches,branch-misses,cache-references,cache-misses \
  "$ART/pkg.test" -test.run '^$' -test.bench '^BenchmarkName$' \
  -test.benchtime=3s -test.count=1
```

Record:

- branch-miss rate: `branch-misses / branches`;
- misses per operation or processed item;
- IPC: `instructions / cycles`;
- instruction delta, because a lower miss rate can still lose after doing more
  arithmetic or loads;
- cache misses, because lookup-table branch removal can move cost into memory.

Pinning and PMU access are environment-specific. If `perf list` or
`/sys/bus/event_source/devices` does not expose a CPU PMU, report branch misses
as **not measured**. Do not substitute elapsed time and call it a counter
result. Virtualized Docker environments commonly omit hardware events; use a
bare-metal or PMU-enabled Linux runner for the final counter gate.

## Assembly Proof

```bash
go tool objdump -s 'package.function' "$ART/pkg.test" > "$ART/function.asm"
go test -c -gcflags='all=-S' -o "$ART/pkg.test" ./path/to/pkg \
  > "$ART/compiler-asm.log" 2>&1
```

On amd64 inspect `Jcc`, `CMOVcc`, `SETcc`, and vector compares/masks. On arm64
inspect conditional `B.*`, `CBZ/CBNZ`, `TBZ/TBNZ`, `CSEL/CSET`, and flag-setting
arithmetic such as `SUBS`. Ignore loop and benchmark-harness branches when the
question concerns one data-dependent condition.

## Candidate Order

Prefer readable ordinary operations first:

1. change data/order so the branch becomes predictable, if ordering semantics
   and total work permit it;
2. hoist invariant conditions or split homogeneous batches;
3. use `min`, `max`, `bits.*`, table lookup, or arithmetic masks where they
   preserve exact unsigned/signed semantics;
4. defer repeated validity branches to one final check only when failure timing
   and error precedence remain unchanged;
5. use SIMD/assembly libraries only after the scalar public path and batch
   crossover are measured.

Avoid clever signed min/max/clamp formulas that can overflow. Do not turn
fail-fast validation into unchecked arithmetic. Lookup tables must include
their cache footprint and bounds-check behavior in the benchmark.

## `segmentio/asm` Gate

`segmentio/asm` contains batch algorithms with generic Go fallbacks and
architecture-specific assembly for selected packages. Before importing it:

- verify the exact function semantics; generic ASCII validity is not decimal,
  UTF-8, JSON, or protocol grammar validation;
- inspect the package's build tags and `.s` files for every release
  architecture;
- compare the normal build with `-tags purego` where supported;
- benchmark lengths below and above the function-call/SIMD crossover;
- include conversion, alignment, tail, invalid-position, and dispatch costs;
- retain the dependency only when the public operation wins materially.

Treat the repository as a set of specialized packages, not as a general Go
SIMD-intrinsics layer. Reuse an existing operation only when its exact grammar,
tail handling, architecture dispatch, and ownership contract match. Otherwise
compare a small feature-scoped kernel with ordinary Go instead of pulling a
broad dependency for one primitive.

For short scalar tokens, an inlined SWAR or ordinary Go kernel can beat an
assembly call. SIMD usually pays when one call processes a sufficiently large
array or byte span.

## Interaction Testing

Branch arithmetic, table lookup, SWAR, SIMD, layout, and PGO can alter the same
instruction and cache costs. Measure each from one baseline, then combine the
accepted independent candidates in one selected combination. Run its protected
public-path/counter/disassembly matrix, then isolate a failed interaction with
the smallest discriminating check. An incremental combination campaign needs a
concrete interaction question; it is not the default after every edit.
Reject a combination when fewer branch misses are offset by more instructions,
table/cache misses, dispatch calls, code footprint, or minority-path cost.

## Acceptance Matrix

| Dimension | Required cases |
|---|---|
| Outcomes | all true, all false, observed mix, random 50/50, alternating/bursty |
| Input size | minimum, common, crossover, large batch, tail lengths |
| Semantics | boundaries, overflow/underflow, invalid position, exact error precedence |
| Machine code | before/after conditional branches, instructions, calls, vector path |
| Counters | cycles/op, instructions/op, branches/op, misses/op and miss rate |
| Public result | `ns/op`, throughput, `B/op`, `allocs/op`, correctness |
| Portability | release architectures, pure-Go path, race/checkptr/cross-build as applicable |

Reject a candidate when only a synthetic 50/50 benchmark wins, predictable
production input regresses, the compiler already emits equivalent branchless
instructions, branch misses fall while cycles rise, or an assembly dependency
duplicates a faster inlined kernel.
