# Behavior And Boundaries

Use this reference to select the proof level and review whether a test reaches
the real production path.

## Start From The Claim

- For a demonstrated repair, qualify the highest observable failing behavior
  test. New or already-correct behavior uses independent examples without
  manufacturing a red baseline.
- For an external boundary, the first test change exercises that boundary: API,
  RPC, middleware, storage, queue, subprocess, or external action.
- Trace the test to the production owner. A favorable fixture or test-only
  substitute is not proof that the real integration is wired.
- Add focused unit tests for branching, invariant enforcement, codecs,
  key/value formats, and deterministic transformations.
- Cover malformed input, wrong ownership or state, unsupported variants,
  replay or idempotency, cancellation, and partial failure when relevant.

## Test Doubles

Follow the consumer authority policy and shared verification procedure for claim limits.
Select the smallest useful substitution; no mandatory stub/fake/mock progression
applies. Mock interactions only when calls, arguments or ordering are themselves
the requirement. Fakes must model the failure modes actually relied on. Exercise
the real owner for the claimed property, and retain required actual integration
checks. Disclose substituted boundaries without discarding valid observations
about the production implementation or independent oracle.

## Select The Boundary

- Pure deterministic owner: focused unit or property test.
- RPC, middleware, or storage wiring without an external chain: process-based
  or in-process integration test using production construction.
- Full application, strategy, chain, or hybrid path: use
  the consumer E2E procedure and its actual harness.

## Review Questions

- Would the test fail if the production integration call were disconnected?
- Does it assert forbidden side effects on failure?
- Can its fixture make the expected result true without the production owner?
- Is the evidence at least as strong as the approved requirement?
