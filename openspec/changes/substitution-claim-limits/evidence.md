# Change evidence

## Parity gap

The retired per-case approval manifests recorded `doubles[].owner_replaced`,
`allowed_proof` and `forbidden_claims` for every substituted boundary. The graph
carried only `substitution.classification`, so a case could classify itself as a
substituted boundary and still be cited for real-owner behavior. This change
restores the recorded limits and makes them checkable.

## Verification

| Check | Result |
| --- | --- |
| `python3 -B -m unittest scripts.test_requirement_tests` | PASS (40 tests, including the four new substitution fixtures) |
| `python3 -B -m unittest scripts.test_discovery_ledger scripts.test_local_verify` | PASS (37 tests) |
| `scripts/requirement_tests.py --change substitution-claim-limits validate` | PASS: 1 requirement, 3 properties, 6 cases, `substitution_gaps: []` |
| `make check` (existing change) | PASS, unchanged because every case there is `NO_TEST_DOUBLE` |
| `make check CHANGE=substitution-claim-limits` | PASS with clean provenance and the complete graph executed |

## Rollout

A consumer case that claims a substituted boundary records `owner_replaced` and
`forbidden_claims` (and optionally `allowed_proof`). A case that cannot yet do so
records `claims_pending` with its reason: validation passes, the gap appears in
the validate output, and readiness stays incomplete for that selection until the
fields exist. An empty reason is rejected.

No existing record in this package needs migration: every case in
`require-executable-requirement-test-matrices` is `NO_TEST_DOUBLE`. Consumer
graphs that carry substituted cases must add the fields; the consumer's next pin
update carries the guidance.
