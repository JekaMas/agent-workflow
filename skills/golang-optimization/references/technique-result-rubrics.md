# Go Optimization Result Rubrics

Use this reference after running the experiment matrix. The labels classify a
measured result, not a technique in isolation. A result cannot be `good` or
`best` when correctness fails, evidence is not representative, or a protected
metric exceeds its regression budget.

- [Common classification](#common-classification)
- [Per-technique rubrics](#per-technique-rubrics)
- [How to distinguish close outcomes](#how-to-distinguish-close-outcomes)

## Common Classification

| Label | Meaning |
|---|---|
| Really bad | Correctness, ownership, portability, or an exact resource gate fails; scaling worsens; cost is merely moved; or the protected public path regresses beyond budget. Revert. |
| Normal | Difference is indistinguishable from noise, below the practical threshold, or confined to an unimportant kernel. Keep the simpler baseline. |
| Good | The named owner and public path improve by a statistically credible and practically useful amount, with protected rows inside budget. |
| Best | The measured owner is eliminated or near its demonstrated lower bound, the public path realizes the expected share of that win, and the result survives workload, architecture, lifecycle, and holdout checks without extra unjustified complexity. |

`Best` does not mean zero nanoseconds, zero allocations, or the largest
percentage. It means best among valid candidates for the production contract.
For example, one required owned return allocation can be optimal, while a
zero-allocation alias that violates lifetime ownership is really bad.

For a leaf technique not named separately, use its family row and add the
exact mechanism-specific gates from that technique's reference. For example,
preallocation uses the escape/allocation row plus retained-capacity checks;
`sync.Map` uses the maps/dispatch row plus key-distribution and memory checks.

## Per-Technique Rubrics

| Technique | Really bad | Normal | Good | Best | Distinguishing evidence |
|---|---|---|---|---|---|
| Work elimination / algorithm | New unbounded work, worse size slope, changed output/order, or setup moved outside timing | Same slope and work count; timing delta below threshold | Fewer operations/rows/bytes and a public-path win across production sizes | Entire redundant stage removed or asymptotic slope improved, with unchanged semantics | Instrumented operation counts, size-slope benchmark, CPU/wall profile, public benchmark |
| Representation / locality | More bytes, pointer chasing, cache misses, retained memory, or conversion at another boundary | Layout changes but bytes visited, misses, and public time do not | Fewer bytes/conversions/misses with bounded memory and public gain | Hot working set crosses a cache boundary or conversion owner disappears across the lifecycle | Bytes touched, object/scan counts, cache crossover and PMU counters, encode/decode/readback benchmarks |
| Escape / allocation | Allocation moves to wrapper/caller, retention grows, or stack/frame growth harms fanout | Escape line changes but `B/op`, `allocs/op`, GC, and public time do not | Named allocation count/bytes fall and allocation profile confirms ownership removal | All avoidable allocations in the public path are gone; required ownership allocations are isolated and documented | `benchmem`, `alloc_space`/objects, `inuse` profile, `-m=2`, frame size, lifecycle memory |
| Pointer density / barriers | Copies or index maintenance exceed scan/barrier gain; correctness or visibility weakens | Pointer count changes without material GC/mutation-path effect | Lower scan work, object count, or barrier CPU with stable update cost | Hot state is pointer-free or immutable where appropriate and GC owner becomes negligible | `/gc/scan/*`, heap objects, barrier frames/assembly, mutation and traversal benchmarks |
| Inlining / devirtualization | Code growth raises I-cache misses, binary size, build time, or minority-path latency | Compiler output changes but generated hot path/public benchmark does not | Hot call, boxing, or interface dispatch disappears and public path improves | Dispatch owner is removed across common shapes with bounded code size and no holdout regression | `-m=2`, generated call sites, objdump, binary/text size, kernel and public benchmarks |
| BCE / SSA / register shape | Source contortion adds spills, larger frames, `morestack`, checks, or slower error paths | Diagnostic changes without fewer instructions/cycles or public gain | Targeted checks/reloads/spills fall and loop/public path improves | Hot loop is check-free at the proven bounds and near the scalar instruction lower bound | BCE/SSA diagnostics, objdump, frame/spill counts, cycles/instructions, boundary tests |
| Branch/layout/SWAR | Branchless path adds instructions and regresses predictable production data, tails, or invalid cases | Miss rate changes but cycles/public time do not, or wins only on synthetic random input | Cycles fall across observed distributions without code-size or edge-case regression | Selected scalar kernel minimizes work across the production mix and remains robust at adversarial distributions | Outcome distributions, branches/misses, cycles/instructions, assembly, common/alternating/random benchmarks |
| SIMD / assembly / intrinsics | Dispatch/call/tail overhead erases gain; unsupported CPU, race, memory, or correctness failure | Kernel wins below a batch crossover absent from production | Production batch sizes improve materially and all tails/architectures remain correct | Dominant kernel approaches measured machine throughput and public path captures the gain with acceptable maintenance | Batch crossover, CPU-feature matrix, code size, assembly, cycles/byte, fuzz/property and public benchmarks |
| PGO | Training overfits; holdout or minority traffic regresses; profile is stale or nonrepresentative | Compiler changes are small or whole-program result is below threshold | Representative and holdout workloads improve without source/operational regressions | Broad whole-program gain survives retraining windows, deployment shapes, and toolchain rebuilds | `-pgo=off` A/B, profile coverage, compiler diff, representative and holdout service results |
| GC pacing / memory limit | OOM risk, thrashing, assist CPU, RSS, or p95/p99 worsens outside SLO | CPU-memory trade changes but no product objective improves | GC CPU or memory headroom improves while throughput and tails stay within budget | Target load, burst recovery, and maximum retained state meet CPU, RSS, latency, and OOM-headroom goals together | GC CPU/assists/cycles, heap/RSS, runtime metrics, load ramps, tail latency, limit-pressure tests |
| Pools / reuse | Stale state/aliasing, retention, contention, or cross-P misses exceed saved churn | Pool hit rate or allocations change without public/GC gain | Temporary allocation owner falls with bounded retained capacity and no mutex owner | Reuse removes dominant churn at production concurrency while misses/reset/retention remain negligible | Hit/miss/size distribution, `benchmem`, heap, mutex/CPU profiles, reset and ownership tests |
| Scheduler / goroutines | Leaks, unbounded queues, lost cancellation, starvation, or worse tails under saturation | Worker count changes but runnable delay, throughput, and tails do not | Runnable/queue delay or saturation improves with bounded ownership and shutdown | Concurrency matches CPU/downstream capacity over load ramps with bounded queues and stable tails/recovery | Go trace, queue/goroutine counts, utilization, throughput, p50/p95/p99, cancellation/shutdown tests |
| Locks / atomics / sharding | Race, ABA/reclamation issue, deadlock, starvation, skew collapse, or invariant loss | Primitive changes but contention is absent or public result unchanged | Contention and tails fall on actual key/read-write distributions with race/fairness proof | Measured contention owner becomes negligible without sacrificing progress, invariants, or portability | Mutex/block/trace profiles, skew matrix, race/stress/PBT, fairness/progress and public load tests |
| Maps / dispatch / reflection | Boxing, hashing, code size, memory, or maintenance exceeds removed overhead | Lookup/dispatch kernel changes but public allocation/time does not | Hash/boxing/reflection owner falls across production cardinality and hit/miss mix | Reflective or repeated dynamic planning leaves the hot loop and remaining lookup is near representation cost | Cardinality/hit-mix benchmarks, allocation/profile, generated calls, heap and binary size |
| IO / syscall / cgo batching | Partial IO, deadlines, cancellation, fairness, or latency breaks; batches grow unbounded | Crossings fall but CPU/wall/public throughput does not, or batching delay offsets gain | Fewer crossings/copies improve throughput or CPU within latency and memory budgets | Protocol-required crossings/copies approach their lower bound across production message sizes | Instrumented calls/bytes, syscall profile, batch crossover, trace, p95/p99, partial/error/cancel tests |
| mmap / zero-copy / kernel path | Faults, RSS, truncation/lifetime hazards, or kernel stalls exceed copy savings | Go heap falls but total RSS/wall time does not | Copies/CPU fall with acceptable faults, RSS, and ownership behavior | Kernel/data path is near minimum-copy for the contract and stable across cold/warm working sets | Major/minor faults, RSS/page cache, copied bytes, kernel/off-CPU evidence, cold/warm latency |
| NUMA / placement | Remote traffic, migrations, scheduler restriction, failover, or single-node behavior worsens | Placement changes without stable per-node or service gain | Remote-memory/migration owner falls on supported fleet shapes | Stable ownership and placement produce repeatable whole-service gain across target hosts without operational fragility | Per-node counters, affinity/cgroup state, migrations, cross-host throughput/tails and failover tests |

## How To Distinguish Close Outcomes

Apply these checks in order:

1. **Validity:** all correctness, race, fuzz/property, ownership, wire, and
   lifecycle tests pass. Otherwise the result is really bad regardless of
   speed.
2. **Comparability:** revisions differ only by the candidate; commands,
   fixtures, toolchain, environment, and timed boundaries match. Otherwise the
   result is inconclusive, not good.
3. **Statistical evidence:** repeated samples show a stable direction under the
   chosen test. A confidence interval crossing no change or a comparison marked
   insignificant is normal/inconclusive.
4. **Practical evidence:** the effect exceeds the declared product threshold
   and baseline variance. A tiny statistically real result can still be normal.
5. **Owner evidence:** the motivating profile/counter/escape/scan owner moves in
   the predicted direction. If not, investigate a confounder.
6. **Public capture:** the production path captures a plausible fraction of the
   kernel win. A large kernel-only win is normal for shipping purposes.
7. **Protected matrix:** exact resources remain within exact gates and noisy
   metrics remain within budgets. One protected regression makes the candidate
   really bad unless explicitly approved as a product trade.
8. **Complexity:** among equally good candidates, the simpler portable one is
   best. Unsafe, assembly, runtime-sensitive, and operational mechanisms need a
   larger demonstrated benefit and support matrix.

After a large win, reprofile. If the original owner disappears and another
frame becomes dominant, the optimization succeeded and the bottleneck moved;
do not call the remaining frame a regression without comparing absolute work.
