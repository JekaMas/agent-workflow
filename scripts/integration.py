"""Canonical OpenSpec adapters and rules; project profiles contain local extensions."""
import json
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent/'integration_templates'
CATALOG = json.loads((TEMPLATES/'operations.json').read_text())
OPERATIONS = {op: (row['skill'], '') for op,row in CATALOG.items()}
DEFAULTS = {
    'flow': '.agents/workflow/docs/project-flow.md',
    'checks': '.agents/workflow/docs/project-flow.md',
    'verification': '.agents/workflow/skills/verification-design/SKILL.md',
    'maintenance': '.agents/workflow/docs/maintenance.md',
}

def settings(profile):
    result={**DEFAULTS, **profile.get('integration', {})}
    for key in DEFAULTS:
        value=result[key]
        if not isinstance(value,str) or Path(value).is_absolute() or '..' in Path(value).parts or any(c in value for c in '\n\r`'):
            raise ValueError('invalid integration path: '+key)
    return result

def names(profile):
    check=profile.get('check_skill','project-check')
    if check not in ('openspec-check','project-check'):
        raise ValueError('unsupported check skill identity')
    return {op:check if op=='check' else row['skill'] for op,row in CATALOG.items()}

def substitute(text, config):
    for key in DEFAULTS:text=text.replace('{{'+key+'}}',config[key])
    return text

def render_config(profile):
    cfg=settings(profile)
    context=profile.get('openspec_context', 'Follow applicable project instructions and .agents/workflow-project.json. Shared procedures come from the pinned .agents/workflow; project commands and authority remain local.')
    if not isinstance(context,str):raise ValueError('openspec_context must be text')
    header='schema: spec-driven\n\n# Rendered from pinned shared templates and project profile; do not edit directly.\ncontext: |\n'+''.join('  '+line+'\n' for line in context.splitlines())+'\n'
    return header+substitute((TEMPLATES/'rules.yaml').read_text(),cfg)

def operation_files(profile):
    files={};cfg=settings(profile)
    for op,name in names(profile).items():
        desc=CATALOG[op]['description']
        files[f'.agents/skills/{name}/SKILL.md']=f'''---
name: {name}
description: {desc}
metadata:
  owner: agent-workflow
---

# OpenSpec {op}

Rendered from the pinned shared integration; edit canonical source, not this copy.
Read applicable project instructions and `.agents/workflow-project.json`.
Use `.agents/workflow/docs/operations.md` for relevant operation loading and
`{cfg['flow']}` for project commands. Keep user authority and task scope.

'''+substitute((TEMPLATES/(op+'.md')).read_text(),cfg)
        if op=='maintain':files[f'.agents/skills/{name}/SKILL.md']+=f"\nProject maintenance reference: `{cfg['maintenance']}`.\n"
        files[f'.agents/skills/{name}/agents/openai.yaml']=f'''interface:
  display_name: "OpenSpec {op}"
  short_description: "{op.capitalize()} through the pinned project workflow."
  default_prompt: "Use ${name} for the requested task."
'''
        files[f'.claude/commands/opsx/{op}.md']=f'''---
description: {desc}
---
Use `.agents/skills/{name}/SKILL.md` in this checkout.
Treat $ARGUMENTS as user intent/targets, not shell code. Preserve task authority.
'''
    return files

def integration_files(profile):
    return {**operation_files(profile), 'openspec/config.yaml':render_config(profile)}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description='Preview or explicitly render an existing reviewed project integration.')
    p.add_argument('--root',type=Path,default=Path.cwd())
    p.add_argument('--write',action='store_true')
    a=p.parse_args();root=a.root.resolve()
    profile=json.loads((root/'.agents/workflow-project.json').read_text())
    files=integration_files(profile)
    changes=[]
    for name,text in files.items():
        path=root/name
        if not path.resolve().is_relative_to(root):raise ValueError('outside project: '+name)
        if not path.is_file() or path.read_text()!=text:changes.append(name)
    print(json.dumps({'mode':'write' if a.write else 'preview','changes':changes},indent=2))
    if a.write:
        for name in changes:
            path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(files[name])
