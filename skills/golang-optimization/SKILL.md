---
name: golang-optimization
description: Implement or review Go performance fixes after diagnostics identify the owner, workload and baseline.
---

# Go Optimization

## Prerequisite

Use
[golang-performance-diagnostics](../golang-performance-diagnostics/SKILL.md)
first when the baseline, owner, workload distribution, profile, escape output,
cache/branch counters, DB scan counts, or before/after comparison is missing.

## Non-Negotiables

- Do not patch from intuition or one hot frame alone.
- Require a performance question, protected behavior, target workload, and
  relevant correctness tests.
- If determinism can be affected, the user or repo context must define where
  determinism is required before changing ordering, canonical bytes, receipts,
  hashes, persisted state, or execution output.
- For new benchmarks or implementation changes made primarily for performance,
  preserve the benchmark-plan approval gate. Reuse applicable approval already
  granted by the user or campaign; do not ask again for the same plan. If it is
  missing or the plan materially changes, present the concrete plan for approval
  before editing the benchmark or performance implementation.
- Estimate possible impact before editing: a 5% frame cannot produce a 20%
  total win.
- Classify the expected result as local-kernel, public-path, memory/GC, or
  whole-system. Do not attach a universal percentage to a technique; bound the
  expected total result by the measured owner and removable work. Use
  [references/technique-expectation-matrix.md](references/technique-expectation-matrix.md).
- Benchmark the production API and equivalent isolated kernel in the same
  binary. Treat the kernel as a measured ceiling, not proof that validation,
  generic dispatch, ownership, or wrapper work can disappear.
- Match production input shapes and distributions: lengths, widths, valid and
  invalid ratios, branch outcomes, cache hits and misses, retained and newly
  formatted values, numeric limb counts, field counts, and batch sizes.
- Keep each candidate change narrow and attributable, but schedule independent
  candidates as one experiment batch. Do not rerun the full protected matrix
  after each edit when one controlled candidate wave can compare them.
- Treat multiple possible implementations as controlled experiments. Define
  the candidate and regression matrices before editing, measure candidates from
  the same baseline in one controlled command/wave, then combine the selected
  non-conflicting candidates and run one protected interaction matrix. Use
  [references/experiment-framework.md](references/experiment-framework.md).
- Give each candidate the cheapest representative microbenchmark or diagnostic
  probe that can falsify its predicted local effect. Reject failed probes before
  profiles, full distributions, protected matrices, lint, or broad tests. Only
  surviving candidates enter the complete correctness/performance cycle.
- For allocation fixes justified by escape-analysis evidence, explicitly
  re-run escape analysis after the patch and compare it with before/after
  benchmark `B/op` and `allocs/op`. Do not call an escape-allocation fix
  complete from benchmarks alone, and do not call it complete from escape
  output alone.
- An allocation fix must reduce or shorten the lifetime/ownership of the
  allocation. Moving the same short-lived allocation to a caller, callee,
  wrapper, helper, or nearby stack frame is not an optimization unless
  before/after evidence proves lower `B/op`, lower `allocs/op`, shorter
  retention, or fewer calls on the target workload.

## Workflow

1. Confirm evidence exists: `benchstat` or comparable benchmark output plus the
   profile/trace/escape data that names the owner.
2. Classify the fix: less work, better algorithm, better data representation,
   better locality, lower allocation churn, lower retained heap, less lock/wait
   time, fewer DB/IO/syscall boundaries, or compiler/runtime machinery.
3. Build the complete candidate matrix before editing. Keep each variable
   independently attributable, but implement independent candidates before the
   planned measurement wave instead of alternating edit and full rerun. Remove
   rejected implementations; do not leave numbered variants, compatibility
   paths, or dormant fallbacks.
4. Start with the simplest source-level change that can plausibly hit the
   target. Escalate to PGO, pooling, atomics, unsafe, SIMD, cgo, assembly, or
   scheduler knobs only after their specific evidence gate is satisfied.
