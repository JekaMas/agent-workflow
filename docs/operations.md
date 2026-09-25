# Shared OpenSpec operations

The project profile selects local instruction, check and maintenance references.
The check skill may retain the compatibility name project-check in existing adopters.

## Entry and loading

Claude-compatible integrations use `/opsx:<operation>`. Installed OpenSpec's
Codex integration uses the exact skill names in the table; it does
not install a native Codex `/opsx` command adapter. A textual opsx request maps to
the matching local skill. A client must discover these checkout-local files;
refresh/reopen its skill discovery after installing them. This document does not
assert UI invocation in an untested client.

Read applicable project instructions and the project profile, the selected operation skill, relevant shared delivery sections
and selected artifacts. Retrieve native instructions only for the artifact or
operation being performed; inspect context/dependencies returned by that command.
Load review/testing/language/domain procedures for actual decisions, not every
operation. Read CLI help when syntax is unknown. Keep small status/result summaries
and retain full outputs outside conversational context when useful.

## Select sections by the current decision

| Phase | Read initially | Extend only for the relevant decision |
|---|---|---|
| new / propose / continue / ff | Local workflow **Start/resume**; shared delivery **Start and plan**; selected native artifact instructions | Shared verification **Challenge the specification**, **Plan from requirements**, **Property and test-set matching** for consequential planning |
| update | Selected affected artifacts; shared delivery **Execute and adapt** | Evidence contracts and decisions invalidated by the update |
| apply / repair | Native apply context files; shared delivery **Execute and adapt**; matching language/owner procedures; affected `verification.json` closure | Decisive feedback, failure diagnosis, relevant verification commands |
| verify | Actual diff/results and acceptance; validated and executed affected `verification.json` closure; shared verification **Inspect, repair and revalidate**, **Completion and handoff** | Oracle qualification, coverage or overlap sections when needed; final verification runs the complete graph |
| sync / archive / bulk-archive | Selected status paths and native instructions; shared delivery **Review and finish** | Main-spec merge/selection and unresolved acceptance evidence |
| explore / onboard | Requested question or next walkthrough operation; behavioral explore also loads the selected verification/discovery scope | Its actual uncertainty or language/domain boundary |

Native instruction responses already supply project context and selected artifact
rules. Inspect raw config for configuration work, discrepancies or missing fields;
otherwise use that returned context rather than rereading the same config. Reuse
unchanged material already read in the current task. This table selects starting
points, not an investigation cap: follow every decision-relevant reference needed
to satisfy the outcome and report missing evidence.

## Operations

| Operation | Skill | Native surface / outcome |
|---|---|---|
| maintain | workflow-maintenance | project workflow/skill/tooling maintenance; not a native CLI subcommand |
| check | openspec-check | project check routing via the profile check guide; executes existing tools, not a native CLI subcommand |
| explore | openspec-explore | list/status/show plus relevant source; clarify intent |
| new | openspec-new-change | new change, status; create metadata |
| continue | openspec-continue-change | status, instructions <next artifact>; author next artifact |
| ff | openspec-ff-change | instructions in dependency order; prepare apply-ready artifacts |
| propose | openspec-propose | new plus artifact instructions; complete proposal package |
| update | openspec-update-change | status/instructions as needed; revise affected artifacts |
| apply | openspec-apply-change | instructions apply; implement, inspect and repair |
| verify | openspec-verify-change | actual source/results versus artifacts; focused inspection |
| sync | openspec-sync-specs | inspect and merge deltas into main specs, validate |
| archive | openspec-archive-change | instructions archive then authorized native archive |
| bulk-archive | openspec-bulk-archive-change | assess and archive each exact selected change |
| onboard | openspec-onboard | guided authorized walkthrough using these operations |

Use process-scoped OPENSPEC_TELEMETRY=0, DO_NOT_TRACK=1 and
OPENSPEC_NO_UPDATE_CHECK=1. A standalone operation respects its requested scope.
A full delivery request continues through authorized operations, iterations,
review, repair and revalidation; no per-artifact approval or fixed iteration limit.
Apply and its sibling operations stop at exactly three points: a spec change is
needed (the finding cannot be satisfied without changing the approved
specification); an absolute implementation blocker the agent cannot resolve
(missing authority, credentials or dependency, a protected/external operation, or
mutually exclusive requirements); or the iteration is finished, 100% implemented,
every check green and verified with `--require-clean` on a committed revision. A
finding aligned with the specification and needing no spec change is never a stop:
put it in the iteration's task list and apply it. An agent's own context, working
memory or effort is never a blocker, and an agent turn boundary, a compacted or
restarted thread, context exhaustion or a truncated response, a prediction of
truncation, a long run, a landed milestone or an unfinished increment is not a stop
condition: checkpoint each step so truncation is resumable, and resume from the
change's recorded checkpoint and continue. When the
specification, design or tasks already state the behaviour and its tests, implement
them; ask only for material decisions the artifacts do not already answer.
Progress updates during a run are not the operation's end: the final message that
closes the agent turn is emitted only at DONE or at one of the three stops.
The completion unit is the authorized iteration: continue through all of its
findings until the verified iteration result or one of the three stops, and never
report a finding, commit, gate or increment as the iteration's outcome.
Concurrent writers, shared or dirty checkouts, and unclear revisions are not
stops either: pin the exact revision you verify (or use an isolated checkout and
record its revision), preserve unrelated edits, and continue the same increment.
The shared delivery procedure owns DONE; project references own domain safeguards.
`make` is optional. Direct native language commands or the local runner provide
required evidence. OpenSpec structure alone does not establish behavior.

Behavioral changes own `openspec/changes/<change>/verification.json`. Use
`scripts/requirement_tests.py validate`, query a nonempty affected closure for
incremental apply/verify, and execute `run --all --require-clean` before final readiness. The graph
pins specification points to properties and single-scenario positive/negative
cases with setup, red/green expectations, exact observed tests and deduplicated
commands; missing or unexecuted nodes remain incomplete.

Behavioral explore/check decisions also own
`openspec/changes/<change>/discovery.json`. Validate it with
`python3 -B scripts/discovery_ledger.py --root . --change <change>` (or the pinned
consumer path). Every selected property/test is covered by exact repository,
semantic Context and JetBrains-index lanes. Exact search must complete; unavailable
semantic/IDE capabilities record the exact reason. Results are classified and the
review records current change, named new change, validation only or no change.

Iteration uses update/continue/apply as needed. Repair uses apply followed by
verify under existing implementation authority. `iterate` and `repair` are
activities, not additional native command names.

## Maintenance

`openspec update` refreshes generated integrations and can overwrite standard
operation paths; it is different from `/opsx:update`. Maintain these shared-rendered
adapters through reviewed edits. Inspect generator output in a disposable directory
before adopting it. Keep package upgrades separate from artifact revision.

Check every route, generated config and rendered adapter with
`python3 .agents/workflow/scripts/check_opsx_routes.py --root .`.

For reproducible setup see [adoption](adoption.md). Project-specific commands and instruction owners are selected by `.agents/workflow-project.json`.
