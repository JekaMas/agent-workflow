#!/usr/bin/env python3
"""Validate, query and execute a change-owned requirement evidence DAG."""

from __future__ import annotations

import argparse
from collections import defaultdict
import datetime as dt
import fnmatch
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any


SCHEMA_VERSION = 1
PREVIEW_BYTES = 64 * 1024
REQUIREMENT = re.compile(r"^### Requirement: (.+?)\s*$")
SCENARIO = re.compile(r"^#### Scenario: (.+?)\s*$")
ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class MatrixError(ValueError):
    """A deterministic manifest/specification contract failure."""


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def normalize_block(lines: list[str]) -> str:
    return "\n".join(line.rstrip() for line in lines).strip() + "\n"


def parse_delta_specs(change_root: Path) -> dict[tuple[str, str], dict[str, Any]]:
    specs_root = change_root / "specs"
    if not specs_root.is_dir():
        raise MatrixError("change has no delta specs directory")
    parsed: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted(specs_root.glob("**/spec.md")):
        capability = path.parent.relative_to(specs_root).as_posix()
        lines = path.read_text(encoding="utf-8").splitlines()
        starts = [index for index, line in enumerate(lines) if REQUIREMENT.match(line)]
        for offset, start in enumerate(starts):
            end = starts[offset + 1] if offset + 1 < len(starts) else len(lines)
            for index in range(start + 1, end):
                if lines[index].startswith("## ") and not lines[index].startswith("### "):
                    end = index
                    break
            title = REQUIREMENT.match(lines[start]).group(1).strip()  # type: ignore[union-attr]
            key = (capability, title)
            if key in parsed:
                raise MatrixError(f"duplicate spec requirement: {capability}::{title}")
            block = normalize_block(lines[start:end])
            scenarios = [
                match.group(1).strip()
                for line in lines[start:end]
                if (match := SCENARIO.match(line))
            ]
            if not scenarios:
                raise MatrixError(f"requirement has no scenarios: {capability}::{title}")
            parsed[key] = {
                "capability": capability,
                "title": title,
                "scenarios": scenarios,
                "fingerprint": sha256_bytes((capability + "\n" + block).encode()),
                "path": path.relative_to(change_root.parent.parent.parent).as_posix(),
            }
    if not parsed:
        raise MatrixError("change delta specs contain no requirements")
    return parsed


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise MatrixError(f"cannot read verification manifest: {error}") from error
    if not isinstance(value, dict):
        raise MatrixError("verification manifest root must be an object")
    return value


