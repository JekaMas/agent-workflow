# Extraction-equivalence review and repair

The commit-by-commit review covered 28 shared commits through 885ecc8 and consumer source through d9845acab. It did not establish a minor-only history: extraction was mixed with separately requested features and several substantive procedural edits. Earlier “same flow” summaries were too broad.

## Material findings and disposition

| Finding | Source and current owner | Repair / retained distinction |
|---|---|---|
| Per-run PBT coverage became pooled coverage; explicit programmatic admission disappeared | Smart Example before 44131121e, shared 5fddba4, skills/event-sequence-pbt/SKILL.md | Restore every required disposition per run plus programmatic disposition/model assertions and focused qualification before the full PBT. Directed witnesses stay inside that run; no mandatory separate manifest. |
| Generic validators moved but default adopter route did not call them | 92866e4, scripts/bootstrap.py and docs/project-flow.md | Generate policy files and invoke both existing consumer validators. Missing/untracked/ignored source fixtures must fail through their real CLI paths. |
| Debugging trigger, discrepancy coverage and per-fix admission were weakened while removing handoffs | 92866e4 / consumer 7e5b2ac1d, skills/hypothesis-debugging | Restore failed direct attempt/unknown owner, hypothesis coverage, each confirmed fix's discriminator/test/rollback boundary and repeated instruction-effectiveness diagnosis. Retain authorized same-change repair and read-only diagnosis scope. |
| Conflict resolution lost feature-slice and top-down ordering | Same commit pair, skills/conflict-resolution | Restore original sequencing and validation-or-explicit-blocker boundary before unrelated slices. Retain exact merge/rebase index-stage semantics. |
| Concurrent-by-default scheduling softened | 0087346, verification-design execution-scheduling | Restore concurrent-by-default independent commands within actual authority/resource/measurement limits; this does not authorize agents. |

## Preservation demonstrated by source comparison

35 of 40 specialist-package files were byte-identical at extraction, four changed and one language-adapter reference was new. 13 of 14 operation bodies retained substantive paragraphs; maintenance routing and command-selection wording were adapted. Authority, exhaustive-investigation and coordinated-review policy bodies were preserved. Local SDKError, assertion/helper/context and suppression contracts were retained in consumer adapters. The shared main adaptive specification preserved generic requirements; product E2E scenarios remained local.

## Commit ledger

| Shared commit | Classification |
|---|---|
| 34c850b | Initial baseline; corresponding pre-extraction runner/workflow source not present in the preceding consumer Git tree. Exact-move proof remains unavailable. |
| 94d49a7 | Minor consumer-context/formatting correction |
| dbadb9f | New rehearsal tooling |
| 7ef1b9d | New review modes, local client and proof guidance |
| 7be0001 | Test-selection correction |
| b8aaa4e | Separately requested API replacement and proof-runner additions |
| 562d862 | Native diagnostic classification addition |
| 4c5f4c1 | New defaults and installer |
| 0f186f0 | Ignored-output rejection |
| 68e6828 | Requested new-repository setup behavior |
| f4258e0 | Git-backed personal releases/source audit |
| be83f1b | Empty-inventory rejection |
| 5fddba4 | Mostly exact specialist moves; substantive PBT drift repaired here |
| 2b8f558 | Documentation |
| dcb75da | Procedure/rule extraction substantially preserved; renderer is new machinery |
| a045c88 | Validation text preserved by deduplication; new lifecycle fixtures |
| c87fb0a | Canonical quickstart/documentation routing |
| 0087346 | Mostly preserved references/specs; scheduling adjustment repaired here |
| c221a5a | Minor paths/links/evidence corrections |
| 92866e4 | Mixed extraction, debugging/conflict changes and adoption feature; lost contracts/wiring repaired here |
| d1f2ee5 | Policy bodies preserved; property-impact split retains local short gate |
| be9367b | Whitespace |
| 585f117 | Evidence/tasks |
| 885ecc8 | Maintenance routing to requested adoption behavior |

Merge trees 21f2fd3, 8afda62, 1e85bbd and 2787b37 equal their respective second parents. The API-provider, bootstrap/adoption and integrated-repair additions remain requested features; this repair does not relabel them as exact relocations or restore retired role machinery.

## Qualification

Instruction changes receive source/clause comparison and paper witnesses, not token-presence tests masquerading as behavioral validation. Paper witnesses: two PBT runs with complementary missing dispositions must not jointly pass; a patch with one unconfirmed cause remains investigatory; an unvalidated/unblocked conflict slice prevents unrelated interleaving. These are predicted agent behavior, not an independent-agent evaluation.

Executable checks use disposable adopted Git repositories: clean staged sources pass both validator CLIs; an untracked skill and a force-added ignored skill fail publication; a tracked missing-reference skill fails packaging; selected stricter consumer policy remains enforced. Current results are recorded in evidence.md. No product tests, hosted inference or external runtime actions are required by this repair.
