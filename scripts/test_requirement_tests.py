"""Requirement evidence DAG fixtures; no product or external service is used."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

from scripts import requirement_tests as evidence


SPEC = """# Spec Delta

## ADDED Requirements

### Requirement: Preserve exact ownership
The fixture SHALL retain one exact owner.

#### Scenario: Matching owner
- **WHEN** the owner matches
- **THEN** access succeeds

#### Scenario: Different owner
- **WHEN** the owner differs
- **THEN** access fails
"""


class RequirementEvidenceGraphTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="requirement-evidence-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.change = "fixture-change"
        self.change_root = self.root / "openspec" / "changes" / self.change
        spec = self.change_root / "specs" / "ownership" / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(SPEC, encoding="utf-8")
        test_source = self.root / "tests" / "ownership_test.py"
        test_source.parent.mkdir(parents=True)
        test_source.write_text("# exact source pinned by the evidence graph\n", encoding="utf-8")
        source_sha256 = evidence.sha256_bytes(test_source.read_bytes())
        parsed = evidence.parse_delta_specs(self.change_root)[
            ("ownership", "Preserve exact ownership")
        ]
        command = {
            "id": "ownership-command",
            "runner": "command",
            "argv": [
                sys.executable,
                "-c",
                "print('match-positive\\nmatch-negative\\ndifferent-positive\\ndifferent-negative')",
            ],
            "cwd": ".",
            "timeout_seconds": 10,
            "authority": "local",
            "expected_markers": [
                "match-positive", "match-negative", "different-positive", "different-negative",
            ],
        }

        def case(
            identity: str,
            scenario: str,
            polarity: str,
            observable: str,
            test_id: str,
        ) -> dict[str, object]:
            return {
                "id": identity,
                "property_id": "R1.P1",
                "polarity": polarity,
                "scenario": scenario,
                "scenario_fingerprint": parsed["scenario_fingerprints"][scenario],
                "setup": f"fixture setup for {scenario}",
                "observable": observable,
                "red_expectation": f"wrong behavior for {scenario} is detected",
                "green_expectation": f"required behavior for {scenario} is observed",
                "invalidation_dependencies": ["src/ownership/**", "tests/ownership_test.py"],
                "test_id": test_id,
                "command_id": "ownership-command",
                "state": "implemented",
                "source_path": "tests/ownership_test.py",
                "source_sha256": source_sha256,
                "substitution": {"classification": "NO_TEST_DOUBLE"},
            }

        self.manifest = {
            "schema_version": 2,
            "change": self.change,
            "requirements": [{
                "id": "R1", "capability": "ownership", "title": "Preserve exact ownership",
                "fingerprint": parsed["fingerprint"],
            }],
            "properties": [{
                "id": "R1.P1", "requirement_id": "R1",
                "scenarios": ["Matching owner", "Different owner"],
                "statement": "Only the exact owner is admitted.",
                "owner": "ownership-service", "oracle": "literal identity equality",
                "source_globs": ["src/ownership/**", "tests/ownership_test.py"],
            }],
            "cases": [
                case("R1.P1.MATCH.POS", "Matching owner", "positive", "matching owner is admitted", "match-positive"),
                case("R1.P1.MATCH.NEG", "Matching owner", "negative", "missing owner is rejected", "match-negative"),
                case("R1.P1.DIFFERENT.POS", "Different owner", "positive", "different owner keeps its own resource", "different-positive"),
                case("R1.P1.DIFFERENT.NEG", "Different owner", "negative", "different owner is rejected", "different-negative"),
            ],
            "commands": [command],
        }
        self.write_manifest()

    def write_manifest(self) -> None:
        (self.change_root / "verification.json").write_text(
            json.dumps(self.manifest, indent=2) + "\n", encoding="utf-8"
        )

    def graph(self) -> evidence.EvidenceGraph:
        return evidence.EvidenceGraph(self.root, self.change)

    def test_valid_graph_queries_deterministic_affected_closure(self) -> None:
        graph = self.graph()
        by_requirement = graph.select(requirement_ids=["R1"])
        by_owner = graph.select(owners=["ownership-service"])
        by_path = graph.select(changed_paths=["src/ownership/store.py"])
        by_scenario = graph.select(scenarios=["R1::Matching owner"])
        by_case = graph.select(case_ids=["R1.P1.MATCH.POS"])
        by_command = graph.select(command_ids=["ownership-command"])
        by_test = graph.select(test_ids=["different-negative"])
        self.assertEqual(by_requirement, by_owner)
        self.assertEqual(by_requirement, by_path)
        self.assertEqual(by_requirement, by_command)
        self.assertEqual(4, len(by_requirement["cases"]))
        self.assertEqual(
            ["R1.P1.MATCH.NEG", "R1.P1.MATCH.POS"], by_scenario["cases"],
        )
        self.assertEqual(["R1.P1.MATCH.POS"], by_case["cases"])
        self.assertEqual(["R1.P1.DIFFERENT.NEG"], by_test["cases"])
        described = graph.describe(by_requirement)
        different = described["nodes"]["cases"]["R1.P1.DIFFERENT.NEG"]
        self.assertEqual("different-negative", different["test_id"])
        self.assertEqual("not_loaded", different["latest_observed_status"])
        with self.assertRaisesRegex(evidence.MatrixError, "selection resolved no properties"):
            graph.select(changed_paths=["src/unrelated.py"])

    def test_missing_polarity_and_uncovered_scenario_fail(self) -> None:
        for mutation, message in (
            (lambda manifest: manifest["cases"].pop(), "scenario 'Different owner' requires positive and negative"),
            (lambda manifest: manifest["properties"][0].update(scenarios=["Matching owner"]), "uncovered scenarios"),
        ):
            with self.subTest(message=message):
                original = copy.deepcopy(self.manifest)
                mutation(self.manifest)
                self.write_manifest()
                with self.assertRaisesRegex(evidence.MatrixError, message):
                    self.graph()
                self.manifest = original

    def test_case_requires_one_exact_scenario_and_review_contract(self) -> None:
        for mutation, message in (
            (lambda case: case.pop("scenario"), "case R1.P1.MATCH.POS.scenario"),
            (lambda case: case.update(scenario_fingerprint="0" * 64), "stale scenario fingerprint"),
            (lambda case: case.pop("setup"), "case R1.P1.MATCH.POS.setup"),
            (lambda case: case.pop("red_expectation"), "red_expectation"),
            (lambda case: case.pop("green_expectation"), "green_expectation"),
            (lambda case: case.pop("invalidation_dependencies"), "invalidation_dependencies"),
        ):
            with self.subTest(message=message):
                original = copy.deepcopy(self.manifest)
                mutation(self.manifest["cases"][0])
                self.write_manifest()
                with self.assertRaisesRegex(evidence.MatrixError, message):
                    self.graph()
                self.manifest = original

    def test_stale_specification_fingerprint_fails(self) -> None:
        spec = self.change_root / "specs" / "ownership" / "spec.md"
        spec.write_text(SPEC.replace("one exact owner", "the canonical exact owner"), encoding="utf-8")
        with self.assertRaisesRegex(evidence.MatrixError, "stale specification fingerprint"):
            self.graph()
        spec.write_text(SPEC, encoding="utf-8")
        self.manifest["cases"][0]["scenario_fingerprint"] = "0" * 64
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "stale scenario fingerprint"):
            self.graph()

    def test_stale_test_source_fingerprint_fails(self) -> None:
        (self.root / "tests" / "ownership_test.py").write_text("# changed test source\n", encoding="utf-8")
        with self.assertRaisesRegex(evidence.MatrixError, "stale test source fingerprint"):
            self.graph()

    def test_duplicate_case_and_command_definitions_fail(self) -> None:
        duplicate_case = copy.deepcopy(self.manifest["cases"][0])
        duplicate_case["id"] = "R1.P1.MATCH.POS.DUP"
        self.manifest["cases"].append(duplicate_case)
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "duplicate case edge"):
            self.graph()

        self.manifest["cases"].pop()
        duplicate_command = copy.deepcopy(self.manifest["commands"][0])
        duplicate_command["id"] = "duplicate-command"
        self.manifest["commands"].append(duplicate_command)
        self.manifest["cases"][1]["command_id"] = "duplicate-command"
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "duplicate command definition"):
            self.graph()

    def test_duplicate_scenario_glob_dependency_and_marker_edges_fail(self) -> None:
        for mutation, message in (
            (lambda manifest: manifest["properties"][0]["scenarios"].append("Matching owner"), "scenarios contains duplicate edges"),
            (lambda manifest: manifest["properties"][0]["source_globs"].append("src/ownership/**"), "source_globs contains duplicate edges"),
            (lambda manifest: manifest["cases"][0]["invalidation_dependencies"].append("src/ownership/**"), "invalidation_dependencies contains duplicate edges"),
            (lambda manifest: manifest["commands"][0]["expected_markers"].append("match-positive"), "expected_markers contains duplicate edges"),
        ):
            with self.subTest(message=message):
                original = copy.deepcopy(self.manifest)
                mutation(self.manifest)
                self.write_manifest()
                with self.assertRaisesRegex(evidence.MatrixError, message):
                    self.graph()
                self.manifest = original

    def test_one_canonical_command_executes_both_cases_once(self) -> None:
        graph = self.graph()
        output = self.root / "evidence" / "result.json"
        report = evidence.run_selection(graph, graph.select(all_cases=True), output)
        self.assertEqual("passed", report["status"])
        self.assertEqual(1, len(report["commands"]))
        self.assertEqual(
            {identity: "passed" for identity in (
                "R1.P1.MATCH.POS", "R1.P1.MATCH.NEG",
                "R1.P1.DIFFERENT.POS", "R1.P1.DIFFERENT.NEG",
            )},
            {identity: row["status"] for identity, row in report["cases"].items()},
        )
        self.assertEqual(
            self.manifest["cases"][0]["source_sha256"],
            report["cases"]["R1.P1.MATCH.POS"]["source_sha256"],
        )
        self.assertTrue(output.is_file())

    def test_planned_and_protected_cases_cannot_pass(self) -> None:
        self.manifest["cases"][0]["state"] = "planned"
        self.manifest["cases"][0]["substitution"] = {"classification": "UNDECIDED"}
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "planned.json")
        self.assertEqual("incomplete", report["status"])
        self.assertEqual("planned", report["cases"]["R1.P1.MATCH.POS"]["status"])

        self.manifest["cases"][0]["state"] = "implemented"
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "cannot have an undecided substitution"):
            self.graph()
        self.manifest["cases"][0]["substitution"] = {"classification": "NO_TEST_DOUBLE"}
        self.manifest["commands"][0]["authority"] = "protected"
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "protected.json")
        self.assertEqual("incomplete", report["status"])
        self.assertEqual("authority_blocked", report["cases"]["R1.P1.MATCH.POS"]["status"])

    def test_missing_expected_identity_and_command_failure_cannot_pass(self) -> None:
        self.manifest["cases"][0]["test_id"] = "absent-case"
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "not an expected marker"):
            self.graph()

        self.manifest["cases"][0]["test_id"] = "match-positive"
        self.manifest["commands"][0]["argv"] = [
            sys.executable,
            "-c",
            "print('match-positive\\nmatch-negative\\ndifferent-positive\\ndifferent-negative'); raise SystemExit(7)",
        ]
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "failed.json")
        self.assertEqual("failed", report["status"])
        self.assertEqual(7, report["commands"][0]["exit_code"])

    def test_go_and_cargo_observers_preserve_exact_failure_states(self) -> None:
        go = "\n".join(json.dumps(row) for row in (
            {"Action": "pass", "Package": "example/p", "Test": "TestPositive"},
            {"Action": "skip", "Package": "example/p", "Test": "TestNegative"},
            {"Action": "fail", "Package": "example/p", "Test": "TestFailed"},
        ))
        self.assertEqual({
            "example/p::TestPositive": "pass",
            "example/p::TestNegative": "skip",
            "example/p::TestFailed": "fail",
        }, evidence.parse_go_events(go))
        cargo = "test ownership::positive ... ok\ntest ownership::negative ... FAILED\n"
        self.assertEqual({
            "ownership::positive": "pass", "ownership::negative": "fail",
        }, evidence.parse_cargo_events(cargo))

    def test_shared_routes_require_incremental_and_final_evidence_execution(self) -> None:
        root = Path(__file__).resolve().parents[1]
        apply = (root / "scripts" / "integration_templates" / "apply.md").read_text(encoding="utf-8")
        verify = (root / "scripts" / "integration_templates" / "verify.md").read_text(encoding="utf-8")
        check = (root / "scripts" / "integration_templates" / "check.md").read_text(encoding="utf-8")
        config = (root / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("verification.json", apply)
        self.assertIn("affected", apply)
        self.assertIn("verification.json", verify)
        self.assertIn("exact observed pass/fail/skip/missing", verify)
        self.assertIn("spec-tests", check)
        self.assertIn("run --all", check)
        self.assertIn("verification.json", config)
        self.assertNotIn("GOTOOLCHAIN=local", (root / "scripts" / "local_verify.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
