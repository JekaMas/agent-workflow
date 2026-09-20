# Implementation reasoning and proof-guided work

Load for an explicit proof obligation or a concrete correctness risk that ordinary
evidence leaves unresolved. A tool catalog is not an adoption plan. Inspect actual
source, installed tools, supported semantics and the consumer's candidate before
choosing an integration. Record applicability, obligation and execution separately.

| Path | Concrete native route after prerequisites are qualified | Acceptance boundary |
|---|---|---|
| Rust bounded implementation reasoning | Existing Kani harness calls the real owner; `cargo kani --harness <exact-name>` from its actual crate, or `kani <file.rs>` for an inspected standalone source | Symbolic inputs, meaningful assumptions, panics/overflow/memory obligations and unwinding assertions; all required obligations completed. A copied model does not prove the crate. |
| Rust proof-guided increment | Existing Verus source and pinned compiler: `verus <verified-source.rs>` with inspected project flags; retain a fitting Creusot integration instead if established | Code, invariants and proof evolve together. Inspect trusted bodies/axioms and executable/caller correspondence, not just theorem text. |
| Go implementation reasoning / proof-guided increment | Qualified Gobra JAR/backend: `java -Xss128m -jar <pinned-gobra.jar> -i <target.gobra>` with actual supported settings | Annotated target, ownership/permissions and arithmetic contracts; establish correspondence to production Go and unverified callers. A separate annotated copy without correspondence leaves that claim unproved. |

These are command shapes, not installed targets. Resolve version-specific help,
real paths, harness names and solver configuration before execution. Preserve native
logs, exact source/tool/config identities and replay instructions. Missing tools,
unsupported constructs, disabled obligations, failed unwinding, timeout and unknown
results do not pass. Do not silently add assumptions or admitted goals to get green.

Plan the next useful contract/code/proof increment in the existing OpenSpec change.
Start with an independent example or counterexample that challenges the contract.
Inspect diagnostics to distinguish implementation, contract, assumption and harness
errors. Repair within intent, rerun affected obligations, retain counterexamples as
ordinary regressions and test unverified interfaces. If integration requires a
product representation/API decision, present that decision before changing it.

For each claim, record: real source/caller boundary; property and representation
invariant; input/domain/fairness bounds; arithmetic/overflow/IO semantics; assumptions,
stubs and trusted components; observed completed obligations; compilation/extraction
or correspondence; omitted behavior and required boundary tests. Kani, Verus and
Gobra answer different questions; success is not an interchangeable proof label.

Existing finite models, Proptest/Rapid, fuzzing, race/schedule exploration and
simulation remain useful complementary evidence. State projection and adapters
need their own conformance checks. Safety does not imply liveness; simulated time
does not measure hardware latency. A whole distributed/crash proof through
Goose/Perennial is a separate justified project, not an ordinary Go check.

Before adopting a material tool, record the uncovered risk, incumbent alternative,
primary-source maintenance/release evidence, platform/toolchain/license fit,
annotation/maintenance cost and exit path. Prefer an established fitting tool;
unknown support remains unknown. No installation follows merely from this file.

Sources for qualification: [Kani installation](https://model-checking.github.io/kani/install-guide.html),
[Kani unwinding](https://model-checking.github.io/kani/tutorial-loop-unwinding.html),
[Verus](https://github.com/verus-lang/verus), and
[Gobra](https://github.com/viperproject/gobra).

## Executable runner

`python3 scripts/local_verify.py kani|verus|gobra --help` exposes native proof
routes. Supply an exact source via `--proof-target`, working directory and scope,
installed `--tool`, pinned `--expect-version`, and new output. Kani requires
`--harness`; Gobra requires `--jar` and `--solver`. The runner preserves native
exit/logs, tool artifact hashes and source freshness. It requires nonempty native
verification summaries, and Gobra's inspected route enables overflow checks and
rejects trusted/abstract selected members. Unsupported summaries remain incomplete.
These are narrow adapters qualified against the consumer's pinned releases;
changing a version requires qualifying its summaries and semantics again.

The consumer owns source extraction/correspondence, contracts, toolchain/solver
pins, replay inputs and integration tests. Keep those inputs in version control.
Generate disposable variants from current source and retain both failed and
restored outcomes. Runtime tests of counterexamples remain distinct from solver
results. No installation or product rewrite follows from invoking this skill.
