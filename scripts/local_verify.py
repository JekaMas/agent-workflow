#!/usr/bin/env python3
"""Run one explicitly selected local check; its result is never task acceptance."""

from __future__ import annotations

import argparse
import hashlib
import datetime as dt
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from collections.abc import Iterable

try:
    from scripts.process_runner import PREVIEW_BYTES, run_process
except ModuleNotFoundError:  # Direct `python scripts/local_verify.py` route.
    from process_runner import PREVIEW_BYTES, run_process


OPENSPEC_VERSION = "1.13.1"
GOLANGCI_VERSION = "2.11.3"
def workflow_tests() -> int:
    """Run only workflow-mechanics tests, rejecting missing or skipped coverage."""
    import unittest

    sys.path.insert(0, os.environ.get("LOCAL_VERIFY_PROJECT_ROOT", str(Path(__file__).resolve().parents[1])))
    names = [
        "scripts.test_local_verify",
        "scripts.test_openspec_workflow",
        "scripts.test_requirement_tests",
        "scripts.test_discovery_ledger",
    ]
    suites = [unittest.defaultTestLoader.loadTestsFromName(name) for name in names]
    selected = {name: suite.countTestCases() for name, suite in zip(names, suites)}
    if any(count == 0 for count in selected.values()):
        print(json.dumps({"status": "no_tests", "selected": selected}))
        return 1
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(unittest.TestSuite(suites))
    passed = result.wasSuccessful() and not result.skipped and result.testsRun > 0
    print(json.dumps({"status": "passed" if passed else "failed", "selected": selected,
                      "tests": result.testsRun, "failures": len(result.failures),
                      "errors": len(result.errors), "skipped": len(result.skipped),
                      "claim": "synthetic workflow/parser/process fixtures only"}))
    return 0 if passed else 1


def openspec_result(raw: str, cwd: Path, change: str) -> tuple[str, dict]:
    try:
        value = json.loads(raw)
        items = value["items"]
        totals = value["summary"]["totals"]
        root = Path(value["root"]["path"]).resolve()
        if not isinstance(items, list) or not items:
            return "no_selection", {}
        if root != cwd.resolve():
            return "wrong_root", {}
        if len(items) != 1 or items[0]["id"] != change or items[0]["type"] != "change":
            return "wrong_selection", {}
        if totals != {"items": 1, "passed": 1, "failed": 0} or items[0]["valid"] is not True:
            return "failed", {"selection": change, "totals": totals}
        return "passed", {"selection": change, "totals": totals, "claim": "spec validation only"}
    except (ValueError, TypeError, KeyError, IndexError):
        return "invalid_output", {}


def task_result(raw: str, cwd: Path, change: str) -> tuple[str, dict]:
    try:
        value = json.loads(raw)
        progress = value["progress"]
        tasks = value["tasks"]
        if Path(value["root"]["path"]).resolve() != cwd.resolve():
            return "wrong_root", {}
        if value["changeName"] != change or Path(value["changeDir"]).resolve() != cwd / "openspec" / "changes" / change:
            return "wrong_selection", {}
        if not isinstance(tasks, list) or not tasks or progress["total"] == 0:
            return "no_selection", {"progress": progress}
        if any(type(progress[key]) is not int for key in ("total", "complete", "remaining")):
            return "invalid_output", {}
        if progress["total"] != len(tasks):
            return "invalid_output", {}
        complete = sum(task["done"] is True for task in tasks)
        if progress != {"total": len(tasks), "complete": complete, "remaining": len(tasks) - complete}:
            return "invalid_output", {}
        if value["state"] != "all_done" or complete != len(tasks):
            return "incomplete_tasks", {"progress": progress}
        return "passed", {"progress": progress, "claim": "task checkboxes complete; evidence review still required"}
    except (ValueError, TypeError, KeyError):
        return "invalid_output", {}


def guidance_result(raw: str, cwd: Path, change: str, surface: str) -> tuple[str, dict]:
    try:
        value = json.loads(raw)
        if Path(value["root"]["path"]).resolve() != cwd.resolve():
            return "wrong_root", {}
        if value["changeName"] != change:
            return "wrong_selection", {}
        if surface not in {"apply", "archive"} and value["artifactId"] != surface:
            return "wrong_selection", {}
        context = value.get("context")
        field = "operationGuidance" if surface in {"apply", "archive"} else "rules"
        guidance = value.get(field)
        if not isinstance(context, str) or not context.strip():
            return "missing_project_guidance", {"surface": surface, "missing": "context"}
        if not isinstance(guidance, list) or not guidance or any(not isinstance(item, str) or not item.strip() for item in guidance):
            return "missing_project_guidance", {"surface": surface, "missing": field}
        return "passed", {"surface": surface, "guidance_items": len(guidance),
                          "claim": "nonempty project guidance delivered; not semantic adequacy or agent adherence"}
    except (ValueError, TypeError, KeyError):
        return "invalid_output", {}


