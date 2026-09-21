# Agent Workflow

Reusable, evidence-driven OpenSpec delivery and verification design, with a
stdlib local-check runner. Consume a pinned Git revision; project adapters own
product requirements, authority, commands and actual supported configurations.

Start with the [developer quickstart](docs/quickstart.md); use the
[detailed flow](docs/project-flow.md) for evidence and completion rules.

## Wire a repository

From this clean reviewed checkout, preview and apply:

```sh
python3 -B scripts/bootstrap.py repo --repo /path/to/project
python3 -B scripts/bootstrap.py repo --repo /path/to/project --apply
```

Git must already be initialized. Languages/module roots are detected; an explicit
profile can override them. Existing OpenSpec/custom integrations use the inspectable
`prepare` → reviewed `--migration-plan` route in [adoption](docs/adoption.md), preserving
active changes. No tools/framework are installed. After cloning an adopted repo,
initialize its pinned submodule and use [the quickstart](docs/quickstart.md).

## Skills

- `skills/openspec-delivery/SKILL.md`: start, resume, plan, implement and finish.
- `skills/verification-design/SKILL.md`: properties, independent oracles, test-set
  matching, falsification, review and coverage-preserving consolidation.

Load these through the consumer's skill router. A submodule is a source pin,
not automatic skill discovery. Keep its initialization explicit:
`git submodule update --init .agents/workflow` from a configured consumer.
A missing checkout is a reported dependency, never permission to use another revision.

## New repositories and specialist skills

Use the preview/apply bootstrap in [adoption](docs/adoption.md). It installs
versioned project adapters and a pinned submodule, not global tools. The tracked
project profile selects Go/Rust routes; event-sequence testing is available for
all languages. Codex adapters and Claude commands resolve the same canonical
source after submodule initialization.

- `skills/hypothesis-debugging`: discriminate unresolved failures and continue authorized repair.
- `skills/conflict-resolution`: preserve both sides’ intended behavior through Git conflicts.
- `skills/sdd-go` and `skills/sdd-rust`: general language evidence and routing.
- `skills/golang-testing`: focused hang/timeout stack diagnosis.
- `skills/golang-performance-diagnostics` and `skills/golang-optimization`:
  measurement before optimization, with conditional advanced references.
- `skills/event-sequence-pbt`: independent state models, domain events,
  dispositions, shrinking and replay in any language; framework recipes are optional.

No specialist is mandatory reading for unrelated work. Consumer product commands,
toolchains, domain contracts and approval boundaries remain local. See
[maintenance](docs/maintenance.md) for updating canonical source and consumer pins.

## Canonical OpenSpec integration

All consumers use the same full operation procedures and artifact/apply/archive
rules from `scripts/integration_templates/`. The renderer produces native project
configuration and client adapters; project profiles select local references.
See [operations](docs/operations.md) and [adoption](docs/adoption.md). The route
validator rejects divergence instead of allowing a separate product-only lifecycle.

## Local runner

`python3 scripts/local_verify.py --help` exposes selected Go, Cargo, OpenSpec
and workflow checks, plus selected Kani/Verus/Gobra proof routes. Results preserve commands, cwd, version, scope, exits and
artifacts. Static Cargo checks do not execute tests. Go selection accepts anchored
top-level names; exact subtest selection needs a separately inspected native run.
Required skipped/empty/failed checks do not pass. Output paths cannot overwrite
existing records. No dependency/tool installation is performed.

Tested adapter versions: OpenSpec 1.13.1 and golangci-lint 2.11.3. Other versions
are rejected until compatibility is qualified. Cargo defaults to Cargo.toml;
consumers pass their actual manifest. Project config is supplied by the consumer.
`LOCAL_VERIFY_PROJECT_CONFIG` selects a consumer config for native integration
fixtures; otherwise this repository's example config is used.
`LOCAL_VERIFY_PROJECT_ROOT` selects consumer test modules for a consumer adapter
check; otherwise shared regression modules are selected.

`make check` runs parser/process and installed native OpenSpec fixtures. Optional
native Go/Cargo adapter experiments live in scripts/test_local_verify_{go,cargo}.py.
No CI service, global configuration or product runtime is installed by this package.

## Provenance

Initially extracted with user authorization from the Smart Example local-workflow
migration. No third-party redistribution license is asserted. Product KB, credentials, historical campaign approvals and audit inputs
are not part of the shared package.

## Rehearse a complete change

`python3 scripts/rehearse_flow.py --output-dir /new/local/path --go-tool /existing/go`
uses the installed OpenSpec and Go toolchain to plan and implement a disposable
integer clamp. It retains red/green/fault/restored/empty-selection evidence and
file-load byte measurements. It is a scripted same-session rehearsal, not a
fresh model evaluation or a measurement of hidden runtime context.

## Configurable model review

The verification-design skill routes spec, implementation and feedback review.
`python3 scripts/model_review.py --help` selects one stateless API-backed review
or judge request using DeepSeek, Anthropic Messages, OpenAI Responses (including
available Codex API models) or GLM-compatible Chat Completions. Supply an exact
model, URL when overriding the provider default, and the name of a key environment
variable. Credentials, hidden reasoning and raw error bodies are not retained.
There is no provider fallback, tool/agent dispatch or service/model installation.
Hosted API execution may incur provider charges; it is not a free-local claim.
The shared review procedure defines dimensional judgments and evidence limits.

## Personal defaults and repository adoption

Use [docs/adoption.md](docs/adoption.md) for previewable personal install/update,
recoverable backups and pinned project adoption. Personal sdd-workflow routes to
existing project conventions first; sdd-maintenance updates the workflow itself.
Generic sdd-go and sdd-rust procedures are conditional fallbacks, not product policy.
Project adapters preserve existing instructions and actual commands. See
[docs/maintenance.md](docs/maintenance.md) for source ownership and validation.
The installer adds no hooks, permissions, models, runtimes or product CI.
