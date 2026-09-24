# Design

## Context

The workflow package is consumed as a pinned submodule by repositories that own
their own `scripts/` directory. The runner and the graph tooling resolve Python
modules by name, so package ownership decides which file a name binds to. The
evidence graph also needs an admission policy at the consumer boundary, because
active changes can predate the graph.

## Decisions

### 1. Resolve suites per package root in separate processes

`workflow_tests()` keeps one process per group: the consumer group runs with
`sys.path[0]` set to the consumer root and the shared group with the shared
package root as its working directory and first path entry. Results are summed
into one report, and a failing group is named. When the consumer root *is* the
shared package (this repository), the single-process path stays.

Alternative considered: import the shared suites under a private package name.
Rejected because the suites import `from scripts import …` themselves, so the
binding must be real; and because a consumer could still shadow a shared module
inside one process.

### 2. Ship one admission wrapper instead of one per consumer

`scripts/evidence_graph_check.py` takes `--root`, `--change`,
`--transition-file` (default `.agents/evidence-transition.json`) and
`--output-dir`, and resolves the shared tools relative to its own location so a
consumer symlink behaves like the pinned file. The transition *list* stays in the
consumer; only the mechanism is shared.

Alternative considered: extend `local_verify.py` with a new kind. Rejected for
now because the wrapper needs pass-through selectors that the runner's
step/status model would have to model, and because the graph tooling already
owns its own record format that consumers forward.

### 3. Keep the transition gap visible and bounded

A recorded change without a graph passes `validate` only, and `ready` refuses it.
The record's reason and members are consumer-owned data, so a reviewer sees
exactly which changes are in transition and cannot extend it silently.

## Risks / Trade-offs

- **[Two processes per run]** The suite runs twice, adding a subprocess. Both
  groups still execute in one command and one result record.
- **[Wrapper drift]** The wrapper forwards to the shared tools; any new
  operation must be added here as well. The alternative is per-consumer copies,
  which already drifted.
