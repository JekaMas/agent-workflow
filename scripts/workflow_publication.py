"""Check reproducible workflow source publication; never installs or edits files."""
import argparse
import json
from pathlib import Path
import subprocess



def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def inspect(root, policy):
    root = root.resolve()
    roots = policy.get('roots', ['.agents/skills', '.claude/commands', 'openspec'])
    owners = policy.get('owners', ['AGENTS.md', '.gitmodules'])
    shared_path = policy.get('shared_path', '.agents/workflow')
    for name in [*roots, *owners, shared_path]:
        if Path(name).is_absolute() or '..' in Path(name).parts:
            raise ValueError('publication policy outside repository: ' + name)
    errors = []
    # The index permits validating an intentional new file before its commit.
    tracked = set(git(root, 'ls-files', '-z').decode().split('\0'))
    candidates = set(owners)
    excluded = []
    for name in roots:
        base = root / name
        if not base.exists():
            continue
        for p in base.rglob('*'):
            if not (p.is_file() or p.is_symlink()):
                continue
            rel = p.relative_to(root).as_posix()
            if any(part in policy.get('exclude_parts', ['__pycache__']) for part in p.parts) or rel in policy.get('exclude_paths', []):
                excluded.append(rel)
                continue
            candidates.add(rel)
    for rel in sorted(candidates):
        p = root / rel
        if rel not in tracked:
            errors.append(f'unpublished workflow candidate: {rel}')
        if not p.exists():
            errors.append(f'missing workflow source: {rel}')
        elif not p.resolve().is_relative_to(root):
            errors.append(f'outside-checkout workflow dependency: {rel}')
    # --no-index also catches ignored paths that happen to be force-added already.
    result = subprocess.run(['git', '-C', str(root), 'check-ignore', '--no-index', '-z', '--stdin'],
                            input='\0'.join(sorted(candidates)).encode(), capture_output=True)
    if result.returncode not in (0, 1):
        errors.append(f'ignore inspection unavailable: exit {result.returncode}')
    else:
        errors.extend('ignored workflow candidate: ' + p for p in result.stdout.decode().split('\0') if p)
    sub = root / shared_path
    try:
        pin = git(root, 'rev-parse', ':' + shared_path).decode().strip()
        actual = git(sub, 'rev-parse', 'HEAD').decode().strip()
        if pin != actual or git(sub, 'status', '--porcelain').strip():
            errors.append('shared workflow differs from clean pinned source')
        for skill in policy.get('required_skills', ['openspec-delivery', 'verification-design']):
            if not (sub / 'skills' / skill / 'SKILL.md').is_file():
                errors.append(f'missing shared skill: {skill}')
    except subprocess.CalledProcessError:
        errors.append('shared workflow pin unavailable; initialize the recorded submodule')
    return {'status': 'failed' if errors else 'passed', 'errors': errors,
            'checked_files': len(candidates), 'excluded_private_or_cache_files': excluded,
            'scope': list(roots),
            'limits': 'Source/index and pinned submodule checks; not arbitrary link-graph, client dispatch, tool installation or semantic validation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--policy', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.root, json.loads(args.policy.read_text()))
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result['errors']))
