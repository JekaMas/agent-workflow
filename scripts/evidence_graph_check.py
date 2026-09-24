#!/usr/bin/env python3
"""Admit and execute a consumer's change-owned requirement-evidence graph.

The graph semantics, selection and execution stay in `requirement_tests.py` and
`discovery_ledger.py`. This wrapper owns the consumer adoption policy: validate
the selected change's graph when it exists, report a named transition gap for a
change recorded before the adoption, and refuse any other change without a graph.
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import subprocess
import sys

SHARED_SCRIPTS = pathlib.Path(__file__).resolve().parent
REQUIREMENT_TESTS = SHARED_SCRIPTS / "requirement_tests.py"
DISCOVERY_LEDGER = SHARED_SCRIPTS / "discovery_ledger.py"
DEFAULT_TRANSITION = pathlib.Path(".agents/evidence-transition.json")
DEFAULT_OUTPUT_DIR = pathlib.Path("data/logs/local_verification")


def transition_changes(root: pathlib.Path, transition_file: pathlib.Path) -> set[str]:
    path = transition_file if transition_file.is_absolute() else root / transition_file
    if not path.is_file():
        return set()

    data = json.loads(path.read_text(encoding="utf-8"))
    changes = data.get("changes")
    if not isinstance(changes, list) or not all(isinstance(item, str) for item in changes):
        print(f"{path}: changes must be a list of change names", file=sys.stderr)
        raise SystemExit(2)

    return set(changes)


def run(command: list[str], root: pathlib.Path) -> int:
    return subprocess.run(command, cwd=root, check=False).returncode


def shared_command(root: pathlib.Path, change: str, script: pathlib.Path) -> list[str]:
    return [sys.executable, "-B", str(script), "--root", str(root), "--change", change]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="consumer repository root")
    parser.add_argument("--change", required=True)
    parser.add_argument("--transition-file", default=str(DEFAULT_TRANSITION))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("operation", choices=["validate", "query", "ready", "run"])
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    root = pathlib.Path(args.root).resolve()
    change_root = root / "openspec" / "changes" / args.change
    if not change_root.is_dir():
        print(f"unknown change: {args.change}", file=sys.stderr)
        return 2

    manifest = change_root / "verification.json"
    if not manifest.is_file():
        recorded = args.change in transition_changes(root, pathlib.Path(args.transition_file))
        reason = (
            f"validation-only: {args.change} predates the evidence graph and reports a "
            "transition gap; author verification.json before claiming graph-backed readiness"
            if recorded
            else f"{manifest} is missing and {args.change} is not recorded in {args.transition_file}"
        )
        print(json.dumps({"change": args.change,
                          "evidence_graph": "transition_gap" if recorded else "missing",
                          "reason": reason}))

        return 0 if recorded and args.operation == "validate" else 1

    if args.operation == "ready":
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = root / args.output_dir / f"evidence-{args.change}-{stamp}.json"
        output.parent.mkdir(parents=True, exist_ok=True)

        return run(shared_command(root, args.change, REQUIREMENT_TESTS)
                   + ["run", "--all", "--require-clean", "--output", str(output), *args.arguments], root)

    if args.operation == "validate":
        exit_code = run(shared_command(root, args.change, REQUIREMENT_TESTS) + ["validate", *args.arguments], root)
        if exit_code != 0:
            return exit_code

        if not (change_root / "discovery.json").is_file():
            print(json.dumps({
                "change": args.change,
                "discovery": "missing",
                "reason": "behavioral selection evidence requires discovery.json; record the exact, semantic and IDE lanes",
            }))

            return 0

        exit_code = run(shared_command(root, args.change, DISCOVERY_LEDGER), root)
        if exit_code == 0:
            print(json.dumps({"change": args.change, "evidence_graph": "validated", "discovery": "validated",
                              "status": "passed"}))

        return exit_code

    return run(shared_command(root, args.change, REQUIREMENT_TESTS) + [args.operation, *args.arguments], root)


if __name__ == "__main__":
    sys.exit(main())