def go_result(raw: str | Iterable[str], expected_packages: set[str] | None = None) -> tuple[str, dict]:
    active_tests: set[tuple[str, str]] = set()
    active_packages: set[str] = set()
    tests: dict[tuple[str, str], str] = {}
    packages: dict[str, str] = {}
    skipped_tests: set[tuple[str, str]] = set()
    skipped_packages: set[str] = set()
    malformed = 0
    saw_failure = False
    terminal_priority = {"pass": 0, "skip": 1, "fail": 2}
    for line in raw.splitlines() if isinstance(raw, str) else raw:
        try:
            event = json.loads(line)
            package, test, action = event.get("Package"), event.get("Test"), event.get("Action")
            if not isinstance(package, str) or not package or not isinstance(action, str):
                raise ValueError("missing event identity")
            if test is not None and (not isinstance(test, str) or not test):
                raise ValueError("invalid test identity")
            if action not in {"start", "run", "pause", "cont", "pass", "fail", "skip", "output", "bench"}:
                raise ValueError("unknown action")
        except (ValueError, TypeError, AttributeError):
            malformed += 1
            continue
        if test:
            key = (package, test)
            if action == "run":
                if key in active_tests or package not in active_packages:
                    malformed += 1
                active_tests.add(key)
            elif action in {"pass", "fail", "skip"}:
                if key not in active_tests:
                    malformed += 1
                active_tests.discard(key)
                tests[key] = max(tests.get(key, "pass"), action, key=terminal_priority.get)
                if action == "skip":
                    skipped_tests.add(key)
            elif action in {"pause", "cont"}:
                if key not in active_tests:
                    malformed += 1
            elif action not in {"output", "bench"}:
                malformed += 1
        elif action == "start":
            if package in active_packages:
                malformed += 1
            active_packages.add(package)
        elif action in {"pass", "fail", "skip"}:
            if package not in active_packages:
                malformed += 1
            active_packages.discard(package)
            packages[package] = max(packages.get(package, "pass"), action, key=terminal_priority.get)
            if action == "skip":
                skipped_packages.add(package)
        elif action not in {"output", "bench"}:
            malformed += 1
        saw_failure = saw_failure or action == "fail"
    counts = {name: sum(value == name for value in tests.values()) for name in ("pass", "fail", "skip")}
    details = {"tests": len(tests), "packages": len(packages), **counts,
               "malformed_lines": malformed, "unfinished_tests": sorted(active_tests),
               "unfinished_packages": sorted(active_packages),
               "skipped_tests": sorted(f"{package}::{test}" for package, test in skipped_tests),
               "skipped_packages": sorted(skipped_packages)}
    observed = set(packages) | active_packages
    details["missing_packages"] = sorted((expected_packages or observed) - observed)
    details["unexpected_packages"] = sorted(observed - (expected_packages or observed))
    details["packages_without_tests"] = sorted(package for package in packages if not any(owner == package for owner, _ in tests))
    if saw_failure:
        return "failed", details
    if malformed or active_tests or active_packages or not packages or details["missing_packages"] or details["unexpected_packages"]:
        return "incomplete", details
    if skipped_tests:
        return "required_skipped", details
    if details["packages_without_tests"]:
        return "no_tests", details
    if skipped_packages:
        return "required_skipped", details
    return "passed", details


