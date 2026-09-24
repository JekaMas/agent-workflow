# Flow alignment ledger (2026-09-24)

New flow (only default, per PRs #9/#10 and this audit):
1. Work continues until absolute DONE — no partials accepted — or a blocker that needs a user decision.
2. Turn boundaries, context, compaction, effort and long runs are never stop conditions; resume from the recorded checkpoint.
3. Exactly three stops: spec contradiction, in-scope-unrepairable spec state, decision the artifacts cannot answer.
4. Explicit spec + tests are implemented, not re-planned; structural gates never imply implementation.

Files: 100 | lines: 10057

| status | file | lines |
|---|---|---|
| aligned | `AGENTS.md` | 8 |
| aligned | `README.md` | 137 |
| aligned (batch 4: checked; markers are scope/authority wording, not stops) | `docs/adoption.md` | 232 |
| aligned | `docs/knowledge-maintenance.md` | 9 |
| aligned | `docs/local-checks.md` | 25 |
| aligned | `docs/maintenance.md` | 100 |
| aligned | `docs/model-review.md` | 15 |
| aligned | `docs/native-openspec.md` | 46 |
| fixed (flow-wide stop conditions merged into one paragraph) | `docs/operations.md` | 106 |
| aligned (evidence graph gates; packaging budgets unrelated) | `docs/project-flow.md` | 125 |
| fixed (removed "stop at a chosen stage"; states DONE-or-three-stops) | `docs/quickstart.md` | 99 |
| aligned | `docs/validation.md` | 36 |
| aligned (rendered rules) | `openspec/config.yaml` | 51 |
| fixed (added requirement: execution continues to DONE or one of three stops) | `openspec/specs/adaptive-development-workflow/spec.md` | 224 |
| aligned (deferral = missing external prerequisite) | `openspec/specs/assurance-routing/spec.md` | 55 |
| aligned | `openspec/specs/portable-workflow/spec.md` | 49 |
| aligned | `policies/coordinated-review.md` | 15 |
| aligned | `policies/exhaustive-investigation.md` | 27 |
| fixed (agent limits are not missing authority) | `policies/explicit-authority.md` | 116 |
| fixed (three stops; no turn boundary; no self-blocker; vague wording removed) | `scripts/integration_templates/apply.md` | 53 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/archive.md` | 1 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/bulk-archive.md` | 1 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/check.md` | 22 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/continue.md` | 1 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/explore.md` | 12 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/ff.md` | 1 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/maintain.md` | 1 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/new.md` | 1 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/onboard.md` | 1 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/propose.md` | 1 |
| aligned (no automatic approval gate; material questions only) | `scripts/integration_templates/rules.yaml` | 45 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/spec-validation.md` | 7 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/sync.md` | 18 |
| aligned/fixed per body (batch 4: checked paragraph by paragraph; ff.md stop-licence removed) | `scripts/integration_templates/update.md` | 1 |
| fixed (structural vs implementation gates; no self-blocker) | `scripts/integration_templates/verify.md` | 25 |
| aligned (blockers are product choices/prerequisites) | `skills/conflict-resolution/SKILL.md` | 38 |
| aligned | `skills/event-sequence-pbt/SKILL.md` | 201 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/change-impact.md` | 19 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/event-modeling.md` | 244 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/examples.md` | 372 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/failure_pattern_map.md` | 60 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/fakes-and-generators.md` | 73 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/language-adapters.md` | 22 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/property_catalog.md` | 202 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/property_discovery.md` | 279 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/rapid_recipes.md` | 333 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/event-sequence-pbt/references/replay-and-review.md` | 53 |
| aligned (benchmark approval reuses existing approval; no new prompt) | `skills/golang-optimization/SKILL.md` | 227 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/branching-and-branchless.md` | 146 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/compiler-and-machine-code.md` | 334 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/data-structures-and-dispatch.md` | 118 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/escape-analysis.md` | 352 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/experiment-framework.md` | 228 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/io-network-and-system-techniques.md` | 129 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/mdbx-ordered-cursor-optimization.md` | 128 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/memory-gc-and-lifetime-techniques.md` | 138 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/optimization-catalog.md` | 157 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/optimization-decision-playbook.md` | 294 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/optimization-technique-notes.md` | 343 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/profile-guided-optimization.md` | 122 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/runtime-and-concurrency-techniques.md` | 354 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/technique-expectation-matrix.md` | 93 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-optimization/references/technique-result-rubrics.md` | 81 |
| aligned (handoff = internal routing) | `skills/golang-performance-diagnostics/SKILL.md` | 116 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-performance-diagnostics/references/benchmarking.md` | 260 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-performance-diagnostics/references/cpu-cache-analysis.md` | 236 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-performance-diagnostics/references/interpreting-performance-results.md` | 234 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-performance-diagnostics/references/kernel-and-io-analysis.md` | 98 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-performance-diagnostics/references/performance-diffs.md` | 307 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-performance-diagnostics/references/profiling-and-tracing.md` | 238 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-performance-diagnostics/references/text-artifacts-and-targeting.md` | 291 |
| aligned | `skills/golang-testing/SKILL.md` | 24 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/golang-testing/references/live-deadlocks.md` | 79 |
| aligned | `skills/hypothesis-debugging/SKILL.md` | 19 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/hypothesis-debugging/references/evidence-sources.md` | 9 |
| aligned | `skills/openspec-delivery/SKILL.md` | 14 |
| fixed (PAUSED scoped to measured budgets) | `skills/openspec-delivery/references/delivery.md` | 68 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/openspec-delivery/references/engineering-evidence.md` | 52 |
| aligned | `skills/sdd-go/SKILL.md` | 45 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/sdd-go/references/concurrency-and-memory.md` | 59 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/sdd-go/references/design-types-and-errors.md` | 62 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/sdd-go/references/language-and-tooling.md` | 48 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/sdd-go/references/testing-and-http.md` | 36 |
| aligned | `skills/sdd-maintenance/SKILL.md` | 14 |
| aligned | `skills/sdd-rust/SKILL.md` | 40 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/sdd-rust/references/async-lifecycle-and-testing.md` | 27 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/sdd-rust/references/boundaries-and-resources.md` | 17 |
| aligned | `skills/sdd-workflow/SKILL.md` | 32 |
| aligned | `skills/verification-design/SKILL.md` | 35 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/architecture-and-contracts.md` | 88 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/behavior-and-boundaries.md` | 43 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/code-inspection.md` | 9 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/execution-scheduling.md` | 42 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/fuzz-and-properties.md` | 38 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/implementation-proof.md` | 65 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/local-verification.md` | 70 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/review-modes.md` | 75 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/state-and-isolation.md` | 44 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/test-boundaries.md` | 47 |
| aligned (batch 5: technical guidance; markers are domain terms - return/partial writes/regression budget/blocked goroutines; scanner-clean) | `skills/verification-design/references/verification.md` | 270 |
