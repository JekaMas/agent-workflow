---
name: golang-performance-diagnostics
description: Diagnose Go CPU, allocation, memory, concurrency or I/O costs with workload evidence before optimization.
---

# Go Performance Diagnostics

## When To Use

Use this skill first for any Go performance or optimization task, including:

- reducing allocations, heap growth, GC pressure, retained memory, or object churn;
- improving latency, throughput, lock/wait time, syscall/IO time, or CPU cost;
- interpreting `go test -bench`, `benchstat`, `pprof`, `go tool trace`, runtime metrics, or production performance data;
- finding where allocations happen with allocation profiles and escape analysis;
- measuring cache references and misses, branch misses, working-set crossovers,
  locality, DB calls, rows scanned, and cache-line contention;
- deciding whether an optimization is justified before touching code.

Do not start with `golang-optimization`. It comes after this diagnostic pass
has produced a named owner, target workload, baseline, and artifact-backed
hypothesis.

## Non-Negotiables

- Start with a performance question, target workload, protected behavior, and
  out-of-scope list.
- Before proposing or implementing a Go optimization, capture at least one
  diagnostic artifact that identifies the owner. For allocation work, include
  both exact benchmark rows and either an allocation profile or escape-analysis
  evidence; use both when the user asks for allocation sources.
- Capture baseline context: `go version`, `go env GOOS GOARCH GOVERSION GOMOD
  GOWORK`, package, benchmark regex, command, `-count`, `-benchtime`,
  `-benchmem`, artifact paths, and repo constraints.
- Use targeted reads for large artifacts. Size-check, search, filter, summarize,
  or open a narrow window first. Do not inspect unknown-size logs/profiles with
  broad `cat`, `sed`, `head`, or `tail`.
- Do not recommend `GODEBUG=allocfreetrace=1` unless the active Go toolchain
  documentation and a local capability check prove support.
- If diagnostics identify a fix, hand off to
  [golang-optimization](../golang-optimization/SKILL.md), including for
  advanced compiler, architecture, concurrency, and runtime-sensitive work.

## Workflow

1. Reproduce with the targeted correctness tests and one planned baseline
   benchmark wave. Group independent benchmark packages into the same launch
   wave, but isolate workloads whose distributions, profiles, DB scaling, or
   acceptance thresholds would be distorted by competing CPU, memory, or IO.
2. Choose the diagnostic that answers the question: CPU, allocation churn,
   retained heap, escape cause, GC context, cache/branch behavior, DB scan
   shape, lock/channel wait, scheduler delay, syscall/network wait, or
   before/after delta.
3. Capture one profile/trace type at a time for final numbers unless the task is
   explicitly exploratory.
4. Convert bulky artifacts to focused text reports for review.
5. Interpret sample indexes and percentages before proposing code changes.
6. Report artifact paths, commands, summary numbers, and the next fix class.

Treat Go scheduler capacity and application worker limits as independent
variables. Unless measuring a scheduler matrix, do not hard-code `GOMAXPROCS`
or `-cpu`; use the machine default, report `runtime.GOMAXPROCS(0)`, and report
application concurrency separately.

When a named owner has several plausible low-risk fixes, the diagnostic handoff
may propose a reversible dirty experiment: one production variable, 3-5
same-shape targeted benchmark runs, no broad test gate during candidate
selection, and complete removal of rejected edits. The caller's current task
authority and retained benchmark-plan approval govern execution; diagnostic
evidence does not grant mutation permission. The optimization skill owns the
protocol and required correctness/profile/escape evidence.

Do not run a separate baseline command for every independent finding when one
benchmark regex or one controlled wave can capture the complete matrix. Capture
all required baseline rows before production optimization, then reuse them
until their workload, fixture, dependency, toolchain, or measured owner changes.

## References

- Benchmark design and reading `ns/op`, `B/op`, `allocs/op`:
  [references/benchmarking.md](references/benchmarking.md).
- CPU, heap, allocation, trace, block, mutex, GC, metrics, labels, and escape
  interpretation:
  [references/profiling-and-tracing.md](references/profiling-and-tracing.md).
- Before/after benchmark, pprof, trace, escape, and BCE comparisons:
  [references/performance-diffs.md](references/performance-diffs.md).
- CPU cache counters, working-set benchmarks, locality, and false-sharing
  diagnostics:
  [references/cpu-cache-analysis.md](references/cpu-cache-analysis.md).
- Syscall/copy counts, netpoll and page-fault evidence, eBPF/off-CPU analysis,
  cgroup throttling, and kernel attribution:
  [references/kernel-and-io-analysis.md](references/kernel-and-io-analysis.md).
- Interpret tests, benchmarks, `benchstat`, profiles, traces, compiler output,
  PMU counters, runtime metrics, and A/B diffs:
  [references/interpreting-performance-results.md](references/interpreting-performance-results.md).
- Text-first commands, filtering, targeting, and live pprof extraction:
  [references/text-artifacts-and-targeting.md](references/text-artifacts-and-targeting.md).

## Core Commands

```bash
go test ./your_package -run '^$' -bench '^BenchmarkName$' -benchmem
go test ./your_package -run '^$' -bench '^BenchmarkName$' -cpuprofile=cpu.out
go test ./your_package -run '^$' -bench '^BenchmarkName$' -memprofile=mem.out -memprofilerate=1
go test ./your_package -run '^$' -bench '^BenchmarkName$' -trace=trace.out
go build -gcflags='all=-m=2' ./your_package
go tool pprof -top -diff_base old.cpu.pprof new.cpu.pprof
go tool trace -pprof=sched trace.out > sched.pb.gz
GODEBUG=gctrace=1 go test ./your_package -run '^$' -bench '^BenchmarkName$' -benchmem
```

## Report Shape

Include the question, workload, protected behavior, exact commands, artifact
paths, benchmark comparison, profile/trace/escape interpretation, and the
smallest evidence-backed next step.
