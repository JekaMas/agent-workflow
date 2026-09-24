# Evidence design and review

## Challenge the specification before semantic implementation

Check that the proposed contract expresses the user's outcome: resolve ambiguous
terms, contradictions, missing rejection/boundary cases and relevant compatibility,
state, concurrency, persistence or operational assumptions. Ask what plausible
wrong implementation could still pass the proposed evidence. Use a known example,
counterexample or independent reference to discriminate it; investigate a weak
oracle before committing to semantic implementation. This normally completes
autonomously, without a separate approval or role gate.

For each behavioral requirement, keep its validation contract in the change-owned
`verification.json` evidence DAG: exact pinned requirement/scenarios and test-source hashes, observable
properties, owner/boundary, independent oracle, positive and negative cases,
exact observed test identities, deduplicated commands, substitution boundaries
with their replaced owner and forbidden claims,
invalidation dependencies and required result. Revisit it when evidence changes
assumptions. Routine nonbehavioral edits may use proportionate inspection instead.
Structural OpenSpec validation does not establish that a specification is correct,
that its oracle is adequate, or that its listed tests executed.

## Qualify decisive feedback

Establish current behavior before a material bug repair. Confirm the decisive
test reaches the intended path, fails for the reported behavioral reason and
accepts trustworthy correct examples where available. Compilation, fixture or
dependency failures are not behavioral reproduction. Preserve previously correct
behavior; new features can use independent examples without contriving a red
baseline. Mocks must not bypass the behavior being claimed.

Keep acceptance and the decisive oracle stable through repair. If the oracle is
wrong, record its correction rationale and diff, then requalify it against the
contract and a discriminating example. Correct routine errors autonomously;
ask only for a material unresolved change in intended behavior. A passing retry
or inability to reproduce one example does not prove the full request satisfied.

## Plan from requirements and actual owners

Identify the requested outcome, important invariants and existing acceptance
criteria. Trace the relevant production path through constructors, producers,
consumers, state transitions, persistence/readback and recovery as applicable.
Expected files are discovery anchors, not an exhaustive boundary unless the user
explicitly restricts edits. Investigate related owners and similar failure cases
until the required behavior and affected scope are accounted for; record unknowns.

For important requirements, connect the requirement to its implementation owner,
a suitable independent oracle and required evidence. Conversely, connect each
material proposed delta to an authorized requirement or necessary supporting work.
Reuse existing spec IDs and evidence links. A compact table is useful when the
mapping is otherwise hard to inspect; do not duplicate tasks or require a table
for a typo. Record consequential choices in design and execution work in tasks.
For interacting state, storage growth or fan-out, use the relevant
consumer architecture risk checks
before settling the design; these are conditional checks, not a role template.

For stateful work, check whether the allowed observations actually distinguish
states requiring different outcomes, including delayed first use, replacement,
restart and pruning where relevant. Identical allowed facts cannot justify two
different required decisions. Present a concrete witness and ask for a material
contract decision rather than introducing an unapproved heuristic or fallback.

Detail the next useful increment and its evidence; keep later work coarse.
Investigation, a prototype or a harness can reduce uncertainty without pretending
to complete implementation. Update affected artifacts as evidence changes.

## Select meaningful checks

Use the consumer risk-based verification routes
and relevant domain skill. Distinguish required checks from optional experiments.
Choose the smallest useful checks for the actual risks, including invalid inputs,
boundaries and interactions. Preserve required broader coverage and explicit user
requirements; cost alone is not permission to remove them.

Expected results must come from the requirement or an independent oracle, not a
copy of implementation logic. Inspect filters, assumptions, dispositions and
assertions for vacuity. For stateful properties, compare required model facts to
observed behavior after applicable transitions, retain shrinking/replay evidence
and saved regressions, and explain excluded or unsupported cases. Select race,
fuzz, recovery, unsafe, model or performance checks only for concrete risks.
Models prove only their stated assumptions and bounds; simulated time is not a
hardware measurement and safety does not establish liveness.

Report planned versus observed coverage for relevant requirements, input/error
classes, states/transitions, faults/recovery, schedules/time, configurations and
actual integration boundaries. Label each applicable dimension covered within
stated scope, partial, unknown or not applicable with a reason. Inspect actual
reachability and omissions. Test counts and line coverage do not establish
adequacy; do not invent a percentage over an undefined domain. Keep a real
boundary check when mocks would otherwise hide the claimed interaction.

Disclose the smallest substituted owner and preserve required real-boundary
evidence. Authorized local testing may use controlled inputs and fakes; external
and protected actions follow the consumer authority boundary.

