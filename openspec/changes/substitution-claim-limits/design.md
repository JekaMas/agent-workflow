# Design

## Context

`verification.json` cases already carry the substituted-owner classification,
setup, observable, red and green expectations, exact test identity and source
fingerprint. The claim limits that the retired campaign manifests enforced have
no equivalent field, and the shared test-boundaries reference only asks for a
disclosure in prose.

## Decisions

### 1. Record the limits on the case, next to the substitution classification

`substitution.owner_replaced` names the replaced owner; `forbidden_claims` lists
what the case may not be cited for; `allowed_proof` optionally states what it may
establish. Keeping them in the existing `substitution` object avoids a new
top-level concept and keeps one case → one boundary.

Alternative considered: require a separate claim record per case. Rejected
because it duplicates the case identity and the source fingerprint.

### 2. Two-phase rollout instead of a silent break

A case with missing fields and no `claims_pending` is rejected with an
actionable message. A case that records `claims_pending` reasons stays valid for
incremental work: `validate` reports the gap and `run --all --require-clean`
refuses readiness for the affected selection. This keeps the requirement
enforceable at the completion boundary without blocking in-flight work, and the
gap is visible in the validator's own output.

Alternative considered: hard-require the fields immediately. Rejected because
consumers with in-flight graphs would fail with no recorded migration path, and
the specification requires reported gaps rather than silent relabelling.

### 3. Leave `NO_TEST_DOUBLE` and `UNDECIDED` alone

A case that substitutes nothing has no owner or claim limit to record. An
implemented `UNDECIDED` case is already rejected; a planned one keeps its
existing shape.

## Risks / Trade-offs

- **[Free-text claims]** `forbidden_claims` is a list of short phrases, not a
  controlled vocabulary. The retired manifests had the same shape, and the
  phrases are reviewable in the diff.
- **[New requirement on existing consumers]** Validation now rejects a
  substituted case without the fields; the `claims_pending` reason is the
  documented migration route and is reported until removed.
