# Native OpenSpec use

These commands are qualified against the installed 1.13.1 spec-driven setup. Inspect the installed version and emitted guidance on upgrades; do not reinstall merely to follow a task.



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
behavior, installed 1.13.1 supports `skip_specs: true` in `.openspec.yaml`; document
why, do not invent a spec or use the flag to omit a changed behavioral contract.


For sync/archive use the shared operation procedures and strict resulting-spec validation in docs/project-flow.md and docs/operations.md.
