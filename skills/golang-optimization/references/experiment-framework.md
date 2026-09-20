# Go Optimization Experiment Framework

Use this reference when more than one algorithm, representation, compiler
shape, architecture path, or runtime mechanism could solve the measured
problem. It turns candidate exploration into reproducible experiments and
prevents individually attractive changes from combining into a regression.

Contents: experiment contract, benchmark and candidate matrices, independent
trials, result classification, combination trials, regression control,
environment control, and the final decision record.

- [Experiment contract](#experiment-contract)
- [Benchmark matrix](#benchmark-matrix)
- [Candidate matrix](#candidate-matrix)
- [Independent trials](#independent-trials)
- [Result classification](#result-classification)
- [Combination trials](#combination-trials)
- [Regression control](#regression-control)
- [Technique-specific controls](#technique-specific-controls)
- [Final decision record](#final-decision-record)

## Experiment Contract

Record this before changing production code:

```text
Question: Which implementation reduces confirmed-bar decode CPU?
Production owner: package.Type.Method, called by path A -> B -> C.
Primary workload: 70% one-limb values, 25% two-limb, 5% wider.
Protected behavior: exact value, canonical bytes, error precedence, bounds.
Primary metric: ns/op at the public API.
Secondary metrics: B/op, allocs/op, cycles/op, instructions/op, code bytes.
Regression budget: no new allocation; <=2% common-path slowdown; no wire drift.
Environment: revision, Go version, GOOS/GOARCH, CPU, GOMAXPROCS, command.
```

The regression budget is a decision boundary, not a claim that measurements
are noise-free. Set it from product/SLO requirements and baseline variance.
Allocation counts, DB calls, rows scanned, wire bytes, and canonical output are
often exact constraints; elapsed time and hardware counters require repeated
samples and a practical effect threshold.

## Benchmark Matrix

Benchmark the production API and the equivalent isolated kernel. The kernel
estimates the algorithmic ceiling; only the public row authorizes production
selection.

Define dimensions before coding:

| Dimension | Required examples |
|---|---|
| Value shape | zero, short/common, boundary, maximum width, overflow/invalid |
| Distribution | production mix, homogeneous, random, alternating, bursty, sorted |
| Output ownership | caller-owned append, exact-capacity, growth, owned return |
| Working set | hot/L1-sized, L2/LLC crossover, larger than LLC |
| Batch | 1, common batch, SIMD/call crossover, maximum supported |
| Reuse | cold, warm, retained representation/cache hit and miss |
| Concurrency | single worker and representative contention when applicable |
| Architecture | every release GOOS/GOARCH/CPU level affected by the candidate |

Keep fixture construction, input conversion, randomization, cache-thrashing,
and result verification outside the timed region. Precompute random or trace
orders; never use `b.N` to size the workload.

## Candidate Matrix

Each row must state why it can affect the measured owner and what evidence can
reject it:

| ID | Candidate | Expected owner change | Required diagnostic | Main risk |
|---|---|---|---|---|
| C0 | current production | baseline | benchmark + profile | none |
| C1 | scalar algorithm | fewer operations | CPU profile + disassembly | width/error paths |
| C2 | branchless/SWAR | fewer misses/instructions | `perf stat` + assembly | predictable inputs |
| C3 | batch SIMD/asm | more values per call | crossover benchmarks | call/tail/portability |
| C4 | compact layout | fewer bytes visited | cache counters/crossover | GC/pointer chasing |
| C5 | PGO | whole-program compiler decisions | app profile + compiler diff | workload overfit |

Do not include a candidate merely because it is sophisticated. A candidate
without a named owner, plausible upper bound, and rejection diagnostic is not
ready to implement.

## Independent Trials

1. Capture baseline correctness, benchmark, profile/counter, compiler, and
   storage/DB evidence required by the question.
2. Start every candidate from the same baseline revision. Change one causal
   variable; do not combine a new algorithm, layout, cache, and unsafe loader in
   one trial.
3. Run the focused correctness suite before performance measurement.
4. Run the identical benchmark command with the same toolchain, CPU policy,
   fixtures, repetition count, and benchtime.
5. Compare with `benchstat` or equivalent statistics and the diagnostic that
   motivated the candidate.
6. Reject candidates that win only in the isolated kernel, one synthetic
   distribution, setup excluded from production, or an unsupported CPU path.
7. Remove rejected code. Preserve its command, measurements, and rejection
   reason in the report, not as a dormant implementation.

Minimal artifact shape:

```bash
go test ./path/to/pkg -run '^$' -bench '^BenchmarkTarget/' \
  -benchmem -benchtime=3s -count=15 > "$ART/C0/bench.txt"
# Run the identical command from the isolated candidate revision into C1.
benchstat "$ART/C0/bench.txt" "$ART/C1/bench.txt" \
  > "$ART/C1/benchstat-vs-C0.txt"
```

Store the revision, command, environment, fixture hash, correctness result, and
diagnostic artifacts beside each candidate result.

When thermal drift, frequency scaling, or shared-host noise is material, run
baseline and candidate in alternating or randomized order. Compile stable test
binaries first. Record CPU affinity, governor/power mode, background load, and
PMU multiplex percentage when those controls are available; otherwise state
the limitation instead of implying laboratory precision.

## Result Classification

Classify every candidate before combining it:

| Class | Decision rule |
|---|---|
| Really bad | Correctness/exact gate fails, protected regression exceeds budget, scaling worsens, or work is moved rather than removed. Revert. |
| Normal | Timing is indistinguishable, below practical significance, or limited to an unimportant kernel. Keep the baseline. |
| Good | Statistical and practical public-path improvement, predicted owner reduction, and protected matrix all agree. |
| Best | Best valid candidate reaches or approaches the measured owner/lower bound across production and holdout matrices with the least justified complexity. |

Read raw outputs and A/B signs with
[the diagnostics interpretation guide](../../golang-performance-diagnostics/references/interpreting-performance-results.md),
then apply the per-family criteria in
[technique-result-rubrics.md](technique-result-rubrics.md). Do not promote a
candidate because one percentage is green. Statistical significance,
practical significance, causal owner movement, public-path capture, and
protected-resource gates are separate decisions.

## Combination Trials

Independent percentage wins are not additive. Two changes can remove the same
instructions, alter inlining, increase code footprint, change cache residency,
or move the bottleneck.

1. Rank independently accepted candidates by public-path gain, risk, and
   architectural scope.
2. Select the simplest winning candidate as `S0`.
3. Combine independently accepted orthogonal candidates in one selected stack;
   run the primary/protected interaction matrix and relevant diagnostics once.
4. If the stack regresses, isolate the interaction with the smallest useful
   sub-benchmark or bisection, then rerun invalidated proof. Use incremental
   combinations only when a concrete interaction question justifies them.
5. For a small set of interacting candidates, test both application orders or
   the relevant pairwise combinations. Use a full factorial matrix only when
   the candidate count and build cost make it practical.
6. Reprofile the final stack. Do not assume the original hot owner remains the
   owner after earlier wins.

Example decision table:

| Stack | Common | Wide | Invalid | B/op | Branch misses | Code bytes | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| C0 | baseline | baseline | baseline | baseline | baseline | baseline | reference |
| C1 | -12% | -4% | +1% | same | same | +0.5% | accept |
| C2 | -9% | -8% | +15% | same | -60% | +3% | reject |
| C1+C3 | -14% | -22% | +1% | same | same | +8% | accept if batch mix pays |

If the combined stack gains less than measurement noise over the simpler
stack, keep the simpler stack. If one candidate changes semantics, canonical
bytes, ownership, failure timing, ordering, or accepted inputs, it is not a
performance-only combination and needs the corresponding behavior approval and
red-first tests.

## Regression Control

Keep a protected matrix that is broader than the optimized row:

- public latency/throughput for common and minority workloads;
- `B/op`, `allocs/op`, retained heap, and GC scan work;
- cycles, instructions, branches/misses, and cache misses where measured;
- DB calls, cursor operations, rows scanned, syscalls, and wire bytes;
- binary/text size, build time, architecture coverage, and toolchain support;
- correctness, race, fuzz/property, deterministic bytes, and malformed input;
- cold/error paths when failure cost or precedence is contractual.

Use exact gates for exact quantities. Use repeated samples and both statistical
and practical significance for noisy timing/counter metrics. A statistically
detectable 0.3% win does not justify unsafe or assembly maintenance; a noisy
3% median movement does not prove a win. Report confidence, observed spread,
effect size, and the product-level threshold.

For CI, prefer correctness and exact-resource guards plus periodic controlled
performance runs. Shared CI timing thresholds are useful only after the runner
variance is measured and the threshold leaves enough margin to avoid flaky
failures while still detecting meaningful regressions.

## Technique-Specific Controls

- **Branchless/SWAR:** test observed, predictable, alternating, and random
  outcomes; compare branches, misses, instructions, cycles, and assembly.
- **SIMD/assembly:** measure scalar-call crossover, batches, tails, invalid byte
  positions, dispatch, pure-Go/release architectures, and code size.
- **Cache/layout:** measure bytes visited, sequential/random access, cache-level
  crossovers, object count, pointer chasing, GC scan, and false sharing.
- **PGO:** train on representative application profiles; evaluate both covered
  and holdout/minority workloads; compare source-only and source-plus-PGO.
- **Allocation:** pair benchmark counters with allocation profiles and escape
  lines; prove ownership disappeared or shortened rather than moved.
- **Database/storage:** instrument calls and rows seen; benchmark at retained
  history limits; do not infer scan complexity from a small fixture.

## Final Decision Record

Report:

1. baseline revision, environment, artifacts, and variance;
2. protected behavior and regression budgets;
3. benchmark and candidate matrices;
4. independent results and rejected candidates;
5. selected combination results and any investigated interactions;
6. final profile/counter/compiler/escape/DB evidence;
7. correctness and portability results;
8. selected implementation and why simpler alternatives were insufficient;
9. removed variants, rollback by revert, and Go/CPU/profile revalidation gates.

Only the selected implementation remains in production. The experiment record
preserves rejected knowledge without adding compatibility branches, runtime
fallbacks, or numbered algorithm versions.
