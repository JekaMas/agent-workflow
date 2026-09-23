# Tasks

## 1. Evidence graph contract

- [x] 1.1 Implement the versioned `verification.json` parser, delta-spec requirement/scenario fingerprinting, exact test-source fingerprinting and complete graph validation; verify missing requirements, missing polarity, uncovered scenarios and stale specification/test fingerprints fail.
- [x] 1.2 Implement canonical command/case deduplication and strict shared-test edge validation; verify true duplicates fail while distinct property observables remain searchable.
- [x] 1.3 Implement deterministic forward/reverse indexes and `query` selection by requirement, scenario, property, owner and changed path; verify sorted unique transitive closure excludes unrelated package neighbors.

## 2. Executable evidence

- [x] 2.1 Implement safe argv-only execution and bounded result artifacts; verify missing executables, timeouts, nonzero exits and authority-blocked cases remain non-passing.
- [x] 2.2 Implement Go JSON and Cargo/libtest observed-case adapters plus explicit-marker command checks; verify missing, failed, skipped and zero-selected expected tests fail.
- [x] 2.3 Implement incremental `run` selection and complete `run --all`; verify deduplicated commands execute once and planned/stale cases block final closure.

## 3. Workflow integration and toolchains

- [x] 3.1 Update verification/delivery guidance, operation templates, config rules and check routing so planning authors the graph, apply/verify run affected closure and final readiness runs all; verify rendered routes contain the contract.
- [x] 3.2 Stop forcing `GOTOOLCHAIN=local` while retaining offline/read-only Go execution; verify an already-cached newer required toolchain runs and an unavailable prerequisite fails without download.
- [x] 3.3 Add adoption/maintenance documentation and portable script publication; verify bootstrap/integration source audits include the graph tool.

## 4. Shared and consumer proof

- [x] 4.1 Add shared unit and lifecycle fixtures covering graph validation, search, execution, deduplication, drift and failure semantics; run the exact affected tests and `make check`.
- [ ] 4.2 Publish a reviewable shared branch/PR, record its exact revision, and update Smart Example's pinned submodule/rendered integration without editing generated consumers independently.
- [ ] 4.3 Add the Smart Example GMX graph with all specification requirements/scenarios and planned positive/negative cases; mark only implemented cases executable and verify iteration-one selection resolves the complete C02/C03 closure.
- [ ] 4.4 Repair the two iteration-one fixtures, add case-level substitution declarations, execute all selected C02/C03 graph cases on the stabilized Smart Example tree, and replace the false checkpoint claim with exact observed evidence.
- [ ] 4.5 Run Smart Example workflow/spec validation and full current required graph closure once after final relevant edits; record any later GMX requirements as planned/incomplete rather than passed.
