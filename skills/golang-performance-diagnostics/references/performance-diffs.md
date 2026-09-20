# Performance Diffs

Use this reference when the question is "what changed?" between a baseline and a
candidate. Use `benchstat` for statistical proof, pprof diffs for sample
movement, escape/BCE diffs for compiler explanations, and trace-derived pprof
diffs for wait-time movement. Use
[interpreting-performance-results.md](interpreting-performance-results.md) to
classify signs, significance, practical value, and cost movement.

These commands were checked against local `go1.26.2 darwin/arm64`.

Contents: baseline discipline, benchmark diffs, profile capture, pprof diffs,
allocation/heap diffs, block/mutex/live diffs, escape diffs, BCE diffs, trace
diffs, and minimal reports.

## Baseline Discipline

Do not switch branches in a dirty worktree. Use two clean worktrees, existing
old/new artifacts, or a throwaway comparison worktree.

Capture context beside artifacts:

```bash
mkdir -p perf/old perf/new perf/diff
go version > perf/old/go.version.txt
go env -json GOOS GOARCH GOVERSION GOMOD GOWORK CGO_ENABLED GOAMD64 \
  > perf/old/go.env.json
printf 'GOMAXPROCS=%s\n' "${GOMAXPROCS:-runtime-default}" \
  > perf/old/gomaxprocs.txt
```

Use the same package, benchmark regex, input shape, `GOOS/GOARCH`, and
`-benchtime` on both sides. For precise final numbers, collect one invasive
profile or trace type at a time.

## Benchmark Diff First

```bash
go test ./path/to/pkg -run '^$' -bench '^BenchmarkFoo$' -benchmem -count=20 \
  > perf/old/bench.txt
go test ./path/to/pkg -run '^$' -bench '^BenchmarkFoo$' -benchmem -count=20 \
  > perf/new/bench.txt
benchstat perf/old/bench.txt perf/new/bench.txt > perf/diff/benchstat.txt
```

Interpretation:

- `ns/op` measures time per operation; repeated A/B comparison establishes
  whether it moved.
- `B/op` measures attributed heap bytes per operation.
- `allocs/op` measures attributed heap allocation count per operation.
- A profile delta explains sample movement but does not prove a timing win.
  Require sufficient samples, the predicted owner movement, and the matching
  public benchmark or service metric; do not apply a universal percentage
  cutoff.

## Capture Comparable Profiles

Use `-count=1` for profiled runs so test cache cannot reuse results.

```bash
PKG=./path/to/pkg
BENCH='^BenchmarkFoo$'

go test "$PKG" -run '^$' -bench "$BENCH" -benchtime=10s -count=1 \
  -cpuprofile perf/old/cpu.pprof \
  > perf/old/profile.log 2>&1
```

For final evidence, capture memory, block, mutex and trace in separate
same-shaped runs. Retain identical sampling rates and settings on both sides.
Combined diagnostics are exploratory only. For narrow allocation investigations,
run this on both baseline and candidate with the same `-memprofilerate`:

```bash
go test "$PKG" -run '^$' -bench "$BENCH" -benchtime=10s -count=1 \
  -memprofile perf/new/mem.pprof \
  -memprofilerate=1 \
  > perf/new/memprofile.log 2>&1
```

## pprof Diff Semantics

- `-diff_base old.pprof new.pprof`: before/after experiment.
- `-base t0.pprof t1.pprof`: cumulative snapshots from the same process.
- `-normalize`: compare relative distribution when totals differ.
- Positive rows: NEW spent more samples there.
- Negative rows: NEW spent fewer samples there.

CPU:

```bash
go tool pprof -top -diff_base perf/old/cpu.pprof perf/new/cpu.pprof \
  > perf/diff/cpu.top.diff.txt
go tool pprof -top -cum -diff_base perf/old/cpu.pprof perf/new/cpu.pprof \
  > perf/diff/cpu.cum.diff.txt
go tool pprof -text -lines -diff_base perf/old/cpu.pprof perf/new/cpu.pprof \
  > perf/diff/cpu.lines.diff.txt
go tool pprof -list='my/module/pkg\.HotFunc' \
  -diff_base perf/old/cpu.pprof perf/new/cpu.pprof \
  > perf/diff/hotfunc.cpu.diff.txt
```