def required_text(row: dict[str, Any], field: str, owner: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise MatrixError(f"{owner}.{field} must be nonempty text")
    return value.strip()


def required_list(row: dict[str, Any], field: str, owner: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list) or not value:
        raise MatrixError(f"{owner}.{field} must be a nonempty list")
    return value


def unique_text_list(row: dict[str, Any], field: str, owner: str) -> list[str]:
    values = required_list(row, field, owner)
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise MatrixError(f"{owner}.{field} must contain nonempty text")
    normalized = [value.strip() for value in values]
    if len(set(normalized)) != len(normalized):
        raise MatrixError(f"{owner}.{field} contains duplicate edges")
    return normalized


def unique_rows(rows: Any, kind: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list) or not rows:
        raise MatrixError(f"manifest {kind} must be a nonempty list")
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise MatrixError(f"{kind}[{index}] must be an object")
        identity = required_text(row, "id", f"{kind}[{index}]")
        if identity in result:
            raise MatrixError(f"duplicate {kind} id: {identity}")
        result[identity] = row
    return result


def safe_relative(raw: str, owner: str) -> Path:
    path = Path(raw)
    if path.is_absolute() or ".." in path.parts:
        raise MatrixError(f"{owner} must be repository-relative")
    return path


def command_key(row: dict[str, Any]) -> bytes:
    fields = {
        "runner": row.get("runner"),
        "argv": row.get("argv"),
        "cwd": row.get("cwd", "."),
        "env": row.get("env", {}),
        "timeout_seconds": row.get("timeout_seconds", 120),
        "authority": row.get("authority", "local"),
        "expected_markers": row.get("expected_markers", []),
    }
    return canonical_json(fields)


class EvidenceGraph:
    def __init__(self, root: Path, change: str, manifest_path: Path | None = None):
        self.root = root.resolve()
        self.change = change
        self.change_root = self.root / "openspec" / "changes" / change
        self.manifest_path = manifest_path or self.change_root / "verification.json"
        self.specs = parse_delta_specs(self.change_root)
        self.raw = load_json(self.manifest_path)
        self.requirements = unique_rows(self.raw.get("requirements"), "requirements")
        self.properties = unique_rows(self.raw.get("properties"), "properties")
        self.cases = unique_rows(self.raw.get("cases"), "cases")
        self.commands = unique_rows(self.raw.get("commands"), "commands")
        self.by_requirement: dict[str, set[str]] = defaultdict(set)
        self.by_scenario: dict[str, set[str]] = defaultdict(set)
        self.by_owner: dict[str, set[str]] = defaultdict(set)
        self.by_case_command: dict[str, set[str]] = defaultdict(set)
        self.by_test: dict[str, set[str]] = defaultdict(set)
        self.validate()

    def validate(self) -> None:
        if self.raw.get("schema_version") != SCHEMA_VERSION:
            raise MatrixError(f"schema_version must be {SCHEMA_VERSION}")
        if self.raw.get("change") != self.change:
            raise MatrixError("manifest change does not match selected change")

        mapped_specs: set[tuple[str, str]] = set()
        requirement_scenarios: dict[str, set[str]] = {}
        for identity, row in self.requirements.items():
            capability = required_text(row, "capability", f"requirement {identity}")
            title = required_text(row, "title", f"requirement {identity}")
            key = (capability, title)
            if key not in self.specs:
                raise MatrixError(f"requirement {identity} does not match a delta spec point")
            if key in mapped_specs:
                raise MatrixError(f"delta spec point mapped twice: {capability}::{title}")
            mapped_specs.add(key)
            expected = self.specs[key]
            if row.get("fingerprint") != expected["fingerprint"]:
                raise MatrixError(f"stale specification fingerprint: {identity}")
            requirement_scenarios[identity] = set(expected["scenarios"])
        missing = sorted(set(self.specs) - mapped_specs)
        if missing:
            raise MatrixError("unmapped delta requirements: " + ", ".join(f"{c}::{t}" for c, t in missing))

        scenario_coverage: dict[str, set[str]] = defaultdict(set)
        for identity, row in self.properties.items():
            requirement_id = required_text(row, "requirement_id", f"property {identity}")
            if requirement_id not in self.requirements:
                raise MatrixError(f"property {identity} has unknown requirement: {requirement_id}")
            required_text(row, "statement", f"property {identity}")
            owner = required_text(row, "owner", f"property {identity}")
            required_text(row, "oracle", f"property {identity}")
            scenarios = unique_text_list(row, "scenarios", f"property {identity}")
            for scenario in scenarios:
                if not isinstance(scenario, str) or scenario not in requirement_scenarios[requirement_id]:
                    raise MatrixError(f"property {identity} has unknown scenario: {scenario!r}")
                scenario_coverage[requirement_id].add(scenario)
                self.by_scenario[f"{requirement_id}::{scenario}"].add(identity)
            globs = unique_text_list(row, "source_globs", f"property {identity}")
            for pattern in globs:
                if not isinstance(pattern, str) or not pattern.strip():
                    raise MatrixError(f"property {identity} has invalid source glob")
                safe_relative(pattern, f"property {identity} source glob")
            self.by_requirement[requirement_id].add(identity)
            self.by_owner[owner].add(identity)
        for requirement_id, scenarios in requirement_scenarios.items():
            missing_scenarios = sorted(scenarios - scenario_coverage[requirement_id])
            if missing_scenarios:
                raise MatrixError(
                    f"requirement {requirement_id} has uncovered scenarios: {', '.join(missing_scenarios)}"
                )

        seen_case_key: set[tuple[str, ...]] = set()
        cases_by_property: dict[str, list[dict[str, Any]]] = defaultdict(list)
        scenario_case_polarities: dict[tuple[str, str], set[str]] = defaultdict(set)
        tests_to_properties: dict[str, set[str]] = defaultdict(set)
        for identity, row in self.cases.items():
            property_id = required_text(row, "property_id", f"case {identity}")
            if property_id not in self.properties:
                raise MatrixError(f"case {identity} has unknown property: {property_id}")
            polarity = row.get("polarity")
            if polarity not in {"positive", "negative"}:
                raise MatrixError(f"case {identity} polarity must be positive or negative")
            observable = required_text(row, "observable", f"case {identity}")
            case_scenarios = unique_text_list(row, "scenarios", f"case {identity}")
            property_scenarios = set(self.properties[property_id]["scenarios"])
            for scenario in case_scenarios:
                if not isinstance(scenario, str) or scenario not in property_scenarios:
                    raise MatrixError(f"case {identity} has unknown property scenario: {scenario!r}")
                scenario_case_polarities[(property_id, scenario)].add(polarity)
            test_id = required_text(row, "test_id", f"case {identity}")
            command_id = required_text(row, "command_id", f"case {identity}")
            if command_id not in self.commands:
                raise MatrixError(f"case {identity} has unknown command: {command_id}")
            state = row.get("state")
            if state not in {"implemented", "planned", "blocked"}:
                raise MatrixError(f"case {identity} state must be implemented, planned or blocked")
            source_path = safe_relative(
                required_text(row, "source_path", f"case {identity}"),
                f"case {identity} source path",
            )
            source_sha256 = row.get("source_sha256")
            if state == "implemented":
                if not isinstance(source_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha256):
                    raise MatrixError(f"implemented case {identity} requires a SHA-256 source fingerprint")
                absolute_source = self.root / source_path
                if not absolute_source.is_file():
                    raise MatrixError(f"implemented case {identity} source is unavailable: {source_path}")
                if sha256_bytes(absolute_source.read_bytes()) != source_sha256:
                    raise MatrixError(f"stale test source fingerprint: {identity}")
            elif source_sha256 is not None and (
                not isinstance(source_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha256)
            ):
                raise MatrixError(f"case {identity} source_sha256 must be a SHA-256 fingerprint")
            substitution = row.get("substitution")
            if not isinstance(substitution, dict) or substitution.get("classification") not in {
                "NO_TEST_DOUBLE", "APPROVED_TEST_DOUBLE", "EXTERNAL_BOUNDARY", "UNDECIDED"
            }:
                raise MatrixError(f"case {identity} must disclose its substitution classification")
            if state == "implemented" and substitution.get("classification") == "UNDECIDED":
                raise MatrixError(f"implemented case {identity} cannot have an undecided substitution boundary")
            key = (property_id, polarity, observable, test_id, *sorted(set(case_scenarios)))
            if key in seen_case_key:
                raise MatrixError(f"duplicate case edge for property {property_id}: {identity}")
            seen_case_key.add(key)
            cases_by_property[property_id].append(row)
            tests_to_properties[test_id].add(property_id)
            self.by_test[test_id].add(identity)
            self.by_case_command[command_id].add(identity)
        for property_id in self.properties:
            polarities = {row["polarity"] for row in cases_by_property[property_id]}
            if polarities != {"positive", "negative"}:
                raise MatrixError(f"property {property_id} requires positive and negative cases")
            for scenario in self.properties[property_id]["scenarios"]:
                if scenario_case_polarities[(property_id, scenario)] != {"positive", "negative"}:
                    raise MatrixError(
                        f"property {property_id} scenario {scenario!r} requires positive and negative cases"
                    )
        for test_id, property_ids in tests_to_properties.items():
            if len(property_ids) > 1:
                for row in self.cases.values():
                    if row["test_id"] == test_id and not str(row.get("distinct_reason", "")).strip():
                        raise MatrixError(
                            f"shared test {test_id} requires distinct_reason on every property edge"
                        )

        seen_commands: dict[bytes, str] = {}
        for identity, row in self.commands.items():
            runner = row.get("runner")
            if runner not in {"go-test-json", "cargo-test", "command"}:
                raise MatrixError(f"command {identity} has unsupported runner")
            argv = required_list(row, "argv", f"command {identity}")
            if any(not isinstance(arg, str) or not arg for arg in argv):
                raise MatrixError(f"command {identity} argv must contain nonempty strings")
            safe_relative(str(row.get("cwd", ".")), f"command {identity} cwd")
            env = row.get("env", {})
            if not isinstance(env, dict) or any(
                not isinstance(key, str) or not ENV_NAME.match(key) or not isinstance(value, str)
                for key, value in env.items()
            ):
                raise MatrixError(f"command {identity} env must contain text names and values")
            timeout = row.get("timeout_seconds", 120)
            if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
                raise MatrixError(f"command {identity} timeout must be finite and positive")
            if row.get("authority", "local") not in {"local", "protected"}:
                raise MatrixError(f"command {identity} authority must be local or protected")
            if runner == "go-test-json" and (len(argv) < 2 or argv[1] != "test"):
                raise MatrixError(f"command {identity} go runner must invoke go test")
            if runner == "cargo-test" and (len(argv) < 2 or argv[1] != "test"):
                raise MatrixError(f"command {identity} cargo runner must invoke cargo test")
            if runner == "command":
                markers = unique_text_list(row, "expected_markers", f"command {identity}")
                if any(not isinstance(marker, str) or not marker for marker in markers):
                    raise MatrixError(f"command {identity} markers must be nonempty text")
            key = command_key(row)
            if key in seen_commands:
                raise MatrixError(
                    f"duplicate command definition: {identity} must reuse {seen_commands[key]}"
                )
            seen_commands[key] = identity
            if identity not in self.by_case_command:
                raise MatrixError(f"unreferenced command: {identity}")

        for identity, row in self.cases.items():
            command = self.commands[row["command_id"]]
            if command["runner"] == "command" and row["test_id"] not in command["expected_markers"]:
                raise MatrixError(
                    f"case {identity} test_id is not an expected marker of {row['command_id']}"
                )

    def select(
        self,
        *,
        requirement_ids: list[str] | None = None,
        property_ids: list[str] | None = None,
        scenarios: list[str] | None = None,
        owners: list[str] | None = None,
        case_ids: list[str] | None = None,
        command_ids: list[str] | None = None,
        test_ids: list[str] | None = None,
        changed_paths: list[str] | None = None,
        all_cases: bool = False,
    ) -> dict[str, list[str]]:
        selected_properties: set[str] = set()
        if all_cases:
            selected_properties.update(self.properties)
        for identity in requirement_ids or []:
            if identity not in self.requirements:
                raise MatrixError(f"unknown requirement selector: {identity}")
            selected_properties.update(self.by_requirement[identity])
        for identity in property_ids or []:
            if identity not in self.properties:
                raise MatrixError(f"unknown property selector: {identity}")
            selected_properties.add(identity)
        for selector in scenarios or []:
            if selector not in self.by_scenario:
                raise MatrixError(f"unknown scenario selector: {selector}")
            selected_properties.update(self.by_scenario[selector])
        for owner in owners or []:
            if owner not in self.by_owner:
                raise MatrixError(f"unknown owner selector: {owner}")
            selected_properties.update(self.by_owner[owner])
        for identity in case_ids or []:
            if identity not in self.cases:
                raise MatrixError(f"unknown case selector: {identity}")
            selected_properties.add(self.cases[identity]["property_id"])
        for identity in command_ids or []:
            if identity not in self.commands:
                raise MatrixError(f"unknown command selector: {identity}")
            selected_properties.update(
                self.cases[case_id]["property_id"] for case_id in self.by_case_command[identity]
            )
        for identity in test_ids or []:
            if identity not in self.by_test:
                raise MatrixError(f"unknown test selector: {identity}")
            selected_properties.update(
                self.cases[case_id]["property_id"] for case_id in self.by_test[identity]
            )
        for raw_path in changed_paths or []:
            path = safe_relative(raw_path, "changed path").as_posix()
            for identity, row in self.properties.items():
                if any(fnmatch.fnmatch(path, pattern) for pattern in row["source_globs"]):
                    selected_properties.add(identity)
        if not selected_properties:
            raise MatrixError("selection resolved no properties")
        selected_cases = sorted(
            identity for identity, row in self.cases.items() if row["property_id"] in selected_properties
        )
        command_ids = sorted({self.cases[identity]["command_id"] for identity in selected_cases})
        requirement_set = sorted({self.properties[identity]["requirement_id"] for identity in selected_properties})
        return {
            "requirements": requirement_set,
            "properties": sorted(selected_properties),
            "cases": selected_cases,
            "commands": command_ids,
        }

    def summary(self, selection: dict[str, list[str]] | None = None) -> dict[str, Any]:
        selected = selection or self.select(all_cases=True)
        try:
            manifest = self.manifest_path.relative_to(self.root).as_posix()
        except ValueError:
            manifest = str(self.manifest_path)
        return {
            "change": self.change,
            "manifest": manifest,
            "manifest_sha256": sha256_bytes(self.manifest_path.read_bytes()),
            "specifications": {
                identity: self.requirements[identity]["fingerprint"]
                for identity in selected["requirements"]
            },
            "selection": selected,
        }

    def describe(self, selection: dict[str, list[str]]) -> dict[str, Any]:
        return {
            **self.summary(selection),
            "nodes": {
                "requirements": {identity: self.requirements[identity] for identity in selection["requirements"]},
                "properties": {identity: self.properties[identity] for identity in selection["properties"]},
                "cases": {
                    identity: {**self.cases[identity], "latest_observed_status": "not_loaded"}
                    for identity in selection["cases"]
                },
                "commands": {identity: self.commands[identity] for identity in selection["commands"]},
            },
        }


def parse_go_events(raw: str) -> dict[str, str]:
    observed: dict[str, str] = {}
    priority = {"pass": 0, "skip": 1, "fail": 2}
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        package, test, action = event.get("Package"), event.get("Test"), event.get("Action")
        if isinstance(package, str) and isinstance(test, str) and action in priority:
            identity = f"{package}::{test}"
            observed[identity] = max(observed.get(identity, "pass"), action, key=priority.get)
    return observed


def parse_cargo_events(raw: str) -> dict[str, str]:
    observed: dict[str, str] = {}
    status = {"ok": "pass", "FAILED": "fail", "ignored": "skip"}
    for line in raw.splitlines():
        match = re.match(r"^test (.+?) \.\.\. (ok|FAILED|ignored)$", line.strip())
        if match:
            observed[match.group(1)] = status[match.group(2)]
    return observed


def git_state(root: Path) -> dict[str, Any]:
    def command(*args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=10, check=False
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    return {"head": command("rev-parse", "HEAD"), "dirty": bool(command("status", "--porcelain"))}


def run_selection(
    graph: EvidenceGraph,
    selection: dict[str, list[str]],
    output: Path,
    *,
    allow_protected: bool = False,
) -> dict[str, Any]:
    if output.exists():
        raise MatrixError(f"refusing to overwrite evidence: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        **graph.summary(selection),
        "git": git_state(graph.root),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "passed",
        "commands": [],
        "cases": {},
    }
    selected_by_command: dict[str, list[str]] = defaultdict(list)
    for case_id in selection["cases"]:
        case = graph.cases[case_id]
        if case["state"] != "implemented":
            report["cases"][case_id] = {
                "status": case["state"],
                "test_id": case["test_id"],
                "source_path": case["source_path"],
                "source_sha256": case.get("source_sha256"),
            }
            report["status"] = "incomplete"
            continue
        command = graph.commands[case["command_id"]]
        if command.get("authority", "local") == "protected" and not allow_protected:
            report["cases"][case_id] = {
                "status": "authority_blocked",
                "test_id": case["test_id"],
                "source_path": case["source_path"],
                "source_sha256": case.get("source_sha256"),
            }
            report["status"] = "incomplete"
            continue
        selected_by_command[case["command_id"]].append(case_id)

    base_env = os.environ.copy()
    base_env.update(
        OPENSPEC_TELEMETRY="0",
        OPENSPEC_NO_UPDATE_CHECK="1",
        DO_NOT_TRACK="1",
        GOWORK="off",
        GOTOOLCHAIN="auto",
        GOFLAGS="-mod=readonly",
        GOPROXY="off",
        GONOPROXY="none",
        CARGO_NET_OFFLINE="true",
        RUSTUP_AUTO_INSTALL="0",
    )
    for command_id in sorted(selected_by_command):
        row = graph.commands[command_id]
        argv = list(row["argv"])
        if row["runner"] == "go-test-json" and "-json" not in argv:
            argv.insert(2, "-json")
        cwd = (graph.root / row.get("cwd", ".")).resolve()
        if not cwd.is_relative_to(graph.root) or not cwd.is_dir():
            raise MatrixError(f"command {command_id} cwd is unavailable")
        env = {**base_env, **row.get("env", {})}
        started = time.monotonic()
        try:
            process = subprocess.run(
                argv,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=float(row.get("timeout_seconds", 120)),
                check=False,
            )
            process_status = "exited"
            exit_code = process.returncode
            stdout, stderr = process.stdout, process.stderr
        except subprocess.TimeoutExpired as error:
            process_status = "timed_out"
            exit_code = None
            stdout = (error.stdout or b"").decode(errors="replace") if isinstance(error.stdout, bytes) else error.stdout or ""
            stderr = (error.stderr or b"").decode(errors="replace") if isinstance(error.stderr, bytes) else error.stderr or ""
        except OSError as error:
            process_status = "unavailable"
            exit_code = None
            stdout, stderr = "", str(error)
        combined = stdout + "\n" + stderr
        if row["runner"] == "go-test-json":
            observed = parse_go_events(stdout)
        elif row["runner"] == "cargo-test":
            observed = parse_cargo_events(combined)
        else:
            observed = {
                marker: "pass" for marker in row.get("expected_markers", []) if marker in combined
            }
        command_result = {
            "id": command_id,
            "argv": argv,
            "cwd": str(cwd),
            "status": process_status,
            "exit_code": exit_code,
            "duration_seconds": time.monotonic() - started,
            "observed_tests": observed,
            "stdout": stdout[:PREVIEW_BYTES],
            "stderr": stderr[:PREVIEW_BYTES],
            "stdout_truncated": len(stdout.encode()) > PREVIEW_BYTES,
            "stderr_truncated": len(stderr.encode()) > PREVIEW_BYTES,
        }
        report["commands"].append(command_result)
        for case_id in selected_by_command[command_id]:
            expected = graph.cases[case_id]["test_id"]
            observed_status = observed.get(expected, "missing")
            if process_status != "exited":
                status = process_status
            elif exit_code != 0:
                status = "command_failed"
            elif observed_status == "pass":
                status = "passed"
            else:
                status = observed_status
            case = graph.cases[case_id]
            report["cases"][case_id] = {
                "status": status,
                "test_id": expected,
                "property_id": case["property_id"],
                "polarity": case["polarity"],
                "scenarios": case["scenarios"],
                "observable": case["observable"],
                "source_path": case["source_path"],
                "source_sha256": case.get("source_sha256"),
            }
            if status != "passed":
                next_status = "failed" if status in {"fail", "command_failed"} else "incomplete"
                if report["status"] != "failed":
                    report["status"] = next_status
    report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def split_values(values: list[str] | None) -> list[str]:
    return [item.strip() for value in values or [] for item in value.split(",") if item.strip()]


def add_selection(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--requirements", action="append")
    parser.add_argument("--properties", action="append")
    parser.add_argument("--scenarios", action="append")
    parser.add_argument("--owners", action="append")
    parser.add_argument("--cases", action="append")
    parser.add_argument("--commands", action="append")
    parser.add_argument("--tests", action="append")
    parser.add_argument("--changed-paths", action="append")
    parser.add_argument("--all", action="store_true")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=Path.cwd())
    result.add_argument("--change", required=True)
    result.add_argument("--manifest", type=Path)
    subparsers = result.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("fingerprints")
    subparsers.add_parser("validate")
    query = subparsers.add_parser("query")
    add_selection(query)
    run = subparsers.add_parser("run")
    add_selection(run)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--allow-protected", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    change_root = root / "openspec" / "changes" / args.change
    try:
        if args.operation == "fingerprints":
            specs = parse_delta_specs(change_root)
            print(json.dumps({f"{capability}::{title}": row for (capability, title), row in specs.items()}, indent=2, sort_keys=True))
            return 0
        manifest = args.manifest
        if manifest is not None and not manifest.is_absolute():
            manifest = root / manifest
        graph = EvidenceGraph(root, args.change, manifest)
        if args.operation == "validate":
            print(json.dumps({"status": "passed", **graph.summary()}, indent=2, sort_keys=True))
            return 0
        selection = graph.select(
            requirement_ids=split_values(args.requirements),
            property_ids=split_values(args.properties),
            scenarios=split_values(args.scenarios),
            owners=split_values(args.owners),
            case_ids=split_values(args.cases),
            command_ids=split_values(args.commands),
            test_ids=split_values(args.tests),
            changed_paths=split_values(args.changed_paths),
            all_cases=args.all,
        )
        if args.operation == "query":
            print(json.dumps({"status": "passed", **graph.describe(selection)}, indent=2, sort_keys=True))
            return 0
        output = args.output if args.output.is_absolute() else root / args.output
        report = run_selection(graph, selection, output, allow_protected=args.allow_protected)
        print(json.dumps({"status": report["status"], "artifact": str(output.resolve())}, sort_keys=True))
        return 0 if report["status"] == "passed" else 1
    except MatrixError as error:
        print(json.dumps({"status": "invalid", "reason": str(error)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
