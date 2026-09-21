# Language And Tooling

Load this reference for standard-library choice, iterators, reflection,
generators, build tags, and static guardrails.

## Deterministic Standard Library Use

- `cmp`/`sort`: centralize explicit canonical ordering.
- `maps`: use helpers for convenience, never as an ordering guarantee.
- `iter`: use for streaming, early stop, composability, or bounded memory only
  with an explicit order/single-pass/error contract.
- `unique`/interning: optimization only; correctness cannot depend on it.
- weak references/cleanup: cache aids only; never correctness-critical.

Test iterator order, early stop, error propagation, and concurrent lifecycle
when applicable.

## Reflection

Prefer explicit code, generics, or generation. Use reflection only when it
materially reduces complexity over a stable type surface. Test nil/interface,
type-edge, and failure behavior. Route hot-path reflection changes through the
performance workflow.

## Generation And Build Tags

- Edit generator inputs, not generated outputs.
- Run and document the canonical regeneration command when inputs change.
- Review generated diffs for intended semantic change and deterministic order.
- Use build tags only for explicit debug, integration, platform, or controlled
  variants; document and test each variant.
- Keep module/toolchain expectations aligned with `go.mod`, CI, and checked-in
  generation commands.

## Static Analysis

Use static checks for high-risk enforceable policies such as:

- the project's actual panic/skip policy;
- secret-bearing logging patterns;
- ignored errors;
- canonical output built from unsorted maps;
- goroutine lifecycle/context mistakes.

Do not create taste-only or high-false-positive rules. Resolve actual defects;
handle exceptions through the consumer's policy. Inspect the reason for existing
suppressions before changing them. A shared skill neither requires a new analyzer
nor changes the project's lint approval boundaries.
