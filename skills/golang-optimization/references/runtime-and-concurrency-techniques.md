# Runtime And Concurrency Techniques

Use this reference only after benchmarks and profiles isolate one narrow
bottleneck that still matters. Each section names the required evidence, the
patch shape, and the proof to collect after the change.

Primary references: [runtime internals](https://go.dev/src/runtime/HACKING),
[scheduler implementation](https://go.dev/src/runtime/proc.go),
[Go memory model](https://go.dev/ref/mem), [`sync`](https://pkg.go.dev/sync),
and [`sync/atomic`](https://pkg.go.dev/sync/atomic).

Contents: gate, G/M/P and bounded concurrency, channels/select, mutexes,
pools, sharded locks, `sync.Map`, `sync.Cond`, atomic snapshots, weak
references, reflection iterators, `container/heap.Fix`, and scheduler knobs.
For compiler and architecture techniques, read
[compiler-and-machine-code.md](compiler-and-machine-code.md).

- [Gate](#gate)
- [G/M/P and bounded concurrency](#gmp-and-bounded-concurrency)
- [Channels and select](#channels-and-select)
- [Mutexes, RWMutex, and starvation](#mutexes-rwmutex-and-starvation)
- [Pools](#pools)
- [Sharded locks](#sharded-locks)
- [`sync.Map`](#syncmap)
- [`sync.Cond`](#synccond)
- [Atomics, snapshots, and lock-free gates](#atomics-snapshots-and-lock-free-gates)
- [Weak references and cleanup](#weak-references-and-cleanup)
- [Reflection iterators](#reflection-iterators)
- [`container/heap.Fix`](#containerheapfix)
- [Scheduler knobs](#scheduler-knobs)

## Gate

| Tool | Required evidence | Reject when |
|---|---|---|
| `sync.Pool` | `B/op`, `allocs/op`, or `alloc_space` names temporary-object churn. | Reuse is owner-local, objects have retained references, or reset cost dominates. |
| Bounded concurrency | Trace shows runnable queues/fanout or external saturation. | Work is CPU-scaling normally or a bound violates latency/throughput. |
| Channel/select change | Block/trace evidence names channel protocol or scan cost. | Change weakens ownership, cancellation, ordering, or close behavior. |
| Mutex/RWMutex change | Mutex/block profile names contention and read/write mix is known. | Critical section is not the owner or fairness/starvation worsens. |
| Sharded locks | Mutex profile or trace `sync` names one lock and keys distribute. | Operations span shards or deterministic global ordering is required. |
| `sync.Map` | Write-once/read-many or disjoint-key mutation beats `map` plus lock. | Typed invariants under one lock matter or key skew keeps one hot slot. |
| `sync.Cond` | Block profile names channel wake/wait protocol overhead. | A channel design is clear and not measurable. |
| Atomic snapshot | Readers need immutable whole-value publication. | In-place mutation, fairness, or wait queues are required. |
| Lock-free state | Mutex/block evidence names contention and a narrow protocol has a proof. | Multi-field invariants, reclamation/ABA, spinning, or fairness are unresolved. |
| Weak/cleanup | Cache entries may disappear without correctness loss. | Residency or cleanup-before-exit is a requirement. |
| Reflection trimming | Reflection cannot be removed and map walking allocates. | Typed code or code generation is feasible. |
| `heap.Fix` | Priority changes in place and remove+push/rebuild churn appears. | Item indexes cannot be kept correct. |
| Scheduler knobs | Trace/service metrics identify scheduler or thread-affinity pressure. | Generic speed tuning. |

## G/M/P And Bounded Concurrency

Use the runtime G/M/P model to interpret evidence, not to justify scheduler
folklore. Trace runnable delay, P utilization, blocked syscalls, goroutine
states, queue depth, and downstream saturation before changing worker counts.
Do not tune from assumptions about local/global run queues or work stealing;
confirm the active toolchain's behavior in runtime source and prove the owner
with trace and load evidence.

Candidates:

- bound runnable workers by CPU or external capacity;
- batch tiny work when queueing/cancellation semantics allow it;
- remove goroutine-per-item fanout when scheduling dominates;
- use owner-local queues or work partitioning when a central queue/lock owns
  contention;
- preserve admission, backpressure, cancellation, drain/discard, stop, and join
  behavior.

Benchmark under load ramps and saturation, not only steady-state throughput.
Report p50/p95/p99, throughput, runnable latency, goroutine count, queue depth,
downstream utilization, and shutdown behavior. An unbounded queue is not an
optimization because it hides backpressure.

## Channels And `select`

Channels express ownership transfer and synchronization; they are not a
universal fastest queue. Compare channels with direct calls, owner-local
buffers, mutex-protected queues, or `sync.Cond` only when block/trace evidence
names the protocol.

For select-heavy loops, measure ready-case count, default/timer frequency,
closed/nil cases, wakeups, fairness, and cancellation latency. Splitting one
large heterogeneous `select` into owned stages can reduce scan/wakeup cost while
adding goroutines and queues; test the full lifecycle.

Required tests cover send/receive ownership, close exactly once, blocked sender
and receiver release, cancellation, timeout, drain/discard policy, no goroutine
leak, and deterministic ordering where required.

## Mutexes, `RWMutex`, And Starvation

Shorten critical sections and move IO, logging, decoding, and allocation out of
locks before sharding or atomics. Compare `Mutex` and `RWMutex` on the actual
read duration, write ratio, key skew, and core count; read-mostly labels alone
do not prove `RWMutex` wins.

Required evidence:

- mutex and block profiles, including holder stacks;
- critical-section duration and read/write/key distribution;
- throughput and p95/p99 across `GOMAXPROCS` and saturation;
- fairness/starvation and writer-progress tests;
- race/stress tests and deterministic multi-lock ordering.

Sharding is accepted only when operations normally stay in one shard and
cross-shard operations have a deterministic lock order.

## Pools

Rules:

- Pool pointers and reset before `Put`.
- Split size classes; do not pool tiny and huge buffers together.
- Never return pooled objects that still alias caller-owned data.
- Compare against owner-local reuse before adding cross-goroutine sharing.

```go
var bufPool = sync.Pool{
	New: func() any { return new(bytes.Buffer) },
}

func encode(r Record) []byte {
	buf := bufPool.Get().(*bytes.Buffer)
	buf.Reset()
	defer bufPool.Put(buf)

	writeRecord(buf, r)
	return append([]byte(nil), buf.Bytes()...) // detach from pooled storage
}
```

Proof: `benchstat` shows lower `B/op` or `allocs/op`; CPU and mutex profiles do
not show reset or sharing as the new owner.

## Sharded Locks

Rules:

- Shard by stable key hash.
- Keep operations single-shard, or define a deterministic multi-shard lock order.
- Benchmark skewed keys, not only uniform keys.

```go
type shard struct {
	mu sync.Mutex
	m  map[string]Value
}

type table struct {
	shards [64]shard
}

func (t *table) get(k string) (Value, bool) {
	s := &t.shards[hash(k)&63]
	s.mu.Lock()
	v, ok := s.m[k]
	s.mu.Unlock()
	return v, ok
}
```

Proof: mutex wait drops in `mutex.pprof` or trace `sync` output on the target
key distribution.

## `sync.Map`

Use only for write-once/read-many caches or disjoint-key mutation. Benchmark it
against `map[K]V` guarded by `sync.RWMutex`.

```go
type rules struct {
	rows sync.Map // string -> *compiledRule
}

func (r *rules) Get(src string) (*compiledRule, error) {
	if v, ok := r.rows.Load(src); ok {
		return v.(*compiledRule), nil
	}
	compiled, err := compileRule(src)
	if err != nil {
		return nil, err
	}
	actual, _ := r.rows.LoadOrStore(src, compiled)
	return actual.(*compiledRule), nil
}
```

Rules: store immutable values, treat `Range` as non-snapshot iteration, and do
not use `sync.Map` for multi-field invariants.

## `sync.Cond`

Use when a hot wait protocol is a predicate protected by a lock.

```go
type queue struct {
	mu    sync.Mutex
	ready *sync.Cond
	rows  []Item
}

func newQueue() *queue {
	q := &queue{}
	q.ready = sync.NewCond(&q.mu)
	return q
}

func (q *queue) Pop() Item {
	q.mu.Lock()
	defer q.mu.Unlock()
	for len(q.rows) == 0 {
		q.ready.Wait()
	}
	v := q.rows[0]
	q.rows = q.rows[1:]
	return v
}
```

Rules: call `Wait` in a loop, mutate the predicate under the lock, and prove
termination with tests plus block-profile before/after data.

## Atomics, Snapshots, And Lock-Free Gates

Use `atomic.Value` or `atomic.Pointer[T]` for immutable read-mostly snapshots.

```go
type routes struct {
	byPath map[string]handler
}

var current atomic.Value // stores *routes

func publish(r *routes) {
	current.Store(r) // r and nested maps are immutable after this point
}
```

Proof: reader latency or lock wait drops; writer cost and stale-read semantics
are acceptable for the product path.

Go's public atomic operations are sequentially consistent, but atomic fields do
not make a multi-field invariant atomic. Good candidates include independent
counters, flags, monotonic sequence numbers, immutable snapshots, and compact
state machines with an explicit transition proof.

Reject atomics for linked structures without reclamation and ABA analysis,
several values that must change together, fairness/wait-queue requirements, or
a global counter whose cache-line contention remains. Lock-free work requires:

- a written state/invariant and linearization-point proof;
- race, stress, long-running concurrency, cancellation, and progress tests;
- mutex/block baseline showing simpler synchronization is the owner;
- contention levels from one worker through production saturation;
- CPU, latency, spinning, scheduler, and cache-line/false-sharing evidence;
- ownership and reclamation proof for every published pointer.

If lock wait falls while CPU or tail latency rises, the candidate may only have
replaced parking with spinning. Remove it unless the complete workload wins.

## Weak References and Cleanup

Use weak references only when recomputation after collection is correct.

```go
type cache struct {
	mu   sync.Mutex
	rows map[string]weak.Pointer[compiledRule]
}

func (c *cache) Get(src string) (*compiledRule, error) {
	c.mu.Lock()
	if p, ok := c.rows[src]; ok {
		if v := p.Value(); v != nil {
			c.mu.Unlock()
			return v, nil
		}
	}
	c.mu.Unlock()
	return compileRule(src)
}
```

Rules: always handle `nil`, do not rely on finalization order, keep explicit
`Close`/`Release` paths for critical resources, and use `runtime.KeepAlive`
after the last point an object must remain reachable.

## Reflection Iterators

Use this only in framework code where reflection is unavoidable.

```go
func copyStringMap(dst map[string]string, src any) {
	v := reflect.ValueOf(src)
	iter := v.MapRange()
	var k, val string
	kv := reflect.ValueOf(&k).Elem()
	vv := reflect.ValueOf(&val).Elem()
	for iter.Next() {
		kv.SetIterKey(iter)
		vv.SetIterValue(iter)
		dst[k] = val
	}
	iter.Reset(reflect.Value{})
}
```

Proof: `alloc_objects` or `alloc_space` drops in the dynamic path. If a concrete
type is available, benchmark the concrete path first.

## `container/heap.Fix`

Use `heap.Fix` for in-place priority updates.

```go
type item struct {
	Priority int
	Index    int
}

func (p *pq) Swap(i, j int) {
	(*p)[i], (*p)[j] = (*p)[j], (*p)[i]
	(*p)[i].Index = i
	(*p)[j].Index = j
}

func (p *pq) Update(it *item, priority int) {
	it.Priority = priority
	heap.Fix(p, it.Index)
}
```

Proof: update-heavy benchmarks improve; tests cover `Swap`, `Push`, `Pop`, and
priority mutation index updates.

## Scheduler Knobs

`runtime.LockOSThread` is for thread-affine OS or native APIs.
`runtime.GOMAXPROCS` is for controlled scheduler/container experiments; manual
calls disable automatic default updates until `runtime.SetDefaultGOMAXPROCS`.

Required proof: host/container CPU context, trace or service metrics naming the
scheduler issue, and before/after `p95`, `p99`, throughput, and saturation.

On supported Go/Linux releases, the runtime can derive and periodically update
the default `GOMAXPROCS` from logical CPU availability and cgroup CPU bandwidth.
Record environment variables, cgroup quota/cpuset, runtime default, and manual
calls before overriding it. A manual value can disable automatic adaptation.

`GODEBUG=asyncpreemptoff=1` is a diagnostic control for preemption questions,
not a production throughput recommendation. `runtime.LockOSThread` reduces
scheduler freedom and is rejected unless an OS/native contract or controlled
affinity experiment requires it. For NUMA and process placement, use
[io-network-and-system-techniques.md](io-network-and-system-techniques.md).
