#!/usr/bin/env python3
"""Verify Git ownership of declared workflow source and active personal entrypoints."""
import argparse
import json
from pathlib import Path
import subprocess


def audit(paths):
    files=set(); errors=[]; repos={}
    for path in paths:
        if not path.exists():
            errors.append('missing source: '+str(path));continue
        if path.is_file(): files.add(path.resolve())
        else:
            for f in path.rglob('*'):
                if f.is_file() and not any(part in ['.git','__pycache__'] for part in f.parts): files.add(f.resolve())
    for path in sorted(files):
        result=subprocess.run(['git','-C',str(path.parent),'rev-parse','--show-toplevel'],capture_output=True,text=True)
        if result.returncode:
            errors.append('source outside Git: '+str(path));continue
        root=Path(result.stdout.strip()).resolve()
        if root not in repos:
            tracked=subprocess.check_output(['git','-C',str(root),'ls-files','-z']).decode().split('\0')
            repos[root]={'tracked':set(tracked),'paths':[]}
        relative=path.relative_to(root).as_posix();repos[root]['paths'].append(relative)
        if relative not in repos[root]['tracked']: errors.append('untracked source: '+str(path))
    if not files: errors.append('no workflow source files selected')
    rows=[]
    for root,data in repos.items():
        result=subprocess.run(['git','-C',str(root),'check-ignore','--no-index','-z','--stdin'],input='\0'.join(data['paths']).encode(),capture_output=True)
        if result.returncode not in [0,1]: errors.append('ignore check unavailable: '+str(root))
        errors += ['ignored source: '+str(root/p) for p in result.stdout.decode().split('\0') if p]
        rows.append({'repository':str(root),'source_files':len(data['paths'])})
    return {'status':'failed' if errors else 'passed','errors':errors,'files':len(files),'repositories':rows,
            'scope':'Declared source roots and resolved personal entrypoints; not arbitrary runtime plugins, private settings, backups or full reference-graph semantics.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--path',action='append',type=Path,default=[])
    p.add_argument('--personal',action='store_true')
    p.add_argument('--home',type=Path,default=Path.home())
    p.add_argument('--workspace',type=Path)
    a=p.parse_args();paths=a.path
    if a.personal:
        paths += [a.home/'.codex/AGENTS.md',a.home/'.claude/CLAUDE.md']
        paths += [a.home/folder/name for folder in ['.agents/skills','.claude/skills'] for name in ['sdd-workflow','sdd-maintenance','sdd-go','sdd-rust']]
    if a.workspace: paths.append(a.workspace/'AGENTS.md')
    if not paths: p.error('select --path, --personal or --workspace')
    result=audit(paths);print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
