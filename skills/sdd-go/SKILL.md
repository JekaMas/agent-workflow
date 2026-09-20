---
name: sdd-go
description: Implement or review Go behavior with targeted tests, ownership and concurrency evidence.
---

# Go development

Project Go conventions and supported toolchains take precedence over these generic
procedures. Inspect the actual module, package, API/error types, owners, callers
and relevant tests. For workspace/module isolation use the project's established
GOWORK setting; do not rewrite go.work to make an isolated check pass.

Define behavior and rejection cases before implementation. Preserve resource
ownership, context propagation, cancellation/deadlines and deterministic contracts.
Use controlled synchronization where feasible; do not infer correctness from sleeps.
Wrap errors according to existing taxonomy and keep diagnostics secret-safe.

Select formatting, actual tests and the existing vet/Staticcheck/lint route; do
not install a parallel analyzer stack. Record package, selector, build tags and
cache/fresh-execution state. Exact child selection requires observed child run and
completion (native JSON can establish this); a parent pass or top-level list cannot.
Use -count=1 when freshness is required. Fuzz seeds are not an exploratory campaign.
Race detection is not exhaustive scheduling; synctest is not distributed simulation.

Choose properties/sequence models, fuzzing, races, fault/recovery tests, proof or
representative repeated benchmarks only for identified risk. Check independent
oracles and decisive negative cases. Retain failing seeds/traces and classify
implementation, oracle, environment and unresolved causes. Repair within authority,
rerun affected checks and return evidence to the governing task; do not mark a
missing check passed. Use shared verification-design for consequential evidence.

For stateful sequence properties, select sibling `event-sequence-pbt/SKILL.md`;
load its language adapter only when relevant.
For hangs/timeouts select sibling `golang-testing`; for measured performance
questions select `golang-performance-diagnostics`, then `golang-optimization`
when evidence supports a fix. Resolve these within this package, not a global copy.