Start with a focused discriminator when useful. A confirmed behavioral defect
should have evidence that detects it; do not manufacture a failing test for a
proof gap or force red/green when the previous behavior is already correct.
Run heavier required checks once their prerequisites are meaningful. Preserve
exit codes, seeds and traces. A timeout, missing prerequisite, unsupported mode,
unintended zero selection or skipped required case is incomplete evidence.

## Property and test-set matching

For consequential behavior, map existing requirement IDs to observable properties
before adding tests. A property states inputs/preconditions, action or transition,
expected relation/invariant, relevant bounds and forbidden outcomes. Identify the
actual owner and an independently justified oracle. Keep the executable map in the
change-owned `verification.json`; it is evidence topology, not another task list.

Use a compact row when relationships are otherwise hard to inspect:

| Requirement / property | Owner, domain and oracle | Test type and existing IDs | Required set / configuration | Observed execution and gaps |
|---|---|---|---|---|

Map in both directions: every important property has suitable evidence; every
selected check contributes an authorized property, regression or required gate.
Several tests may cover one property at different boundaries; one test may cover
several properties only if its observations discriminate each. A suite's name or
test count is not evidence that the mapping holds.

Use the graph's reverse indexes to select affected cases by requirement, property,
owner or changed path. Run the deduplicated transitive closure for each increment
and the complete required graph at final readiness. Every property needs explicit
positive and negative cases, and every specification scenario needs a property
edge. Missing, stale, planned-only, skipped, zero-selected, failed, timed-out or
authority-blocked required nodes remain non-passing.

| Property or risk | Suitable evidence; choose by actual obligation |
|---|---|
| Pure arithmetic, codec, validation | Examples and boundary/negative tests; PBT/metamorphic checks for broad domains, with independent expectations |
| State transitions, retry, idempotency | State-machine properties and minimized sequence regressions; check after intermediate transitions, not only final state |
| Interface / mixed-language compatibility | Shared independent vectors and actual adapters; widths, overflow, canonical bytes, errors and versions |
| Persistence, migration, recovery | Actual storage owner, reopen/restart and fault boundaries; seeds alone do not establish migration correctness |
| Cancellation, ordering, concurrent ownership | Deterministic schedule/deadline checks where suitable plus race/real-runtime evidence required by the claim; safety and liveness are separate |
| User-visible interaction | Boundary integration and affected visual/interaction inspection; unit checks do not replace visual evidence |
| Performance or resource bound | Matched representative repeated measurements and allocation/retention/latency evidence; functional tests do not establish speed |

Separate fast feedback, required broader backstops and optional budgeted exploration.
Record exact selectors, package/crate, tags/features and intended cases/families.
Inspect runner output to reconcile intended versus executed selection: missing
required tests, unintended zero runs, skips, unsupported configurations, timeouts
and failures remain gaps. Generated families use domains, budgets and replayable
samples rather than pretending every possible input can be enumerated. Do not
sum overlapping counts into a coverage percentage. Record what the runner cannot
observe; a manifest's declared command mapping cannot fill that gap.

### Challenge falsifiability and prevent false evidence

Ask which plausible wrong behavior each decisive check would reject: inverted
boundary, omitted transition, wrong units, ignored cancellation, duplicate effect,
stale state or corrupted persistence as relevant. Inspect that the test reaches
the owner and assertion, checks an independent expected result, and cannot pass
through filtering, early exit, swallowed failure or a substitute for that owner.
Round-trip agreement alone can hide paired codec bugs; add independent vectors
when interoperability is claimed. Document material oracle uncertainty.

Use a known failing version, a minimized counterexample or an isolated deliberate
fault when needed to qualify the detector. Mutation testing is optional and
risk-driven; no requirement to install a tool or mutate production for every edit.
Keep acceptance stable through repair. Record an oracle correction separately,
with its reason and renewed qualification. Never delete a failing case, weaken an
assertion, widen a tolerance or filter a counterexample merely to obtain green.
Keep original failures and distinguish a behavioral failure from harness/setup.

### Remove duplicate work without deleting distinct protection

Before adding tests, search relevant existing cases and saved regressions. Extend
an existing test/property when it cleanly covers the new obligation; add a separate
case when the input partition, owner, boundary or failure mode is distinct.
Use the strict overlap rule below before removal. Parameterize repeated setup
without copying production logic into expected results. Keep regression examples
when they add a unique counterexample or cheap deterministic signal, even if a
random campaign might eventually find them.

