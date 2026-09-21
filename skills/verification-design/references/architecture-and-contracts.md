# Architecture And Contracts

Load this reference when the change affects package ownership, transport/domain
separation, configuration, services, persistence, or public contracts.

## Ownership And Boundaries

- Keep domain behavior independent of HTTP/RPC/JSON-RPC request and response
  structs. Decode/map at the transport boundary and call a testable domain or
  service API.
- Keep packages cohesive and exports narrow. Prefer composition and explicit
  dependencies over mutable globals, shared-utils dumping grounds, or god
  objects.
- Name one owner for every state transition, retry policy, queue, cache, index,
  and cleanup decision. Do not preserve a second fallback owner merely to keep
  tests green.
- Map third-party names once at the adapter boundary. Reuse one semantic token
  across API, storage, logs, tests, docs, and runtime bindings.
- Convert untrusted generic values to canonical domain values at API, config,
  DB, parser, or adapter boundaries. Downstream code should not repeatedly trim,
  normalize, reinterpret, or validate an already canonical value.

Example boundary shape:

```text
transport request -> boundary decode/canonicalize -> domain command
domain result -> transport response mapping
```

## Configuration

- Document every new or changed flag, config field, environment variable, and
  default.
- Treat behavior-affecting defaults as explicit decisions. Apply approved
  defaults once at top-level loading/initialization, not as scattered fallback
  values inside handlers, adapters, executors, or strategies.
- Fail fast when a missing value can affect canonical state or external
  transactions. Do not silently default critical endpoints, identities,
  addresses, keys, chain IDs, or execution policy.
- Never expose configuration secrets in logs, errors, fixtures, or examples.

## Approval Boundaries

Use the consumer authority policy for the controlling approval
rule and retain approvals already granted. Evaluate whether the change affects
service/process/background-worker topology, an inter-service interaction or
cross-service coordination contract, or public/storage types and canonical
encodings. A package-local lock, queue or cancellation edit does not by itself
create an additional approval gate; its actual contract impact controls.

When required approval is missing, present before/after ownership, data flow,
failure/recovery behavior, compatibility, rollout and proving tests. Continue
independent authorized work.

## Persistence

- KV: document buckets, deterministic key encoding/order, value schema/version,
  isolation, and migration behavior.
- SQL: document tables/columns, keys, constraints/indexes, transaction
  boundaries, idempotency, retries, and migration direction.
- Hybrid storage: name the source of truth and reconciliation direction.
- Never rely on implicit DB iteration order for canonical output.
- Route storage migrations to the consumer migration procedure and actual schema owner.

## Interactions, scaling and resource contracts

For changes that share state, ordering, caches or lifecycle ownership, inspect
combined transitions as well as each requirement independently. Include relevant
delayed activation, restart, pruning and owner replacement; independently passing
cases do not establish that their interaction is correct.

When a change affects storage footprint, fan-out, retained state or hot-path cost,
identify meaningful cardinalities (for example strategies, markets, subscriptions,
rows or concurrent requests), expected growth and resource bounds. Inspect cold,
warm, invalidated and reopened state where applicable, including unrelated rows
and physical file-backed DB size when that is the claim. Record the workload,
actual budget/oracle and required result; no universal 1/10/100 matrix or benchmark
is imposed on unrelated edits. Use performance diagnostics only for a concrete
measurement question. A bounded test does not establish unbounded scale.

## Review Checks

- Can the domain behavior be tested without a server or real external IO?
- Does every new public name have one meaning across layers?
- Are defaults and failure behavior explicit at the correct boundary?
- Is there one source of truth and one write owner?
- Are public constants/contracts commented and reflected in their canonical KB
  document?
