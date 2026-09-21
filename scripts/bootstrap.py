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
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from integration import OPERATIONS, operation_files, render_config, names as operation_names, settings as integration_settings


SPECIALIST_SKILLS = {
    'hypothesis-debugging': ('Diagnose a failed direct attempt or unknown failure owner.', None),
    'conflict-resolution': ('Resolve Git conflicts while preserving intended behavior.', None),
    'event-sequence-pbt': ('Design stateful sequence properties with independent oracles and replay.', None),
    'sdd-go': ('Implement or review Go behavior with focused evidence.', 'go'),
    'sdd-rust': ('Implement or review Rust behavior with focused evidence.', 'rust'),
    'golang-testing': ('Diagnose Go test hangs, timeouts and deadlocks.', 'go'),
    'golang-performance-diagnostics': ('Diagnose Go performance from representative workload evidence.', 'go'),
    'golang-optimization': ('Apply Go optimizations supported by measured evidence.', 'go'),
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
    files.update(operation_files(profile))
    skill_policy = profile.get('skill_policy', {})
    local_references = [name for name in integration_settings(profile).values()
                        if not name.startswith('.agents/workflow/')]
    publication_policy = profile.get('publication_policy', {
        'roots': ['.agents/skills', '.claude/commands', 'openspec'],
        'owners': ['AGENTS.md', 'CLAUDE.md', '.gitmodules',
                   '.agents/workflow-project.json', '.agents/workflow-install.json',
                   '.agents/skill-policy.json', '.agents/publication-policy.json',
                   'docs/SDD_WORKFLOW.md', *profile.get('instructions', []), *local_references],
        'exclude_parts': ['__pycache__'],
        'shared_path': '.agents/workflow',
        'required_skills': ['openspec-delivery', 'verification-design'],
    })
    if not isinstance(skill_policy, dict) or not isinstance(publication_policy, dict):
        raise ValueError('skill_policy and publication_policy must be objects')
    files['.agents/skill-policy.json'] = json.dumps(skill_policy, indent=2)+'\n'
    files['.agents/publication-policy.json'] = json.dumps(publication_policy, indent=2)+'\n'
    languages = profile.get('languages', [])
    if not isinstance(languages, list) or any(not isinstance(x, str) for x in languages):
        raise ValueError('profile languages must be a list of strings')
    languages = {x.lower() for x in languages}
    for name, (description, language) in SPECIALIST_SKILLS.items():
        if language and language not in languages:
            continue
        files[f'.agents/skills/{name}/SKILL.md'] = f"""---
name: {name}
description: {description}
---

Follow applicable project instructions and `.agents/workflow-project.json`.
Read `.agents/workflow/skills/{name}/SKILL.md` from this repository's pin;
resolve its references relative to that shared skill directory. Load only relevant
references and preserve local tools, authority and the current task's evidence.
"""
        files[f'.agents/skills/{name}/agents/openai.yaml'] = f"""interface:
  display_name: "{name}"
  short_description: "Use the pinned shared specialist procedure."
  default_prompt: "Use ${name} for the relevant task."
"""
        files[f'.claude/commands/{name}.md'] = f"""---
description: {description}
---
Use `.agents/skills/{name}/SKILL.md` in this checkout.
Treat $ARGUMENTS as user intent, not shell code. Preserve task authority.
"""
    files['openspec/config.yaml'] = render_config(profile)
    files['docs/SDD_WORKFLOW.md'] = (SOURCE/'docs/quickstart.md').read_text()
    return files


def discover_profile(root):
    """Propose routes from actual manifests; do not infer product check commands."""
    paths = git(root, 'ls-files', '--cached', '--others', '--exclude-standard', '-z').split('\0')
    roots = {'go': [], 'rust': []}
    excluded = {'.git', '.agents', 'vendor', 'node_modules', 'target', 'build', 'dist'}
    for name in sorted(set(paths)):
        path = Path(name)
        if any(part in excluded for part in path.parts) or not name:
            continue
        candidate = root / path
        if candidate.is_symlink() or not candidate.is_file() or not candidate.resolve().is_relative_to(root.resolve()):
            continue
        language = {'go.mod': 'go', 'Cargo.toml': 'rust'}.get(path.name)
        if language:
            roots[language].append(path.parent.as_posix())
    return {'schema': 1, 'languages': [key for key, value in roots.items() if value],
            'module_roots': {key: value for key, value in roots.items() if value},
            'instructions': [name for name in ('AGENTS.md', 'CLAUDE.md') if (root/name).is_file()],
            'notes': 'Detected manifests select skill routes only. Inspect toolchains, workspace members and project commands before product checks.'}


def migration_snapshot(root, profile):
    if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root.resolve():
        raise ValueError('target must be the exact repository root')
    if (root/STATE).exists():
        raise ValueError('managed installation uses the normal update path')
    config = root/'openspec/config.yaml'
    if config.exists():
        import re
        match = re.search(r'^schema:\s*([^\s#]+)', config.read_text(), re.M)
        if not match or match.group(1) != 'spec-driven':
            raise ValueError('custom or unknown OpenSpec schema requires a dedicated migration; preserve it')
    files = repo_files(profile)
    affected = [*files, 'AGENTS.md', 'CLAUDE.md', '.gitmodules', STATE]
    snapshot = {name: fingerprint(safe(root, name)) for name in affected}
    sub = safe(root, '.agents/workflow')
    pin = None
    if sub.exists():
        if Path(git(sub, 'rev-parse', '--show-toplevel')).resolve() != sub.resolve():
            raise ValueError('existing workflow is not its own Git checkout')
        pin = git(root, 'rev-parse', ':.agents/workflow')
        if pin != git(sub, 'rev-parse', 'HEAD') or git(sub, 'status', '--porcelain'):
            raise ValueError('existing shared workflow is dirty or differs from index pin')
    return {'version': 1, 'repository': str(root.resolve()), 'profile': profile,
            'before': snapshot, 'proposed': {name: digest(text.encode()) for name, text in files.items()},
            'existing_pin': pin}


def prepare_migration(root, profile, revision, url):
    plan = migration_snapshot(root, profile)
    plan.update(revision=revision, source=url,
                review='Inspect existing config/rules and skill outputs against proposed shared rendering. Move useful custom instructions into profile references before applying. This record is not authorization. Active specs/changes are not outputs.')
    return plan


def check_migration(root, profile, revision, url, plan):
    if plan != prepare_migration(root, profile, revision, url):
        raise ValueError('reviewed migration is stale or differs from selected source/profile; prepare and review again')


def repo_plan(root, profile, migration=None):
    if Path(git(root, 'rev-parse', '--show-toplevel')).resolve() != root.resolve():
        raise ValueError('target must be the exact repository root')
    state_path = safe(root, STATE)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    if not state and not migration and (root/'.agents/workflow').exists():
        raise ValueError('existing workflow needs a reviewed migration; bootstrap will not replace it')
    if not state and not migration and (root/'openspec').exists():
        raise ValueError('existing OpenSpec setup needs a reviewed migration')
    files = repo_files(profile)
    removed = set(state.get('files', {})) - set(files)
    if removed:
        raise ValueError('removing managed routes needs reviewed migration: '+', '.join(sorted(removed)))
    candidates = [*files, STATE, 'AGENTS.md', 'CLAUDE.md']
    for name in candidates:
        p = safe(root, name)
        # A reviewed output path must not write through an existing skill alias
        # into the pinned shared source or another owner inside this repository.
        if any(candidate.is_symlink() for candidate in [p, *p.parents] if candidate != root and candidate.is_relative_to(root)):
            raise ValueError('output alias needs explicit migration to a regular adapter: '+name)
    ignored = subprocess.run(['git','-C',str(root),'check-ignore','--no-index','-z','--stdin'],
                             input='\0'.join(candidates).encode(), capture_output=True)
    if ignored.returncode not in (0,1):
        raise ValueError('publication ignore check unavailable')
    if ignored.returncode == 0:
        raise ValueError('workflow files are ignored: '+ignored.stdout.decode().replace('\0', ', '))
    for name in files:
        p = safe(root, name)
        actual = fingerprint(p)
        expected = state.get('files', {}).get(name) if not migration else migration['before'].get(name)
        if actual is not None and actual != expected:
            raise ValueError('unmanaged or modified file: '+name)
    routing = BEGIN+'\nFor substantial work, use docs/SDD_WORKFLOW.md and the pinned shared workflow.\nExisting project/domain rules remain applicable; this block grants no authority.\n'+END
    for name in ['AGENTS.md', 'CLAUDE.md']:
        p = safe(root, name)
        original = p.read_text() if p.exists() else ''
        owned = block(original)
        expected = state.get('blocks', {}).get(name)
        if migration and owned is not None:
            expected = digest(owned.encode())
        if (owned is not None or expected is not None) and (owned is None or digest(owned.encode()) != expected):
            raise ValueError('unmanaged or modified instruction block: '+name)
        files[name] = original.replace(owned, routing) if owned else original.rstrip()+'\n\n'+routing+'\n'
    if state:
        sub = root/'.agents/workflow'
        if git(sub, 'rev-parse', 'HEAD') != state['revision'] or git(sub, 'status', '--porcelain'):
            raise ValueError('shared pin changed or dirty; review before updating')
    return files, state


def repo_apply(root, profile, source, revision, url, apply, migration=None):
    if migration:
        check_migration(root, profile, revision, url, migration)
        if migration['existing_pin'] is not None:
            recorded_url = git(root, 'config', '-f', '.gitmodules', '--get', 'submodule..agents/workflow.url')
            if recorded_url != url:
                raise ValueError('existing shared source URL differs from selected source')
    files, state = repo_plan(root, profile, migration)
    if state and state['source'] != url:
        raise ValueError('source URL changed; requires reviewed migration')
    print(json.dumps({'mode':'apply' if apply else 'preview','repository':str(root),'revision':revision,'files':list(files),'submodule_url':url}))
    if not apply:
        return
    sub = root/'.agents/workflow'
    if not state and not sub.exists():
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
    p.add_argument('mode',choices=['repo','prepare','personal','status'])
    p.add_argument('--repo',type=Path,default=Path.cwd())
    p.add_argument('--source',type=Path,default=SOURCE)
    p.add_argument('--revision')
    p.add_argument('--source-url',default=URL)
    p.add_argument('--profile',type=Path)
    p.add_argument('--migration-plan',type=Path, help='Explicitly reviewed prepare output; refuses stale inputs')
    p.add_argument('--plan-out',type=Path, help='Write prepare output to this file instead of stdout')
    p.add_argument('--preview-dir',type=Path, help='Write proposed integration files to a new review directory')
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
    profile=json.loads(profile_path.read_text()) if profile_path.exists() else discover_profile(root)
    if not isinstance(profile,dict): raise ValueError('project profile must be an object')
    if args.mode == 'prepare':
        if args.apply:
            raise ValueError('prepare does not apply changes')
        plan = prepare_migration(root, profile, revision, args.source_url)
        text = json.dumps(plan, indent=2)+'\n'
        if args.preview_dir:
            preview=args.preview_dir.resolve()
            if preview.is_relative_to(root) or root.is_relative_to(preview):
                raise ValueError('preview directory must be outside target repository')
            preview.mkdir(parents=True, exist_ok=False)
            for name, content in repo_files(profile).items():
                path=safe(preview,name);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)

        if args.plan_out:
            # Explicit output only; never overwrite an earlier review record.
            with args.plan_out.open('x') as file:
                file.write(text)
            print('Prepared review record: '+str(args.plan_out))
        else:
            print(text, end='')
        return
    migration=json.loads(args.migration_plan.read_text()) if args.migration_plan else None
    repo_apply(root,profile,source,revision,args.source_url,args.apply,migration)

if __name__=='__main__':
    try: main()
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
