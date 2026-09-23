#!/usr/bin/env python3
"""Validate, query and execute a change-owned requirement evidence DAG."""

from __future__ import annotations

import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

try:
    from scripts.process_runner import run_process
except ModuleNotFoundError:  # Direct `python scripts/requirement_tests.py` route.
    from process_runner import run_process


SCHEMA_VERSION = 2
REQUIREMENT = re.compile(r"^### Requirement: (.+?)\s*$")
SCENARIO = re.compile(r"^#### Scenario: (.+?)\s*$")
DELTA_SECTION = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$", re.IGNORECASE)
ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
POLICY_ENV = {
    "PATH", "GOWORK", "GOTOOLCHAIN", "GOFLAGS", "GOPROXY", "GONOPROXY",
    "CARGO_NET_OFFLINE", "RUSTUP_AUTO_INSTALL",
}
RUNNERS = {"go-test-json", "cargo-test", "python-unittest", "node-test-tap", "command"}


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
        active_section: str | None = None
        fenced = False
        eligible: list[bool] = []
        for line in lines:
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                fenced = not fenced
                eligible.append(False)
                continue
            if not fenced:
                section = DELTA_SECTION.match(line)
                if section:
                    active_section = section.group(1).upper()
            eligible.append(not fenced and active_section in {"ADDED", "MODIFIED"})
        starts = [
            index for index, line in enumerate(lines)
            if eligible[index] and REQUIREMENT.match(line)
        ]
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
            scenario_starts = [index for index in range(start, end) if eligible[index] and SCENARIO.match(lines[index])]
            scenarios = [SCENARIO.match(lines[index]).group(1).strip() for index in scenario_starts]
            if not scenarios:
                raise MatrixError(f"requirement has no scenarios: {capability}::{title}")
            scenario_fingerprints: dict[str, str] = {}
            for scenario_offset, scenario_start in enumerate(scenario_starts):
                scenario_end = (
                    scenario_starts[scenario_offset + 1]
                    if scenario_offset + 1 < len(scenario_starts)
                    else end
                )
                scenario_title = SCENARIO.match(lines[scenario_start]).group(1).strip()
                scenario_block = normalize_block(lines[scenario_start:scenario_end])
                scenario_fingerprints[scenario_title] = sha256_bytes(
                    (capability + "\n" + title + "\n" + scenario_block).encode()
                )
            parsed[key] = {
                "capability": capability,
                "title": title,
                "scenarios": scenarios,
                "scenario_fingerprints": scenario_fingerprints,
                "fingerprint": sha256_bytes((capability + "\n" + block).encode()),
                "path": path.relative_to(change_root.parent.parent.parent).as_posix(),
            }
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
    if value != value.strip():
        raise MatrixError(f"{owner}.{field} must not contain surrounding whitespace")
    return value


def required_list(row: dict[str, Any], field: str, owner: str) -> list[Any]:
    value = row.get(field)
    if not isinstance(value, list) or not value:
        raise MatrixError(f"{owner}.{field} must be a nonempty list")
    return value


def unique_text_list(row: dict[str, Any], field: str, owner: str) -> list[str]:
    values = required_list(row, field, owner)
    if any(not isinstance(value, str) or not value.strip() for value in values):
        raise MatrixError(f"{owner}.{field} must contain nonempty text")
    if any(value != value.strip() for value in values):
        raise MatrixError(f"{owner}.{field} must not contain surrounding whitespace")
    normalized = list(values)
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


def normalized_argv(row: dict[str, Any]) -> list[str]:
    argv = list(row.get("argv", []))
    if row.get("runner") == "go-test-json" and len(argv) >= 2 and argv[0:2] == ["go", "test"]:
        argv = [arg for arg in argv if arg != "-json"]
        argv.insert(2, "-json")
    return argv


def command_key(row: dict[str, Any]) -> bytes:
    fields = {
        "argv": normalized_argv(row),
        "cwd": row.get("cwd", "."),
        "env": row.get("env", {}),
        "timeout_seconds": row.get("timeout_seconds", 120),
        "authority": row.get("authority", "local"),
    }
    return canonical_json(fields)


