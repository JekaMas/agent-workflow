# Tasks

## 1. Suite resolution

- [x] 1.1 Split `workflow_tests()` into a consumer group and a shared group, each in its own process with its own package root, and keep the single-process path when the consumer root is the shared package.
- [x] 1.2 Cover the consumer package binding, the failing-group report, and the shadowing trap with fixtures.

## 2. Shared admission wrapper

- [x] 2.1 Ship `scripts/evidence_graph_check.py` with validate, query, run, ready, the transition policy and a unique readiness record.
- [x] 2.2 Cover delegation, the recorded transition gap, the unrecorded refusal, selector forwarding and the unknown-selector refusal.
- [x] 2.3 Document both routes in `docs/project-flow.md`.

## 3. Verification

- [x] 3.1 Author this change's `verification.json` with independent positive and negative cases per property and the exact test identities.
- [x] 3.2 Author this change's `discovery.json` for the selected properties and tests.
- [x] 3.3 Run the shared check, this change's graph and the consumer regression; record results in `evidence.md`.
