# Update specifications in an existing consumer

Use this guide when maintaining an adopted repository after the OpenSpec 1.14.3
upgrade. It does not authorize a product-spec migration, implementation, sync or
archive. The requested work and the consumer's own instructions select that scope.
The [operation map](operations.md) owns lifecycle routing; [native CLI usage](native-openspec.md)
owns the qualified command surface.

## Select the operation

| Intended change | Owner and procedure |
|---|---|
| Install or upgrade the OpenSpec CLI | Separate prerequisite management, using the authorized package-install method. This package qualifies 1.14.3 exactly; inspect the installed version before changing anything. |
| Upgrade the consumer's pinned shared workflow and rendered adapters | The reviewed source release and [adoption/update procedure](adoption.md#repository-updates-and-checks). Preserve project references and use the managed or custom path below. |
| Revise a proposal, delta spec, design or tasks | The consumer's `openspec-update-change` operation, with current native artifact instructions and the existing schema. This edits the selected change's content. |

The native CLI command `openspec update` regenerates CLI integrations. It is
separate from the update-artifacts operation (`/opsx:update` in Claude, or the
checkout-local `openspec-update-change` skill). Inspect CLI generator output in
a disposable directory before adopting it. Never run `openspec update --force`
over this package's canonical custom adapters.

## Resolve the consumer and selected change

Confirm the exact repository/worktree, branch and revision, inspect dirty paths,
and preserve unrelated active changes. Read the consumer's applicable instructions,
profile and selected workflow pin. A personal installation does not override a
consumer's pin. Inspect related main specs and active changes; resume the matching
intent rather than creating a competing change or migrating every active change.

These read-only examples assume the selected repository's default OpenSpec store.
Run them from that exact root. For an explicitly selected alternate root/store,
retain its supported selection flags on every native command; inspect CLI help
if needed instead of guessing flags or falling back to another store.

```sh
cd /path/to/consumer
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --short
export OPENSPEC_TELEMETRY=0 DO_NOT_TRACK=1 OPENSPEC_NO_UPDATE_CHECK=1
openspec --version
openspec list --json
openspec list --specs --json
openspec status --change <change> --json
openspec instructions specs --change <change> --json
```

Use the resolved schema and returned artifact paths. For sync, native status
supplies `planningHome.root` for main specs and
`artifactPaths.specs.existingOutputPaths` for existing deltas. Preserve an exact
caller-selected subset. An invalid selected path blocks writes; an empty selection
performs none. A store-backed write needs authority for that returned root.
Do not assume the repository's local `openspec/` tree is the selected store.

Before edits, capture a baseline of the selected planning files. If the returned
`planningHome.root` belongs to Git, resolve its actual Git owner with
`git -C /resolved/planning-root rev-parse --show-toplevel` and inspect selected
paths in that owner. Native `--store` flags do not redirect Git commands. For a
non-Git store, retain explicit before/after file comparisons instead. Inspect any
consumer-repository edits separately; a consumer diff cannot cover an external
store. Inspect new/untracked files directly or against the captured baseline,
because ordinary Git diffs omit them.

Before authoring each affected artifact, read its current native instructions,
including context, rules, dependencies and output definition. Keep concrete output
paths inside the selected `changeDir` after resolving parent symlinks; use only
artifacts defined by the selected schema. A different/custom schema requires its
own deliberate migration. See the canonical [artifact-path rules](../scripts/integration_templates/artifact-paths.md).

## Revise the contract without losing obligations

Author the selected delta under the native specs instructions. Use `ADDED` for new
requirements. For `MODIFIED`, retain the full resulting requirement and all retained
scenarios, including unchanged obligations; a fragment of the edit is insufficient.
Handle removals and renames explicitly under the selected operation's rules. Keep
unrelated requirements and changes intact. Update affected design, tasks and
verification evidence coherently, marking results invalidated by a changed input
while retaining evidence that still applies.

OpenSpec 1.14.3 reports descriptions over 500 characters as warnings in `ADDED`
delta requirements and in main specs; strict validation fails on those warnings.
Keep new requirement descriptions within the limit, with detailed cases in their
scenarios. Change validation deliberately leaves inherited `MODIFIED` blocks whole:
never split, trim or rewrite existing content merely to meet the length limit.
Restructure an inherited requirement only when the user explicitly requests a
change for that purpose, preserving every behavior and scenario under the native
schema's procedure. Do not weaken acceptance or disable strict validation.

Strict validation also rejects extra delta prose/sections that archive would
discard. Express durable obligations in retained requirements/scenarios and keep
rationale in proposal/design without losing required behavior.

