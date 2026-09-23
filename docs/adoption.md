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
files, installs the exact committed package into a detached Git release checkout, and
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

## New repository or existing repository without OpenSpec

One-time source checkout (Git and Python 3.10+ required):

```sh
git clone https://github.com/JekaMas/agent-workflow.git /path/to/agent-workflow
cd /path/to/agent-workflow
```

Use a clean reviewed revision. Before merge, select the reviewed feature commit;
cloning main alone does not include an unmerged change. Initialize a new project's
Git repository first with `git init /path/to/project` if needed.

```sh
python3 -B scripts/bootstrap.py repo --repo /path/to/project
python3 -B scripts/bootstrap.py repo --repo /path/to/project --apply
```

The first command previews; the second applies. No profile file is required:
Go/Rust manifests propose language routes and module roots. Existing AGENTS/CLAUDE
text is preserved around one managed routing block. Review detected roots and
actual toolchains/commands; discovery does not execute product checks. Other
languages get the same lifecycle, debugging, conflict and sequence-testing routes.
Use `--profile /path/to/profile.json` when overriding detection or supplying project
command references, context and exceptions. The resulting profile is tracked.

The tool adds the exact shared submodule pin, Codex skills, Claude commands,
OpenSpec configuration and docs/SDD_WORKFLOW.md. It installs no tools, dependencies,
models, plugins or hooks. OpenSpec remains a separately installed prerequisite;
its absence is not successful native validation. Review and commit generated files,
.gitmodules and the gitlink. Ignored required outputs and unowned collisions fail.

## Existing OpenSpec or custom workflow integration

Use the same source checkout. Preserve the installed schema and all active changes.
For an existing spec-driven setup:

```sh
python3 -B scripts/bootstrap.py prepare --repo /path/to/project --plan-out /tmp/workflow-adoption.json --preview-dir /tmp/workflow-proposed
# Inspect the existing config/skills and proposed outputs; preserve useful custom
# rules in project profile references. Reprepare with --profile if needed.
python3 -B scripts/bootstrap.py repo --repo /path/to/project --migration-plan /tmp/workflow-adoption.json
python3 -B scripts/bootstrap.py repo --repo /path/to/project --migration-plan /tmp/workflow-adoption.json --apply
```

`prepare` writes only the explicitly named review record (or prints it when
--plan-out is omitted). It never overwrites an earlier record. The record lists
prior fingerprints and proposed output hashes, the project profile, exact source
revision and affected paths; it is not permission. Review rendered files under /tmp/workflow-proposed against existing sources, not hashes alone. The preview directory must be new and outside the target repository. Passing a reviewed plan explicitly selects replacement of its listed
integration outputs. Reconcile custom instructions before applying; preparation
cannot infer which custom rule is obsolete. Use the same --profile for prepare
and apply when one was selected. Any drift in affected files, profile or revision
rejects before setup. A different/custom schema requires a deliberate schema
migration and remains untouched by this path.

Existing output symlinks need explicit conversion to regular adapters before managed adoption; the installer refuses to write through an alias into another owner. Custom consumers may retain those links and use reviewed pin/render updates instead.

The installer never writes existing specs, changes, tasks or historical evidence.
It can adopt a clean existing shared submodule only when its indexed pin and source
URL agree. Existing managed installations use normal update, not migration-plan
mode. No --force option bypasses file identity or ignore checks. Local file source
URLs are supported explicitly for fixtures; no global Git transport change.

## Finish setup

From the consumer, after reviewing and staging the intended setup files (publication validation rejects untracked sources):

```sh
python3 -B .agents/workflow/scripts/bootstrap.py status --repo .
python3 -B .agents/workflow/scripts/skill_packages.py --root . --policy .agents/skill-policy.json validate
python3 -B .agents/workflow/scripts/workflow_publication.py --root . --policy .agents/publication-policy.json
python3 -B .agents/workflow/scripts/check_opsx_routes.py --root .
```

Behavioral changes additionally keep
`openspec/changes/<change>/verification.json`. Consumer check adapters expose
structural graph validation with the ordinary spec check, an affected query/run
during apply and verify, and `requirement_tests.py run --all` during final
readiness. Read the tool from the exact `.agents/workflow` pin; do not copy a
second implementation into the consumer.

Inspect native OpenSpec status/instructions for an existing selected change or a
disposable fixture; do not create or archive a product change solely for setup.
Refresh Codex/Claude discovery if needed. After a fresh clone, developers only need
`git submodule update --init --recursive` plus already-documented prerequisites.
No personal installation or Makefile is required. Plain-language tasks can follow
AGENTS.md/CLAUDE.md and docs/SDD_WORKFLOW.md in any agent; UI aliases are conveniences.

## Repository updates and checks

