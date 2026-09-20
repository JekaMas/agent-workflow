# Compiler And Machine-Code Techniques

Use this reference only after the public benchmark and an equivalent kernel or
profile isolate a compiler, instruction, architecture, or foreign-call cost.

Primary references: [compiler pipeline](https://go.dev/src/cmd/compile/README),
[SSA backend](https://go.dev/src/cmd/compile/internal/ssa/README),
[`compile` flags and directives](https://pkg.go.dev/cmd/compile),
[`go tool asm`](https://pkg.go.dev/cmd/asm), and
[architecture build variables](https://go.dev/doc/install/source#environment).

Contents: inlining, bounds-check elimination, register pressure, build/link
shape, disassembly/SSA, SWAR/SIMD, cache-line padding and prefetch, cgo,
unsafe/runtime internals, and validation.

- [Inlining and call shape](#inlining-and-call-shape)
- [Bounds-check elimination](#bounds-check-elimination)
- [Register pressure and stack frames](#register-pressure-and-stack-frames)
- [Build constraints, architecture targets, and link shape](#build-constraints-architecture-targets-and-link-shape)
- [Assembly analysis and decision gate](#assembly-analysis-and-decision-gate)
- [SIMD, SWAR, and batch APIs](#simd-swar-and-batch-apis)
- [Cache-line padding and prefetch](#cache-line-padding-and-prefetch)
- [cgo](#cgo)
- [Unsafe and runtime internals](#unsafe-and-runtime-internals)

| Technique | Required evidence | Reject when |
|---|---|---|
| Inlining/BCE source shape | Public-to-kernel gap plus compiler diagnostics name calls or checks. | Only a helper improves or diagnostics change without public-path gain. |
| Register/frame shape | Disassembly names spills, redundant reloads, or large hot frames. | Source contortion moves traffic or grows stack/calls. |
| Build/architecture shape | Fleet baseline or binary/link evidence names an available feature/cost. | Build-machine features exceed fleet guarantees or only size changes. |
| SWAR/SIMD | Repeated fixed-width byte work or a batch crossover is measured. | Dispatch, tails, or conversion erase the complete-path win. |
| Cache-line padding/prefetch | Counters identify false sharing or stable miss latency. | Work is single-threaded/read-mostly, line size is unknown, or no counters exist. |
| Assembly/unsafe/cgo | One narrow hot path has a material gap safe Go cannot close. | Routine tuning, unclear pointer ownership, or missing architecture proof. |

## Inlining And Call Shape

Inlining is a whole-call-path property. A helper that benchmarks faster in
isolation can push its public caller over the compiler budget and make the real
path slower.

Collect focused evidence:

```bash
go test -c -gcflags='all=-m=2' -o "$ART/pkg.test" ./path/to/pkg \
  > "$ART/inline_escape.log" 2>&1
rg -n 'HotPath|can inline|cannot inline|cost .* exceeds budget|inlining call' \
  "$ART/inline_escape.log"
```

Required comparison:

- public API and equivalent kernel in the same binary;
- before/after `can inline` and call-site decisions;
- disassembly proving whether a `CALL` remains;
- public-path `benchstat`, not a helper-only benchmark.

Prefer changing source shape, reducing wrapper work, or specializing a real hot
boundary before compiler directives. Do not use `//go:noinline` to make a
benchmark stable unless the benchmark explicitly measures call cost. Treat
`//go:nosplit` and `//go:noescape` as runtime/assembly contracts, not generic
speed annotations.

## Bounds-Check Elimination

Produce package-scoped BCE evidence:

```bash
go test -c -gcflags='all=-d=ssa/check_bce/debug=1' \
  -o "$ART/pkg_bce.test" ./path/to/pkg > "$ART/bce.log" 2>&1
rg -n 'HotPath|Found IsInBounds|Found IsSliceInBounds' "$ART/bce.log"
```

A dominating guard can prove an entire fixed-width access range:

```go
func load8(b []byte, offset int) (uint64, bool) {
	if offset < 0 || offset > len(b)-8 {
		return 0, false
	}
	_ = b[offset+7] // proof for the accesses below, not a substitute for guard
	return uint64(b[offset]) |
		uint64(b[offset+1])<<8 |
		uint64(b[offset+2])<<16 |
		uint64(b[offset+3])<<24 |
		uint64(b[offset+4])<<32 |
		uint64(b[offset+5])<<40 |
		uint64(b[offset+6])<<48 |
		uint64(b[offset+7])<<56, true
}
```

Rules:

- never add a sentinel index unless all inputs reaching it are proven valid;
- cover zero, short, exact, offset, and overflow-adjacent lengths;
- inspect generated assembly for panic calls as well as BCE diagnostics;
- keep the change only when the public benchmark improves; a rejected upfront
  bounds proof may be slower even when it removes checks;
- revalidate after Go upgrades because BCE is not a language guarantee.

## Register Pressure And Stack Frames

Inspect before rewriting. Stack loads/stores can be argument/ABI movement,
spills, stack maps, or deliberate locals; source variable count alone does not
identify register pressure.

Candidates include shortening live ranges, consuming decoded values near their
definitions, splitting cold/error paths, avoiding simultaneous duplicate
representations, and comparing large by-value arguments with pointers. A
pointer can reduce copies while adding aliasing or escape; a split helper can
reduce liveness while adding a call or blocking inlining.

Required evidence:

- final linked disassembly and frame size for the named symbol;
- spill/reload and `runtime.morestack*` changes, not just source locals;
- inlining/call-shape and escape changes;
- public benchmark plus CPU profile or cycles/instructions;
- representative concurrency when per-goroutine frame growth matters.

Reject a change that only moves stack traffic, increases call overhead, or
forces larger goroutine stacks to reach a helper-only win.

## Build Constraints, Architecture Targets, And Link Shape

Set architecture levels from the minimum guaranteed deployment fleet, not the
build host. Compare `GOAMD64`, `GOARM64`, and other target controls only when
the release matrix permits them; cross-build proves compilation, not runtime
performance or instruction support.

Use build constraints for genuinely architecture-specific implementations.
Keep one selected implementation per supported build target and avoid a hot
per-call feature branch when build-time selection is sufficient. For runtime-
selected standard-library or package paths, use documented CPU-feature disable
controls only as diagnostic A/B tools.

Linker flags such as stripping symbols primarily affect binary/debug size, not
automatic execution speed. Internal/external linking can change platform and
cgo behavior and must be measured in the final binary. The stable `gc`
toolchain has no general user-facing C/C++-style LTO switch; use PGO for the
supported whole-program feedback path rather than inventing an LTO workflow.

Report binary/text size, clean build time, final objdump, startup where
relevant, symbol/debug/observability loss, and every deployment architecture.

Before preserving a compiler workaround, compare the active stable toolchain
with [`gotip`](https://pkg.go.dev/golang.org/dl/gotip) in an isolated experiment
when repository policy permits it. Tip results can show that a workaround is
about to become redundant, but tip is not release evidence. Public tools such
as Compiler Explorer can help share reduced assembly examples; never upload
private code or data, and use the locally built final binary as acceptance
evidence.

## Assembly Analysis And Decision Gate

Inspect the exact generated symbol before considering handwritten assembly:

```bash
go test -c -o "$ART/pkg.test" ./path/to/pkg
go tool nm "$ART/pkg.test" | rg 'HotPath'
go tool objdump -s 'project/pkg\.HotPath' "$ART/pkg.test" \
  > "$ART/hotpath.objdump.txt"
go test -c -gcflags='example.com/project/pkg=-S' \
  -o "$ART/pkg_asm.test" ./path/to/pkg > "$ART/compile_asm.log" 2>&1
GOSSAFUNC=HotPath go test -c -o "$ART/pkg_ssa.test" ./path/to/pkg
```

Review `CALL`, `RET`, panic calls, hardware divide, `MUL`/carry chains,
`memmove`, `memequal`, branches, spills, and redundant loads. Confirm the
compiler has not already emitted the desired instruction sequence.

Before assembly, try source-level forms based on `math/bits`, explicit fixed
blocks, invariant reciprocal arithmetic, and architecture-selected unsafe
loads. Keep assembly only when:

- the public path has a material repeatable gap, not merely an isolated
  two-nanosecond kernel gap;
- call and feature-dispatch cost is included;
- each supported architecture has an implementation or the package explicitly
  restricts support;
- property/fuzz tests compare it against the selected Go reference;
- ABI, stack maps, pointer maps, and toolchain upgrades have named owners.

Do not retain assembly as a dormant alternative. If it loses or is neutral,
remove it and document the rejection.

## SIMD, SWAR, And Batch APIs

SWAR inside ordinary integer registers is often preferable for short fixed
tokens because it has no external call or CPU-feature dispatch. Validate all
bytes before reduction, prove no overread, and benchmark the dispatch misses.
Explicit independent blocks can expose instruction-level parallelism, but
unrolling remains only if the complete path wins.

SIMD requires a workload that amortizes setup and dispatch: padded records,
long fields, or a real batch API. Do not invent padding or batching solely to
make SIMD benchmarks favorable. Measure:

- scalar/SWAR versus SIMD at actual token lengths;
- single-item and production batch sizes;
- supported CPU features and architecture coverage;
- invalid-byte position and tail handling;
- end-to-end decoder throughput, not only the vector kernel.

Prefer stable compiler intrinsics or standard-library architecture paths before
handwritten assembly. If the active toolchain exposes experimental SIMD (for
example Go 1.26 `GOEXPERIMENT=simd` / `simd/archsimd` on supported amd64
targets), treat it as an experimental candidate: verify local capability and
release notes, keep it out of stable portability promises, compare its final
machine code and public crossover, and define removal/revalidation on every Go
upgrade.

## Cache-Line Padding And Prefetch

Use
[CPU cache analysis](../../golang-performance-diagnostics/references/cpu-cache-analysis.md)
first. Padding is for measured write/write false sharing, not generic alignment.
It increases every element's footprint and can turn an L1/L2-resident array
into a higher-level-cache workload.

Required padding proof:

- release architecture and measured cache-line size;
- two or more writers own distinct fields/slots on the same line;
- concurrency scaling and counters identify coherence traffic or misses;
- padded and unpadded complete workloads include memory/GC costs;
- layout tests lock size, alignment, and offsets intentionally.

Software prefetch generally requires assembly or architecture-specific
intrinsics. Use it only when counter sampling identifies a stable future access,
the distance can hide measured miss latency, and ordinary contiguous traversal,
batching, or hot/cold splitting is insufficient. Include over-prefetch,
different working-set sizes, and every supported architecture in benchmarks.
Remove prefetch when it is neutral; do not retain it as a hint-only fallback.

## cgo

Treat the boundary as a measured cost and test batching first.

```go
func HashAll(dst []Digest, src [][]byte) {
	for len(src) > 0 {
		n := min(len(src), 256)
		hashBatch(dst[:n], src[:n]) // one cgo call for the batch
		dst, src = dst[n:], src[n:]
	}
}
```

Proof: compare Go-only, cgo-per-item, and cgo-batched variants with platform and
compiler recorded in the report.

## Unsafe and Runtime Internals

High-risk tools: `//go:linkname`, `//go:noescape`, `//go:nosplit`,
`unsafe.Pointer`/`uintptr` tricks, `runtime.Pinner`, and runtime internals.

Rules:

- Do not use `uintptr` round-trips to hide escapes.
- `//go:noescape` belongs on external/assembly declarations whose pointer
  behavior is fully controlled.
- Revalidate on every Go, OS, and architecture upgrade.
- Use build-time architecture selection for native-endian or unaligned loads;
  avoid a nanosecond-path runtime feature branch unless measured.
- Keep a safe implementation for every other supported architecture, or make
  the support restriction explicit at build time.
- A caller must prove the complete byte extent before an unsafe load. Unsafe
  may remove checks; it must not remove validation.
- Never mutate storage obtained through `unsafe.StringData`, retain its pointer,
  or expose it as a writable slice.
- Prefer separate typed `string` and `[]byte` entry points or a closed generic
  input set over zero-copy conversion when a callee could retain or mutate.

```go
func bytesView(s string) []byte {
	if s == "" {
		return nil
	}
	return unsafe.Slice(unsafe.StringData(s), len(s))
}
```

This is read-only. Mutating the returned bytes corrupts string immutability.

For a fixed-width read-only load, document architecture, endianness, alignment,
range proof, and lifetime at the load site. One unaligned load can beat eight
shifts on amd64/arm64, but it is retained only with public-path benchmark and
disassembly evidence.

An architecture-selected native loader can use this shape only after the caller
proves the range and the build tag proves little-endian unaligned access:

```go
//go:build amd64 || arm64

func load8String(input string, offset int) uint64 {
	ptr := unsafe.Add(unsafe.Pointer(unsafe.StringData(input)), offset)
	return *(*uint64)(ptr)
}
```

The pointer is read-only and call-local. Do not reuse this for an architecture
whose unaligned or endian behavior differs, and do not expose a mutable alias of
the string.

Required validation for unsafe memory code:

```bash
go test ./path/to/pkg
go test -race ./path/to/pkg
go test -gcflags=all=-d=checkptr=2 ./path/to/pkg
GOARCH=amd64 go test -c -o "$ART/pkg_amd64.test" ./path/to/pkg
GOARCH=arm64 go test -c -o "$ART/pkg_arm64.test" ./path/to/pkg
```

Also fuzz short lengths, every invalid-byte position, exact boundaries, and
offset accesses. Cross-build proves compilation, not runtime correctness; run
on each release architecture or in an approved emulator/CI environment.

```go
func callWithPinnedBuffer(buf []byte) {
	if len(buf) == 0 {
		return
	}
	var p runtime.Pinner
	p.Pin(&buf[0])
	defer p.Unpin()
	callCWithPointer(unsafe.Pointer(&buf[0]))
	runtime.KeepAlive(buf)
}
```

Keep the `Pinner` alive for as long as C may retain the Go pointer.