Unknown metadata keys also fail strict validation. This CLI silently ignores
lowercase `x-` metadata; that is not a supported extension API or a way to carry
enforced obligations. Preserve useful metadata under a documented owner and resolve
unsupported keys deliberately rather than hiding required behavior in an ignored
field. The [native upgrade notes](native-openspec.md#upgrading-from-1131) and
[canonical rules](../scripts/integration_templates/rules.yaml) own these constraints.

Validate the selected change and inspect its diff before implementation or closure.
These Git examples use the resolved planning Git owner and selected paths relative
to that owner; use the captured before/after comparison for a non-Git store:

```sh
openspec validate <change> --type change --strict --json --no-interactive
git -C /resolved/planning-git-owner diff --check -- <selected-planning-paths>
git -C /resolved/planning-git-owner diff -- <selected-planning-paths>
git -C /path/to/consumer diff --check -- <selected-consumer-paths>
git -C /path/to/consumer diff -- <selected-consumer-paths>
```

Use the consumer's [spec and evidence checks](project-flow.md#exact-local-check-commands)
for its actual change type. Native structural validity does not establish product
behavior. When implementation is authorized, retrieve
`openspec instructions apply --change <change> --json`; before checking a task,
confirm its returned `sourcePath`, one-based `line` and unchanged checkbox text.
Refresh instructions if the location or text changed. Task completion needs the
actual outcome and required evidence, not a similarly numbered checkbox.

## Synchronize and archive the selected work

Use the existing [sync](../scripts/integration_templates/sync.md),
[archive](../scripts/integration_templates/archive.md) or
[bulk-archive](../scripts/integration_templates/bulk-archive.md) procedure for the
authorized selection. Sync may occur without closure; archive may synchronize
directly or follow a prior sync. There is no `openspec instructions sync` operation.
Sync reads current specs instructions before writing and preserves root, selection
and full modified content. Resolve retained links from the resulting main-spec
location; execution notes belong in change evidence.

Before archive, strictly validate the selected deltas, satisfy the consumer's
completion/evidence contract and establish archive authority. A blocking sync or
incomplete required work prevents closure. Bulk closure assesses each selected
change separately and preserves unselected work. Do not force a blocked change
through archive or infer authority from a green readiness check.

After either sync or archive, inspect the resulting diff and strictly validate
every affected main spec using the same selected root/store:

```sh
openspec validate <capability> --type spec --strict --json --no-interactive
git -C /resolved/planning-git-owner diff --check -- <selected-planning-paths>
git -C /resolved/planning-git-owner diff -- <selected-planning-paths>
git -C /path/to/consumer diff --check -- <selected-consumer-paths>
git -C /path/to/consumer diff -- <selected-consumer-paths>
```

Supply a meaningful `## Purpose` for a new capability; an archive-generated
placeholder can fail strict validation even when archive succeeds. An inherited
long `MODIFIED` block may pass change validation and still fail strict main-spec
validation after sync. Surface that finding and resolve it within the explicit
authority above; do not silently restructure accepted contracts or ignore the
failure. Resolve and revalidate resulting spec defects before reporting closure;
an unresolved strict finding keeps closure incomplete. The shared
[resulting-spec validation procedure](../scripts/integration_templates/spec-validation.md)
owns this gate. Archive success alone does not establish valid synchronization,
product acceptance or publication authority.

## Upgrade integration sources separately

For a managed consumer, use a clean reviewed shared-source release and the
[bootstrap preview/apply update](adoption.md#repository-updates-and-checks).
Review the proposed profile, pin and managed outputs before applying. Existing
managed-file drift is a conflict to reconcile; do not hand-edit
`.agents/workflow-install.json` ownership hashes or use the custom renderer as an
ownership-check bypass. Bootstrap does not rewrite product specs, changes, tasks
or historical evidence.

For a reviewed custom integration, follow [the canonical renderer procedure](adoption.md#one-openspec-integration-for-all-consumers).
Preview `integration.py --root .` from the pinned package, reconcile local custom
rules into the shared templates or project references, and use `--write` only for
the reviewed outputs. Run `check_opsx_routes.py --root .` and inspect native emitted
instructions. Existing unmanaged integrations that need managed adoption use the
separate [prepare/review/adopt procedure](adoption.md#existing-openspec-or-custom-workflow-integration).
None of these operations automatically migrates a custom schema or authorizes
product-spec synchronization.

Machine-wide personal defaults use the existing
[personal installer](adoption.md#personal-defaults) from a clean reviewed release,
with its preview and authorized apply steps. That operation is separate from the
installed CLI version and each consumer's committed workflow pin. Keep its backups
and installer state local; do not replace managed links or hashes by hand.
