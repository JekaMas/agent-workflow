# Unified workflow evidence

## Observations
- Shared specialist reference/UI/config tests: passed, four tests.
- Portable policy fixtures: passed, two tests; nested-reference policy is consumer-selected, missing reference and outside-root paths fail.
- Bootstrap: 26 tests passed after a retained failure/repair. Cases include fresh clone/client routes, unmanaged collisions, managed drift, existing active artifacts, changed plan/profile/revision refusal, custom-schema refusal, empty Git repository and inspectable prepare outputs.
- Initial full shared check passed before adding the alias regression. That regression then failed because Git's ignore query rejected the alias before the intended precise preflight error. The operation made no writes. Moved alias inspection before ignore lookup; all 26 bootstrap tests passed without weakening the expected refusal.
- Strict native OpenSpec 1.13.1 validation of this change passed.
- Changed shared Markdown links: 16 resolved in the pre-pin inspection. Consumer shared links await its new pin; these are not marked passed yet.

## Paper traces (predictions, not independent-agent runs)
- Typo: applicable instructions and scoped inspection; no hypothesis, proof or migration setup.
- Normal feature: existing OpenSpec operations/specs/design/tasks; useful increments, selected checks, review and authorized repair; task-level evidence controls DONE.
- Recurrent failure: hypothesis-debugging selects evidence/discriminator, records negative knowledge, repairs only within authority and revalidates in the same change.
- Conflict: conflict-resolution inspects the actual Git operation/index stages and both behaviors; tests selected combined behavior, preserves product decisions and publication boundary.
- UI/concurrency: existing shared verification routes select actual visual or state/schedule evidence; generic extraction does not replace consumer harnesses.
- Approval-bound deployment: prepare reviewable local result, preserve exact external gate, continue independent work and report pending rollout separately.

## Limits
These are code/fixture/native mechanics and self-review evidence. No product runtime, hosted inference, external deployment, fresh-agent efficacy comparison or client UI refresh was executed. Product protected-operation/search conventions, operational runbooks, native proof targets and registered campaign manifests remain local. Historical inventories are not runtime imports.
