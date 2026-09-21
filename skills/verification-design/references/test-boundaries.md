# Test boundary claims and proportionate records

## Evidence follows the boundary

Identify the actual owner under test and each material substituted dependency.
Distinguish controlled input from replacing implementation. A generated invalid
message may test the actual parser; a mocked parser cannot prove that parser.
A database seed does not prove migration or initialization. A fake clock may
support logical deadline behavior but does not measure real scheduler timing.
A shipped simulator under test is the product owner, not automatically a double.

State what was exercised and what remains unverified. A substituted dependency
does not disqualify observations about the actual implementation or an independent
oracle. It does prevent claims about the replaced owner's real behavior unless
separate evidence supplies that claim. Never describe fabricated observations as
real external receipts, live outcomes or operator data. Preserve any acceptance
criterion requiring actual construction, persistence, transport, integration,
visual inspection or operational evidence. Substitution cannot silently satisfy it.

## Properties, execution and falsification

Use [shared verification](verification.md#property-and-test-set-matching)
for requirement → property → oracle → test type → selected set → observed result.
Inspect code and runtime results, not just declarations. Qualify decisive checks
against plausible wrong behavior; retain counterexamples, shrinking outcomes and
replay commands. Generated families record domain, assumptions/filters, bounds,
configuration and replay seed/corpus. Explore and shrink within that contract; record material changes to the domain
and reassess affected evidence.

## Choose proportionate records

Default to the selected OpenSpec change's evidence and native test reports.
Record command/cwd, source and relevant dirty state, configuration/tool version,
selection, outcomes and important artifact identities once per useful run.
A compact property map is sufficient; a typo may need only inspection evidence.
Batch identity capture at verification and handoff boundaries.

Use a machine-readable manifest when complex mixed-boundary campaigns, immutable
datasets, replay corpora, multiple repository identities or explicit acceptance
need it. Reuse an existing format that answers that need. Use dataset manifests for provenance and run records for observed execution. Preserve small irreplaceable failures;
record access/retention limits for larger artifacts. /tmp is not durable storage.