def proof_result(kind: str, raw: str) -> tuple[str, dict]:
    """Qualify pinned native summaries; a process exit alone is insufficient."""
    if kind == 'kani':
        match = re.search(r'Complete - (\d+) successfully verified harnesses, (\d+) failures, (\d+) total', raw)
        ok = bool(match and int(match[1]) > 0 and int(match[2]) == 0 and match[1] == match[3]
                  and 'VERIFICATION:- SUCCESSFUL' in raw and 'VERIFICATION:- FAILED' not in raw and '- Status: FAILURE' not in raw)
    elif kind == 'verus':
        rows = re.findall(r'verification results:: (\d+) verified, (\d+) errors', raw)
        ok = len(rows) == 1 and int(rows[0][0]) > 0 and int(rows[0][1]) == 0
    else:
        members = re.findall(r'Gobra found (\d+) methods and functions', raw)
        errors = re.findall(r'Gobra found (\d+) errors', raw)
        abstract = re.findall(r'(\d+) specified members? of the package under verification (?:is|are) trusted or abstract', raw)
        ok = (len(members) == 1 and int(members[0]) > 0 and errors and all(int(n) == 0 for n in errors)
              and abstract and all(int(n) == 0 for n in abstract) and 'timed out' not in raw.lower())
    return ('passed' if ok else 'incomplete'), {'claim': 'selected implementation obligation under recorded semantics; not whole-product proof'}


def proof_failure(kind: str, raw: str) -> str:
    """Classify known native diagnostics, never infer a product defect from exit 1."""
    if re.search(r'(?im)^.*(?:solver returned unknown|VERIFICATION:- UNKNOWN)\s*$', raw):
        return 'solver_unknown'
    if re.search(r'(?im)^.*(?:unsupported feature|unsupported construct|not supported by (?:kani|verus|gobra))', raw):
        return 'unsupported'
    if re.search(r'(?im)^error\[E[0-9]+\]|^error: (?:could not compile|failed to (?:invoke|find))', raw):
        return 'harness_or_environment'
    violations = {
        'kani': 'VERIFICATION:- FAILED' in raw and '- Status: FAILURE' in raw,
        'verus': bool(re.search(r'(?m)^error: (?:postcondition|precondition|assertion) (?:not satisfied|failed)', raw)),
        'gobra': 'Postcondition might not hold.' in raw or 'Assertion might not hold.' in raw,
    }
    return 'property_violation' if violations.get(kind) else 'unclassified_failure'


