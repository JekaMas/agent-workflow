# MDBX Ordered Cursor Optimization

Use this reference after profiling or DB instrumentation shows that cursor
opens, repeated range seeks, or row-by-row cursor crossings own meaningful cost.
The key contract and the exact question must be established before changing the
scan. MDBX ordering can remove work only when the persisted key order matches the
query order.

## Contents

- Start With Semantics
- Exact Nested-Window Probe
- Contiguous Partitions: Scan Once
- Why Probabilistic Filters Usually Do Not Help
- Cursor and Byte Ownership
- Measurement Matrix
- Escalation Gate

## Start With Semantics

Name the exact set being queried. Similar words can refer to different durable
facts:

- an open-work index answers questions about work that remains open;
- an event bucket answers questions about transitions that occurred;
- a latest-value bucket cannot answer historical range questions;
- a derived cache cannot replace authoritative evidence after restart unless its
  rebuild and invalidation contract is proven.

Do not use a recent-window result to suppress older backlog. For example,
"nothing expired in the last 256 blocks" does not imply "nothing is overdue"
when an open item may have expired 257 or more blocks ago.

## Exact Nested-Window Probe

For a bucket ordered as:

```text
big_endian_time_or_block || stable_identity
```

several nested questions such as "is any row in the last 32, 64, 128, or 256
blocks?" can share one cursor:

1. Open one cursor for the transaction.
2. Probe thresholds from oldest to newest: `256 -> 128 -> 64 -> 32`.
3. Encode every lower bound in the same lexicographically sortable fixed-width
   format used by the key.
4. Use `Seek`/`SetRange` for each lower bound.
5. The answer is true only when the returned key belongs to the same partition
   and its ordered value is no greater than the inclusive upper bound.
6. Close the cursor once after all probes.

Oldest-to-newest ordering lets MDBX advance the same cursor monotonically. Do
not reopen the bucket for each threshold. Use fixed-size stack key buffers where
the encoded width is known. If escape analysis shows a local key moving to the
heap through the cursor interface, prepare the fixed key array in caller-owned
block or operation scratch and pass it into the probe; do not add a global cache.

The expected shape is `O(W log N)` for `W` windows, independent of rows inside
each window because each answer needs only the lower-bound row. Measure at
`1/10K/1M` total rows and include absent, boundary, present, future, malformed,
and partition-mismatch cases.

## Contiguous Partitions: Scan Once

Nested point/range probes are not always optimal. When every row from adjacent
ordered partitions is required, use one `First` or initial `Seek`, then one
`Next` pass while classifying the leading key field. Reopening or reseeking each
partition repeats B-tree and cgo work without reducing rows visited.

Choose between the two patterns with measured cardinality:

| Query | Preferred cursor shape |
|---|---|
| Existence in several nested ranges | One cursor, monotonic `Seek` per threshold |
| Every row in adjacent partitions | One cursor, one ordered `Next` scan |
| Earliest due item | One cursor, `First`, inspect one row |
| First `K` due items | `First` plus bounded `Next`, at most `K` valid rows |
| Many row payloads across cgo | Investigate an exposed MDBX batch API |

## Why Probabilistic Filters Usually Do Not Help

Bloom and Cuckoo filters answer membership, not ordered enumeration. They add
hashing, memory, update, deletion, rebuild, restart, and invalidation ownership.
They cannot return the next due identities and false positives still require an
MDBX check. A rolling bitset can answer a bounded historical boolean only when
dense block/time ownership and exact restart reconstruction are approved.

Reject a derived filter when an exact ordered seek is already sub-microsecond or
when a false negative could suppress lifecycle work.

## Cursor and Byte Ownership

- Cursor key/value bytes are transaction/cursor scoped. Copy values that must
  survive cursor movement; otherwise borrow them only until the next cursor
  operation.
- Reuse one cursor only within its owning transaction and serialized operation.
- Do not share an MDBX transaction or cursor across strategy goroutines without
  explicit ownership proof.
- Validate canonical key fields without allocating strings on every row.
- Keep malformed-key behavior fail-closed. An optimization must not turn an
  unreadable row into evidence that no work exists.

## Measurement Matrix

Instrument and report:

- cursor opens/closes;
- `First`, `Seek`, `SeekExact`, `Next`, `Prev`, and `Last` calls;
- rows observed and rows decoded;
- key/value bytes read;
- cgo crossings where measurable;
- `ns/op`, `B/op`, and `allocs/op`;
- total cardinality and matching cardinality independently.

Benchmark the same transaction shape before and after. A kernel benchmark proves
the cursor ceiling; a production-path benchmark proves whether wrappers,
decoding, metrics, and ownership preserve the gain.

## Escalation Gate

If exact enumeration of hundreds of rows is dominated by one cgo cursor call per
row, key parsing and Go allocation changes cannot reach a sub-microsecond target.
Before adding a new index or cache, check whether the installed libmdbx exposes a
batch cursor API and whether the Go/KV wrapper exposes it. Extending that boundary
requires explicit API, pointer-lifetime, transaction-lifetime, malformed-row,
ordering, and cross-platform tests.