From a clean checkout of a newer shared release, run the same repo preview/apply
commands. Omit --profile to retain the recorded project profile. Managed-file hashes
and instruction-block hashes must match; edits outside the blocks survive. Dirty
or unexpectedly moved shared source is a conflict. There is no --force bypass.
Ownership state is `.agents/workflow-install.json`; do not hand-edit hashes to hide
unreviewed drift. If project-owned configuration needs changing, review the intended
migration and adjust the integration explicitly rather than tricking the updater.

Use `python3 -B .agents/workflow/scripts/bootstrap.py status --repo .` to inspect
managed files, routing blocks and pin. Run all consumer workflow checks in docs/project-flow.md (including packaging and publication), shared `make check` and the selected
project's native OpenSpec checks. Installed product commands remain project-owned.
Use the exact checks in docs/project-flow.md; missing native prerequisites are not
passes. A failed clone/fetch leaves visible partial Git setup for inspection; the
installer does not reset a repository to conceal an environment failure.

## New repositories and distribution

The personal sdd-workflow route makes the method available in new repositories.
A user request to create a new repository includes standard workflow adoption
within authorized project setup. Use sdd-maintenance for an existing repository;
opening it alone does not authorize configuration changes. Team members use the versioned project
wrappers and submodule, not another developer's home paths. Skills remain plain
portable files; a plugin package is optional distribution, not a new runtime or
permission requirement. Do not automatically rewrite global OpenSpec profile settings.

Active personal instruction/skill files resolve into tracked files in the release
Git checkout. Backups, installer state and inactive old export snapshots are
recovery data, not active workflow source. Releases with edits or untracked files
are rejected before activation. Update from a clean canonical source checkout.

## Specialist skills in adopted repositories

The tracked project profile selects language routes through `languages` (for
example `["go", "rust"]`). Every newly adopted repository gets `hypothesis-debugging`, `conflict-resolution` and
`event-sequence-pbt` adapters. Go adds `sdd-go`, `golang-testing`,
`golang-performance-diagnostics` and `golang-optimization`; Rust adds `sdd-rust`.
Other languages use the same event/model/oracle contract with their existing
framework. The bootstrap does not install testing or profiling tools.

Codex discovers the thin `.agents/skills/<name>/SKILL.md` adapters; Claude can
invoke `/<name>` through `.claude/commands/<name>.md`. Both read canonical content
under the consumer's pinned `.agents/workflow/skills/`. References stay in that
package and load only for the current question. Ordinary Go work does not load
all specialist references; event-sequence testing activates for stateful risks.

After cloning a consumer, run `git submodule update --init --recursive` to obtain
its exact shared source. Existing adopted repositories receive new routes through
the usual reviewed bootstrap preview/apply update. Custom integrations can use the reviewed prepare/adopt path above, or retain reviewed local adapters/relative links; no automatic overwrite. Removing
languages that would orphan managed routes requires an explicit migration.

Personal installation still exposes only the four sdd-* routers, avoiding a
second global copy of specialist names. Those routers can load conditional
specialists from their selected package when no project equivalent exists.

## One OpenSpec integration for all consumers

`scripts/integration_templates/` owns all 14 operation procedures and the full
artifact/apply/archive rules. `scripts/integration.py` renders those into project
skill adapters, Claude commands and `openspec/config.yaml`; OpenSpec reads the
concrete config, not an unsupported YAML include. Bootstrap uses this same renderer.

A project's tracked `.agents/workflow-project.json` may select `integration.flow`,
`checks`, `verification` and `maintenance` reference paths plus `openspec_context`.
Keep product knowledge and commands in those references. `check_skill` preserves
an existing openspec-check or project-check identity; both use the same procedure.
`workflow_make_group` optionally requires every target in a local Make group to
be documented in its check guide. Make is not required for new consumers.

Managed adopters use the normal bootstrap update. For an already reviewed custom
integration, inspect the profile and run the renderer first without writes:

```sh
python3 .agents/workflow/scripts/integration.py --root .
python3 .agents/workflow/scripts/integration.py --root . --write
python3 .agents/workflow/scripts/check_opsx_routes.py --root .
```

The write mode intentionally replaces the rendered outputs; use it only after
reviewing local deltas into shared templates or project references. It is not an
automatic conflict bypass. Do not use it to bypass bootstrap ownership hashes in
a managed adopter. The route check rejects adapter/config drift, missing local
references and ignored commands. Inspect native emitted guidance after rule edits.

Generated policy files select packaging rules and publication scope. Profiles may
supply `skill_policy` and `publication_policy` objects; preserve existing stricter
consumer policies when migrating. Ordinary managed updates add missing policy
outputs but refuse unmanaged collisions. Default packaging does not impose Smart
Example's metadata budget, flat references or approval conventions.

The default publication inventory includes generated sources and local instruction/
integration references selected by the profile. Extend its explicit roots/owners
for additional project-specific workflow scripts and assets; source discovery does
not parse arbitrary prose or claim the whole repository reference graph is covered.