def command_plan(args: argparse.Namespace) -> tuple[list[str], list[tuple[str, list[str]]]]:
    if args.kind in {'kani', 'verus', 'gobra'}:
        if not args.tool or not args.proof_target or not args.expect_version:
            raise ValueError('proof requires explicit --tool, --proof-target and --expect-version')
        target = str(args.proof_target.resolve())
        if args.kind == 'gobra':
            if not args.jar or not args.solver:
                raise ValueError('Gobra requires exact --jar and --solver')
            prefix = [args.tool, '-Xmx1g', '-Xss128m', '-jar', str(args.jar.resolve())]
            return [*prefix, '--version'], [('proof', [*prefix, '-i', target, '--overflow', '--logLevel', 'DEBUG', '--z3Exe', str(args.solver.resolve())])]
        if args.kind == 'kani':
            if not args.harness:
                raise ValueError('Kani requires one exact --harness')
            return [args.tool, '--version'], [('proof', [args.tool, target, '--harness', args.harness, '-Z', 'concrete-playback', '--concrete-playback', 'print'])]
        return [args.tool, '--version'], [('proof', [args.tool, target])]
    if args.kind == "workflow-tests":
        return [sys.executable, "--version"], [("workflow-tests", [sys.executable, str(Path(__file__).resolve()), "_workflow-tests"])]
    if args.kind == "openspec":
        if not args.change or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.change):
            raise ValueError("--change must name one flat OpenSpec change")
        tool = args.tool or "openspec"
        commands = [("specs", [tool, "validate", args.change, "--type", "change", "--strict", "--json", "--no-interactive"])]
        if args.require_project_guidance:
            for surface in ("proposal", "specs", "design", "tasks", "apply", "archive"):
                commands.append((f"guidance:{surface}", [tool, "instructions", surface, "--change", args.change, "--json"]))
        if args.require_tasks_complete and not args.require_project_guidance:
            commands.append(("tasks", [tool, "instructions", "apply", "--change", args.change, "--json"]))
        return [tool, "--version"], commands
    if args.kind in {"go-test", "go-lint"}:
        if not args.package or any(not p.strip() or p.startswith("-") or any(c.isspace() for c in p) for p in args.package):
            raise ValueError("explicit nonempty --package arguments are required")
        tool = args.tool or ("go" if args.kind == "go-test" else "golangci-lint")
        if args.kind == "go-lint":
            return [tool, "version"], [("lint", [tool, "run", "--timeout", f"{args.timeout}s", *args.package])]
        if not args.test or not args.test.startswith("^") or not args.test.endswith("$"):
            raise ValueError("--test must be an anchored Go test selector")
        if "/" in args.test:
            raise ValueError("slash-containing Go subtest selectors are unsupported: parent success cannot prove exact leaf selection; use an inspected native command")
        command = [tool, "test", "-json", "-count=1", "-timeout", f"{args.timeout}s", "-run", args.test]
        if args.race:
            command.append("-race")
        return [tool, "version"], [("packages", [tool, "list", "-f", "{{.ImportPath}}", *args.package]), ("tests", [*command, *args.package])]
    tool = args.tool or "cargo"
    manifest = args.manifest or "Cargo.toml"
    if args.kind == "cargo-fmt":
        command = [tool, "fmt", "--manifest-path", manifest, "--all", "--", "--check"]
    else:
        command = [tool, "clippy", "--offline", "--locked", "--manifest-path", manifest, "--all-targets", "--", "-D", "warnings"]
    component = "fmt" if args.kind == "cargo-fmt" else "clippy"
    return [tool, component, "--version"], [(args.kind, command)]


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("kind", choices=["workflow-tests", "openspec", "go-test", "go-lint", "cargo-fmt", "cargo-clippy", "kani", "verus", "gobra"])
    result.add_argument("--cwd", type=Path, required=True)
    result.add_argument("--scope", action="append", required=True, help="affected relative path; metadata, not a second task list")
    output = result.add_mutually_exclusive_group(required=True)
    output.add_argument("--output", type=Path, help="new result file; an existing file is never overwritten")
    output.add_argument("--output-dir", type=Path, help="create a unique run directory here")
    result.add_argument("--timeout", type=float, default=120)
    result.add_argument("--tool", help="existing executable; never installed by this runner")
    result.add_argument("--change")
    result.add_argument("--require-tasks-complete", action="store_true", help="pre-archive checkbox gate; never archives or accepts the implementation")
    result.add_argument("--require-project-guidance", action="store_true", help="verify context, all four artifact rules and both operation guidance surfaces are delivered")
    result.add_argument("--package", action="append")
    result.add_argument("--test", help="anchored top-level Go test selector; slash-containing exact-leaf subtest selectors are unsupported")
    result.add_argument("--race", action="store_true")
    result.add_argument("--manifest")
    result.add_argument("--proof-target", type=Path, help="exact generated source; cwd-relative, with consumer correspondence evidence")
    result.add_argument("--harness")
    result.add_argument("--expect-version", help="selected version text required in native output")
    result.add_argument("--jar", type=Path)
    result.add_argument("--solver", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    cwd = args.cwd.resolve()
    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        args.output = Path(tempfile.mkdtemp(prefix=f"{args.kind}-", dir=args.output_dir)) / "result.json"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with args.output.open("x", encoding="utf-8"):
            pass
    except FileExistsError:
        print(f"refusing to overwrite existing evidence: {args.output}", file=sys.stderr)
        return 2
    report = {"schema_version": 1, "kind": args.kind, "cwd": str(cwd), "scope": args.scope,
              "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "timeout_seconds": args.timeout if math.isfinite(args.timeout) else str(args.timeout),
              "status": "invalid_configuration", "claim": "selected check only; not overall DONE", "steps": []}
    env = os.environ.copy()
    env.update(OPENSPEC_TELEMETRY="0", OPENSPEC_NO_UPDATE_CHECK="1", DO_NOT_TRACK="1",
               GOWORK="off", GOTOOLCHAIN="auto", GOFLAGS="-mod=readonly", GOPROXY="off", GONOPROXY="none",
               CARGO_NET_OFFLINE="true", RUSTUP_AUTO_INSTALL="0")
    try:
        if not cwd.is_dir() or not math.isfinite(args.timeout) or args.timeout <= 0:
            raise ValueError("existing --cwd and finite positive --timeout required")
        if any(not scope.strip() or Path(scope).is_absolute() or ".." in Path(scope).parts for scope in args.scope):
            raise ValueError("--scope must contain nonempty repository-relative paths")
        if args.kind in {'kani', 'verus', 'gobra'}:
            if not args.proof_target:
                raise ValueError('missing proof target')
            args.proof_target = (cwd / args.proof_target).resolve()
            if not args.proof_target.is_file():
                raise ValueError('proof target missing')
            report['proof_source_sha256'] = hashlib.sha256(args.proof_target.read_bytes()).hexdigest()
            report['proof_artifact_sha256'] = {}
            for path in [Path(args.tool)] if args.kind != 'gobra' and args.tool else [args.jar, args.solver]:
                if path and path.is_file():
                    report['proof_artifact_sha256'][str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
        version_command, commands = command_plan(args)
        version = run_process(version_command, cwd, env, min(args.timeout, 15), args.output.with_name(f"{args.output.name}.version"))
        report["tool"] = {"command": version_command, "version": version["stdout"].strip(), "exit_code": version["exit_code"]}
        report["steps"].append(version)
        if version["status"] != "exited" or version["exit_code"] != 0:
            report["status"] = version["status"] if version["status"] != "exited" else "tool_version_failed"
        elif args.kind in {'kani', 'verus', 'gobra'} and args.expect_version not in version['stdout'] + version['stderr']:
            report['status'] = 'unsupported_tool_version'
        elif args.kind == "openspec" and version["stdout"].strip() != OPENSPEC_VERSION:
            report["status"] = "unsupported_tool_version"
        elif args.kind == "go-lint" and not re.search(rf"\b{re.escape(GOLANGCI_VERSION)}\b", version["stdout"]):
            report["status"] = "unsupported_tool_version"
        else:
            expected_packages: set[str] | None = None
            for index, (label, command) in enumerate(commands):
                process = run_process(command, cwd, env, args.timeout, args.output.with_name(f"{args.output.name}.{index}"))
                process["label"] = label
                report["steps"].append(process)
                if process["status"] != "exited":
                    status, details = process["status"], {}
                elif process["exit_code"] != 0:
                    status, details = "failed", {}
                    if args.kind in {'kani', 'verus', 'gobra'}:
                        details['failure_class'] = proof_failure(args.kind, process['stdout'] + process['stderr'])
                        details['limit'] = 'native diagnostic category; inspect contract, harness and implementation before assigning a product defect'
                elif args.kind in {'kani', 'verus', 'gobra'}:
                    if hashlib.sha256(args.proof_target.read_bytes()).hexdigest() != report['proof_source_sha256']:
                        status, details = 'stale_source', {}
                    elif process.get('stdout_truncated') or process.get('stderr_truncated'):
                        status, details = 'incomplete', {'reason': 'summary exceeds parser capture; inspect full native logs'}
                    else:
                        status, details = proof_result(args.kind, process['stdout'] + process['stderr'])
                elif args.kind == "openspec":
                    if label.startswith("guidance:"):
                        status, details = guidance_result(process["stdout"], cwd, args.change, label.split(":")[1])
                        if status == "passed" and label == "guidance:apply" and args.require_tasks_complete:
                            status, details = task_result(process["stdout"], cwd, args.change)
                    else:
                        status, details = (task_result if label == "tasks" else openspec_result)(process["stdout"], cwd, args.change)
                elif args.kind == "go-test":
                    if label == "packages":
                        expected_packages = set(process["stdout"].splitlines())
                        invalid = any(not name or any(c.isspace() for c in name) for name in expected_packages)
                        status = "invalid_output" if invalid or process.get("stdout_truncated") else "passed" if expected_packages else "no_selection"
                        details = {"expected_packages": sorted(expected_packages)}
                    elif process.get("stdout_artifact"):
                        with Path(process["stdout_artifact"]).open(encoding="utf-8", errors="replace") as stream:
                            status, details = go_result(stream, expected_packages)
                    else:
                        status, details = go_result(process["stdout"], expected_packages)
                elif args.kind == "workflow-tests":
                    try:
                        details = json.loads(process["stdout"])
                        status = "passed" if details["status"] == "passed" and details["tests"] > 0 and details["skipped"] == 0 else "incomplete"
                    except (ValueError, TypeError, KeyError):
                        status, details = "invalid_output", {}
                else:
                    status, details = "passed", {"claim": "static command exit only; no test execution claimed"}
                process["result"], process["observed"] = status, details
                report["status"] = status
                if status != "passed":
                    break
    except (ValueError, OSError) as error:
        report["reason"] = str(error)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for index, step in enumerate(report["steps"]):
        for stream in ("stdout", "stderr"):
            preview = step.pop(stream)
            if f"{stream}_artifact" not in step:
                artifact = args.output.with_name(f"{args.output.name}.{index}.{stream}.log")
                artifact.write_text(preview, encoding="utf-8")
                step[f"{stream}_artifact"] = str(artifact)
    report["artifact"] = str(args.output.resolve())
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{args.kind}: {report['status']} ({args.output})")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(workflow_tests() if sys.argv[1:] == ["_workflow-tests"] else main())
