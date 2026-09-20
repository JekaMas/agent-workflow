# Agent Workflow

Reusable, evidence-driven OpenSpec delivery and verification design, with a
stdlib local-check runner. Consume a pinned Git revision; project adapters own
product requirements, authority, commands and actual supported configurations.

## Skills

- `skills/openspec-delivery/SKILL.md`: start, resume, plan, implement and finish.
- `skills/verification-design/SKILL.md`: properties, independent oracles, test-set
  matching, falsification, review and coverage-preserving consolidation.

Load these through the consumer's skill router. A submodule is a source pin,
not automatic skill discovery. Keep its initialization explicit:
`git submodule update --init .agents/workflow` from a configured consumer.
A missing checkout is a reported dependency, never permission to use another revision.

## Local runner

`python3 scripts/local_verify.py --help` exposes selected Go, Cargo, OpenSpec
and workflow checks. Results preserve commands, cwd, version, scope, exits and
artifacts. Static Cargo checks do not execute tests. Go selection accepts anchored
top-level names; exact subtest selection needs a separately inspected native run.
Required skipped/empty/failed checks do not pass. Output paths cannot overwrite
existing records. No dependency/tool installation is performed.

Tested adapter versions: OpenSpec 1.13.1 and golangci-lint 2.11.3. Other versions
are rejected until compatibility is qualified. Cargo defaults to Cargo.toml;
consumers pass their actual manifest. Project config is supplied by the consumer.
`LOCAL_VERIFY_PROJECT_CONFIG` selects a consumer config for native integration
fixtures; otherwise this repository's example config is used.

`make check` runs parser/process and installed native OpenSpec fixtures. Optional
native Go/Cargo adapter experiments live in scripts/test_local_verify_{go,cargo}.py.
No CI service, global configuration or product runtime is installed by this package.

## Provenance

Initially extracted with user authorization from the Smart Example local-workflow
migration. This repository is private; no third-party redistribution license is
asserted. Product KB, credentials, historical campaign approvals and audit inputs
are not part of the shared package.
