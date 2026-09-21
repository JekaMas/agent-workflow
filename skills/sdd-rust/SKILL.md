---
name: sdd-rust
description: Implement or review Rust behavior with precise Cargo selection and risk-based evidence.
---

# Rust development

Follow the repository's Rust conventions and actual workspace/manifests/toolchain.
Inspect the owner, callers, types, error boundaries and related tests. Keep typed
validation, ownership, cancellation/resource release and secret-safe diagnostics
at the actual boundaries. Do not import another project's framework or signing rules.

Use formatting, selected tests, then Clippy as applicable. Select manifest/package,
lib/bin/integration target, full test name, features and profile deliberately.
Harness --exact filters names; it does not select the Cargo target. Confirm the
intended nonignored test executed. Offline dependency access does not stop test
code from making network calls. Custom harnesses require inspected semantics.

For demonstrated defects, qualify a meaningful behavioral failure; already-correct
behavior needs independent examples, not a contrived red baseline. Match properties
and oracles to requirements, preserve overflow/arithmetic and serialization semantics.
Use Proptest/fuzzing, concurrency exploration, Miri/sanitizers, proof or performance
measurements only when they answer a concrete risk and prerequisites are authorized.
Bounded proof and extracted helper correspondence do not prove callers, I/O or the
whole binary. Inspect assumptions/stubs/bounds and replay useful counterexamples.

Repair findings without weakening contracts, revalidate affected checks and return
actual evidence and limits to the governing workflow. Missing/unsupported/timeout
results remain non-success. Use shared verification-design when evidence needs design.

For stateful sequence properties, select sibling `event-sequence-pbt/SKILL.md`;
load its language adapter only when relevant.

## Conditional references

- `references/async-lifecycle-and-testing.md`: async ownership, cancellation, test seams and dependency checks.
- `references/boundaries-and-resources.md`: typed validation, errors, resource bounds and canonical data where required.

Framework, provider/signing details, toolchain and actual test selectors stay in
the consumer adapter. Do not bulk-load references for unrelated edits.
