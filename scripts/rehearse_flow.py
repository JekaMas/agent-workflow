"""Disposable planning/implementation rehearsal, not a fresh-agent evaluation.

Run with --output-dir NEW_PATH and --go-tool an existing supported Go binary.
Retains native instruction responses, exact sources, checks and staged load sizes.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--output-dir', type=Path, required=True)
p.add_argument('--go-tool', required=True)
a = p.parse_args()
a.output_dir.mkdir(parents=True, exist_ok=False)
output = a.output_dir.resolve()
root = Path(__file__).resolve().parents[1]
project = output / 'project'
project.mkdir()
env = dict(os.environ, OPENSPEC_TELEMETRY='0', DO_NOT_TRACK='1', OPENSPEC_NO_UPDATE_CHECK='1',
           GOTOOLCHAIN='local', GOWORK='off', GOPROXY='off', GOFLAGS='-mod=readonly', PYTHONDONTWRITEBYTECODE='1')
env.pop("GOROOT", None)  # Let the explicitly selected binary resolve its own toolchain.
steps = []

def run(label, command, expected=0):
    result = subprocess.run(command, cwd=project, env=env, capture_output=True, text=True, timeout=120)
    (output / (label + '.stdout')).write_text(result.stdout)
    (output / (label + '.stderr')).write_text(result.stderr)
    steps.append({'label': label, 'command': command, 'exit': result.returncode, 'expected': expected})
    (output / 'steps.json').write_text(json.dumps(steps, indent=2))
    if result.returncode != expected:
        raise RuntimeError(f'{label}: expected {expected}, observed {result.returncode}; inspect retained logs')
    return result.stdout

def write(path, text):
    q = project / path
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text(text)

write('AGENTS.md', 'Use the installed OpenSpec spec-driven flow. Implement only the clamp library.\nUse local Go tests; no services or dependencies. Keep one task list and actual evidence.\n')
(project / 'openspec').mkdir()
shutil.copy2(root / 'openspec/config.yaml', project / 'openspec/config.yaml')
run('openspec-version', ['openspec', '--version'])
go_version = run('go-version', [a.go_tool, 'version'])
run('new-change', ['openspec', 'new', 'change', 'bounded-clamp', '--schema', 'spec-driven', '--json'])
change = 'openspec/changes/bounded-clamp/'
run('proposal-instructions', ['openspec', 'instructions', 'proposal', '--change', 'bounded-clamp', '--json'])
write(change+'proposal.md', '''## Why
A local caller needs an integer clamp with explicit inverted-range rejection.
## What Changes
Add Clamp(x, lo, hi) returning a bounded integer or an error.
## Capabilities
### New Capabilities
- bounded-clamp: Clamp integer values without arithmetic overflow.
### Modified Capabilities
## Impact
New dependency-free Go library and focused tests in this disposable project.
''')
for artifact in ['specs','design']:
    run(artifact+'-instructions', ['openspec','instructions',artifact,'--change','bounded-clamp','--json'])
write(change+'specs/bounded-clamp/spec.md', '''## ADDED Requirements
### Requirement: Bound integer values
Clamp SHALL return lo for x below lo, hi for x above hi, and x within the inclusive interval, without overflowing integer arithmetic.
#### Scenario: In-range input
- **WHEN** x is 4, lo is 2 and hi is 8
- **THEN** the result is 4 with no error
#### Scenario: Out-of-range input
- **WHEN** x is 9, lo is 2 and hi is 8
- **THEN** the result is 8 with no error
### Requirement: Reject inverted ranges
Clamp SHALL return an error when lo exceeds hi.
#### Scenario: Inverted range
- **WHEN** lo is 8 and hi is 2
- **THEN** the operation returns an error
''')
write(change+'design.md', '''## Context
Dependency-free integer API in a disposable local fixture.
## Goals / Non-Goals
Implement exact clamping and rejection. No IO, services, product changes or performance claim.
## Decisions
Use comparisons rather than subtraction to avoid overflow. Tests use independent fixed vectors including platform integer extremes. Generated properties cover containment, in-range preservation, idempotence and monotonicity; seeds 1 and 2, 1000 samples each. No generated coverage percentage claimed.
## Risks / Trade-offs
Generated samples do not exhaust the integer domain. Fixed extrema cover boundary arithmetic. A deliberately wrong high-bound branch must be detected.
## Verification
Requirement bound: TestClampCases, TestClampProperties, TestClampMonotonic.
Requirement rejection: inverted-range fixed case. Required set is all three top-level tests, with observed nonzero execution and no skips. Preserve failing and repaired evidence.
''')
run('tasks-instructions',['openspec','instructions','tasks','--change','bounded-clamp','--json'])
tasks='''## 1. Deliver clamp behavior
- [ ] 1.1 Qualify decisive tests against a deliberately incomplete implementation.
- [ ] 1.2 Implement exact behavior and verify examples/properties and fault detection.
'''
write(change+'tasks.md',tasks)
run('apply-instructions',['openspec','instructions','apply','--change','bounded-clamp','--json'])
version=go_version.split()[2].removeprefix('go')
write('go.mod',f'module rehearsal.local/clamp\n\ngo {version}\n')
write('clamp.go','package clamp\nfunc Clamp(x, lo, hi int) (int, error) { return x, nil }\n')
write('clamp_test.go', '''package clamp
import ("testing"; "testing/quick"; "math/rand")
func TestClampCases(t *testing.T) {
 max := int(^uint(0)>>1); min := -max-1
 for _, c := range []struct{x,lo,hi,want int; bad bool}{
 {4,2,8,4,false},{1,2,8,2,false},{9,2,8,8,false},{4,4,4,4,false},
 {min,min,max,min,false},{max,min,max,max,false},{min,-2,2,-2,false},
 {max,-2,2,2,false},{0,8,2,0,true},
 } { got,err:=Clamp(c.x,c.lo,c.hi); if (err!=nil)!=c.bad || (!c.bad && got!=c.want) {t.Errorf("%+v got %d err %v",c,got,err)} }
}
func TestClampProperties(t *testing.T) {
 prop:=func(x,lo,hi int)bool{ if lo>hi {lo,hi=hi,lo}; v,e:=Clamp(x,lo,hi); if e!=nil||v<lo||v>hi{return false}; if x>=lo&&x<=hi&&v!=x{return false}; again,e:=Clamp(v,lo,hi); return e==nil&&again==v }
 if e:=quick.Check(prop,&quick.Config{MaxCount:1000,Rand:rand.New(rand.NewSource(1))});e!=nil{t.Fatal(e)}
}
func TestClampMonotonic(t *testing.T) {
 prop:=func(x,y,lo,hi int)bool{if lo>hi{lo,hi=hi,lo};if x>y{x,y=y,x};a,e:=Clamp(x,lo,hi);b,f:=Clamp(y,lo,hi);return e==nil&&f==nil&&a<=b}
 if e:=quick.Check(prop,&quick.Config{MaxCount:1000,Rand:rand.New(rand.NewSource(2))});e!=nil{t.Fatal(e)}
}
''')
runner=root/'scripts/local_verify.py'
def check(label, expected=0, selector='^TestClamp.*$'):
    snapshot = output / (label + '-inputs')
    snapshot.mkdir()
    for name in ['clamp.go', 'clamp_test.go', 'go.mod']:
        shutil.copy2(project / name, snapshot / name)
    run(label,[sys.executable,str(runner),'go-test','--cwd',str(project),'--scope','clamp.go','--package','.', '--test',selector,'--tool',a.go_tool,'--output',str(output/(label+'.json'))],expected)
check('red',1)
def require_behavioral_failure(label):
    evidence = json.loads((output / (label + '.json')).read_text())
    native = next(step for step in evidence['steps'] if step.get('label') == 'tests')
    events = [json.loads(line) for line in Path(native['stdout_artifact']).read_text().splitlines()]
    if not any(e.get('Test') == 'TestClampCases' and e.get('Action') == 'fail' for e in events):
        raise RuntimeError(label + ': required behavioral failure absent')
    if any(e.get('Action') == 'build-fail' for e in events):
        raise RuntimeError(label + ': build failure is not behavioral evidence')
require_behavioral_failure('red')
good='''package clamp
import "errors"
func Clamp(x, lo, hi int) (int, error) {
 if lo > hi { return 0, errors.New("inverted range") }
 if x < lo { return lo, nil }
 if x > hi { return hi, nil }
 return x, nil
}
'''
write('clamp.go',good)
run('gofmt',[str(Path(a.go_tool).with_name('gofmt')),'-w','clamp.go','clamp_test.go'])
good=(project/'clamp.go').read_text()
check('green')
write('clamp.go',good.replace('return hi, nil','return lo, nil'))
check('deliberate-fault',1)
require_behavioral_failure('deliberate-fault')
write('clamp.go',good)
check('restored')
check('zero-selection',1,'^TestAbsent$')
write(change+'tasks.md',tasks.replace('[ ]','[x]'))
write(change+'evidence.md','Examples and 2x1000 deterministic property samples passed. Wrong implementation and deliberate high-bound fault were rejected. Zero-test selection was rejected. Exact commands, seeds, native guidance and initial failures are retained in the parent output directory. This fixture is not product acceptance or an independent agent evaluation.\n')
run('ready',[sys.executable,str(runner),'openspec','--cwd',str(project),'--scope','openspec','--change','bounded-clamp','--require-project-guidance','--require-tasks-complete','--output',str(output/'ready.json')])
stages={
 'initial':[project/'AGENTS.md'],
 'planning':[root/'skills/openspec-delivery/SKILL.md',root/'skills/openspec-delivery/references/delivery.md',root/'skills/verification-design/SKILL.md',root/'skills/verification-design/references/verification.md',project/'openspec/config.yaml']+[output/(s+'-instructions.stdout') for s in ['proposal','specs','design','tasks']],
 'implementation':[output/'apply-instructions.stdout']+[project/(change+n) for n in ['proposal.md','design.md','tasks.md','specs/bounded-clamp/spec.md']]
}
report={'claim':'scripted same-session rehearsal; bytes of explicitly selected files, not actual model tokens or a fresh agent context','stages':{},'steps':steps,'result':'passed'}
for stage,files in stages.items():
    report['stages'][stage]={'bytes':sum(f.stat().st_size for f in files),'files':[{'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]}
(output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v['bytes'] for k,v in report['stages'].items()}))
