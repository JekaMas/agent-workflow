# Native OpenSpec use

These commands are qualified against the installed 1.14.3 spec-driven setup. Inspect the installed version and emitted guidance on upgrades; do not reinstall merely to follow a task.



Work from the exact repository/worktree. Inspect its dirty state and record
branch/base/owner in the change's design or evidence; preserve unrelated work.
Read existing related specs and active changes before choosing a change. Resume
the matching intent; do not silently implement another active product change.

The installed CLI provides these commands. Prefix CLI calls with
`OPENSPEC_TELEMETRY=0 DO_NOT_TRACK=1 OPENSPEC_NO_UPDATE_CHECK=1` for this local flow;
these process-scoped settings do not change global configuration.

```sh
openspec --version
openspec list --json
openspec list --specs --json
openspec new change <name> --schema spec-driven --json
openspec status --change <name> --json
openspec instructions proposal --change <name> --json
openspec instructions specs --change <name> --json
openspec instructions design --change <name> --json
openspec instructions tasks --change <name> --json
openspec instructions apply --change <name> --json
```

`new` creates metadata; it does not author the proposal. Read each instruction's
context, rules, dependencies and template before writing that artifact. For apply,
read its resolved context files and operation guidance. Do not run `init`, install
OpenSpec, edit package-managed templates, or generate another schema to use this
setup. The generated checkout-local operation skills bridge agent routing to the CLI.

On resume, read status, the selected change's task cursor, affected requirements
and design decisions, then linked evidence needed for the next action. Do not
reload all historical logs, role templates or unrelated change trees. Verify the
actual worktree still matches the recorded identity.

Routine typo/config-description changes with no durable planning need may be
completed directly. If such work needs a durable change but alters no specified
behavior, the qualified CLI supports `skip_specs: true` in `.openspec.yaml`; document
why, do not invent a spec or use the flag to omit a changed behavioral contract.


For sync/archive use the shared operation procedures and strict resulting-spec validation in docs/project-flow.md and docs/operations.md.

## Upgrading from 1.13.1

OpenSpec 1.14.3 is the exact shared runner pin. Upgrade the CLI separately from
the reviewed shared-source and consumer-pin rollout. Run native fixtures on that
version; do not widen the gate to an untested version range. The historical
1.13.1 extraction receipts in validation.md keep their original proof boundary.

Strict validation now fails on requirement descriptions over 500 characters and
on extra delta sections/prose archive would discard. Preserve the complete
contract when repairing a finding; do not trim obligations or suppress strict
validation. Lowercase `x-` metadata is ignored by this CLI without a warning;
other unknown keys still fail strict validation. It is not a supported extension
API. Symlink layouts remain unofficial and are not qualified by this package.

Apply returns each task's `sourcePath` and `line`; confirm that exact checkbox
before editing it. Completed tracked tasks still require review before archive.
The shared rendered procedures also retain canonical artifact-path checks and
removed-requirement provenance. Do not run `openspec update --force` over these
custom generated adapters; update their pinned source and renderer through the
reviewed adoption path.

Release references: [1.14.2](https://github.com/Fission-AI/OpenSpec/releases/tag/v1.14.2)
and [1.14.3](https://github.com/Fission-AI/OpenSpec/releases/tag/v1.14.3).
