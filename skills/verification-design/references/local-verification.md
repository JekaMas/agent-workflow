# Local Verification By Risk

This matrix guides evidence selection; it does not authorize execution or
repairs. For read-only audits or tasks that exclude execution, inspect accessible
source, configuration and existing results, then report inadequate evidence and
propose the smallest useful experiment. For work that explicitly includes local
verification, including instruction/workflow changes, select checks from the
changed behavior and required claim. Prefer an existing
free tool when it supplies comparable useful evidence. Missing capabilities do
not authorize installation, dependency/CI changes, product fixes, or every
available verifier. Follow the task-scope boundary in the applicable project instructions.

Keep repository revision, working directory, supported toolchain, features/build
tags, environment assumptions, and exact selector with each result. Confirm that
the intended tests actually executed; zero matches, skipped required cases,
timeouts, setup failures, and unknown exits are not passing validation. Retain
nonzero exits through wrappers and filters. Existing CI may reuse documented
local commands; local evidence does not establish a CI or deployed result.

| Change or identified risk | Select local evidence | Add only when the remaining claim needs it |
|---|---|---|
| Documentation typo or metadata-only routing | Inspect meaning, focused diff, frontmatter and referenced paths; propose an existing scoped validator only if further evidence is needed and execute it only within task authority | A routing comparison for changed activation behavior; no product suite for spelling alone |
| Go ordinary behavior/error handling | Focused production-boundary tests with positive, invalid and boundary inputs; required package/static checks from the consumer Go command guide | Broader package coverage when the dependency closure changes |
| Go cancellation, deadlines or shared state | Force the disputed cancellation/overlap, assert worker termination, ownership cleanup, deadline/error propagation and bounded waiting | `-race` on affected packages for concurrent memory access; event-sequence PBT for order/retry/recovery spaces that examples cannot cover |
| Rust handler, codec or async lifecycle | Focused crate tests through the affected handler/owner; invalid/boundary inputs, error redaction, cancellation and resource release; applicable format/Clippy checks | Socket/server integration only when the socket boundary matters; no live provider request for a local-only task |
| Rust unsafe, atomics or memory ordering | State the safety invariant, aliasing/lifetime/arithmetic assumptions and synchronization contract; inspect all callers and targeted regressions | Existing Miri setup for supported undefined-behavior risks, an existing schedule model such as Loom for the disputed ordering, or an applicable sanitizer. Check toolchain/target/features and unsupported operations before relying on a result; a missing tool needs an explicit setup decision |
| Rust/Go protocol or numeric boundary | Exercise both actual encoders/decoders against a shared independent contract: version, unknown/missing fields, signedness, integer limits, precision, overflow, canonical ordering and error projection | Boundary fuzzing and retained minimized corpora for untrusted inputs; round-trip agreement alone is not an independent oracle |
| Persistence, migration or recovery | Legacy/current/malformed rows, idempotence, interrupted batches and reopen/replay through the real local storage owner; assert source/derived ownership and forbidden writes | Fault injection or generated event sequences for crash/retry ordering; record the recovery bound and fairness assumptions |
| UI behavior or layout | Focused interaction/state tests plus visual inspection of the affected screen and relevant viewport/states | Browser journey only when the claim crosses that journey; report unavailable visual evidence rather than substituting a unit result |
| Performance claim | Representative matched baseline/candidate workload, repeated samples, relevant allocations/memory and throughput or latency distribution; isolate measurement load | Profile the measured bottleneck; recovery-under-load measurement when that is the claim. Logical/simulated time is not hardware latency |

Choose only applicable positive, negative and boundary cases. For generated tests,
review the oracle's independence, domain filters, effective event coverage,
shrinking and saved regression. A skipped precondition is not exercised behavior.
When execution is authorized, select focused discriminators before a costly campaign; shared model/harness/owner
changes can still require the full dedicated suite.

Separate model correctness, implementation conformance and operational behavior.
For formal or schedule-model evidence, record assumptions, bounds, stubs/trusted
bodies, unsupported features, and correspondence to production arithmetic,
overflow, synchronization and I/O. Safety evidence alone does not establish
liveness. Preserve required stronger proof instead of replacing it with an
easier tool or a narrower model.

Each long or short-excluded suite has a named owner and documented local command
with exact selection and observed pass/failure/skip evidence. Retain deterministic
regressions for confirmed failures. Preserve existing CI coverage if present;
adding CI is not a local task's completion prerequisite.

## Tool adoption and uncovered risks

Reuse the installed language tools, existing property harnesses and documented
runner first. Do not install a specialist without a concrete property, actual
implementation target and usable harness. For a material new dependency, record
primary-source maintenance/releases, toolchain/platform compatibility, maintainer
continuity, documentation/adoption, license, incumbent alternative and exit path;
unknown evidence stays unknown. Community size is not correctness evidence.

Stateful fuzzing needs an action generator/decoder, independent transition oracle,
real implementation driver, meaningful illegal operations and minimized replayable
failures. A fuzz dependency alone supplies none of these. A shared model needs
explicit adapters for each language's observations, encoding, arithmetic, errors,
time and cancellation. No simulator implicitly controls another language's runtime.

Use history checking for a linearizability claim, schedule exploration for a
specific ordering risk, mutation for a concrete oracle-adequacy question, and
bounded/deductive proof for a suitable isolated invariant. Each requires declared
assumptions, limits and a compatibility pilot. Prefer native types, ownership and
validated constructors to prevent invalid states; test their escape hatches.
No specialist tool or dispatcher is a default completion prerequisite.
