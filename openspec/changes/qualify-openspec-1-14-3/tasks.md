# Tasks

## 1. Qualify the current CLI and shared flow

- [x] 1.1 Review upstream 1.13.2–1.14.3 and the exact shared source, preserve PR #16 as a dependency, install user-selected 1.14.3 locally, and record the native baseline findings in design.md.
- [x] 1.2 Update the exact runner pin and compatibility docs; verify the native current-version positive path, the unqualified-version rejection and retained large-artifact cases.
- [x] 1.3 Preserve the two overlong requirements and qualify strict warning/metadata behavior with native positive and negative disposable fixtures.
- [x] 1.4 Refresh canonical authoring/apply/verify safety guidance and verify native task provenance, both rendered client routes and drift rejection in a disposable consumer.
- [x] 1.5 Reconcile the required Make check set, native all-item strict validation and the complete clean-state change DAG using retained valid greens; record self-review and exact rollout limits in verification.md.

## Resume

Use the isolated worktree on `fix/openspec-1.14.3-20261023`. Implementation and qualification are complete. See verification.md for the
171 passing suite cases, clean-state DAG receipt, corrected one-case qualification
and eleven current passing graph edges. The supported native lane remains the
local spec-driven CLI. Consumer/global-workflow rollout is separate.
The original consumer acceptance task 4.5 in the evidence-graph change remains open.

## Workflow follow-up

- Review draft PR #17 after its parser dependency PR #16; no merge or product-pin rollout is implied.
- Archive only after review and inspect synchronized specs.
