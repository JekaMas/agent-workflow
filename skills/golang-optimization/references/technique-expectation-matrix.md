# Go Optimization Technique Expectations

Use this matrix after diagnostics identify the owner and before selecting an
implementation. Expected impact is bounded by the measured owner; no technique
has a universal percentage gain. After measurement, classify the result with
[technique-result-rubrics.md](technique-result-rubrics.md).

Primary orientation: [Go diagnostics](https://go.dev/doc/diagnostics),
[compiler pipeline](https://go.dev/src/cmd/compile/README),
[runtime internals](https://go.dev/src/runtime/HACKING),
[GC guide](https://go.dev/doc/gc-guide), and
[PGO guide](https://go.dev/doc/pgo/).

- [Impact model](#impact-model)
- [Technique matrix](#technique-matrix)
- [Cross-cutting expectations](#cross-cutting-expectations)
- [Version-sensitive mechanisms](#version-sensitive-mechanisms)

## Impact Model

Classify the promised result before implementation:

| Scope | Meaning | Required acceptance row |
|---|---|---|
| Kernel | One isolated arithmetic, parse, encode, or lookup kernel | Kernel plus unchanged public path; kernel-only wins do not ship |
| Public path | One production API or operation | End-to-end benchmark with production distributions and ownership |
| Memory/GC | Allocation rate, retained heap, scan work, or pause/assist cost | Allocation/heap profile, runtime metrics, and workload latency/throughput |
| Whole system | Scheduler, contention, IO, kernel, PGO, or deployment behavior | Representative load/service test and the lower-level diagnostic |

For serial CPU work, estimate the upper bound from the profile owner and the
fraction plausibly removable. For wall-time work, split CPU, GC, scheduler,
lock, syscall, storage, network, and queueing first; CPU-frame percentages do
not bound an IO or concurrency redesign in the same way.

## Technique Matrix

| Family | Use when evidence names | Expected result | Complexity / risk | Required acceptance |
|---|---|---|---|---|
| Work elimination / algorithm | repeated or poorly scaling work | Path or system gain; can exceed micro-tuning | Medium | Size/distribution slope, public benchmark, same semantics |
| Representation / locality | conversion churn, bytes visited, cache crossover | Path plus memory/GC gain | Medium | Counters/crossover, heap/GC, complete lifecycle |
| Escape / allocation | `alloc_space`, objects, or escape owner | Lower allocation/GC; CPU only if allocation is material | Low-Medium | `benchmem`, allocation profile, escape diff, ownership proof |
| Pointer density / barriers | GC scan or write-barrier frames | Memory/GC and mutation-path gain | Medium | `/gc/scan`, heap/object counts, barrier assembly/profile, lifecycle |
| Inlining / devirtualization | hot calls, interfaces, wrapper gap | Usually local/path; capped by call share | Medium | `-m=2`, final objdump, public benchmark |
| BCE / SSA / register shape | checks, spills, redundant loads, large frames | Local/path; often modest unless loop dominates | Medium | SSA/BCE, spills/frame diff, CPU profile, public benchmark |
| Branch/layout/SWAR | branch misses or fixed-width byte work | Distribution-dependent local/path gain | Medium | Observed/predictable/random distributions, PMU, assembly |
| SIMD / assembly / intrinsics | narrow kernel remains dominant after scalar work | Large kernel gain; public gain depends on call/batch crossover | High | CPU-feature matrix, tails, fuzz/property, code size, public path |
| PGO | stable representative executable profile | Whole-program CPU gain, workload-dependent | Medium | `-pgo=off` control, holdout traffic, compiler/profile diff |
| GC pacing / memory limit | GC CPU, assists, RSS, or limit pressure | System trade between CPU, heap, and latency | Medium-High | Load test, heap/RSS, GC CPU/assists, OOM headroom |
| Pools / reuse | temporary churn survives simpler ownership fixes | Allocation/GC gain; may add contention/retention | Medium | Hit/miss/reset distribution, retained heap, mutex/CPU profile |
| Scheduler / goroutines | runnable delay, fanout, queue or syscall stalls | Throughput/tail-latency gain | Medium-High | Trace, saturation, queue depth, goroutine count, p95/p99 |
| Locks / atomics / sharding | mutex/block owner and known access pattern | Contention gain; little benefit without contention | High | Race/stress/PBT, fairness, skew, mutex/block/trace evidence |
| Maps / dispatch / reflection | hash, boxing, dictionary, or reflective loop | Local/path CPU and allocation gain | Medium | Cardinality/hit mix, generated calls, allocations, binary size |
| IO / syscall / cgo batching | many small crossings or copies | Path/system gain proportional to crossings/copies removed | Medium-High | Syscall counts, bytes copied, trace, deadlines/cancellation |
| mmap / zero-copy / kernel path | copies/page cache/kernel wait dominates | System gain with ownership/lifetime trade | High | Faults/RSS, kernel evidence, truncation/lifetime/error tests |
| NUMA / placement | multi-socket remote-memory or migration evidence | System gain on specific fleet only | High | Per-node counters, affinity/placement, cross-host validation |

## Cross-Cutting Expectations

Every technique must specify:

- the production owner, workload distribution, protected behavior, and
  out-of-scope surfaces;
- a baseline artifact and a technique-specific diagnostic that can falsify the
  hypothesis;
- public-path results, not only helper or synthetic-kernel results;
- exact-resource regressions: allocations, retained bytes, DB rows/calls,
  syscalls, wire bytes, object count, binary/code size, and goroutine count;
- noisy-metric regressions: latency, throughput, cycles, instructions, misses,
  GC CPU, build time, and power/thermal limitations where relevant;
- correctness, race, fuzz/property, deterministic output, ownership, and
  cancellation tests appropriate to the mechanism;
- architecture, OS, CPU feature, Go version, and deployment revalidation gates;
- removal of rejected variants and rollback by reverting the selected change.

An optimization that merely changes where work is charged is not complete.
Examples include moving allocation to a wrapper, moving decode work from DB to
the caller, reducing branch misses while increasing cycles, lowering Go heap by
adding unmanaged mmap RSS, or reducing lock wait by creating unbounded queues.

## Version-Sensitive Mechanisms

Record `go version`, release notes, active `GOEXPERIMENT`, architecture feature
level, and runtime environment before relying on compiler or runtime behavior.

- Stack allocation, inlining, BCE, register allocation, map implementation,
  PGO, cgo overhead, GC, and scheduler defaults can change between Go releases.
- Experimental packages and features are evaluation candidates, not stable
  production defaults. Require an explicit support policy and remove the path
  if the experiment disappears or changes contract.
- The stable `gc` toolchain has PGO and linker dead-code elimination, but no
  general user-facing C/C++-style LTO switch. Do not invent an LTO expectation.
- Rebenchmark after toolchain upgrades even when source is unchanged; a source
  contortion that helped an older compiler may regress or become redundant.
