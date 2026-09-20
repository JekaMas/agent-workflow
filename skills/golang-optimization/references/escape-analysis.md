# Escape Analysis Counting And Fixes

Load this reference when the optimization target is heap allocation, retained
heap, GC pressure, or an exact `B/op` / `allocs/op` row. The goal is to count
what can escape, classify the owner and lifetime, then prove the fix removes or
shortens that allocation instead of moving it.

## Mental Model

Go escape analysis is static data-flow analysis. The compiler creates locations
for variables and implicit allocations, connects them with assignment edges, and
marks a location heap-owned when a pointer to stack storage can be stored in
heap memory or outlive its declaring frame. It also records parameter-flow
summaries so static call sites can reason about arguments.

Practical rules:

- Creation syntax does not decide stack vs heap; sharing and lifetime decide.
- A value can move to heap when its address is returned, stored in a retained
  object, captured by reference, boxed into an escaping interface, passed to a
  leaking parameter, or created with runtime-sized storage.
- Taking an address is not automatically a heap allocation. Sharing down the
  current call stack can stay on stack; sharing up, storing, or otherwise
  retaining beyond the declaring frame forces heap ownership.
- Pointer syntax is a signal of sharing. Do not replace value construction with
  pointer construction just to "match" an escape report; preserve readable
  ownership and fix the real retention path.
- Escape output is conservative. Treat each line as a candidate owner, not as a
  measured allocation count.
- The compiler does not fully distinguish struct fields, slice elements, or map
  entries. Classify those as ownership-family signals, then confirm with exact
  benchmarks or allocation profiles.

## Compiler Counting Model

Use this model to understand why the compiler reports one variable as escaping
and another as stack-local.

The compiler creates a graph:

- A **location** represents storage for a variable, literal, `new`, `make`,
  closure, method value, temporary, parameter, result, or synthetic sink.
- An **edge** represents an assignment flow from source location to destination
  location.
- Each edge has a **dereference count**:

| Source code shape | Edge count | Meaning |
|---|---:|---|
| `p = &q` | `-1` | `q`'s address flows to `p`. |
| `p = q` | `0` | `q`'s value flows to `p`. |
| `p = *q` | `+1` | value reachable after one dereference flows to `p`. |
| `p = **q` | `+2` | value reachable after two dereferences flows to `p`. |

Counts are lower-bounded at `-1`; the address of an addressable expression can
flow, but the compiler does not keep subtracting below "address taken."

The solver walks from each root location and computes the **minimum dereference
count** to every other location. Negative counts mean "an address of this
location reaches the root." Non-negative counts mean "a value reachable from
this location reaches the root."

Decision points:

| Compiler question | If yes | How to read it in reports |
|---|---|---|
| Does `l.derefs < 0`? | `l`'s address flows to the root. | Look for `&x escapes`, `moved to heap: x`, or flow lines with `&`. |
| Does the root outlive `l`? | `l` must be heap allocated. | Root is heap, result, outer loop scope, or enclosing frame that outlives an inner closure/loop object. |
| Does address flow only to a non-outliving caller frame? | `l` can remain stack-local. | `&x does not escape` is valid when sharing down the stack is bounded. |
| Is `l` a parameter and it flows to heap/result/mutator/callee? | record a parameter leak summary. | `leaking param`, `leaking param to result`, `mutates param`, `calls param`. |
| Does `make`/literal have unknown or too-large bounded storage? | may force heap or hybrid lowering. | `too large for stack`, dynamic-size `make`, or no stack proof. |

The compiler's `outlives` relation is also countable:

| Outlives case | Why it matters |
|---|---|
| Heap root | Heap outlives every stack frame. |
| Result parameter | Callers may retain returned values, so results are pessimistically treated as outliving locals, except statically known closure cases. |
| Outer loop scope | A variable declared outside a loop outlives values allocated inside later iterations. |
| Enclosing function frame | An outer frame outlives storage allocated in a child closure frame. |
| Same frame and same loop scope | Address flow can stay stack-local if it does not reach another outliving sink. |

Manual counting rule:

1. Pick the allocation origin, not just the helper in the report.
2. Trace every `from ... at ...` line as one flow path.
3. Add deref counts along that path:
   - `&` subtracts one;
   - plain assignment adds zero;
   - `*` adds one per dereference;
   - interface boxing/call arguments preserve the current flow while moving it
     to a callee or heap-like unknown sink.
4. Ask whether the destination outlives the origin.
5. If the minimum path has negative count and outlives the origin, it is a heap
   escape. If only value flow reaches a result or parameter summary, classify it
   as a leak summary and inspect callers.

Do not overcount one compiler explanation chain. A chain with four `from ...`
lines is one allocation origin with one reason path, not four heap allocations.

## How To Prevent The Escape The Compiler Counted

Fix the counted path, not the line that looks suspicious.

| Counted compiler path | Why it escapes | Prevention target |
|---|---|---|
| Negative deref path reaches result or heap: `root = &local` | address of stack storage reaches an outliving root | Return a value, let caller pass destination storage, or make retained ownership explicit and intentional. |
| Negative deref path reaches outer loop variable | storage allocated in one iteration can be observed in another | Move owner inside the loop if per-iteration, or allocate/reuse explicit storage outside the loop if shared lifetime is intended. |
| Negative deref path reaches enclosing frame through closure | child closure storage would outlive its frame | Capture by value when possible, move storage to the enclosing owner, or avoid retaining closure state. |
| Parameter leak to heap/result | caller argument is retained or returned by callee | Change callee API to copy, consume, or write into caller-owned destination; inspect callers before marking fixed. |
| Interface conversion to escaping call argument | concrete value is boxed into an interface whose callee summary leaks | Call the concrete method, make the interface boundary higher-level/less frequent, or prebuild retained interface objects. |
| Dynamic `make` or variable-size backing store | compiler/toolchain and proven bound decide placement; newer Go releases can stack-allocate more variable-sized slices | Read the active toolchain's `-m=2` result first. Use bounded arrays or split small/large paths only when public benchmarks and stack/frame evidence improve. |
| `append` path with unknown capacity | backing storage may be allocated and retained | Pre-size exactly, keep reusable capacity, or append into caller-owned scratch. |
| `math/big` result returned as pointer | result storage is owned by callee and returned | Use `Into(dst)` or bounded fixed-width arithmetic; pool only non-retained variable-count temps. |
| String/byte conversion reaches retained sink | conversion creates owned memory for a longer-lived value | Avoid conversion, use typed bytes, intern/static IDs, or copy only once at the real retention boundary. |

After a fix, re-count the path:

1. Did the negative deref path to an outliving root disappear?
2. Did the sink stop outliving the origin?
3. Did a parameter leak summary become non-leaking, shorter, or caller-owned?
4. Did dynamic storage become compile-time bounded or explicit scratch/pool
   ownership?
5. Did exact `B/op` / `allocs/op` or retained heap improve?

If the answer is only "the escape line moved to another nearby helper," reject
the patch unless measured allocation lifetime or workload call count improved.

## Evidence Workflow

Run escape analysis and measurement together:

```sh
go test -c -gcflags='all=-m=2' -o "$ART/pkg_escape.test" ./pkg \
  > "$ART/escape_analysis_raw.log" 2>&1

go test ./pkg -run '^$' -bench '<exact row>' -benchmem -count=1 \
  > "$ART/exact_bench.log" 2>&1

go test ./pkg -run '^$' -bench '<exact row>' -benchmem \
  -memprofile "$ART/mem.out" -count=1 \
  > "$ART/exact_bench_memprofile.log" 2>&1

go tool pprof -top -alloc_space "$ART/pkg_escape.test" "$ART/mem.out" \
  > "$ART/pprof_alloc_space_top.txt"

go tool pprof -list '<function-regex>' -alloc_space \
  "$ART/pkg_escape.test" "$ART/mem.out" \
  > "$ART/pprof_alloc_space_list.txt"
```

Use `alloc_space` for allocation-source work. `inuse_space` answers a different
question: what remains live at profile time.