def path_glob_regex(pattern: str) -> re.Pattern[str]:
    """Compile repository-relative glob syntax where * never crosses '/'."""

    result = "^"
    index = 0
    while index < len(pattern):
        character = pattern[index]
        if character == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                index += 2
                if index < len(pattern) and pattern[index] == "/":
                    result += "(?:[^/]+/)*"
                    index += 1
                else:
                    result += ".*"
                continue
            result += "[^/]*"
        elif character == "?":
            result += "[^/]"
        elif character == "[":
            closing = pattern.find("]", index + 1)
            if closing == -1:
                result += r"\["
            else:
                content = pattern[index + 1:closing]
                if content.startswith("!"):
                    content = "^" + content[1:]
                result += "[" + content + "]"
                index = closing
        else:
            result += re.escape(character)
        index += 1
    return re.compile(result + "$")


def path_glob_matches(path: str, pattern: str) -> bool:
    return bool(path_glob_regex(pattern).fullmatch(path))


def source_owns_test(runner: str, test_id: str, source: str) -> bool:
    """Tie an implemented exact test identity to the file whose hash protects it."""

    if runner == "go-test-json" and "::" in test_id:
        name = test_id.rsplit("::", 1)[1].split("/", 1)[0]
        return bool(re.search(rf"(?m)^func\s+{re.escape(name)}\s*\(", source))
    if runner == "cargo-test":
        name = test_id.rsplit("::", 1)[-1]
        return bool(re.search(rf"(?m)^\s*(?:pub\s+)?fn\s+{re.escape(name)}\s*\(", source))
    if runner == "python-unittest" and test_id.startswith("unittest::"):
        name = test_id.rsplit(".", 1)[-1]
        return bool(re.search(rf"(?m)^\s*def\s+{re.escape(name)}\s*\(", source))
    if runner == "node-test-tap":
        return test_id.startswith("node::") and test_id.removeprefix("node::") in source
    return runner == "command"