Show only regressions:

```bash
go tool pprof -top -drop_negative \
  -diff_base perf/old/cpu.pprof perf/new/cpu.pprof
```

Save a reusable diff profile:

```bash
go tool pprof -proto -diff_base perf/old/cpu.pprof perf/new/cpu.pprof \
  > perf/diff/cpu.diff.pprof
```

## Allocation and Heap Diffs

Use the same `sample_index` on both sides.

```bash
go tool pprof -top -sample_index=alloc_space \
  -diff_base perf/old/mem.pprof perf/new/mem.pprof \
  > perf/diff/alloc_space.top.diff.txt
go tool pprof -top -sample_index=alloc_objects \
  -diff_base perf/old/mem.pprof perf/new/mem.pprof \
  > perf/diff/alloc_objects.top.diff.txt
go tool pprof -top -sample_index=inuse_space \
  -diff_base perf/old/mem.pprof perf/new/mem.pprof \
  > perf/diff/inuse_space.top.diff.txt
go tool pprof -text -lines -sample_index=alloc_space \
  -diff_base perf/old/mem.pprof perf/new/mem.pprof \
  > perf/diff/alloc_space.lines.diff.txt
```

Read by question:

- `alloc_space`: allocation churn and GC pressure changed.
- `alloc_objects`: object-count churn changed.
- `inuse_space`: retained live heap changed.
- `inuse_objects`: retained object count changed.

## Block, Mutex, and Live-Service Diffs

Benchmark artifacts:

```bash
go tool pprof -top -cum -diff_base perf/old/block.pprof perf/new/block.pprof \
  > perf/diff/block.cum.diff.txt
go tool pprof -top -cum -diff_base perf/old/mutex.pprof perf/new/mutex.pprof \
  > perf/diff/mutex.cum.diff.txt
```

Live delta profile:

```bash
go tool pprof -top -cum \
  'http://localhost:6060/debug/pprof/block?seconds=30'
go tool pprof -top -cum \
  'http://localhost:6060/debug/pprof/mutex?seconds=30'
```

Cumulative snapshots from one process:

```bash
curl -o perf/t0.block.pprof 'http://localhost:6060/debug/pprof/block'
sleep 60
curl -o perf/t1.block.pprof 'http://localhost:6060/debug/pprof/block'
go tool pprof -top -cum -base perf/t0.block.pprof perf/t1.block.pprof
```

Enable live block/mutex profiles deliberately and temporarily. All-event modes
such as `SetBlockProfileRate(1)` and `SetMutexProfileFraction(1)` have high
overhead.

## Escape Analysis Diffs

Use after benchmark or allocation-profile diffs show meaningful allocation
movement.

```bash
go build -a -p=1 -trimpath -gcflags='all=-m=3' ./path/to/pkg \
  2> perf/old/escape.raw.txt
go build -a -p=1 -trimpath -gcflags='all=-m=3' ./path/to/pkg \
  2> perf/new/escape.raw.txt
```

Normalize:

```bash
normalize_escape() {
  sed -E \
    -e 's/[[:space:]]+$//' \
    -e '/^# /d' \
    -e '/^go: downloading /d' \
    -e '/^go: found /d' \
    -e 's#(^|[[:space:]])/[^[:space:]]*/pkg/mod/# GOPATH/pkg/mod/#g' \
    -e 's#(^|[[:space:]])/tmp/go-build[0-9]+/# /tmp/go-build/#g' \
    "$1" | LC_ALL=C sort
}

normalize_escape perf/old/escape.raw.txt > perf/old/escape.norm.txt
normalize_escape perf/new/escape.raw.txt > perf/new/escape.norm.txt
diff -u --label old.escape --label new.escape \
  perf/old/escape.norm.txt perf/new/escape.norm.txt \
  > perf/diff/escape.diff.txt || true
```