Use pprof first to find measured allocation lines, then use `-m=2` output to
explain why those lines escape. In pprof `list` output, `flat` bytes are
allocated in the listed function; `cum` bytes include callees. Do not optimize a
caller just because its cumulative column is large.

## How To Count Escape Cases

Never count raw escape lines as allocation counts. Count them as static cases,
then join them to benchmark/profile evidence.

Build one row per allocation origin:

| Column | Meaning |
|---|---|
| `file:function:line` | Allocation origin, not just the helper where it was reported. |
| `escape_line` | Exact compiler line: `escapes to heap`, `moved to heap`, `leaking param`, `too large for stack`, etc. |
| `flow_reason` | Return, assignment to heap object, closure capture, interface boxing, dynamic size, call param leak, append growth, conversion, or retained contract. |
| `owner_lifetime` | Host-call temp, caller frame, loop iteration, execution lifetime, module lifetime, DB/cache/action/log retained, async retained, trace-only, cold/error-only. |
| `fix_hypothesis` | What allocation disappears or gets shorter-lived. |
| `measured_row` | Exact benchmark row and `ns/op`, `B/op`, `allocs/op`. |
| `status` | `FIXABLE`, `RETAINED_BY_CONTRACT`, `TRACE_ONLY`, `COLD_ERROR_ONLY`, `REJECTED`, or `DONE`. |

When reading compiler chains, keep the whole path:

```text
&T literal escapes to heap
from x (assigned)
from x (interface-converted)
from x (passed to call[argument escapes])
```

Count that as one allocation origin with an interface-conversion/call-argument
flow reason, not four independent allocations.

Aggregate by issue type:

| Group key | Use |
|---|---|
| allocation kind | `new/make`, string/byte conversion, `append`, `big.Int`/`big.nat`, map/slice, closure, interface, method value, retained payload |
| owner lifetime | distinguishes a real optimization from a moved allocation |
| function/import family | points to similar surfaces |
| measured impact | exact `B/op`, `allocs/op`, `alloc_space`, and target workload call count |

Sort first by confirmed measured impact, then by static frequency. Static
frequency alone is not priority.

## Common Escape Causes And Fix Patterns

| Cause | Example pattern | Preferred fix |
|---|---|---|
| Return pointer to local | `return &x` | Return value, or let caller own storage and pass `dst *T`. |
| Retained object stores pointer/slice | `obj.buf = b` | Copy intentionally and mark retained-by-contract, or transfer ownership with explicit release semantics. |
| Dynamic slice size | `make([]byte, n)` | Use fixed array when max size is small/known, or caller-provided/pool-owned buffer when lifetime is explicit. |
| String/byte conversion | `string(b)`, `[]byte(s)` | Avoid conversion, write bytes directly, intern/static-ID stable strings, or copy only at retained boundary. |
| `append` growth | `append(dst, src...)` with unknown cap | Pre-size exactly, reuse caller-owned scratch, or keep capacity across calls. |
| `math/big` temporaries | returning `*big.Int`, `Set`, `Mul`, `Div` growing `nat` | Use `Into(dst)` APIs, retained scratch with capacity, `uint256` fast path for bounded values, or pool only non-retained variable-count temps. |
| Interface boxing / formatting | `fmt.Sprintf`, `any(v)` in hot path | Use typed append/strconv helpers; keep formatting on trace/error paths. |
| Interface call when concrete method is available | `io.ReadFull(r, buf)` where `r` is concrete and owned | Call the concrete method directly if the interface provides no needed abstraction. |
| Closure capture / method value | callback stores locals or receiver | Inline small hot path, pass explicit values, avoid per-call closure/method values. |
| Map/slice per-call init | `map[...]...{}` or `make(map...)` per call | Move immutable maps to module scope, prebuild per-module state, or use fixed arrays/switches for tiny domains. |
| Large or unknown stack object | compiler reports too large/unknown size | Treat this as "compiler cannot prove bounded stack size" until confirmed; if truly fixed and small, make the size compile-time constant. Otherwise classify as required or pool with clear ownership. |

## Before/After Acceptance

Accept an escape fix only when at least one is true:

- the exact benchmark row reduces `B/op` or `allocs/op`;
- retained heap or `alloc_space` drops for the target workload;
- target workload call count drops;
- ownership/lifetime is explicitly shortened and measured by a relevant profile.

Reject it when:

- the same allocation moves to a caller/helper with the same lifetime;
- escape text improves but `B/op` and `allocs/op` do not;
- `B/op` drops but wall time regresses beyond the approved gate;
- the fix adds unclear ownership for DB/cache/log/action/result data.

## Counting Examples

Pointer return:

```go
// Count as: return-flow escape, caller-owned lifetime.
func makeUser() *user {
    u := user{name: "n"}
    return &u
}

// Fix: return a value when callers do not require identity/mutation sharing.
func makeUser() user {
    return user{name: "n"}
}
```

Count:

| Flow | Derefs | Outlives? | Decision |
|---|---:|---:|---|
| result `~r0 = &u` | `-1` | yes, caller result outlives callee frame | `u` escapes |

Non-escaping address share:

```go
// Count as: address is shared down the stack only. It may not escape.
func printUser(u user) {
    println(&u)
}
```

Count:

| Flow | Derefs | Outlives? | Decision |
|---|---:|---:|---|
| `println` receives `&u` | `-1` | no retained result/heap sink | `u` can stay stack-local |

Caller-owned destination:

```go
// Count as: callee allocation with returned-result ownership.
func price(a, b *big.Int) *big.Int {
    return new(big.Int).Div(a, b)
}

// Fix: caller owns capacity and lifetime.
func priceInto(dst, a, b *big.Int) {
    dst.Div(a, b)
}
```

Count:

| Flow | Derefs | Outlives? | Decision |
|---|---:|---:|---|
| `return new(big.Int)` | `-1` address/result flow | yes | allocation belongs to callee result |
| `dst.Div(a, b)` | `0` value mutation through caller-owned storage | caller already owns `dst` | no new result allocation required |

Fixed-size output:

```go
// Count as: temporary buffer escape if generic writer retains or boxes it.
var buf [32]byte
encode(buf[:])
write(ptr, buf[:])

// Fix only when runtime memory is documented write-through and not retained.
mem, ok := module.Memory().Read(ptr, 32)
if !ok {
    return false
}
encode(mem[:32])
```

Count:

| Flow | Derefs | Outlives? | Decision |
|---|---:|---:|---|
| `buf[:]` passed to generic writer | depends on writer parameter leak summary | inspect `leaking param` / retained sink | may escape |
| runtime memory view used synchronously | no retained Go slice; bytes written to external memory | not a Go heap owner | accepted only with runtime API proof |

Dynamic slice:

```go
// Classify from the active toolchain's escape output.
buf := make([]byte, n)

// Fix when max size is small and compile-time known.
var buf [64]byte
use(buf[:n])
```

Count:

| Flow | Derefs | Outlives? | Decision |
|---|---:|---:|---|
| `make([]byte, n)` where `n` varies | placement is toolchain- and bound-dependent; Go 1.26 can stack-allocate more variable-sized backing stores | inspect `-m=2`, frame/stack growth, and `benchmem` | measured stack or heap path; do not assume |
| `[64]byte` local with checked `n <= 64` | fixed frame size | no outliving sink by itself | stack candidate |

Interface conversion:

```go
// Count as: concrete value boxed into an interface call.
input := bytes.NewBuffer(data)
_, _ = io.ReadFull(input, buf)

// A direct Read is not equivalent: short nonempty input returns a short count
// with nil error, while ReadFull returns io.ErrUnexpectedEOF. Preserve the fill
// and error contract; specialize only with independent short/empty-input proof.
input := bytes.NewBuffer(data)
n, err := io.ReadFull(input, buf)
// Handle n and err according to the caller contract; do not discard them.
```

Count:

| Flow | Derefs | Outlives? | Decision |
|---|---:|---:|---|
| `input` assigned to interface argument | `0` value boxed into interface; callee param may leak | depends on callee summary, often heap-like for unknown interface use | concrete buffer can escape |
| `input.Read` concrete call | no interface box | callee summary is concrete/static | can remove escape if no other sink retains it |
