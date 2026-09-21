#!/usr/bin/env python3
"""Validate repo skills and expose them to an enclosing Codex workspace."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


REPO_ROOT = Path.cwd()
SKILLS_DIR = REPO_ROOT / ".agents" / "skills"
COMPAT_SKILLS_DIR = REPO_ROOT / ".codex" / "skills"
METADATA_BUDGET_BYTES = None
POLICY = {}
NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
REFERENCE_ROUTE_RE = re.compile(
    r"(?<![A-Za-z0-9_./-])"
    r"(references/[A-Za-z0-9][A-Za-z0-9_.-]*(?:/[A-Za-z0-9][A-Za-z0-9_.-]*)*)"
)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")

    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, separator, value = line.partition(":")
        if separator:
            values[key.strip()] = value.strip()
    return values


def skill_dirs() -> list[Path]:
    return sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir())


def routed_reference_paths(skill_text: str) -> set[str]:
    """Return explicit skill-local references/* routes named in SKILL.md."""

    return {match.group(1) for match in REFERENCE_ROUTE_RE.finditer(skill_text)}


def validate_skill_references(skill_dir: Path, skill_text: str) -> list[str]:
    """Validate one-level reference routing for one skill."""

    errors: list[str] = []
    references_dir = skill_dir / "references"
    routed = routed_reference_paths(skill_text)

    for route in sorted(routed):
        route_path = Path(route)
        if POLICY.get('flat_references', False) and len(route_path.parts) != 2:
            errors.append(
                f"{skill_dir / 'SKILL.md'}: nested reference route is not allowed: {route}"
            )
        if not (skill_dir / route_path).is_file():
            errors.append(
                f"{skill_dir / 'SKILL.md'}: unresolved routed reference: {route}"
            )

    if not references_dir.exists():
        return errors
    if not references_dir.is_dir():
        errors.append(f"reference path is not a directory: {references_dir}")
        return errors

    for path in sorted(references_dir.rglob("*")):
        relative = path.relative_to(skill_dir).as_posix()
        if path.is_dir() and POLICY.get('flat_references', False):
            errors.append(f"nested reference directory is not allowed: {relative}")
            continue
        if POLICY.get('direct_references', False) and path.is_file() and relative not in routed:
            errors.append(
                f"reference file is not directly named by SKILL.md: {skill_dir / relative}"
            )

    return errors


def validate_repo() -> int:
    errors: list[str] = []
    metadata_bytes = 0

    if not SKILLS_DIR.is_dir():
        errors.append(f"missing canonical skill directory: {SKILLS_DIR}")
        skills: list[Path] = []
    else:
        skills = skill_dirs()

    if POLICY.get('compatibility_link', False):
        if not COMPAT_SKILLS_DIR.is_symlink():
            errors.append(f"compatibility path is not a symlink: {COMPAT_SKILLS_DIR}")
        elif COMPAT_SKILLS_DIR.resolve() != SKILLS_DIR.resolve():
            errors.append(f"compatibility path does not resolve to {SKILLS_DIR}")

    names: set[str] = set()
    for skill_dir in skills:
        skill_file = skill_dir / "SKILL.md"
        metadata_file = skill_dir / "agents" / "openai.yaml"
        if not skill_file.is_file():
            errors.append(f"missing SKILL.md: {skill_dir}")
            continue

        skill_text = skill_file.read_text(encoding="utf-8")
        errors.extend(validate_skill_references(skill_dir, skill_text))

        try:
            frontmatter = parse_frontmatter(skill_file)
        except ValueError as error:
            errors.append(f"{skill_file}: {error}")
            continue

        name = frontmatter.get("name", "")
        description = frontmatter.get("description", "")
        if name != skill_dir.name:
            errors.append(f"{skill_file}: name {name!r} does not match folder")
        if not NAME_RE.fullmatch(name):
            errors.append(f"{skill_file}: invalid skill name {name!r}")
        if name in names:
            errors.append(f"duplicate skill name: {name}")
        names.add(name)
        if not description:
            errors.append(f"{skill_file}: missing description")
        metadata_bytes += len(name.encode()) + len(description.encode())

        if not metadata_file.is_file():
            if POLICY.get('require_ui', False):
                errors.append(f"missing agents/openai.yaml: {skill_dir}")
            continue
        metadata = metadata_file.read_text(encoding="utf-8")
        if not metadata.startswith("interface:\n"):
            errors.append(f"{metadata_file}: missing interface mapping")
        short_match = re.search(r'^  short_description: "([^"]+)"$', metadata, re.MULTILINE)
        if not short_match:
            errors.append(f"{metadata_file}: missing quoted short_description")
        elif not 25 <= len(short_match.group(1)) <= 64:
            errors.append(f"{metadata_file}: short_description must be 25-64 characters")
        if f"${name}" not in metadata:
            errors.append(f"{metadata_file}: default_prompt must mention ${name}")
        if POLICY.get('require_implicit', False) and "allow_implicit_invocation: false" in metadata:
            errors.append(f"{metadata_file}: implicit invocation is disabled")

    if METADATA_BUDGET_BYTES is not None and metadata_bytes > METADATA_BUDGET_BYTES:
        errors.append(
            f"repo skill name+description metadata is {metadata_bytes} bytes; "
            f"budget is {METADATA_BUDGET_BYTES}"
        )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"repo skills valid: count={len(skills)} "
        f"metadata_bytes={metadata_bytes}/{METADATA_BUDGET_BYTES}"
    )
    return 0


def default_workspace_root() -> Path:
    for parent in REPO_ROOT.parents:
        if (parent / "AGENTS.md").is_file():
            return parent
    raise ValueError("no enclosing workspace with AGENTS.md; pass --workspace-root")


def link_workspace(workspace_root: Path, check: bool, replace: bool) -> int:
    workspace_root = workspace_root.expanduser().resolve()
    destination = workspace_root / ".agents" / "skills"
    errors: list[str] = []

    if not check:
        destination.mkdir(parents=True, exist_ok=True)

    for skill_dir in skill_dirs():
        link = destination / skill_dir.name
        expected = skill_dir.resolve()

        if link.is_symlink() and link.resolve() == expected:
            continue
        if check:
            errors.append(f"missing or stale workspace skill link: {link}")
            continue
        if link.exists() or link.is_symlink():
            if not replace:
                errors.append(f"refusing to replace existing path: {link}")
                continue
            if not link.is_symlink():
                errors.append(f"refusing to replace non-symlink path: {link}")
                continue
            link.unlink()

        relative_target = os.path.relpath(skill_dir, destination)
        link.symlink_to(relative_target, target_is_directory=True)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    action = "verified" if check else "linked"
    print(f"workspace skills {action}: root={workspace_root} count={len(skill_dirs())}")
    return 0


def configure(root, policy=None):
    global REPO_ROOT, SKILLS_DIR, COMPAT_SKILLS_DIR, METADATA_BUDGET_BYTES, POLICY
    REPO_ROOT = Path(root).resolve()
    POLICY = policy or {}
    SKILLS_DIR = REPO_ROOT / POLICY.get('skills_path', '.agents/skills')
    COMPAT_SKILLS_DIR = REPO_ROOT / POLICY.get('compatibility_path', '.codex/skills')
    for path in (SKILLS_DIR, COMPAT_SKILLS_DIR):
        if not path.resolve().is_relative_to(REPO_ROOT):
            raise ValueError('skill policy path outside repository')
    METADATA_BUDGET_BYTES = POLICY.get('metadata_budget_bytes')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--policy', type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="validate canonical repo skill packaging")

    link_parser = subparsers.add_parser(
        "link-workspace",
        help="link repo skills into an enclosing workspace discovery path",
    )
    link_parser.add_argument("--workspace-root", type=Path)
    link_parser.add_argument("--check", action="store_true")
    link_parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    if args.root or args.policy:
        import json
        configure(args.root or REPO_ROOT, json.loads(args.policy.read_text()) if args.policy else {})

    if args.command == "validate":
        return validate_repo()

    try:
        workspace_root = args.workspace_root or default_workspace_root()
    except ValueError as error:
        parser.error(str(error))
    return link_workspace(workspace_root, args.check, args.replace)


if __name__ == "__main__":
    raise SystemExit(main())