5. Preserve correctness, accepted syntax, canonical bytes, determinism,
   ownership, cancellation, boundedness, and stop/join behavior. Keep
   normalization and canonicalization at their approved constructors or
   boundaries, never as incidental hot-path work.
6. Run one invalidated correctness wave, one controlled protected benchmark
   matrix, and the diagnostics invalidated by the selected batch. For
   compiler-aware changes, rerun inlining, BCE, disassembly, escape, branch, or
   cache evidence as applicable in the same diagnostic wave.
7. Report accepted and rejected candidates, protected-path regressions,
   residual ownership costs, portability, and toolchain revalidation gates.

### Reversible Dirty Experiment Gate

Use an uncommitted production edit as a measurement probe only after a CPU,
allocation, trace, compiler, or DB artifact names the owner and the protected
behavior already has tests:

1. Record the exact dirty-state classification and preserve unrelated work.
2. Change one variable without adding compatibility code or running broad tests.
3. Run the same targeted production-shaped benchmark 3-5 times with unchanged
   fixtures, CPU settings, timing mode, and logging mode.
4. If the result is neutral, noisy, or regresses a protected row, remove only
   the experiment completely. Do not retain a dormant toggle or fallback.
5. If it wins, restore required observability and ownership, add or strengthen
   focused behavior tests and benchmarks, then rerun the benchmark, diagnostic,
   escape analysis when allocations are involved, and relevant tests.

An experiment result is candidate-selection evidence, not completion evidence.
Only the correctly owned and tested implementation may be committed.

When more than one candidate survives independently, do not add their reported
wins. Combine the selected candidates, then run one full protected interaction
matrix against the original baseline. If the combination regresses or fails to
match the candidate evidence, isolate it with the smallest discriminating
sub-benchmark or bisection; do not restart the entire matrix after every edit.
Compiler, branch, cache, allocation, and PGO effects can overlap or reverse one
another.

For escape/allocation work, the diagnostic comparison must include:

- exact before/after benchmark rows with `ns/op`, `B/op`, and `allocs/op`;
- the specific escape-analysis lines that changed, disappeared, or remained;
- an ownership/lifetime comparison showing whether allocation ownership moved,
  disappeared, became shorter-lived, or remains retained by contract;
- a classification of remaining escapes as fixable, cold/error-only,
  trace-only, or retained-by-contract;
- a rejection reason for any escape that remains intentionally.

## Advanced Mechanism Gate

Before PGO, pooling, sharding, atomics, unsafe, cgo, SIMD, assembly, prefetch,
or scheduler/runtime knobs, record:

- the simpler source-level fixes tried or rejected and why they are
  insufficient;
- the exact profile, counter, compiler, disassembly, or trace evidence naming
  the remaining cost;
- the ownership, pointer-lifetime, scheduling, canonical-ordering, ABI, and
  architecture risks that apply;
- correctness, race, `checkptr`, fuzz/property, cross-build, and deterministic
  output tests required by the mechanism;
- Go/toolchain/OS/architecture support and upgrade revalidation;
- rollback by reverting the selected implementation, not by retaining a
  dormant production fallback.

## Result Check

When deciding whether an optimization worked:

- Compare the protected benchmark rows before and after with the same command
  shape, `GOMAXPROCS`, `-count`, `-benchmem`, fixtures, and workload.
- Use available machine CPUs for all test and benchmark processes. Set Go test
  `-parallel` to the detected CPU count; do not lower `GOMAXPROCS`, package
  parallelism, or test parallelism preemptively for shared global state. Fix a
  concurrent failure by making state test-owned. If that isolation requires a
  disproportionate redesign, omit `t.Parallel` only on the affected test and
  leave a comment naming the global owner. Never infer application concurrency
  from `GOMAXPROCS`; report it separately from application worker controls. A
  single-worker application row is allowed only inside an explicit scaling
  matrix and does not serialize the surrounding Go test process.
