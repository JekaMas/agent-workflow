# Rust async lifecycle and verification

Use the crate's existing runtime and test harness; this guidance does not require
Tokio, Axum, a new dependency or a running server. Select the boundary named by the
requirement: pure owner, in-process service/router, or actual socket integration.

- Drive readiness and completion through observable results, channels or controlled
  futures. Avoid sleeps as synchronization; time bounds may guard failure.
- Spawned work needs ownership, cancellation/exit and join/observation paths.
- Do not hold blocking synchronization guards across await. Hold an async mutex
  across await only when it intentionally owns a serialized operation; document
  the invariant, cancellation behavior and bounded completion.
- Audit every reader/writer of process-global state or inject state instead; one
  application lock does not establish process-wide safety.
- Cover malformed input, cancellation, partial failure, safe errors and resource
  release. Keep ordinary tests independent of live credentials/provider calls.
- If live evidence is required and authorized, select the exact gated operation;
  ignored, skipped, unavailable or early-success paths do not establish execution.

Keep format, selected behavior tests and Clippy in the relevant order. Select
Cargo manifest/package/target, exact harness name, features and profile explicitly.
Offline dependency resolution does not block test network calls. Missing offline
dependencies or toolchains remain unavailable checks; installation authority comes
from the task, not this reference. Custom harnesses need inspected selection rules.

Use existing dependencies. Update lockfiles through the package manager, inspect
unrelated churn, and state build/security impact of new crates or features.