class EvidenceGraph:
    def __init__(self, root: Path, change: str, manifest_path: Path | None = None):
        self.root = root.resolve()
        self.change = change
        self.change_root = self.root / "openspec" / "changes" / change
        self.manifest_path = (manifest_path or self.change_root / "verification.json").resolve()
        if not self.manifest_path.is_relative_to(self.change_root.resolve()):
            raise MatrixError("verification manifest must stay inside the selected change")
        self.specs = parse_delta_specs(self.change_root)
        self.raw = load_json(self.manifest_path)
        self.requirements = unique_rows(self.raw.get("requirements"), "requirements")
        self.properties = unique_rows(self.raw.get("properties"), "properties")
        self.cases = unique_rows(self.raw.get("cases"), "cases")
        self.commands = unique_rows(self.raw.get("commands"), "commands")
        self.by_requirement: dict[str, set[str]] = defaultdict(set)
        self.by_scenario: dict[str, set[str]] = defaultdict(set)
        self.by_scenario_cases: dict[str, set[str]] = defaultdict(set)
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
        scenario_tests_by_polarity: dict[tuple[str, str, str], set[str]] = defaultdict(set)
        tests_to_properties: dict[str, set[str]] = defaultdict(set)
        tests_to_scenarios: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for identity, row in self.cases.items():
            property_id = required_text(row, "property_id", f"case {identity}")
            if property_id not in self.properties:
                raise MatrixError(f"case {identity} has unknown property: {property_id}")
            polarity = row.get("polarity")
            if polarity not in {"positive", "negative"}:
                raise MatrixError(f"case {identity} polarity must be positive or negative")
            observable = required_text(row, "observable", f"case {identity}")
            scenario = required_text(row, "scenario", f"case {identity}")
            property_scenarios = set(self.properties[property_id]["scenarios"])
            if scenario not in property_scenarios:
                raise MatrixError(f"case {identity} has unknown property scenario: {scenario!r}")
            requirement_id = self.properties[property_id]["requirement_id"]
            requirement = self.requirements[requirement_id]
            spec = self.specs[(requirement["capability"], requirement["title"])]
            if row.get("scenario_fingerprint") != spec["scenario_fingerprints"][scenario]:
                raise MatrixError(f"stale scenario fingerprint: {identity}")
            scenario_case_polarities[(property_id, scenario)].add(polarity)
            self.by_scenario_cases[f"{requirement_id}::{scenario}"].add(identity)
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
            setup = required_text(row, "setup", f"case {identity}")
            red_expectation = required_text(row, "red_expectation", f"case {identity}")
            green_expectation = required_text(row, "green_expectation", f"case {identity}")
            generic_setup = f"Execute the exact {scenario} scenario at "
            if setup.startswith(generic_setup):
                raise MatrixError(f"case {identity} setup must name a concrete fixture or boundary")
            if red_expectation == f"The case fails if {scenario} violates: {observable}":
                raise MatrixError(f"case {identity} red_expectation is a templated observable restatement")
            if green_expectation == f"The case passes only when {observable}":
                raise MatrixError(f"case {identity} green_expectation is a templated observable restatement")
            invalidation_dependencies = unique_text_list(
                row, "invalidation_dependencies", f"case {identity}"
            )
            for dependency in invalidation_dependencies:
                safe_relative(dependency, f"case {identity} invalidation dependency")
            source_sha256 = row.get("source_sha256")
            if state == "implemented":
                if not isinstance(source_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", source_sha256):
                    raise MatrixError(f"implemented case {identity} requires a SHA-256 source fingerprint")
                absolute_source = self.root / source_path
                if not absolute_source.is_file():
                    raise MatrixError(f"implemented case {identity} source is unavailable: {source_path}")
                if sha256_bytes(absolute_source.read_bytes()) != source_sha256:
                    raise MatrixError(f"stale test source fingerprint: {identity}")
                runner = self.commands[command_id].get("runner")
                if runner in RUNNERS and not source_owns_test(
                    str(runner), test_id, absolute_source.read_text(encoding="utf-8")
                ):
                    raise MatrixError(
                        f"case {identity} source_path does not own exact test identity {test_id}"
                    )
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
            key = (property_id, scenario, polarity, observable, test_id)
            if key in seen_case_key:
                raise MatrixError(f"duplicate case edge for property {property_id}: {identity}")
            seen_case_key.add(key)
            cases_by_property[property_id].append(row)
            tests_to_properties[test_id].add(property_id)
            tests_to_scenarios[test_id].add((property_id, scenario))
            scenario_tests_by_polarity[(property_id, scenario, polarity)].add(test_id)
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
                positive_tests = scenario_tests_by_polarity[(property_id, scenario, "positive")]
                negative_tests = scenario_tests_by_polarity[(property_id, scenario, "negative")]
                if positive_tests & negative_tests:
                    raise MatrixError(
                        f"property {property_id} scenario {scenario!r} must use independent "
                        "positive and negative test identities"
                    )
        for test_id, property_ids in tests_to_properties.items():
            if len(property_ids) > 1:
                for row in self.cases.values():
                    if row["test_id"] == test_id and not str(row.get("distinct_reason", "")).strip():
                        raise MatrixError(
                            f"shared test {test_id} requires distinct_reason on every property edge"
                        )
        for test_id, scenario_edges in tests_to_scenarios.items():
            if len(scenario_edges) > 1:
                for row in self.cases.values():
                    if row["test_id"] != test_id:
                        continue
                    reason = str(row.get("distinct_reason", "")).strip()
                    if not reason or row["scenario"] not in reason:
                        raise MatrixError(
                            f"multi-scenario test {test_id} requires a scenario-specific "
                            f"distinct_reason naming {row['scenario']!r}"
                        )

        seen_commands: dict[bytes, str] = {}
        for identity, row in self.commands.items():
            runner = row.get("runner")
            if runner not in RUNNERS:
                raise MatrixError(f"command {identity} has unsupported runner")
            argv = required_list(row, "argv", f"command {identity}")
            if any(not isinstance(arg, str) or not arg for arg in argv):
                raise MatrixError(f"command {identity} argv must contain nonempty strings")
            cwd_path = safe_relative(str(row.get("cwd", ".")), f"command {identity} cwd")
            absolute_cwd = (self.root / cwd_path).resolve()
            if not absolute_cwd.is_relative_to(self.root) or not absolute_cwd.is_dir():
                raise MatrixError(f"command {identity} cwd is unavailable")
            env = row.get("env", {})
            if not isinstance(env, dict) or any(
                not isinstance(key, str) or not ENV_NAME.match(key) or not isinstance(value, str)
                for key, value in env.items()
            ):
                raise MatrixError(f"command {identity} env must contain text names and values")
            forbidden_env = sorted(POLICY_ENV & set(env))
            if forbidden_env:
                raise MatrixError(
                    f"command {identity} env may not override execution policy: "
                    + ", ".join(forbidden_env)
                )
            timeout = row.get("timeout_seconds", 120)
            if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
                raise MatrixError(f"command {identity} timeout must be finite and positive")
            if row.get("authority", "local") not in {"local", "protected"}:
                raise MatrixError(f"command {identity} authority must be local or protected")
            if runner == "go-test-json" and (len(argv) < 2 or argv[1] != "test"):
                raise MatrixError(f"command {identity} go runner must invoke go test")
            if runner == "cargo-test" and (len(argv) < 2 or argv[1] != "test"):
                raise MatrixError(f"command {identity} cargo runner must invoke cargo test")
            if runner == "cargo-test":
                required_text(row, "test_namespace", f"command {identity}")
            if runner == "python-unittest" and "unittest" not in argv:
                raise MatrixError(f"command {identity} python runner must invoke unittest")
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
            if command["runner"] == "command" and row.get("evidence_kind", "behavioral") != "structural":
                raise MatrixError(
                    f"case {identity} behavioral evidence requires a typed test observer, not command markers"
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
        selected_cases: set[str] = set()
        broad_properties: set[str] = set()
        if all_cases:
            broad_properties.update(self.properties)
        for identity in requirement_ids or []:
            if identity not in self.requirements:
                raise MatrixError(f"unknown requirement selector: {identity}")
            broad_properties.update(self.by_requirement[identity])
        for identity in property_ids or []:
            if identity not in self.properties:
                raise MatrixError(f"unknown property selector: {identity}")
            broad_properties.add(identity)
        for selector in scenarios or []:
            if selector not in self.by_scenario:
                raise MatrixError(f"unknown scenario selector: {selector}")
            selected_cases.update(self.by_scenario_cases[selector])
        for owner in owners or []:
            if owner not in self.by_owner:
                raise MatrixError(f"unknown owner selector: {owner}")
            broad_properties.update(self.by_owner[owner])
        for identity in case_ids or []:
            if identity not in self.cases:
                raise MatrixError(f"unknown case selector: {identity}")
            selected_cases.add(identity)
        for identity in command_ids or []:
            if identity not in self.commands:
                raise MatrixError(f"unknown command selector: {identity}")
            selected_cases.update(self.by_case_command[identity])
        for identity in test_ids or []:
            if identity not in self.by_test:
                raise MatrixError(f"unknown test selector: {identity}")
            selected_cases.update(self.by_test[identity])
        for raw_path in changed_paths or []:
            path = safe_relative(raw_path, "changed path").as_posix()
            matched = False
            for identity, row in self.properties.items():
                if any(path_glob_matches(path, pattern) for pattern in row["source_globs"]):
                    broad_properties.add(identity)
                    matched = True
            for identity, row in self.cases.items():
                if any(path_glob_matches(path, pattern) for pattern in row["invalidation_dependencies"]):
                    selected_cases.add(identity)
                    matched = True
            if not matched:
                raise MatrixError(f"changed path has no evidence mapping: {path}")
        selected_cases.update(
            identity for identity, row in self.cases.items()
            if row["property_id"] in broad_properties
        )
        selected_properties.update(broad_properties)
        selected_properties.update(self.cases[identity]["property_id"] for identity in selected_cases)
        if not selected_cases:
            raise MatrixError("selection resolved no evidence cases")
        selected_case_ids = sorted(selected_cases)
        selected_command_ids = sorted({
            self.cases[identity]["command_id"] for identity in selected_case_ids
        })
        requirement_set = sorted({self.properties[identity]["requirement_id"] for identity in selected_properties})
        return {
            "requirements": requirement_set,
            "properties": sorted(selected_properties),
            "cases": selected_case_ids,
            "commands": selected_command_ids,
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

    def describe(
        self,
        selection: dict[str, list[str]],
        evidence_paths: list[Path] | None = None,
        requested_selectors: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        statuses = load_observed_statuses(self, evidence_paths or [])
        return {
            **self.summary(selection),
            "requested_selectors": requested_selectors or {},
            "nodes": {
                "requirements": {identity: self.requirements[identity] for identity in selection["requirements"]},
                "properties": {identity: self.properties[identity] for identity in selection["properties"]},
                "cases": {
                    identity: {
                        **self.cases[identity],
                        "latest_observed_status": statuses.get(identity, "not_loaded"),
                        "current_evidence_fingerprint": case_evidence_fingerprint(self, identity),
                    }
                    for identity in selection["cases"]
                },
                "commands": {identity: self.commands[identity] for identity in selection["commands"]},
            },
        }


def repository_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return sorted(item.decode(errors="surrogateescape") for item in result.stdout.split(b"\0") if item)
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    )


def dependency_snapshot(root: Path, patterns: list[str]) -> dict[str, list[dict[str, str]]]:
    files = repository_files(root)
    snapshot: dict[str, list[dict[str, str]]] = {}
    for pattern in patterns:
        matches: list[dict[str, str]] = []
        for relative in files:
            if not path_glob_matches(relative, pattern):
                continue
            absolute = (root / relative).resolve()
            if not absolute.is_relative_to(root) or not absolute.is_file():
                continue
            matches.append({"path": relative, "sha256": sha256_bytes(absolute.read_bytes())})
        snapshot[pattern] = matches
    return snapshot


def case_evidence_fingerprint(graph: EvidenceGraph, case_id: str) -> str:
    case = graph.cases[case_id]
    property_row = graph.properties[case["property_id"]]
    requirement = graph.requirements[property_row["requirement_id"]]
    command = graph.commands[case["command_id"]]
    value = {
        "requirement_fingerprint": requirement["fingerprint"],
        "property": property_row,
        "case": case,
        "execution": json.loads(command_key(command)),
        "runner": command["runner"],
        "test_namespace": command.get("test_namespace"),
        "dependencies": dependency_snapshot(graph.root, case["invalidation_dependencies"]),
    }
    return sha256_bytes(canonical_json(value))


def load_observed_statuses(graph: EvidenceGraph, paths: list[Path]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for raw_path in paths:
        path = raw_path if raw_path.is_absolute() else graph.root / raw_path
        path = path.resolve()
        if not path.is_relative_to(graph.root) or not path.is_file():
            raise MatrixError(f"evidence result is unavailable or outside repository: {raw_path}")
        report = load_json(path)
        if report.get("change") != graph.change:
            raise MatrixError(f"evidence result belongs to another change: {raw_path}")
        for case_id, row in report.get("cases", {}).items():
            if case_id not in graph.cases or not isinstance(row, dict):
                continue
            if row.get("evidence_fingerprint") == case_evidence_fingerprint(graph, case_id):
                statuses[case_id] = str(row.get("status", "unknown"))
            else:
                statuses[case_id] = "stale"
    return statuses


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


def parse_cargo_events(raw: str, namespace: str) -> dict[str, str]:
    observed: dict[str, str] = {}
    priority = {"pass": 0, "skip": 1, "fail": 2}
    status = {"ok": "pass", "FAILED": "fail", "ignored": "skip"}
    for line in raw.splitlines():
        match = re.match(r"^test (.+?) \.\.\. (ok|FAILED|ignored)$", line.strip())
        if match:
            identity = f"{namespace}::{match.group(1)}"
            outcome = status[match.group(2)]
            observed[identity] = max(observed.get(identity, "pass"), outcome, key=priority.get)
    return observed


def parse_unittest_events(raw: str) -> dict[str, str]:
    observed: dict[str, str] = {}
    priority = {"pass": 0, "skip": 1, "fail": 2}
    outcome_status = {
        "ok": "pass",
        "FAIL": "fail",
        "ERROR": "fail",
        "expected failure": "skip",
        "unexpected success": "fail",
    }
    start = re.compile(
        r"^(\S+) \(([^)]+)\) \.\.\. ?(.*)$", re.MULTILINE
    )
    outcome_line = re.compile(
        r"^(ok|FAIL|ERROR|expected failure|unexpected success|skipped(?: .*)?)$",
        re.MULTILINE,
    )
    starts = list(start.finditer(raw))
    for index, match in enumerate(starts):
        end = starts[index + 1].start() if index + 1 < len(starts) else len(raw)
        segment = match.group(3) + "\n" + raw[match.end():end]
        outcome_matches = list(outcome_line.finditer(segment))
        if not outcome_matches:
            continue
        method, qualified = match.group(1), match.group(2)
        raw_outcome = outcome_matches[-1].group(1)
        if not qualified.endswith("." + method):
            qualified = qualified + "." + method
        outcome = "skip" if raw_outcome.startswith("skipped") else outcome_status[raw_outcome]
        identity = f"unittest::{qualified}"
        observed[identity] = max(observed.get(identity, "pass"), outcome, key=priority.get)
    return observed


def parse_node_tap_events(raw: str) -> dict[str, str]:
    observed: dict[str, str] = {}
    priority = {"pass": 0, "skip": 1, "fail": 2}
    for line in raw.splitlines():
        match = re.match(r"^\s*(ok|not ok)\s+\d+\s+-\s+(.+?)(?:\s+#\s+(SKIP|TODO).*)?$", line)
        if not match:
            continue
        result, name, directive = match.groups()
        outcome = "skip" if directive else ("pass" if result == "ok" else "fail")
        identity = f"node::{name.strip()}"
        observed[identity] = max(observed.get(identity, "pass"), outcome, key=priority.get)
    return observed


def git_state(root: Path) -> dict[str, Any]:
    def command(*args: str) -> tuple[bool, str]:
        result = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=10, check=False
        )
        return result.returncode == 0, result.stdout.strip()
    head_ok, head = command("rev-parse", "HEAD")
    status_ok, status = command("status", "--porcelain")
    if not head_ok or not status_ok:
        return {"status": "unknown", "head": None, "dirty": None}
    return {"status": "known", "head": head, "dirty": bool(status)}


def run_selection(
    graph: EvidenceGraph,
    selection: dict[str, list[str]],
    output: Path,
    *,
    allow_protected: bool = False,
    require_clean: bool = False,
    requested_selectors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if output.exists():
        raise MatrixError(f"refusing to overwrite evidence: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    provenance = git_state(graph.root)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        **graph.summary(selection),
        "requested_selectors": requested_selectors or {},
        "git": provenance,
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "status": "passed",
        "commands": [],
        "cases": {},
    }
    selected_by_command: dict[str, list[str]] = defaultdict(list)

    def case_result(case_id: str, status: str) -> dict[str, Any]:
        case = graph.cases[case_id]
        return {
            "status": status,
            "test_id": case["test_id"],
            "property_id": case["property_id"],
            "polarity": case["polarity"],
            "scenario": case["scenario"],
            "scenario_fingerprint": case["scenario_fingerprint"],
            "setup": case["setup"],
            "observable": case["observable"],
            "red_expectation": case["red_expectation"],
            "green_expectation": case["green_expectation"],
            "invalidation_dependencies": case["invalidation_dependencies"],
            "source_path": case["source_path"],
            "source_sha256": case.get("source_sha256"),
            "evidence_fingerprint": case_evidence_fingerprint(graph, case_id),
        }

    if require_clean and (provenance.get("status") != "known" or provenance.get("dirty") is not False):
        for case_id in selection["cases"]:
            report["cases"][case_id] = case_result(case_id, "provenance_blocked")
        report["status"] = "incomplete"
        report["finished_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return report

    for case_id in selection["cases"]:
        case = graph.cases[case_id]
        if case["state"] != "implemented":
            report["cases"][case_id] = case_result(case_id, case["state"])
            report["status"] = "incomplete"
            continue
        command = graph.commands[case["command_id"]]
        if command.get("authority", "local") == "protected" and not allow_protected:
            report["cases"][case_id] = case_result(case_id, "authority_blocked")
            report["status"] = "incomplete"
            continue
        selected_by_command[case["command_id"]].append(case_id)

    policy_env = dict(
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
        argv = normalized_argv(row)
        cwd = (graph.root / row.get("cwd", ".")).resolve()
        env = {**os.environ, **row.get("env", {}), **policy_env}
        process = run_process(
            argv,
            cwd,
            env,
            float(row.get("timeout_seconds", 120)),
            output.with_name(f"{output.name}.{command_id}"),
        )
        process_status = str(process["status"])
        exit_code = process["exit_code"]
        stdout = str(process["stdout"])
        stderr = str(process["stderr"])
        stdout_complete = Path(str(process["stdout_artifact"])).read_text(
            encoding="utf-8", errors="replace"
        )
        stderr_complete = Path(str(process["stderr_artifact"])).read_text(
            encoding="utf-8", errors="replace"
        )
        combined = stdout_complete + "\n" + stderr_complete
        if row["runner"] == "go-test-json":
            observed = parse_go_events(stdout_complete)
        elif row["runner"] == "cargo-test":
            observed = parse_cargo_events(combined, row["test_namespace"])
        elif row["runner"] == "python-unittest":
            observed = parse_unittest_events(combined)
        elif row["runner"] == "node-test-tap":
            observed = parse_node_tap_events(combined)
        else:
            lines = set(combined.splitlines())
            observed = {marker: "pass" for marker in row.get("expected_markers", []) if marker in lines}
        command_result = {
            "id": command_id,
            "argv": argv,
            "cwd": str(cwd),
            "status": process_status,
            "exit_code": exit_code,
            "duration_seconds": process["duration_seconds"],
            "observed_tests": observed,
            "stdout": stdout,
            "stderr": stderr,
            "stdout_artifact": process["stdout_artifact"],
            "stderr_artifact": process["stderr_artifact"],
            "stdout_truncated": process["stdout_truncated"],
            "stderr_truncated": process["stderr_truncated"],
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
            report["cases"][case_id] = case_result(case_id, status)
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


def requested_selection(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "requirements": split_values(args.requirements),
        "properties": split_values(args.properties),
        "scenarios": split_values(args.scenarios),
        "owners": split_values(args.owners),
        "cases": split_values(args.cases),
        "commands": split_values(args.commands),
        "tests": split_values(args.tests),
        "changed_paths": split_values(args.changed_paths),
        "all": bool(args.all),
    }


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
    query.add_argument("--evidence", action="append", type=Path)
    run = subparsers.add_parser("run")
    add_selection(run)
    run.add_argument("--output", required=True, type=Path)
    run.add_argument("--allow-protected", action="store_true")
    run.add_argument("--require-clean", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    root = args.root.resolve()
    change_root = root / "openspec" / "changes" / args.change
    try:
        if args.operation == "fingerprints":
            specs = parse_delta_specs(change_root)
            sources: dict[str, str | None] = {}
            default_manifest = change_root / "verification.json"
            if default_manifest.is_file():
                raw = load_json(default_manifest)
                for case in raw.get("cases", []):
                    if not isinstance(case, dict) or not isinstance(case.get("source_path"), str):
                        continue
                    source = safe_relative(case["source_path"], "case source path")
                    absolute = root / source
                    sources[source.as_posix()] = sha256_bytes(absolute.read_bytes()) if absolute.is_file() else None
            print(json.dumps({
                "specifications": {
                    f"{capability}::{title}": row for (capability, title), row in specs.items()
                },
                "test_sources": sources,
            }, indent=2, sort_keys=True))
            return 0
        manifest = args.manifest
        if manifest is not None and not manifest.is_absolute():
            manifest = root / manifest
        if manifest is None and not (change_root / "verification.json").is_file():
            if args.operation == "validate" and not parse_delta_specs(change_root):
                print(json.dumps({
                    "status": "not_required",
                    "change": args.change,
                    "reason": "no ADDED or MODIFIED behavioral requirements",
                }, indent=2, sort_keys=True))
                return 0
        graph = EvidenceGraph(root, args.change, manifest)
        if args.operation == "validate":
            print(json.dumps({"status": "passed", **graph.summary()}, indent=2, sort_keys=True))
            return 0
        requested = requested_selection(args)
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
            print(json.dumps({
                "status": "passed",
                **graph.describe(selection, args.evidence, requested),
            }, indent=2, sort_keys=True))
            return 0
        output = (args.output if args.output.is_absolute() else root / args.output).resolve()
        if not output.is_relative_to(root):
            raise MatrixError("evidence output must stay inside repository")
        report = run_selection(
            graph,
            selection,
            output,
            allow_protected=args.allow_protected,
            require_clean=args.require_clean,
            requested_selectors=requested,
        )
        print(json.dumps({
            "status": report["status"],
            "artifact": str(output),
            "git": report["git"],
            "requested_selectors": report["requested_selectors"],
        }, sort_keys=True))
        return 0 if report["status"] == "passed" else 1
    except MatrixError as error:
        print(json.dumps({"status": "invalid", "reason": str(error)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
