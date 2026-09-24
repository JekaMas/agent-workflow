# Flow alignment ledger (2026-09-24)

New flow (only default, per PRs #9/#10 and this audit):
1. Work continues until absolute DONE — no partials accepted — or a blocker that needs a user decision.
2. Turn boundaries, context, compaction, effort and long runs are never stop conditions; resume from the recorded checkpoint.
3. Exactly three stops: spec contradiction, in-scope-unrepairable spec state, decision the artifacts cannot answer.
4. Explicit spec + tests are implemented, not re-planned; structural gates never imply implementation.

Files: 100 | lines: 10057

| status | file | lines |
|---|---|---|
| TODO — read paragraph by paragraph | `AGENTS.md` | 8 |
| TODO — read paragraph by paragraph | `README.md` | 137 |
| TODO — read paragraph by paragraph | `docs/adoption.md` | 232 |
| TODO — read paragraph by paragraph | `docs/knowledge-maintenance.md` | 9 |
| TODO — read paragraph by paragraph | `docs/local-checks.md` | 25 |
| TODO — read paragraph by paragraph | `docs/maintenance.md` | 100 |
| TODO — read paragraph by paragraph | `docs/model-review.md` | 15 |
| TODO — read paragraph by paragraph | `docs/native-openspec.md` | 46 |
| fixed (flow-wide stop conditions merged into one paragraph) | `docs/operations.md` | 106 |
| aligned (evidence graph gates; packaging budgets unrelated) | `docs/project-flow.md` | 125 |
| TODO — read paragraph by paragraph | `docs/quickstart.md` | 99 |
| TODO — read paragraph by paragraph | `docs/validation.md` | 36 |
| aligned (rendered rules) | `openspec/config.yaml` | 51 |
| TODO — read paragraph by paragraph | `openspec/specs/adaptive-development-workflow/spec.md` | 224 |
| TODO — read paragraph by paragraph | `openspec/specs/assurance-routing/spec.md` | 55 |
| TODO — read paragraph by paragraph | `openspec/specs/portable-workflow/spec.md` | 49 |
| TODO — read paragraph by paragraph | `policies/coordinated-review.md` | 15 |
| TODO — read paragraph by paragraph | `policies/exhaustive-investigation.md` | 27 |
| fixed (agent limits are not missing authority) | `policies/explicit-authority.md` | 116 |
| fixed (three stops; no turn boundary; no self-blocker; vague wording removed) | `scripts/integration_templates/apply.md` | 53 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/archive.md` | 1 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/bulk-archive.md` | 1 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/check.md` | 22 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/continue.md` | 1 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/explore.md` | 12 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/ff.md` | 1 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/maintain.md` | 1 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/new.md` | 1 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/onboard.md` | 1 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/propose.md` | 1 |
| aligned (no automatic approval gate; material questions only) | `scripts/integration_templates/rules.yaml` | 45 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/spec-validation.md` | 7 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/sync.md` | 18 |
| TODO — read paragraph by paragraph | `scripts/integration_templates/update.md` | 1 |
| fixed (structural vs implementation gates; no self-blocker) | `scripts/integration_templates/verify.md` | 25 |
| TODO — read paragraph by paragraph | `skills/conflict-resolution/SKILL.md` | 38 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/SKILL.md` | 201 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/change-impact.md` | 19 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/event-modeling.md` | 244 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/examples.md` | 372 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/failure_pattern_map.md` | 60 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/fakes-and-generators.md` | 73 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/language-adapters.md` | 22 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/property_catalog.md` | 202 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/property_discovery.md` | 279 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/rapid_recipes.md` | 333 |
| TODO — read paragraph by paragraph | `skills/event-sequence-pbt/references/replay-and-review.md` | 53 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/SKILL.md` | 227 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/branching-and-branchless.md` | 146 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/compiler-and-machine-code.md` | 334 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/data-structures-and-dispatch.md` | 118 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/escape-analysis.md` | 352 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/experiment-framework.md` | 228 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/io-network-and-system-techniques.md` | 129 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/mdbx-ordered-cursor-optimization.md` | 128 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/memory-gc-and-lifetime-techniques.md` | 138 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/optimization-catalog.md` | 157 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/optimization-decision-playbook.md` | 294 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/optimization-technique-notes.md` | 343 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/profile-guided-optimization.md` | 122 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/runtime-and-concurrency-techniques.md` | 354 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/technique-expectation-matrix.md` | 93 |
| TODO — read paragraph by paragraph | `skills/golang-optimization/references/technique-result-rubrics.md` | 81 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/SKILL.md` | 116 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/references/benchmarking.md` | 260 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/references/cpu-cache-analysis.md` | 236 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/references/interpreting-performance-results.md` | 234 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/references/kernel-and-io-analysis.md` | 98 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/references/performance-diffs.md` | 307 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/references/profiling-and-tracing.md` | 238 |
| TODO — read paragraph by paragraph | `skills/golang-performance-diagnostics/references/text-artifacts-and-targeting.md` | 291 |
| TODO — read paragraph by paragraph | `skills/golang-testing/SKILL.md` | 24 |
| TODO — read paragraph by paragraph | `skills/golang-testing/references/live-deadlocks.md` | 79 |
| TODO — read paragraph by paragraph | `skills/hypothesis-debugging/SKILL.md` | 19 |
| TODO — read paragraph by paragraph | `skills/hypothesis-debugging/references/evidence-sources.md` | 9 |
| TODO — read paragraph by paragraph | `skills/openspec-delivery/SKILL.md` | 14 |
| fixed (PAUSED scoped to measured budgets) | `skills/openspec-delivery/references/delivery.md` | 68 |
| TODO — read paragraph by paragraph | `skills/openspec-delivery/references/engineering-evidence.md` | 52 |
| TODO — read paragraph by paragraph | `skills/sdd-go/SKILL.md` | 45 |
| TODO — read paragraph by paragraph | `skills/sdd-go/references/concurrency-and-memory.md` | 59 |
| TODO — read paragraph by paragraph | `skills/sdd-go/references/design-types-and-errors.md` | 62 |
| TODO — read paragraph by paragraph | `skills/sdd-go/references/language-and-tooling.md` | 48 |
| TODO — read paragraph by paragraph | `skills/sdd-go/references/testing-and-http.md` | 36 |
| TODO — read paragraph by paragraph | `skills/sdd-maintenance/SKILL.md` | 14 |
| TODO — read paragraph by paragraph | `skills/sdd-rust/SKILL.md` | 40 |
| TODO — read paragraph by paragraph | `skills/sdd-rust/references/async-lifecycle-and-testing.md` | 27 |
| TODO — read paragraph by paragraph | `skills/sdd-rust/references/boundaries-and-resources.md` | 17 |
| TODO — read paragraph by paragraph | `skills/sdd-workflow/SKILL.md` | 32 |
| TODO — read paragraph by paragraph | `skills/verification-design/SKILL.md` | 35 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/architecture-and-contracts.md` | 88 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/behavior-and-boundaries.md` | 43 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/code-inspection.md` | 9 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/execution-scheduling.md` | 42 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/fuzz-and-properties.md` | 38 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/implementation-proof.md` | 65 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/local-verification.md` | 70 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/review-modes.md` | 75 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/state-and-isolation.md` | 44 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/test-boundaries.md` | 47 |
| TODO — read paragraph by paragraph | `skills/verification-design/references/verification.md` | 270 |
