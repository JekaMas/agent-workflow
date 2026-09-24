# Consumer script packages and shared evidence admission

## Why

Two adoption gaps surfaced in a real consumer (`0xAtelerix/smart_example`) that
owns a `scripts/` directory:

1. `workflow_tests()` inserted the consumer root and then imported the shared
   suites as `scripts.test_requirement_tests` and `scripts.test_discovery_ledger`.
   The consumer's own `scripts` package won, so shared suites failed with
   `ModuleNotFoundError`. The consumer had to add five symlink adapters to work
   around it.
2. Every consumer adopting the evidence graph needs the same admission logic:
   validate the graph and discovery ledger, forward selectors, execute the
   complete graph for readiness, and treat active changes that predate the graph
   as a bounded, visible transition instead of a bypass. That logic was being
   written per consumer.

## What changes

- `workflow-tests` runs the consumer suites from the consumer root and the shared
  suites from the shared package, each in its own process, and reports the
  failing group. A consumer module with a shared suite's name can no longer
  shadow it.
- The pinned package ships `scripts/evidence_graph_check.py`, which owns the
  consumer admission policy: `validate` (graph plus discovery ledger),
  `query`/`run` selector forwarding, and `ready` (complete graph with clean
  provenance and a unique record). A change recorded in the consumer's
  `.agents/evidence-transition.json` reports a validation-only `transition_gap`;
  an unrecorded change without a graph is refused.
- `docs/project-flow.md` documents both routes.

## Non-goals

- No product, domain or toolchain behavior.
- No change to graph semantics, selection, execution or evidence fingerprints,
  which remain in `requirement_tests.py` and `discovery_ledger.py`.
- No consumer campaign data or project command shapes; those stay local.