For consolidation, record old case → retained property/case mapping and inspect
both positive and negative coverage, configuration, isolation and diagnostic
quality. Run affected retained sets and required backstops; unresolved coverage
means preserve the test. Deduplicate repeated execution of the same unaffected
set separately from deleting test code. Broad suite cleanup requires explicit
scope; this workflow migration does not authorize product-test deletion.

## Inspect, repair and revalidate

Review the actual diff, surrounding owners and observed results against the
requirements in both directions. Check initialization, error paths, ordering,
interfaces and recovery where they affect the requested outcome. Inspect visible
UI behavior when applicable; a screenshot or browser interaction is evidence
only for what was actually observed. A clean checker result is not code review.

Classify material findings as a demonstrated defect, missing evidence, artifact
drift or a material decision. Record the affected requirement, exact location,
reason and useful discriminator or missing observation. A suspicion is a
hypothesis, not a confirmed defect. Keep existing failures distinct from changes
introduced here, using a comparable baseline where feasible.

Within an implementation request, repair authorized defects, update stale
artifacts and rerun affected checks without asking whether to continue. A review
stage's read-only procedure does not stop its implementation parent. A user
request for review only remains read-only: report findings and proposed repairs.
Review and repair use this procedure without separate role assignments.

Revalidate according to what changed: shared model/harness, build settings or
contract changes can invalidate broad evidence; a narrowly isolated change may
invalidate only focused results. Record why prior results remain applicable,
including relevant source identity. Do not silently reuse stale green output.
Repeat review and repair while material findings or required evidence remain.
There is no fixed iteration count. If attempts stop producing information, change
the investigation or record the exact blocker instead of repeating the same run.
Never weaken assertions, bounds or requirements to make a check green.

## Learn from material failures

Before repair, classify the failure as product, specification/oracle,
harness/environment or unresolved. Preserve the initial failure even if a retry
passes. Choose the cheapest experiment that separates the leading hypotheses,
then run affected validation and the required broader backstop. Do not silently
quarantine a required failure or infer reliability from eventual success.

Use the existing change/debugging record for material or repeated failures:
scope/revision and requirement; failure/replay link; hypothesis; discriminating
experiment and predicted outcomes; observed result and remaining uncertainty;
disposition (supported/refuted/inconclusive/superseded); next action or revisit
condition. Record observable evidence and concise rationale, not private reasoning
transcripts. Search relevant prior failures before retrying an approach. One
unsuccessful attempt does not justify a permanent “never do this” instruction.

Keep concrete counterexamples as normal regressions, scoped rejected hypotheses
in the change record, and confirmed durable constraints in design/references.
Preserve provenance and applicability; supersede stale conclusions when their
assumptions change. Do not add another ledger service or global memory system.

## Completion and handoff

Use the current workflow's continuation and completion decisions. Resolve material
findings; label required criteria as supported, unverified/blocked or genuinely
not applicable with a reason. The absence of findings is not proof that uninspected
scope is correct. Record review coverage and remaining limitations honestly.

Evidence should identify the requirement/owner, oracle, command and working
directory, scope, tool version, relevant source state, outcome and bounded result
artifact. Link the existing evidence record from tasks rather than duplicating
it. Check final artifacts match the delivered behavior and inspect the final diff.
Finish when the requested outcome and required evidence are complete; stop optional
polishing. Missing required checks block DONE. Local completion does not imply
external approval, deployment or live acceptance. Do not archive incomplete work.

Retain decisive failed and successful artifacts, not only final green output.
Record the actual tested source/patch and oracle/config identity when the worktree
is dirty, with relevant features/tags, seed/trace and replay command. Keep small
irreplaceable counterexamples in the repository and link larger local artifacts
with their access and retention limits. Promote important failures before temporary
storage expires; /tmp is not durable retention. No posting is authorized by
preparing an evidence index. A resumed task should find and replay a relevant
counterexample from the existing change record without reconstructing a transcript.

For interruption, leave concise resume notes in tasks with completed outcomes,
remaining work, evidence and the next action. Historical campaign records provide
requirements and evidence; they do not introduce another lifecycle or task list.

## Test overlap and preservation

Tests overlap only when they exercise the same production owner, input partition,
property, observable and failure class, and neither contributes a unique
counterexample. Similar code, setup or names are insufficient. Before removing,
merging or moving tests, map every previous property, regression and positive or
negative case to retained evidence, including any explicitly required gate.
Audit touched and relied-on tests; a whole-suite optimization requires its own
scope. Applicable campaign approvals and evidence limits remain mandatory regardless
of efficiency.
