# Substitution claim limits in the evidence graph

## Why

The retired per-case approval manifests recorded, for every substituted
boundary, which owner the double replaced (`doubles[].owner_replaced`), what the
case was allowed to prove (`allowed_proof`) and which claims it could not
support (`forbidden_claims`). The requirement-evidence graph replaced those
records with a single `substitution.classification` value plus free text, so
those limits are no longer recorded or checked anywhere. A case can therefore
claim a substituted boundary and still be cited for real-owner behavior without
anything in the graph contradicting it.

## What changes

- A case whose `substitution.classification` is `APPROVED_TEST_DOUBLE` or
  `EXTERNAL_BOUNDARY` must record `owner_replaced` and a non-empty
  `forbidden_claims` list, and may record `allowed_proof`.
- A case that cannot record those fields yet may instead record
  `claims_pending` with its migration reason. The graph reports the missing
  fields as a substitution gap in `validate`, and readiness
  (`run --all --require-clean`) stays incomplete while a selected case has one.
- `NO_TEST_DOUBLE` and `UNDECIDED` are unaffected; an implemented `UNDECIDED`
  case keeps its existing rejection.

## Non-goals

- No approval requirement returns: user authorization stays at real external,
  provider-spending, protected and deployment boundaries.
- No change to graph selection, execution, fingerprints or existing
  `NO_TEST_DOUBLE` records.
