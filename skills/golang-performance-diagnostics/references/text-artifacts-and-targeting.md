# Text Artifacts and Targeting

Use this reference when profiles, traces, compiler output, or live pprof
endpoints must be converted into reviewable text for an LLM agent or code
review. Prefer small targeted reports over broad binary artifacts or raw logs.

For before/after profile, trace-derived profile, benchmark, or escape-analysis
comparisons, read [performance-diffs.md](performance-diffs.md).

These commands were checked against local `go1.26.2 darwin/arm64`.

Contents: target selection, CPU text reports, allocation/heap text reports,
call graphs, trace-derived text profiles, block/mutex text, live pprof text,
escape-analysis text, runtime diagnostics, and artifact hygiene.

## Target the Workload First

Profile one package and one benchmark family when possible. Each package uses a
separate test binary, and profile-generating `go test` flags leave `pkg.test`
behind for source/symbol analysis.

```bash
go test ./path/to/pkg \
  -run '^$' \
  -bench '^BenchmarkName$' \
  -benchmem \
  -cpuprofile=cpu.pprof \
  -memprofile=mem.pprof \
  -count=1 \
  > bench-profile.log 2>&1
```

For blocking, mutex contention, and timeline evidence:

```bash
go test ./path/to/pkg \
  -run '^$' \
  -bench '^BenchmarkName$' \
  -blockprofile=block.pprof \
  -mutexprofile=mutex.pprof \
  -trace=trace.out \
  -count=1 \
  > contention-trace.log 2>&1
```

Targeting rules:

- Use `-run '^$'` when only benchmarks should run.
- Use anchored `-bench` regexes; do not profile the whole suite by default.
- Use `-count=1` for profile capture and higher `-count` for benchmark
  comparison.
- Use `-benchtime` only to collect enough samples or model a fixed workload.
- Collect one invasive diagnostic type at a time when precision matters.

## CPU Profile Text

```bash
go tool pprof -top -nodecount=40 cpu.pprof > cpu-top.txt
go tool pprof -top -cum -nodecount=40 cpu.pprof > cpu-cum.txt
go tool pprof -text -lines -nodecount=80 cpu.pprof > cpu-lines.txt
go tool pprof -list='my/module/pkg\.HotFunc' cpu.pprof > hotfunc-source.txt
go tool pprof -disasm='my/module/pkg\.HotFunc' cpu.pprof > hotfunc-asm.txt
```

Filter runtime/framework noise only after keeping an unfiltered top report:

```bash
go tool pprof -text \
  -focus='my/module|my/module/pkg' \
  -hide='runtime\.|testing\.' \
  -nodecount=80 \
  cpu.pprof > cpu-focused.txt
```

Read CPU reports:

- `flat` is local sample cost in the function body.
- `cum` is the function plus callees and is useful for owner paths.
- A high `cum`, low `flat` dispatcher points to callees or call count.
- CPU profiles do not explain sleeping, I/O wait, lock wait, or scheduler delay.

## Allocation and Heap Text

Use the sample index that matches the question:

```bash
go tool pprof -top -sample_index=alloc_space mem.pprof > alloc-space-top.txt
go tool pprof -top -sample_index=alloc_objects mem.pprof > alloc-objects-top.txt
go tool pprof -top -sample_index=inuse_space mem.pprof > inuse-space-top.txt
go tool pprof -top -sample_index=inuse_objects mem.pprof > inuse-objects-top.txt
go tool pprof -text -lines -sample_index=alloc_space mem.pprof > alloc-lines.txt
go tool pprof -list='my/module/pkg\.' -sample_index=alloc_space mem.pprof > alloc-source.txt
```

Interpretation:

- `alloc_space`: allocation churn and likely GC pressure.
- `alloc_objects`: object-count pressure, tiny temporaries, boxing, closures.
- `inuse_space`: retained live heap, leaks, caches, backing-array pinning.
- `inuse_objects`: retained object count.

For narrow allocation benchmarks, increase precision only when the overhead is
acceptable:

```bash
go test ./path/to/pkg \
  -run '^$' \
  -bench '^BenchmarkName$' \
  -benchmem \
  -memprofile=mem.pprof \
  -memprofilerate=1 \
  -count=1 \
  > memprofile.log 2>&1
```

## Text Call Graphs

Use call graph text when `top` identifies a suspect but ownership is unclear:

```bash
go tool pprof -tree cpu.pprof > cpu-tree.txt
go tool pprof -peek='my/module/pkg\.HotFunc' cpu.pprof > hotfunc-neighborhood.txt
go tool pprof -traces cpu.pprof > cpu-sample-traces.txt
go tool pprof -dot -nodecount=80 cpu.pprof > cpu-callgraph.dot
```

For allocation ownership:

```bash
go tool pprof -tree -sample_index=alloc_space mem.pprof > alloc-tree.txt
go tool pprof -dot -sample_index=alloc_space -nodecount=80 mem.pprof > alloc-callgraph.dot
```

`-traces` can be very large. Use it only after `top`, `list`, `tree`, or
`peek` leaves a specific stack question unanswered.

## Trace to Text Profiles

Open the trace UI for timeline work, but use pprof conversion for text review:

