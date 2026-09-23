#!/usr/bin/env python3
"""Validate exact, semantic and JetBrains-index discovery decisions for an OpenSpec change."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


SCHEMA_VERSION = 1
SEARCH_KINDS = {"exact", "semantic", "jetbrains-index"}
SEARCH_STATUSES = {"completed", "unavailable", "not_applicable"}
DISPOSITIONS = {"current_change", "new_change", "validation_only", "no_change"}
CLASSIFICATIONS = {
    "change_candidate", "reusable_unchanged", "interface_dependency",
    "test_proof", "irrelevant", "unresolved",
}


class DiscoveryError(ValueError):
    """A deterministic discovery-ledger contract failure."""


def text(row: dict[str, Any], field: str, owner: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise DiscoveryError(f"{owner}.{field} must be normalized nonempty text")
    return value


def text_list(row: dict[str, Any], field: str, owner: str, *, allow_empty: bool = False) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list) or (not value and not allow_empty):
        raise DiscoveryError(f"{owner}.{field} must be a {'list' if allow_empty else 'nonempty list'}")
    if any(not isinstance(item, str) or not item.strip() or item != item.strip() for item in value):
        raise DiscoveryError(f"{owner}.{field} must contain normalized nonempty text")
    if len(set(value)) != len(value):
        raise DiscoveryError(f"{owner}.{field} contains duplicates")
    return value


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DiscoveryError(f"cannot read discovery ledger: {error}") from error
    if not isinstance(value, dict):
        raise DiscoveryError("discovery ledger root must be an object")
    return value


def load_graph_ids(change_root: Path) -> tuple[set[str], set[str]]:
    manifest = change_root / "verification.json"
    if not manifest.is_file():
        return set(), set()
    raw = load(manifest)
    properties = {
        row.get("id") for row in raw.get("properties", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    tests = {
        row.get("test_id") for row in raw.get("cases", [])
        if isinstance(row, dict) and isinstance(row.get("test_id"), str)
    }
    return properties, tests


def validate(
    root: Path,
    change: str,
    ledger_path: Path | None = None,
    selected_properties: list[str] | None = None,
    selected_tests: list[str] | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    change_root = (root / "openspec" / "changes" / change).resolve()
    path = (ledger_path or change_root / "discovery.json").resolve()
    if not path.is_relative_to(change_root):
        raise DiscoveryError("discovery ledger must stay inside the selected change")
    raw = load(path)
    if raw.get("schema_version") != SCHEMA_VERSION:
        raise DiscoveryError(f"schema_version must be {SCHEMA_VERSION}")
    if raw.get("change") != change:
        raise DiscoveryError("ledger change does not match selected change")

    known_properties, known_tests = load_graph_ids(change_root)
    scope = raw.get("scope")
    if not isinstance(scope, dict):
        raise DiscoveryError("scope must be an object")
    scoped_properties = text_list(scope, "property_ids", "scope", allow_empty=True)
    scoped_tests = text_list(scope, "test_ids", "scope", allow_empty=True)
    unknown_properties = sorted(set(scoped_properties) - known_properties)
    unknown_tests = sorted(set(scoped_tests) - known_tests)
    if unknown_properties:
        raise DiscoveryError("unknown scoped properties: " + ", ".join(unknown_properties))
    if unknown_tests:
        raise DiscoveryError("unknown scoped tests: " + ", ".join(unknown_tests))

    reviews = raw.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        raise DiscoveryError("reviews must be a nonempty list")
    covered_properties: set[str] = set()
    covered_tests: set[str] = set()
    seen_ids: set[str] = set()
    for index, review in enumerate(reviews):
        owner = f"reviews[{index}]"
        if not isinstance(review, dict):
            raise DiscoveryError(f"{owner} must be an object")
        identity = text(review, "id", owner)
        if identity in seen_ids:
            raise DiscoveryError(f"duplicate review id: {identity}")
        seen_ids.add(identity)
        text(review, "question", owner)
        property_ids = text_list(review, "property_ids", owner, allow_empty=True)
        test_ids = text_list(review, "test_ids", owner, allow_empty=True)
        if not property_ids and not test_ids:
            raise DiscoveryError(f"{owner} must cover a property or exact test")
        if set(property_ids) - set(scoped_properties):
            raise DiscoveryError(f"{owner} names a property outside scope")
        if set(test_ids) - set(scoped_tests):
            raise DiscoveryError(f"{owner} names a test outside scope")
        covered_properties.update(property_ids)
        covered_tests.update(test_ids)

        searches = review.get("searches")
        if not isinstance(searches, list) or len(searches) != len(SEARCH_KINDS):
            raise DiscoveryError(f"{owner}.searches must contain exact, semantic and jetbrains-index")
        by_kind: dict[str, dict[str, Any]] = {}
        for search_index, search in enumerate(searches):
            search_owner = f"{owner}.searches[{search_index}]"
            if not isinstance(search, dict):
                raise DiscoveryError(f"{search_owner} must be an object")
            kind = text(search, "kind", search_owner)
            if kind not in SEARCH_KINDS or kind in by_kind:
                raise DiscoveryError(f"{search_owner}.kind must be one unique supported search kind")
            by_kind[kind] = search
            status = text(search, "status", search_owner)
            if status not in SEARCH_STATUSES:
                raise DiscoveryError(f"{search_owner}.status is unsupported")
            text(search, "query", search_owner)
            text(search, "outcome", search_owner)
            if kind == "exact" and status != "completed":
                raise DiscoveryError(f"{search_owner} exact search must complete")
            if status != "completed":
                text(search, "reason", search_owner)
            results = search.get("results", [])
            if not isinstance(results, list):
                raise DiscoveryError(f"{search_owner}.results must be a list")
            for result_index, result in enumerate(results):
                result_owner = f"{search_owner}.results[{result_index}]"
                if not isinstance(result, dict):
                    raise DiscoveryError(f"{result_owner} must be an object")
                classification = text(result, "classification", result_owner)
                if classification not in CLASSIFICATIONS:
                    raise DiscoveryError(f"{result_owner}.classification is unsupported")
                text(result, "reason", result_owner)
                if "path" in result:
                    relative = Path(text(result, "path", result_owner))
                    if relative.is_absolute() or ".." in relative.parts:
                        raise DiscoveryError(f"{result_owner}.path must be repository-relative")
                if "line" in result and (not isinstance(result["line"], int) or result["line"] <= 0):
                    raise DiscoveryError(f"{result_owner}.line must be a positive integer")

        disposition = text(review, "disposition", owner)
        if disposition not in DISPOSITIONS:
            raise DiscoveryError(f"{owner}.disposition is unsupported")
        text(review, "rationale", owner)
        if disposition == "new_change":
            target = text(review, "target_change", owner)
            if target == change:
                raise DiscoveryError(f"{owner}.target_change must be a different change")

    required_properties = set(selected_properties or scoped_properties)
    required_tests = set(selected_tests or scoped_tests)
    missing_properties = sorted(required_properties - covered_properties)
    missing_tests = sorted(required_tests - covered_tests)
    if missing_properties:
        raise DiscoveryError("uncovered discovery properties: " + ", ".join(missing_properties))
    if missing_tests:
        raise DiscoveryError("uncovered discovery tests: " + ", ".join(missing_tests))
    return {
        "status": "passed",
        "change": change,
        "ledger": path.relative_to(root).as_posix(),
        "properties": sorted(required_properties),
        "tests": sorted(required_tests),
        "reviews": sorted(seen_ids),
    }


def split(values: list[str] | None) -> list[str]:
    return [item.strip() for value in values or [] for item in value.split(",") if item.strip()]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--change", required=True)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--properties", action="append")
    parser.add_argument("--tests", action="append")
    args = parser.parse_args(argv)
    try:
        result = validate(
            args.root,
            args.change,
            args.ledger,
            split(args.properties),
            split(args.tests),
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except DiscoveryError as error:
        print(json.dumps({"status": "invalid", "reason": str(error)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
