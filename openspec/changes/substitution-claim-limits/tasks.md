# Tasks

## 1. Validation

- [x] 1.1 Require `owner_replaced` and a non-empty `forbidden_claims` list for `APPROVED_TEST_DOUBLE` and `EXTERNAL_BOUNDARY` cases, allow `allowed_proof`, and keep `NO_TEST_DOUBLE`/`UNDECIDED` unaffected.
- [x] 1.2 Report a `claims_pending` case as a substitution gap in validation output and keep readiness incomplete while a selected case has one.

## 2. Guidance

- [x] 2.1 Record the case shape in the test-boundaries and verification references and in the project-flow command guide.

## 3. Verification

- [x] 3.1 Cover the rejected case, the accepted case, the reported pending gap with blocked readiness, and the unaffected classifications.
- [x] 3.2 Author this change's `verification.json` and `discovery.json`, run the shared check and this change's graph, and record the results in `evidence.md`.
