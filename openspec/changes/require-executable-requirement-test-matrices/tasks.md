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
- [x] 4.2 Publish reviewable PR #6 at shared revision `9216236921ad3555a5a9098347a43fded15975ac`, and update Smart Example commit `e34a34a7f7d2b8e8ea04ec0c493de688c803256d` to that exact submodule pin plus rendered integration.
- [x] 4.3 Add the Smart Example GMX graph with all forty requirements/every scenario, explicit planned positive/negative cases and exact implemented I-1/I-2 cases; the I-1 property selection resolves 19 cases through two deduplicated commands.
- [x] 4.4 Repair the two iteration-one fixtures, add `GMX-C02-TD-01..04` and `GMX-C03-TD-01` declarations, execute all 19 selected C02/C03 cases on stabilized Smart Example commit `e34a34a7f7d2b8e8ea04ec0c493de688c803256d`, and replace the false checkpoint claim with exact observed evidence.
- [ ] 4.5 Run Smart Example workflow/spec validation and full current required graph closure once after final relevant edits; record any later GMX requirements as planned/incomplete rather than passed.

## 5. Review-driven scenario precision

- [x] 5.1 Reject multi-scenario case claims; pin every case to one exact scenario fingerprint and require setup, observable, red expectation, green expectation and invalidation dependencies.
- [x] 5.2 Migrate the shared and Smart Example graphs to schema v2, add the missing GMX stale/flat/portfolio cases, run the affected closures, update the Smart pin and retain final green workflow evidence.
- [x] 5.3 Make verification gradual by default: run directly invalidated cases first, expand only as dependencies require, reuse uninvalidated green evidence, and execute the full iteration selection once at the stable boundary.

## 6. Scrutiny findings and default discovery flow

- [x] 6.1 Close B1-B10: typed Python/Node observers, normalized IDs, executable invalidation/result loading, ADDED/MODIFIED-only parsing, observed status, immutable execution policy, canonical command identity, shared process runner, correct glob semantics, and non-behavioral/older-change compatibility.
- [x] 6.2 Close D1-D14: early cwd/provenance/path validation, source ownership, changed-path completeness, discriminating contracts, independent polarity cases, complete DAG registration, portable rehearsal toolchains, Python-version-compatible parsing, self-executing `make check`, dirty/requested-selector evidence, qualified Cargo/Go observations, source/spec/dependency fingerprints and byte-accurate artifacts.
- [x] 6.3 Add and test the change-owned discovery ledger; require exact, semantic Context and capability-aware JetBrains-index lanes plus classified results and an explicit current/new/validation/no-change disposition in explore and check.
- [x] 6.4 Audit every active shared OpenSpec change and move generally applicable behavior into defaults; migrate every behavioral active change to the executable graph or prove it has no ADDED/MODIFIED behavior.
- [ ] 6.5 Run directly touched tests, then related property closures, then one full stabilized shared change DAG and `make check`; retain the final scrutiny evidence without repeated full-suite runs after each edit.
- [ ] 6.6 Update Smart Example to the final shared commit, render repository adapters, migrate its GMX Node observer and discovery ledger, run affected GMX properties, then one final full current required graph/checkpoint.
