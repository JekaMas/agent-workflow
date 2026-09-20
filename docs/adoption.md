# Adopt and update the shared workflow

Keep one clean canonical checkout of this repository at the exact reviewed release.
Use Python 3.10+ and Git; adoption does not install tools, runtimes, models, plugins
or hooks. OpenSpec is a separate prerequisite; qualify the installed version with
native checks before claiming working integration. Ordinary fixes in an unconfigured
repository do not require workflow installation.

## Personal defaults

From the clean shared source checkout:

```sh
python3 -B scripts/bootstrap.py personal --replace-global
python3 -B scripts/bootstrap.py personal --replace-global --apply
```

The first command previews. The second is appropriate only under explicit authority
to replace personal instructions. It backs up existing Codex/Claude instruction
files, installs the exact committed package into a local release directory, and
links thin global instructions plus four distinctly named skills: sdd-workflow,
sdd-maintenance, sdd-go and sdd-rust. It does not install global openspec-* adapters,
which could shadow project implementations. Existing unrelated skills stay intact.
`--workspace-root <container>` additionally replaces that workspace's AGENTS.md
with the generic multi-repository router, with its own backup. Do not use this
option on a product repository root that owns domain instructions.

Defaults prefer the actual repository's workflow and pin. The personal release is
fallback/routing, not a substitute for an adopted project's selected source.
Restart/refresh clients to validate actual discovery. Claude's cloud sessions do
not inherit local home-directory skills; project adapters are versioned separately.

Updates use a clean checkout of the newly reviewed release and the same preview /
apply commands (initial --replace-global is no longer needed). Existing managed
instructions or skill links that drift cause refusal; reconcile deliberately rather
than forcing replacement. There is no background updater or automatic remote pull.
The selected workspace route, if any, is retained on later personal updates.

State and original backups live under `~/.local/share/agent-workflow/`.
`personal-install.json` identifies the release and backup; the backup's restore.json
maps each prior file and original symlink. To restore initial instructions, inspect
that record and replace only the managed links with their saved original files or
symlink targets. A release rollback uses a clean checkout of the chosen earlier
release and the personal installer again; do not manually move current without
reconciling its state file. Never publish personal backups with this package.

## Adopt a repository

Create an isolated project branch/worktree as appropriate. Inspect its existing
instructions, module roots, commands, lint/tool versions and expected runtime side
effects. Prepare a project profile JSON with languages, module roots, references
to project-owned commands and important exceptions; it is documentation, not code
that the bootstrap executes. Keep secrets and developer-machine paths out of it.

From the clean shared checkout:

```sh
python3 -B scripts/bootstrap.py repo --repo /path/to/project --profile /path/to/profile.json
python3 -B scripts/bootstrap.py repo --repo /path/to/project --profile /path/to/profile.json --apply
```

This adds a pinned `.agents/workflow` submodule, project profile, operation skills,
Claude command shims, OpenSpec configuration, short project guide and bounded routing
blocks in AGENTS.md/CLAUDE.md. Existing instruction text outside the blocks survives.
Git submodule setup stages .gitmodules and the exact gitlink; review and stage generated
files normally. No product file is edited and no product command is executed.

The default source URL is the public agent-workflow repository. Publish the selected
shared commit before adopting it from that URL. `--source-url` supports an explicitly
selected alternate repository, including a local fixture. Local-file transport is
enabled only for that single Git command, never in global config. `--source` names
the clean local source checkout; it is required when running an installer from an
installed archive release, which has no Git metadata. Use --revision only when the
source checkout is already at that exact commit; the tool never switches it for you.

An existing OpenSpec tree, existing workflow checkout or unowned output collision
is a migration boundary: the bootstrap refuses it. Inspect and adapt that project's
existing integration instead of overwriting it. Smart Example retains its custom
adapters and is updated through its own maintenance flow.

## Repository updates and checks

From a clean checkout of a newer shared release, run the same repo preview/apply
commands. Omit --profile to retain the recorded project profile. Managed-file hashes
and instruction-block hashes must match; edits outside the blocks survive. Dirty
or unexpectedly moved shared source is a conflict. There is no --force bypass.
Ownership state is `.agents/workflow-install.json`; do not hand-edit hashes to hide
unreviewed drift. If project-owned configuration needs changing, review the intended
migration and adjust the integration explicitly rather than tricking the updater.

Use `python3 -B .agents/workflow/scripts/bootstrap.py status --repo .` to inspect
managed files, routing blocks and pin. Run shared `make check` and the selected
project's native OpenSpec checks. Installed product commands remain project-owned.
Use the exact checks in docs/project-flow.md; missing native prerequisites are not
passes. A failed clone/fetch leaves visible partial Git setup for inspection; the
installer does not reset a repository to conceal an environment failure.

## New repositories and distribution

The personal sdd-workflow route makes the method available in new repositories.
Use sdd-maintenance to request adoption; creating files is explicit task work, not
a silent side effect of opening a repo. Team members use the versioned project
wrappers and submodule, not another developer's home paths. Skills remain plain
portable files; a plugin package is optional distribution, not a new runtime or
permission requirement. Do not automatically rewrite global OpenSpec profile settings.