```bash
go tool trace -pprof=sync trace.out > trace-sync.pprof
go tool pprof -top -cum trace-sync.pprof > trace-sync-top.txt

go tool trace -pprof=net trace.out > trace-net.pprof
go tool pprof -top -cum trace-net.pprof > trace-net-top.txt

go tool trace -pprof=syscall trace.out > trace-syscall.pprof
go tool pprof -top -cum trace-syscall.pprof > trace-syscall-top.txt

go tool trace -pprof=sched trace.out > trace-sched.pprof
go tool pprof -top -cum trace-sched.pprof > trace-sched-top.txt
```

Use each trace profile for a specific question:

- `sync`: goroutine synchronization blocking.
- `net`: network blocking.
- `syscall`: syscall blocking.
- `sched`: scheduler latency.

Trace is the right next tool when wall time is high but CPU profiles are too
small to explain it.

## Block and Mutex Text

For tests and benchmarks:

```bash
go tool pprof -top -cum block.pprof > block-top.txt
go tool pprof -tree block.pprof > block-tree.txt
go tool pprof -list='my/module/pkg\.' block.pprof > block-source.txt

go tool pprof -top -cum mutex.pprof > mutex-top.txt
go tool pprof -tree mutex.pprof > mutex-tree.txt
go tool pprof -list='my/module/pkg\.' mutex.pprof > mutex-source.txt
```

Interpretation:

- Block profile stacks show where goroutines waited.
- Mutex profile stacks show contended lock holders, commonly around `Unlock`.
- Mutex/block cumulative time can exceed elapsed wall time because goroutine
  wait time is summed.
- High event count with tiny delay is weaker evidence than high delay unless
  event count itself is the target metric.

`-blockprofile` without `-blockprofilerate` records all blocking events. Use
that for narrow benchmarks; sample more lightly in services.

## Live Service pprof Text

Expose `net/http/pprof` only on an internal/debug listener.

```go
import (
	"log"
	"net/http"
	_ "net/http/pprof"
)

func serveDebug() {
	go func() {
		log.Println(http.ListenAndServe("localhost:6060", nil))
	}()
}
```

Useful text-first commands:

```bash
go tool pprof -top 'http://localhost:6060/debug/pprof/profile?seconds=30'
go tool pprof -top 'http://localhost:6060/debug/pprof/heap?gc=1'
go tool pprof -top -sample_index=alloc_space 'http://localhost:6060/debug/pprof/allocs'
go tool pprof -top -cum 'http://localhost:6060/debug/pprof/block?seconds=30'
go tool pprof -top -cum 'http://localhost:6060/debug/pprof/mutex?seconds=30'
curl 'http://localhost:6060/debug/pprof/goroutine?debug=2' > goroutines.txt
curl -o trace.out 'http://localhost:6060/debug/pprof/trace?seconds=5'
```

For goroutine dumps:

```bash
rg -n 'sync\.Mutex|sync\.RWMutex|chan receive|chan send|select|semacquire|IO wait' goroutines.txt
```

Enable service block/mutex profiles deliberately and temporarily:

```go
runtime.SetBlockProfileRate(1)     // every blocking event; high overhead
runtime.SetMutexProfileFraction(1) // every contention event; high overhead
```

Use larger sampling values for production-like services and restore defaults
after the diagnostic window.

## Escape Analysis Text

Escape output is compiler context, not proof. Start from allocation evidence,
then filter escape output to hot package lines.

```bash
go build -gcflags='all=-m=3' ./path/to/pkg 2> escape.log
go test ./path/to/pkg -run '^$' -gcflags='all=-m=3' 2> escape-test.log
rg -n 'my/module/pkg|escapes to heap|moved to heap|does not escape|can inline|cannot inline|inlining call' escape.log
```

Diagnostic-only no-inlining comparison:

```bash
go build -gcflags='all=-m=3 -l' ./path/to/pkg 2> escape-noinline.log
```

Use `-l` only to make logs easier to read. It changes compiler behavior, so do
not use no-inline benchmark numbers as optimization proof.

## Runtime Text Diagnostics

```bash
GODEBUG=gctrace=1 ./myservice 2> gc-trace.txt
GODEBUG=schedtrace=1000 ./myservice 2> sched-trace.txt
GODEBUG=schedtrace=1000,scheddetail=1 ./myservice 2> sched-detail.txt
```

Use runtime text as context:

- `gctrace=1`: one line per GC cycle; correlate with allocation rate and
  latency.
- `schedtrace=1000`: scheduler summary every 1000 ms.
- `scheddetail=1`: detailed scheduler, processor, thread, and goroutine state.

Do not justify a patch from runtime text alone. Connect it to a benchmark,
profile, trace, or service metric.

## Artifact Hygiene

- Keep binary profiles and traces on disk; send text summaries to review.
- Save unfiltered `top` output before filtered/focused reports.
- Use `-nodecount`, `-focus`, `-hide`, `-lines`, `-sample_index`, and anchored
  regexes to reduce reports.
- The large-file rule has priority over convenience commands. Do not begin with
  `cat`, broad `sed`, broad `head`/`tail`, or similar whole-file reads for
  artifacts that may be large.
- Before opening text artifacts, size-check or narrow first:
  `wc -c file`, `rg -n 'pattern' file`, pprof summary output, or a focused
  `sed -n 'start,endp'` window around a known match.
- Use streaming scripts for large text outputs when targeted shell filters are
  not enough.
- Do not eagerly load JSON, CSV, logs, traces, or generated text over 1 GB.
- Do not attach profiles, traces, logs, or goroutine dumps that may contain
  secrets without redaction.
