#!/usr/bin/env python3
"""Preview/apply pinned personal defaults or repository workflow adoption. No tool installation."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

SOURCE = Path(__file__).resolve().parents[1]
URL = 'https://github.com/JekaMas/agent-workflow.git'
BEGIN = '<!-- agent-workflow:start -->'
END = '<!-- agent-workflow:end -->'
STATE = '.agents/workflow-install.json'
OPERATIONS = {
    'explore': ('openspec-explore', 'Explore intent and uncertainty; do not implement a proposal-only question.'),
    'new': ('openspec-new-change', 'Inspect related changes; use openspec new change <name> --schema spec-driven --json and status. A new-only request stops at the created change.'),
    'propose': ('openspec-propose', 'Create a matching change if needed. Use native artifact instructions to prepare proposal, specs, design and tasks in dependency order; do not invent acceptance.'),
    'continue': ('openspec-continue-change', 'Read native status/instructions and create the next artifact. Larger delivery requests may continue under their existing scope.'),
    'ff': ('openspec-ff-change', 'Prepare apply-ready artifacts through native instructions in dependency order, preserving consequential unresolved decisions.'),
    'update': ('openspec-update-change', 'Revise affected artifacts coherently. This is artifact revision, not the openspec update integration-refresh CLI. Do not edit product code for an update-only request.'),
    'apply': ('openspec-apply-change', 'Read openspec instructions apply --change <name> --json and its context. Implement useful increments, inspect, repair and revalidate within scope; update the one task list only against evidence.'),
    'verify': ('openspec-verify-change', 'Inspect actual diff, owners and evidence against requirements in both directions. Run relevant authorized checks. Verify-only does not authorize tracked-file fixes; implementation-and-repair scope continues through repair.'),
    'sync': ('openspec-sync-specs', 'Inspect and merge selected delta requirements into main specs under current authority. Preserve unrelated changes and strictly validate each affected main spec. Do not archive implicitly.'),
    'archive': ('openspec-archive-change', 'Read native archive guidance. Establish required behavior/evidence and archive authority before native archive. Inspect the resulting diff and strictly validate affected main specs; no archive of incomplete work.'),
    'bulk-archive': ('openspec-bulk-archive-change', 'Assess each explicitly selected change separately using archive rules, resolve overlapping deltas, and preserve incomplete changes.'),
    'onboard': ('openspec-onboard', 'Guide the next authorized operation through this actual setup; do not invent a product task or run external actions as a demonstration.'),
    'check': ('project-check', 'Resolve requested selector and target. Read .agents/workflow/docs/project-flow.md, run relevant existing checks and inspect results; do not merely suggest execution or run all tools. Missing required checks remain incomplete.'),
}


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE, text=True, env={**os.environ, 'GIT_OPTIONAL_LOCKS':'0'}).strip()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fingerprint(path):
    if not path.exists() and not path.is_symlink():
        return None
    return {'sha256': digest(path.read_bytes()), 'link': os.readlink(path) if path.is_symlink() else None}


def safe(root, name):
    p = root / name
    if Path(name).is_absolute() or '..' in Path(name).parts or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError('outside target root: ' + name)
    return p


def block(text):
    if text.count(BEGIN) != text.count(END) or text.count(BEGIN) > 1:
        raise ValueError('ambiguous instruction routing markers')
    if BEGIN not in text:
        return None
    return text[text.index(BEGIN):text.index(END)+len(END)]


def repo_files(profile):
    files = {'.agents/workflow-project.json': json.dumps(profile, indent=2)+'\n'}
    for op, (name, action) in OPERATIONS.items():
        files[f'.agents/skills/{name}/SKILL.md'] = f'''---
name: {name}
description: {op.capitalize()} work through this repository's pinned SDD workflow.
---

Read applicable project instructions, `.agents/workflow-project.json` and
`.agents/workflow/docs/project-flow.md` in this checkout. Use the pinned shared
openspec-delivery procedure and only relevant language/domain references.
{action}
'''
        files[f'.agents/skills/{name}/agents/openai.yaml'] = f'''interface:
  display_name: "SDD {op}"
  short_description: "{op.capitalize()} using the pinned project workflow."
  default_prompt: "Use ${name} for the requested task."
'''
        files[f'.claude/commands/opsx/{op}.md'] = f'''---
description: {op.capitalize()} using the pinned project workflow.
---
Use `.agents/skills/{name}/SKILL.md` in this checkout.
Treat $ARGUMENTS as user intent/targets, not shell code. Preserve task authority.
'''
    files['openspec/config.yaml'] = '''schema: spec-driven
context: |
  Follow this repository's applicable instructions and .agents/workflow-project.json.
  Shared procedures live in the pinned .agents/workflow; project commands and
  authority remain local. No artifact, skill or checklist grants external access.
rules:
  proposal:
    - State requested outcome, scope and non-goals; inspect related existing specs.
  specs:
    - Challenge ambiguity and rejection/compatibility cases; map important requirements to falsifiable properties and independent oracles.
  design:
    - Record consequential choices, risks, assumptions and required evidence, including actual owners, configurations and limits.
  tasks:
    - Keep one authoritative checklist. Detail the next useful increment and link evidence; missing, skipped, empty or timed-out checks are not passes.
operations:
  apply:
    guidance:
      - Use .agents/workflow/docs/project-flow.md and the project's actual commands. Continue useful authorized implementation, inspection, repair and affected revalidation.
      - Replan within intent; ask only for remaining material ambiguity or authority after independent work. Preserve requirements and failures; do not weaken acceptance to get green.
      - DONE requires the requested outcome, matching artifacts, current required evidence, inspected behavior/diff and resolved material findings. A checkpoint, clean review or checkbox alone is insufficient.
  archive:
    guidance:
      - Inspect requirements, tasks and actual evidence. Archive only completed work within user authority; do not bypass pending checks or infer deployment approval.
'''
    files['docs/SDD_WORKFLOW.md'] = '''# Development workflow

For substantial work use OpenSpec Propose → Apply → Verify; revise artifacts when
new evidence changes the approach. Small edits do not need a ceremonial change.
Codex uses `$openspec-propose`, `$openspec-apply-change`, `$openspec-verify-change`.
Claude uses `/opsx:propose`, `/opsx:apply`, `/opsx:verify`. Include the task/change.
Apply owns relevant checks, inspection, authorized repair and revalidation.

The selected change's tasks.md is the only checklist. Required unavailable checks
remain incomplete. Archive completed changes explicitly; publication/deployment
have their own authority. The full procedure is in `.agents/workflow/docs/project-flow.md`.

Use `$project-check` or `/opsx:check` with workflow, spec <change>, ready <change>
or a selected language target. Exact local commands remain in project instructions
and `.agents/workflow-project.json`; the shared package does not impose product suites.

Inspect setup ownership with `python3 .agents/workflow/scripts/bootstrap.py status --repo .`.
Shared updates are explicit and pinned; see `.agents/workflow/docs/adoption.md`.
'''
    return files


def repo_plan(root, profile):
    if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root.resolve():
        raise ValueError('target must be the exact repository root')
    state_path = safe(root, STATE)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if not state and (root/'.agents/workflow').exists():
        raise ValueError('existing workflow needs a reviewed migration; bootstrap will not replace it')
    if not state and (root/'openspec').exists():
        raise ValueError('existing OpenSpec setup needs a reviewed migration')
    files = repo_files(profile)
    candidates = [*files, STATE, 'AGENTS.md', 'CLAUDE.md']
    ignored = subprocess.run(['git','-C',str(root),'check-ignore','--no-index','-z','--stdin'],
                             input='\0'.join(candidates).encode(), capture_output=True)
    if ignored.returncode not in (0,1):
        raise ValueError('publication ignore check unavailable')
    if ignored.returncode == 0:
        raise ValueError('workflow files are ignored: '+ignored.stdout.decode().replace('\0', ', '))
    for name in files:
        p = safe(root, name)
        actual = fingerprint(p)
        expected = state.get('files', {}).get(name)
        if actual is not None and actual != expected:
            raise ValueError('unmanaged or modified file: '+name)
    routing = BEGIN+'\nFor substantial work, use docs/SDD_WORKFLOW.md and the pinned shared workflow.\nExisting project/domain rules remain applicable; this block grants no authority.\n'+END
    for name in ['AGENTS.md', 'CLAUDE.md']:
        p = safe(root, name)
        original = p.read_text() if p.exists() else ''
        owned = block(original)
        expected = state.get('blocks', {}).get(name)
        if (owned is not None or expected is not None) and (owned is None or digest(owned.encode()) != expected):
            raise ValueError('unmanaged or modified instruction block: '+name)
        files[name] = original.replace(owned, routing) if owned else original.rstrip()+'\n\n'+routing+'\n'
    if state:
        sub = root/'.agents/workflow'
        if git(sub, 'rev-parse', 'HEAD') != state['revision'] or git(sub, 'status', '--porcelain'):
            raise ValueError('shared pin changed or dirty; review before updating')
    return files, state


def repo_apply(root, profile, source, revision, url, apply):
    files, state = repo_plan(root, profile)
    if state and state['source'] != url:
        raise ValueError('source URL changed; requires reviewed migration')
    print(json.dumps({'mode':'apply' if apply else 'preview','repository':str(root),'revision':revision,'files':list(files),'submodule_url':url}))
    if not apply:
        return
    sub = root/'.agents/workflow'
    if not state:
        command = ['git','-C',str(root)]
        if Path(url).is_dir():
            command += ['-c','protocol.file.allow=always']
        subprocess.run(command+['submodule','add','--',url,'.agents/workflow'],check=True)
    if not subprocess.run(['git','-C',str(sub),'cat-file','-e',revision+'^{commit}'],capture_output=True).returncode == 0:
        subprocess.run(['git','-C',str(sub),'fetch','origin',revision],check=True)
    subprocess.run(['git','-C',str(sub),'checkout','--detach',revision],check=True)
    subprocess.run(['git','-C',str(root),'add','.agents/workflow'],check=True)
    new = {'version':1,'revision':revision,'source':url,'files':{},'blocks':{}}
    for name, text in files.items():
        p = safe(root,name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        if name in ['AGENTS.md','CLAUDE.md']:
            new['blocks'][name] = digest(block(text).encode())
        else:
            new['files'][name] = fingerprint(p)
    safe(root,STATE).write_text(json.dumps(new,indent=2)+'\n')


def personal(source, revision, home, workspace, apply, replace):
    base = home/'.local/share/agent-workflow'
    state_path = base/'personal-install.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    targets = {home/'.codex/AGENTS.md':'defaults/personal.md', home/'.claude/CLAUDE.md':'defaults/personal.md'}
    if workspace:
        targets[workspace/'AGENTS.md'] = 'defaults/workspace.md'
    skills = ['sdd-workflow','sdd-maintenance','sdd-go','sdd-rust']
    links = {home/parent/name:'skills/'+name for parent in ['.agents/skills','.claude/skills'] for name in skills}
    for p in targets:
        current = fingerprint(p)
        expected = state.get('targets',{}).get(str(p))
        if expected is not None and current != expected:
            raise ValueError('modified managed instructions: '+str(p))
        if expected is None and current is not None and not replace:
            raise ValueError('initial replacement requires --replace-global; backup will be kept: '+str(p))
    for p, relative in links.items():
        if p.exists() or p.is_symlink():
            if not p.is_symlink() or os.readlink(p) != str(base/'current'/relative):
                raise ValueError('unmanaged personal skill: '+str(p))
    print(json.dumps({'mode':'apply' if apply else 'preview','revision':revision,'instructions':[str(p) for p in targets],'skills':[str(p) for p in links],'backup_required':not bool(state)}))
    if not apply:
        return
    release = base/'releases'/revision
    if not release.exists():
        release.parent.mkdir(parents=True,exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix='release-',dir=release.parent))
        subprocess.run(['git','clone','--no-hardlinks','--no-checkout',str(source),str(stage)],check=True)
        subprocess.run(['git','-C',str(stage),'checkout','--detach',revision],check=True)
        stage.rename(release)
    if not (release/'.git').is_dir():
        raise ValueError('legacy exported release is not Git-backed; select a new reviewed release')
    if git(release,'rev-parse','HEAD') != revision or git(release,'status','--porcelain','--untracked-files=all'):
        raise ValueError('modified or untracked release; refuse activation')
    for folder in ['defaults','skills','docs','scripts']:
        for path in (release/folder).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                git(release,'ls-files','--error-unmatch','--',path.relative_to(release).as_posix())
    if state.get('revision') == revision and all(state.get('targets',{}).get(str(p)) == fingerprint(p) and p.is_symlink() for p in targets) and all(p.exists() for p in links):
        print('Already installed at selected revision')
        return
    backup = base/'backups'/str(time.time_ns())
    backup.mkdir(parents=True,exist_ok=False,mode=0o700)
    history={'previous_revision':state.get('revision'),'files':{}}
    for i,p in enumerate(targets):
        if p.exists() or p.is_symlink():
            history['files'][str(p)]={'link':os.readlink(p) if p.is_symlink() else None,'backup':str(backup/str(i))}
            (backup/str(i)).write_bytes(p.read_bytes())
    (backup/'restore.json').write_text(json.dumps(history,indent=2)+'\n')
    pointer=base/'current.next';pointer.symlink_to(release);os.replace(pointer,base/'current')
    for p,relative in {**targets,**links}.items():
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists() or p.is_symlink(): p.unlink()
        p.symlink_to(base/'current'/relative)
    merged=dict(state.get('targets',{}));merged.update({str(p):fingerprint(p) for p in targets})
    state={'revision':revision,'targets':merged,'backup':str(backup),'workspace':str(workspace) if workspace else state.get('workspace')}
    state_path.write_text(json.dumps(state,indent=2)+'\n')
    print('Installed release; previous instructions recoverable from '+str(backup))


def status(root):
    state=json.loads(safe(root,STATE).read_text())
    profile=json.loads(safe(root,'.agents/workflow-project.json').read_text())
    repo_plan(root,profile)
    print(json.dumps({'status':'passed','revision':state['revision'],'claim':'owned files, instruction blocks and clean pin; not product validation'}))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['repo','personal','status'])
    p.add_argument('--repo',type=Path,default=Path.cwd())
    p.add_argument('--source',type=Path,default=SOURCE)
    p.add_argument('--revision')
    p.add_argument('--source-url',default=URL)
    p.add_argument('--profile',type=Path)
    p.add_argument('--home',type=Path,default=Path.home())
    p.add_argument('--workspace-root',type=Path)
    p.add_argument('--replace-global',action='store_true')
    p.add_argument('--apply',action='store_true')
    args=p.parse_args()
    root=args.repo.resolve()
    if args.mode=='status': return status(root)
    source=args.source.resolve(); revision=git(source,'rev-parse',(args.revision or 'HEAD')+'^{commit}')
    if args.apply and (git(source,'rev-parse','HEAD')!=revision or git(source,'status','--porcelain')):
        raise ValueError('apply requires a clean source checkout at the selected revision')
    if args.mode=='personal':
        workspace=args.workspace_root.resolve() if args.workspace_root else None
        state=args.home/'.local/share/agent-workflow/personal-install.json'
        if workspace is None and state.exists():
            stored=json.loads(state.read_text()).get('workspace')
            workspace=Path(stored) if stored else None
        return personal(source,revision,args.home.resolve(),workspace,args.apply,args.replace_global)
    profile_path=args.profile or root/'.agents/workflow-project.json'
    profile=json.loads(profile_path.read_text()) if profile_path.exists() else {'schema':1,'languages':[],'instructions':[],'notes':'Inspect actual manifests and project conventions before selecting product checks.'}
    if not isinstance(profile,dict): raise ValueError('project profile must be an object')
    repo_apply(root,profile,source,revision,args.source_url,args.apply)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
