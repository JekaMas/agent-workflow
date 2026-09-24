# Change evidence

## Reproduction

The gaps were reproduced against the pinned revision with a real consumer
(`0xAtelerix/smart_example`, which owns `scripts/`):

| Observation | Result |
| --- | --- |
| Consumer without any workaround, pinned runner | `workflow-tests: failed` — `ModuleNotFoundError: No module named 'scripts.test_requirement_tests'` and the same for `scripts.test_discovery_ledger` |
| Same consumer, patched runner | `workflow-tests: passed` with the consumer suites from the consumer package and the shared suites from this package |
| Consumer with five symlink adapters, patched runner | `workflow-tests: passed` (the workaround becomes unnecessary) |

## Verification

| Check | Result |
| --- | --- |
| `python3 -B scripts/test_local_verify.py` | PASS (36 tests, including the three consumer-package fixtures) |
| `python3 -B scripts/test_evidence_graph_check.py` | PASS (7 tests) |
| `scripts/evidence_graph_check.py --change consumer-workflow-and-evidence-adoption validate` | PASS (2 requirements, 5 properties, 10 cases) |
| `make check` | PASS after the declared source fingerprints of the existing change were refreshed for the edited runner test file |
| `make check CHANGE=consumer-workflow-and-evidence-adoption` | PASS (graph validation, discovery ledger and complete execution with clean provenance) |

## Notes

- The consumer keeps its own Makefile target shapes, its `.agents/evidence-transition.json` record and its docs; only the mechanism moved here.
- Editing `scripts/test_local_verify.py` invalidates declared sources of the existing `require-executable-requirement-test-matrices` change, so its `source_sha256` entries were refreshed in this change. That coupling is expected: the same file is the regression surface for the runner.
