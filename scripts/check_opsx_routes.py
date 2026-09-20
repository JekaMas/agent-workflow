"""Check all shared-rendered OpenSpec routes, local references and config drift."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from integration import integration_files, names, settings, OPERATIONS as CATALOG
OPERATIONS={op:name for op,(name,_) in CATALOG.items()}

def inspect(root):
    root=root.resolve();errors=[];rows=[]
    try:
        profile=json.loads((root/'.agents/workflow-project.json').read_text())
        expected=integration_files(profile); routes=names(profile);cfg=settings(profile)
    except (OSError,ValueError) as exc:
        return {'status':'failed','errors':['integration profile unavailable: '+str(exc)],'routes':[]}
    for op,skill in routes.items():
        paths=[root/f'.agents/skills/{skill}/SKILL.md',root/f'.claude/commands/opsx/{op}.md']
        if any(not p.is_file() or not p.resolve().is_relative_to(root) for p in paths):
            errors.append('missing or nonlocal route: '+op);continue
        text,command=[p.read_text() for p in paths]
        targets=re.findall(r'`(\.agents/skills/[^`]+/SKILL\.md)`',command)
        if targets!=[f'.agents/skills/{skill}/SKILL.md']:errors.append('command target mismatch: '+op)
        result=subprocess.run(['git','-C',str(root),'check-ignore','--no-index','--quiet',str(paths[1])],capture_output=True)
        if result.returncode==0:errors.append('command excluded from checkout publication: '+op)
        elif result.returncode!=1:errors.append('command publication check unavailable: '+op)
        rows.append({'operation':op,'skill':skill,'skill_bytes':len(text.encode()),'command_bytes':len(command.encode())})
    for name,text in expected.items():
        p=root/name
        if not p.is_file() or not p.resolve().is_relative_to(root) or p.read_text()!=text:
            errors.append('shared integration drift: '+name)
    for name in [*profile.get('instructions',['AGENTS.md','CLAUDE.md']),*cfg.values(),'.agents/workflow/skills/openspec-delivery/SKILL.md']:
        p=root/name
        if not p.is_file() or not p.resolve().is_relative_to(root):errors.append('missing instruction owner: '+name)
    group=profile.get('workflow_make_group')
    if group:
        make=(root/'Makefile').read_text() if (root/'Makefile').is_file() else ''
        groups=re.findall(r'^\.PHONY: ('+re.escape(group)+r'[^\n]*)$',make,re.M)
        guide=root/cfg['checks'];documented=set(re.findall(r'^\| `([^`]+)` \|',guide.read_text(),re.M)) if guide.is_file() else set()
        if len(groups)!=1:errors.append('missing or ambiguous workflow Make target group')
        else:
            for target in groups[0].split():
                if target not in documented:errors.append('workflow target lacks client check route: '+target)
    return {'status':'failed' if errors else 'passed','errors':errors,'routes':rows,
            'claim':'all rendered routes, config equality, reference availability and UTF-8 sizes; not UI dispatch or agent quality'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path.cwd());a=p.parse_args()
    result=inspect(a.root);print(json.dumps(result,indent=2));raise SystemExit(bool(result['errors']))