- For allocation work, check both the benchmark counters and the allocation
  owner/lifetime:
  - accepted: allocation disappears, `B/op` or `allocs/op` drop, retained heap
    drops, the allocation becomes shorter-lived, or call count drops on the
    target workload;
  - rejected: the same allocation is merely moved to a caller, callee, wrapper,
    helper, setup path, or nearby stack frame without reducing benchmark
    allocation counters, retention, lifetime, or target-workload calls;
  - documented: allocation remains because ownership is retained by contract
    (for example DB keys, action payloads, durable logs, cached values, or
    result structs).
- If the benchmark improves but escape analysis shows the same owner moved,
  explain why the benchmark improvement is real and not fixture/setup movement.
- If escape analysis improves but `B/op` and `allocs/op` do not, do not accept
  the slice without another measured benefit such as reduced retained heap,
  lower GC pressure, or fewer target-workload calls.

## References

- Select the technique family and set evidence, payoff, risk, and acceptance
  expectations:
  [references/technique-expectation-matrix.md](references/technique-expectation-matrix.md).
- Classify measured outcomes as really bad, normal, good, or best for the
  selected technique:
  [references/technique-result-rubrics.md](references/technique-result-rubrics.md).
- Plan, isolate, compare, combine, and regression-control multiple candidate
  implementations:
  [references/experiment-framework.md](references/experiment-framework.md).
- Choose the fix class and common patch shape:
  [references/optimization-catalog.md](references/optimization-catalog.md).
- Apply decision algorithms, metrics, and code examples:
  [references/optimization-decision-playbook.md](references/optimization-decision-playbook.md).
- Use concrete algorithm, decimal, serialization, DB, layout, and workload
  findings:
  [references/optimization-technique-notes.md](references/optimization-technique-notes.md).
- Trace escape ownership and validate allocation fixes:
  [references/escape-analysis.md](references/escape-analysis.md).
- Analyze branch prediction, branchless arithmetic, `perf stat`, generated
  assembly, and `segmentio/asm`:
  [references/branching-and-branchless.md](references/branching-and-branchless.md).
- Evaluate inlining, BCE, disassembly, SWAR/SIMD, unsafe, cgo, architecture
  files, cache-line padding, and prefetch:
  [references/compiler-and-machine-code.md](references/compiler-and-machine-code.md).
- Evaluate pooling, sharding, `sync.Map`, `sync.Cond`, atomics, weak references,
  reflection, `heap.Fix`, and scheduler knobs:
  [references/runtime-and-concurrency-techniques.md](references/runtime-and-concurrency-techniques.md).
- Evaluate pointer density, write barriers, GC pacing and memory limits, stack
  growth, retention, and experimental arenas:
  [references/memory-gc-and-lifetime-techniques.md](references/memory-gc-and-lifetime-techniques.md).
- Evaluate maps, interfaces, generics, reflection plans, and zero-copy
  representation boundaries:
  [references/data-structures-and-dispatch.md](references/data-structures-and-dispatch.md).
- Evaluate `io.Copy` fast paths, vectored IO, netpoll, mmap, raw syscalls, cgo
  crossings, and NUMA/process placement:
  [references/io-network-and-system-techniques.md](references/io-network-and-system-techniques.md).
- Reuse MDBX cursors, exploit ordered fixed-width keys, choose monotonic seeks
  versus contiguous scans, and reject unjustified probabilistic summaries:
  [references/mdbx-ordered-cursor-optimization.md](references/mdbx-ordered-cursor-optimization.md).
- Evaluate whole-program PGO after source-level optimization:
  [references/profile-guided-optimization.md](references/profile-guided-optimization.md).
- Measure cache hits and misses, locality, working-set crossovers, and false
  sharing before layout changes:
  [CPU cache analysis](../golang-performance-diagnostics/references/cpu-cache-analysis.md).

## Report Shape

Include the question, protected behavior, production workload, baseline,
candidate matrix, selected and rejected changes, benchmark/profile/compiler or
counter comparison, allocation owners, advanced-risk decision, tests,
portability, rollback, upgrade revalidation, and remaining uncertainty.
