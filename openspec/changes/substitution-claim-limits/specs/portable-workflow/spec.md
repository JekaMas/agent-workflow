# Spec Delta

## ADDED Requirements

### Requirement: Substituted cases record their owner and claim limits
A case whose substitution classification is not `NO_TEST_DOUBLE` SHALL record the
replaced owner and at least one forbidden claim, and MAY record the proof it is
allowed to carry. A case that records its migration reason instead SHALL be
reported as a substitution gap, and readiness SHALL remain non-passing until the
fields exist.

#### Scenario: Substituted case limits
- **WHEN** an implemented case classifies itself as an approved or external-boundary substitution
- **THEN** it is accepted with a recorded owner, at least one forbidden claim and optionally its allowed proof
- **AND** it is rejected with a message naming both missing fields when it records neither owner nor forbidden claims

#### Scenario: Migration gap is visible
- **WHEN** such a case records `claims_pending` with its migration reason
- **THEN** validation passes and reports the gap for that case
- **AND** readiness with clean provenance stays incomplete while the gap exists
- **AND** an empty or absent migration reason is rejected instead of silently accepted

#### Scenario: Unsubstituted case is unaffected
- **WHEN** a case records `NO_TEST_DOUBLE`, or a planned case records `UNDECIDED`
- **THEN** no owner or claim limit is required
- **AND** an implemented `UNDECIDED` case keeps its existing rejection
