# Go Optimization Technique Notes

Load this reference only when selecting, implementing, or reviewing one of the
specific techniques below. Keep `SKILL.md` focused on the workflow and result
gates.

Contents: WASM writes, public/kernel ceilings, workload shapes, fixed decimal
parse/format, JSON/CBOR, database scans, allocation ownership, inlining/BCE,
layout/locality, and measured scalar algorithms.

## Immediate WASM Memory Output Writes

When a Go host function only needs to return a fixed-size value into WASM linear
memory, prefer writing directly into the runtime-provided memory view over
building a temporary Go buffer and calling a generic write method.

Use this only when all of the following are true:

- The runtime API documentation and implementation for the version in use
  explicitly guarantee that the memory read/view is write-through, not a copy.
- The returned slice is used synchronously and is not retained, appended to,
  stored in DB/cache/log/action/result structs, passed to async work, or exposed
  after the host call returns.
- No memory grow or reallocation can happen between obtaining the view and
  writing the bytes.
- The output size and representation are fixed and validated before writing.
- The destination is cleared when partial writes or shorter encodings are
  possible.
- Escape analysis plus exact isolated benchmarks prove that the old temporary
  buffer allocation disappeared and `B/op` or `allocs/op` improved.

Good fit: fixed-size numeric outputs such as 32-byte unsigned integer values
written immediately into WASM memory.

Bad fit: retained DB keys/values, action payloads, durable logs, descriptor
strings, result structs, cache entries, or any buffer whose ownership outlives
the host call.

Review checklist:

- Confirm runtime API docs and implementation were checked for write-through
  semantics.
- Confirm the slice lifetime is strictly inside the host call.
- Confirm the patch did not move the same allocation to a caller/helper or
  increase retained heap elsewhere.
- Compare against simpler alternatives such as stack buffers, direct byte
  writes, or the existing runtime write API, and reject variants that only move
  allocation ownership.

## Public Path, Kernel Ceiling, And Workload Shapes

Benchmark three layers when a hot operation has wrappers or generic dispatch:

1. the public production API;
2. the narrow equivalent kernel doing the same numeric/ownership work;
3. optional sub-kernels only when a profile names them.

Run them in the same benchmark binary with the same fixture and toolchain. The
public-to-kernel gap is the maximum plausible wrapper win. If they are already
within noise, stop changing wrappers.

Use a shape matrix instead of one convenient value:

- short, typical, boundary, and maximum lengths;
- native-width and multi-limb values;
- retained and newly formatted output;
- canonical, rejected, and cold escaped/error input;
- expected hit/miss or valid/invalid distributions;
- scale, field count, row count, and batch width where relevant.

A branch that wins on `0..99` hits but slows representative misses is rejected
unless production evidence establishes the required hit rate. Likewise, a
maximum-width improvement does not justify slowing common one-limb values.

With Go versions that support it, prefer `testing.B.Loop` so the compiler can
inline the measured body while the harness keeps values alive. Keep setup and
fixture conversion outside the timed loop, and use package-level sinks only
where needed to prevent dead-code elimination.

## Exact Decimal And Fixed-Width Parsing

When the contract is unsigned fixed-scale text, model it as one scaled integer.
Do not parse through floating point or a general decimal package unless the
contract genuinely accepts exponent, sign, whitespace, or arbitrary scale.

Optimization order:

1. parse directly from the caller's `string` or `[]byte`; avoid conversion
   between them;
2. validate syntax and scale once at the constructor/decoder boundary;
3. accumulate into the narrowest proven integer width, then enter a wide path
   only after overflow or width requires it;
4. use caller-owned `Into` and append APIs for hot paths;
5. retain canonical immutable text only when repeated output justifies its
   lifetime and memory cost.

Do not add trimming, case folding, suffix rewriting, or other normalization to
the numeric hot path. Accepted syntax and canonicalization are behavior, not a
performance implementation detail.

For dense ASCII digits, a measured SWAR parser can validate and reduce several
digits at once. Required proof:

- every byte position is validated, including decimal-point boundaries;
- lengths around every specialized shape are covered;
- scalar and SWAR results match a trusted exact reference;
- common and miss/error distributions improve end to end;
- the dispatch branch costs less than the saved arithmetic.

Explicit independent blocks can expose instruction-level parallelism better
than a tiny loop, but only keep unrolling that improves the public benchmark.
Generated per-scale masks or duplicated shape-specific code are rejected when
their isolated win disappears behind shared dispatch or materially expands the
audited surface.

## Fixed-Width Formatting And Invariant Arithmetic

For fixed-scale output, write integer and fractional digits directly into their
final positions. Avoid formatting into a shifted buffer and then copying a
prefix when one division by the scale can place both fields.

Useful ordinary tools include `math/bits` (`Mul64`, `Add64`, `Sub64`,
`LeadingZeros64`, `Div64`), digit-pair tables, fixed-width chunk writers, and
skipping known-zero high limbs. Benchmark the complete formatter, not only the
division helper.

For a constant divisor in a proven hot multi-limb path, reciprocal
multiplication may beat serial hardware division. It requires:

- a documented derivation or published algorithm;
- bounded correction steps, never an unbounded data-dependent retry loop;
- boundary tests against `bits.Div64`;
- randomized/property comparison against an exact reference such as
  `math/big`;
- complete-path benchmarks across limb widths and scales;
- generated assembly inspection confirming the intended instruction shape.

Chunk base is an algorithm choice. A smaller base can simplify local writes
while increasing the number of wide divisions. Count actual reductions and
measure one-, two-, three-, and four-limb values before selecting it.

## JSON, CBOR, And Aggregate Storage Codecs

Separate owned interoperability APIs from caller-buffer hot APIs:

- `Marshal*` must return owned bytes and normally allocates once;
- `Append*` can be allocation-free when caller capacity is sufficient;
- `Parse*Into` can reuse caller-owned destination storage;
- prefix decoders can consume one positional field without slicing/copying the
  whole parent record.

For quoted fixed-scale JSON, append quotes and canonical decimal bytes directly.
Parse ordinary unescaped strings directly from input and reserve a standards-
compliant JSON unescape path for escaped strings. Benchmark both; do not report
the escaped path's required ownership as a canonical-path allocation.

For compact deterministic CBOR records, compare:

- generic reflective maps;
- generic `toarray` structs;
- manual positional CBOR using typed scalar append/decode;
- fixed binary only when schema evolution and wire-size tradeoffs permit it;
- raw decimal text only when human-readable storage is a real requirement.

Manual positional CBOR is acceptable only with approved schema ownership,
golden bytes, byte equivalence to the reference encoder, strict malformed and
overflow rejection, fuzz/round-trip tests, and real DB readback benchmarks.
Prefer minimal unsigned integers and explicit wide-integer encoding; do not
retain compatibility decoders or alternate canonical forms without an approved
migration contract.

## Database Calls, Cursor Work, And Scaling

Do not infer DB calls or rows scanned from source review. Instrument the storage
interface or cursor wrapper and report exact `Get`, `Put`, cursor, seek, next,
previous, and rows-seen counts for the benchmarked operation.

Different questions can require different bounded reads: exact identity lookup,
latest-by-prefix lookup, and a time-range scan are not automatically reducible
to one `Get`. For each read, document its key ordering and why `Get`, `First`,
`Last`, `SetRange`, `Prev`, or `Next` is selected.

Prove scale with history sizes such as 1, 100, 10,000, and the configured
retention maximum. Report whether calls and rows are constant, logarithmic via
the DB seek, or linear in the bounded result count. A range scan can be correct
when rows seen are capped by the requested window; an unbounded prefix walk is
not accepted because a small fixture happens to be fast.

Keep transaction ownership outside nanosecond codec benchmarks, then add a
real-transaction benchmark separately. Respect storage-engine thread affinity:
create and use a transaction on the same locked OS thread when the engine
requires it. Build fixed-width keys with exact-capacity append or direct indexed
writes; reject `fmt`, temporary strings, and normalization in key construction
unless the key contract requires them.

## Failure Paths And Required Ownership

Benchmark valid hot paths and representative failures separately. Generic
conversion of a typed string error into `error` can allocate; fixed package
errors can be represented as typed string constants and pre-boxed once when
profiles prove this owner. Do not replace errors with panics for speed.

Classify remaining allocations by contract:

- required owned return (`String`, `Marshal*`, detached payload);
- retained cache/DB/action/log ownership;
- escaped/decoded slow-path ownership;
- avoidable temporary, conversion, boxing, reflection, or growth.

Use escape analysis plus per-row allocation profiles to name every owner. Do
not describe an allocation as serialization overhead when it belongs to a
wrapper copy, token lookup, symbol normalization, or benchmark setup.

## Inlining, BCE, And Generic Dispatch

Use compiler output to select ordinary source changes before unsafe or assembly:

```bash
go test -c -gcflags='all=-m=2' -o "$ART/pkg.test" ./path/to/pkg \
  > "$ART/inline_escape.log" 2>&1
go test -c -gcflags='all=-d=ssa/check_bce/debug=1' \
  -o "$ART/pkg_bce.test" ./path/to/pkg > "$ART/bce.log" 2>&1
```

Inspect `can inline`, `inlining call`, `cost exceeds budget`, `escapes to heap`,
and `Found Is(In|SliceIn)Bounds` only for the named hot functions. Compiler
messages are hypotheses; public benchmark counters decide acceptance.

Findings to apply:

- Extracting a value-only helper can make the public wrapper exceed the
  inlining budget and regress it even when the helper is faster directly.
- A concrete or closed type path can beat interface/provider dispatch; generic
  code is not automatically slower, so compare generated call shapes.
- One dominating length check can remove repeated bounds checks. Do not add
  dummy indexing unless the preceding validation proves the index is valid on
  every path.
- Fewer BCE diagnostics do not guarantee fewer instructions or lower latency.
- Re-run these diagnostics after every Go toolchain upgrade; inlining budgets
  and generated bounds checks are not stable contracts.