Heap-escape and inline summaries:

```bash
rg 'escapes to heap|moved to heap' perf/old/escape.norm.txt \
  > perf/old/heapescapes.txt || true
rg 'escapes to heap|moved to heap' perf/new/escape.norm.txt \
  > perf/new/heapescapes.txt || true
comm -13 perf/old/heapescapes.txt perf/new/heapescapes.txt \
  > perf/diff/new.heapescapes.txt || true
comm -23 perf/old/heapescapes.txt perf/new/heapescapes.txt \
  > perf/diff/removed.heapescapes.txt || true

rg 'can inline|cannot inline|inlining call' perf/old/escape.norm.txt \
  > perf/old/inline.txt || true
rg 'can inline|cannot inline|inlining call' perf/new/escape.norm.txt \
  > perf/new/inline.txt || true
diff -u perf/old/inline.txt perf/new/inline.txt \
  > perf/diff/inline.diff.txt || true
```

Rule:

```text
benchstat says B/op or allocs/op changed
pprof says where allocation bytes or objects changed
escape diff says why compiler allocation decisions changed
```

## Bounds-Check Diffs

Use after CPU profiles or disassembly point at a hot loop where index checks are
plausible.

```bash
go build -a -p=1 -trimpath -gcflags='all=-d=ssa/check_bce/debug=1' ./path/to/pkg \
  > perf/old/bce.raw.txt 2>&1
go build -a -p=1 -trimpath -gcflags='all=-d=ssa/check_bce/debug=1' ./path/to/pkg \
  > perf/new/bce.raw.txt 2>&1

rg -n 'Found IsInBounds|Found IsSliceInBounds|my/module/pkg|HotFunc' \
  perf/old/bce.raw.txt > perf/old/bce.filtered.txt || true
rg -n 'Found IsInBounds|Found IsSliceInBounds|my/module/pkg|HotFunc' \
  perf/new/bce.raw.txt > perf/new/bce.filtered.txt || true
diff -u perf/old/bce.filtered.txt perf/new/bce.filtered.txt \
  > perf/diff/bce.diff.txt || true
```

Fewer BCE lines matter only when `benchstat`, CPU profiles, or disassembly also
move in the expected hot function.

## Trace Diffs

There is no useful general subtraction of full trace timelines. Convert traces
to pprof-like profiles, then diff those.

```bash
for name in old new; do
  for typ in net sync syscall sched; do
    go tool trace -pprof="$typ" "perf/$name/trace.out" \
      > "perf/$name/trace.$typ.pprof"
  done
done

for typ in net sync syscall sched; do
  go tool pprof -top -cum \
    -diff_base "perf/old/trace.$typ.pprof" "perf/new/trace.$typ.pprof" \
    > "perf/diff/trace.$typ.cum.diff.txt"
done
```

Read:

- `trace.sync`: synchronization blocking moved.
- `trace.sched`: scheduler latency moved.
- `trace.net`: network blocking moved.
- `trace.syscall`: syscall blocking moved.

Use `-normalize` only when durations or total events differ and the question is
relative distribution.

## Minimal Report

These commands are for known-small generated summary files. If a report may be
large or noisy, size-check and narrow first.

```bash
sed -n '1,80p' perf/diff/benchstat.txt
sed -n '1,80p' perf/diff/cpu.top.diff.txt
sed -n '1,80p' perf/diff/alloc_space.top.diff.txt
sed -n '1,80p' perf/diff/block.cum.diff.txt
sed -n '1,80p' perf/diff/trace.sched.cum.diff.txt
sed -n '1,80p' perf/diff/new.heapescapes.txt
sed -n '1,80p' perf/diff/bce.diff.txt
```

Report the target metric, commands, artifact paths, `benchstat` result,
profile/trace owner movement, compiler-diagnostic movement, correctness tests,
and remaining uncertainty.
