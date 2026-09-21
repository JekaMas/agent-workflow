# Fuzz And Properties

Use this reference when examples do not cover a broad input or transition
space.

## Fuzzing

Fuzz external decoding and validation boundaries with valid seeds plus malformed
and adversarial inputs. Assert:

- no panic or process corruption;
- stable, safe error classes;
- bounded allocation, work, and recursion where inputs control size;
- deterministic results for identical inputs;
- no forbidden persistence or external action after rejection.

Retain minimized failures as regression seeds when they represent distinct
behavior.

## Property Tests

Use properties for lifecycle and ordering rules, retry and idempotency,
canonicalization and round trips, numeric bounds and units, and meaningful
cross-products. State the invariant before selecting generators.

Constrain generators only by true domain validity. Over-constrained generators
can encode the implementation and hide failures. Include boundary values,
invalid transitions, duplicates, and reordered events as relevant.

Route stateful sequences to `event-sequence-pbt`. Preserve the seed and shrunk
sequence for every actionable failure.

## Closure

A property test provides evidence for its exercised owner, invariant, input
domain, and bounds. It is not a proof over all executions or evidence that an
application or external integration invokes that owner correctly; pair it with
boundary evidence when the requirement includes wiring.
