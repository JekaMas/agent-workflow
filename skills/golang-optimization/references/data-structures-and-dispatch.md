# Data Structures And Dispatch

Use this reference when profiles name map hashing/growth, interface conversion,
generic dictionary calls, reflection, method values, or string/byte conversion.

Primary references: current [map implementation](https://go.dev/src/internal/runtime/maps/map.go),
[interface runtime](https://go.dev/src/runtime/iface.go),
[generics implementation](https://go.googlesource.com/proposal/+/master/design/generics-implementation-dictionaries-go1.18.md),
[`reflect`](https://pkg.go.dev/reflect), and [`unsafe`](https://pkg.go.dev/unsafe).

- [Maps and dense domains](#maps-and-dense-domains)
- [Interfaces and boxing](#interfaces-and-boxing)
- [Generics and generated call shape](#generics-and-generated-call-shape)
- [Reflection plans](#reflection-plans)
- [Zero-copy representation boundaries](#zero-copy-representation-boundaries)

## Maps And Dense Domains

Current Go map implementations and compiler/runtime details are toolchain-
sensitive. Optimize the contract and measured workload rather than depending on
an undocumented bucket/group layout.

Go 1.24 and later use a Swiss-table-based map implementation, including compact
group handling for small maps. Treat that as current implementation context,
not a stable public layout or a reason to skip cardinality benchmarks.

Candidates:

- use `make(map[K]V, expected)` when cardinality is bounded and known;
- choose compact keys that avoid conversion and preserve exact identity;
- compare linear scan, sorted slice plus binary search, map, bitmap, or direct
  indexed slice at real cardinalities and update/read ratios;
- build immutable indexes once when repeated lookup amortizes construction;
- avoid temporary normalized strings in lookup hot paths; normalization belongs
  at the approved constructor/boundary.

Benchmark hits, misses, skew, cardinality, build/update cost, iteration, memory,
and deterministic-output work. A small map can lose to a linear slice; a dense
integer domain can favor a bitmap or slice. Map iteration remains unordered and
must not become canonical output without explicit ordering.

## Interfaces And Boxing

Not every interface conversion allocates, but interface dispatch can block
static inlining/devirtualization and conversions can box or escape values.

Candidates:

- convert at an outer boundary and run a typed inner kernel;
- replace repeated `any` conversion or method-value creation in hot loops with
  direct typed calls;
- compare value and pointer receivers when copy size, aliasing, and escape
  behavior differ;
- use PGO for a whole executable when production dispatch is polymorphic but
  dominated by a small set of concrete receivers.

Required evidence: call-site CPU/allocation profile, `-m=2`, final disassembly,
public benchmark, and binary-size comparison when specialization duplicates
code.

## Generics And Generated Call Shape

Do not assume generics are either free or slow. Go can share code across GC
shapes and pass dictionaries; operator-only code, interface methods, and
constraint method calls can produce different call shapes.

Compare:

- generic, interface, and concrete variants through the public API;
- representative scalar, struct, and pointer-shaped instantiations;
- direct calls, dictionary/itab lookups, inlining, and escape decisions;
- binary/text size across the real instantiation set.

Keep a generic abstraction when it removes duplication without a measured
public regression. Keep concrete specialization only for a named hot shape and
remove unselected variants.

## Reflection Plans

When reflection cannot be removed, perform it once to build a typed execution
plan: field indexes, offsets, codecs, validators, or closures. Keep repeated
`reflect.Value.Interface`, method lookup, map walking, and type discovery out of
element loops.

Compare reflective, cached-plan, generated typed, and narrowly unsafe-offset
candidates only when the owner justifies each risk tier. Required proof:

- schema/type cache ownership and invalidation;
- `alloc_objects`, `alloc_space`, CPU, and public throughput;
- malformed, embedded/unexported, nil, and schema-change tests;
- race tests for shared plans;
- toolchain/architecture revalidation for unsafe offsets.

Use the lower-risk reflection iterator guidance in
[runtime-and-concurrency-techniques.md](runtime-and-concurrency-techniques.md)
when map iteration itself owns allocations.

## Zero-Copy Representation Boundaries

Zero-copy string/byte views are ownership changes, not merely instruction
changes. Use ordinary conversion unless profiles prove its allocation/copy is
material and the lifetime is explicit.

Good candidates: immutable mapped data, request-scoped read-only input, or
ownership-transferred buffers that cannot be reused or mutated while the view
exists.

Reject for pooled/mutable network buffers, retained cache keys, asynchronous
work, or APIs that allow mutation. For unsafe views require:

- exact producer/consumer lifetime and immutability proof;
- no retained pointer after storage reuse or unmap;
- race, fuzz, `checkptr`, architecture, and GC-liveness tests;
- public allocation/CPU gain that includes the original conversion boundary;
- no use of `uintptr` to hide ownership or escape behavior.

Separate typed `string` and `[]byte` APIs can be clearer and faster than an
unsafe conversion or interface-shaped shared API.
