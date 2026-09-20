# Optimization Catalog

Use this reference after baseline evidence identifies a bottleneck and the agent
needs to choose the class of fix. For detailed algorithms and examples, read
[optimization-decision-playbook.md](optimization-decision-playbook.md). For
compiler/architecture or runtime/concurrency gates, read
[compiler-and-machine-code.md](compiler-and-machine-code.md) or
[runtime-and-concurrency-techniques.md](runtime-and-concurrency-techniques.md).
For the complete evidence/payoff/risk matrix, read
[technique-expectation-matrix.md](technique-expectation-matrix.md).

Contents: fix-class selection, evidence, risk gates, and compact patch shapes.

## Fix-Class Order

Prefer lower rows only after upper rows are ruled out or insufficient.

| Class | Evidence | First patch shape | Risk gate |
|---|---|---|---|
| Do less work | repeated parsing, formatting, sorting, hashing, lookup, helper calls | hoist, cache, batch, skip | cache lifetime, invalidation, bounds |
| Better algorithm/data structure | poor growth across input sizes, search/sort/lookup/division owner | index, sort once, precompute, SWAR/chunking, invariant arithmetic | edge cases and distributions |
| Better representation | conversion churn, pointer chasing, serialization overhead | fixed units, compact structs, columns, preallocation | unit/rounding contract |
| Better locality | measured cache misses or working-set crossover | split hot/cold fields, compact hot rows, contiguous batches, access-order change | pointer chasing, ownership, full-operation cost |
| Lower allocation | high `B/op`, `allocs/op`, `alloc_space`, `alloc_objects` | caller buffers, prealloc, concrete APIs, fewer conversions | aliasing and retention |
| Lower GC scan/barriers | `/gc/scan`, GC CPU, assists, barrier frames | flatten pointer graphs, split hot/cold, immutable snapshots | copy cost, retained memory, ownership |
| Concurrency tuning | CPU low but wall time high; block/mutex/trace owner | shorter critical sections, bounded workers, batching | ownership, cancellation, determinism |
| IO/system boundary | trace/kernel evidence names copies, syscalls, crossings, faults | preserve fast paths, vector/batch, mmap or placement only when proven | deadlines, lifetime, portability, memory |
| Compiler/runtime-aware source | hot interface/reflection/bounds/fmt/string-byte/call frames or measured branch misses | concrete types, simpler loops, BCE-friendly guards, inlineable wrappers, append APIs, measured branchless arithmetic | compiler/counter evidence and benchmark after Go upgrades |
| Profile-guided optimization | representative whole-program CPU profile and source fixes are already exhausted | build the final main package with `-pgo`; compare identical binaries/workloads | workload representativeness, profile ownership, regressions, build size/time |
| Advanced mechanisms | ordinary fixes fail and bottleneck is isolated | `sync.Pool`, atomics, unsafe, SIMD, cgo, asm, scheduler knobs | larger measured payoff, portability, ownership, and safety tests |

## Patch Shapes

Hoist invariant work:

```go
type matcher struct {
	re *regexp.Regexp
}

func newMatcher(pattern string) (*matcher, error) {
	re, err := regexp.Compile(pattern)
	if err != nil {
		return nil, err
	}
	return &matcher{re: re}, nil
}
```

Build an index:

```go
type usersByID struct {
	rows []User
	idx  map[string]int
}

func buildUsersByID(rows []User) usersByID {
	idx := make(map[string]int, len(rows))
	for i := range rows {
		idx[rows[i].ID] = i
	}
	return usersByID{rows: rows, idx: idx}
}
```

Store hot numerics in internal fixed units:

```go
type Level struct {
	PriceTicks int64
	SizeLots   int64
	Side       uint8
}
```

Use columns when loops touch only one or two fields:

```go
type LevelColumns struct {
	PriceTicks []int64
	SizeLots   []int64
	Side       []uint8
}
```

Append into caller-owned buffers:

```go
func AppendLevel(dst []byte, l Level) []byte {
	dst = strconv.AppendInt(dst, l.PriceTicks, 10)
	dst = append(dst, ':')
	dst = strconv.AppendInt(dst, l.SizeLots, 10)
	return dst
}
```

Move slow work outside the lock:

```go
func (s *Store) Update(k string, v Value) {
	next := prepareValue(v)
	s.mu.Lock()
	s.rows[k] = next
	s.mu.Unlock()
}
```

Prefer append-style formatting on hot paths:

```go
func AppendStatus(dst []byte, id int64, status string) []byte {
	dst = strconv.AppendInt(dst, id, 10)
	dst = append(dst, ':')
	return append(dst, status...)
}
```

## API Shape, Generics, Reflection, and Stdlib

Use this section when profiles point to abstraction overhead.

- Prefer concrete types in tight loops when interface dispatch or boxing appears
  in CPU or allocation profiles.
- Use generics when they remove real duplication across multiple call sites; if
  a generic helper is hot, benchmark it against concrete and stdlib helpers.
- Prefer `slices`, `maps`, `cmp`, `sort`, `strconv`, `encoding/binary`,
  `math/bits`, and append-style APIs where they fit the workload.
- Treat map iteration as unordered. For deterministic output, sort keys with an
  explicit comparator.
- Prefer code generation, generics, specialized stdlib functions, or explicit
  code before reflection. If reflection cannot be removed, use
  [runtime-and-concurrency-techniques.md](runtime-and-concurrency-techniques.md).

## Repo Example: Orderbook Numeric Conversion

Evidence from `application/cex/orderbooknumeric`:

- Benchmark: `BenchmarkFromDecimalSnapshotSPXDepth`.
- Baseline: about `104us/op`, `85.1kB/op`, `3.20k allocs/op`.
- Allocation profile: `fromDecimalLevels` owns most cumulative allocation.
- Hot callees include `math/big`, `shopspring/decimal.Mul`, `rescale`, and
  `NewFromString`.

Useful hypotheses:

- Cache scale multipliers instead of rebuilding decimal/big values per level.
- Parse fixed-format market data into exact integer units when semantics allow.
- Preallocation is already present, so slice growth is not the main owner.
- Cold error formatting in escape logs is not a target unless profiles prove it.

Required proof:

- exactness, zero/rounding, scale, and invalid-level tests;
- variable-depth benchmarks such as 1, 10, 100, 1000;
- before/after `benchstat` for time, bytes, and allocation count;
- allocation profile proving the targeted owner moved or shrank.