When ordinary source shape is insufficient, continue with
[compiler-and-machine-code.md](compiler-and-machine-code.md) for unsafe loads,
architecture files, assembly, SIMD, and compiler directives, or
[runtime-and-concurrency-techniques.md](runtime-and-concurrency-techniques.md)
for ownership- and scheduler-sensitive mechanisms.

## Layout And Representation

Use `unsafe.Sizeof`, `Alignof`, and `Offsetof` in tests to lock a deliberately
chosen hot struct layout. Order fields to reduce padding, but measure array or
cache workloads before claiming a speedup. Narrow integer backends reduce range
and wire requirements; they do not necessarily shrink a struct when a string,
pointer, or alignment boundary dominates its size.

Keep compile-time metadata zero-sized when possible and runtime metadata in the
smallest validated representation that covers the contract. Benchmark generic,
concrete, and runtime-metadata APIs separately: dictionary/interface dispatch,
inlining, and padding can outweigh the nominal field-size saving.

## Cache Locality And Hot/Cold Data

Load
[CPU cache analysis](../../golang-performance-diagnostics/references/cpu-cache-analysis.md)
before changing layout for locality. Require hardware counters or a controlled
working-set crossover; `unsafe.Sizeof` alone is not performance evidence.

Choose the representation from the access pattern:

- keep an array-of-structs when each operation consumes most fields;
- consider structure-of-arrays when scans repeatedly touch one field;
- split large cold payloads from compact hot metadata when the hot scan does
  not dereference the payload;
- retain contiguous inline values when pointer chasing would dominate;
- group adjacent operations only when ordering and cancellation stay intact.

Compare at least:

- element size and bytes visited per operation;
- sequential and representative random access;
- working sets below and above cache boundaries;
- `ns/element`, cycles/op, instructions/op, cache misses/op when available;
- allocations, object count, retained heap, and GC scan cost.

Do not accept a smaller hot struct that merely moves every operation through a
new pointer. Do not pad read-mostly rows to a cache line. Do not claim cache
improvement when only branch count, arithmetic, or compiler code shape changed.

## Measured Scalar Algorithm Patterns

Treat these as candidates, never defaults. Each survived or failed in a real
fixed-decimal workload and therefore has a concrete gate:

- **Pairwise decimal accumulation:** retain it for short or irregular text when
  SWAR dispatch costs more than the saved arithmetic.
- **Forward SWAR parsing:** validate and reduce 8-byte digit blocks only after
  proving the full extent; use independent blocks to expose instruction-level
  parallelism when the complete parser improves.
- **Reverse SWAR formatting:** pack digit lanes with reciprocal multiply/shift
  arithmetic, insert a known decimal point in the packed word, then write exact
  widths. Reject overstores that mutate caller capacity beyond the returned
  slice.
- **Digit-pair tables:** prefer them for short formatting when a small-value
  cache or extra hit/miss branch regresses representative misses.
- **Invariant division:** compare chunk bases by actual wide divisions. Use a
  derived reciprocal only with bounded corrections, property tests against
  exact division, and disassembly proving the intended multiply/carry chain.
- **Branchless digit width:** `bits.Len*` plus a threshold correction can beat a
  comparison tree, but a predictable switch can still beat unconditional
  branchless threshold work. Measure outcome distributions and instructions.
- **Shape selection:** a compile-time bitset or specialized exact-width path can
  select proven widths cheaply. Reject generated per-scale variants when shared
  dispatch erases the kernel win or expands the audited surface materially.
- **Closed-set generic dispatch:** direct type switches can inline better than
  interface/provider methods. Compare public assembly and dictionary calls;
  generics are not inherently free or slow.
- **Caller-owned big-number output:** write into reused `big.Int`/`uint256`
  storage. Classify a fresh owned result allocation as contractual rather than
  disguising it with unsafe aliases, pooling, or benchmark setup.

For every candidate, benchmark the public API, equivalent kernel, common and
wide shapes, misses/errors, `B/op`, and `allocs/op`. Remove the candidate when
only the isolated kernel or synthetic distribution wins.

Parsing and formatting candidates are separate experiments. Forward SWAR can
win for validated 8-byte digit blocks while reverse packed arithmetic or a
digit-pair table wins formatting; neither result implies that one representation
or dispatch shape is best in both directions. Compare scalar, SWAR, and assembly
at the actual token widths and batch sizes, then combine winners incrementally
using [experiment-framework.md](experiment-framework.md).

For short tokens, account for feature dispatch and the Go-to-assembly call in
the public row. Wider vectors are not automatically faster: independent scalar
or SWAR blocks can expose enough instruction-level parallelism without call,
shuffle, and tail overhead. Prefer batch assembly when one call amortizes those
costs across several values. Keep overstore formatters internal and prove the
entire writable extent; public append APIs must not modify bytes beyond the
returned slice.

For wide integer formatting, compare chunk bases by complete reduction count,
not local chunk speed. A base that simplifies SIMD output can require different
division behavior than the best scalar base. Keep architecture-specific bases
only when their complete public paths win and emit identical canonical bytes.
