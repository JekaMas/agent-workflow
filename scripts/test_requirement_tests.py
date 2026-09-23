"""Requirement evidence DAG fixtures; no product or external service is used."""

from __future__ import annotations

import copy
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
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
        (test_source.parent / "__init__.py").write_text("", encoding="utf-8")
        test_source.write_text(
            """import unittest


class OwnershipTest(unittest.TestCase):
    def test_match_positive(self):
        self.assertTrue(True)

    def test_match_negative(self):
        self.assertTrue(True)

    def test_different_positive(self):
        self.assertTrue(True)

    def test_different_negative(self):
        self.assertTrue(True)
""",
            encoding="utf-8",
        )
        source_sha256 = evidence.sha256_bytes(test_source.read_bytes())
        parsed = evidence.parse_delta_specs(self.change_root)[
            ("ownership", "Preserve exact ownership")
        ]
        command = {
            "id": "ownership-command",
            "runner": "python-unittest",
            "argv": [sys.executable, "-m", "unittest", "-v", "tests.ownership_test"],
            "cwd": ".",
            "timeout_seconds": 10,
            "authority": "local",
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
                "setup": f"Construct the ownership fixture for {scenario} and invoke its exact branch.",
                "observable": observable,
                "red_expectation": f"The {scenario} branch accepts the wrong ownership relation.",
                "green_expectation": f"The {scenario} branch returns the expected ownership result.",
                "invalidation_dependencies": ["src/ownership/**", "tests/ownership_test.py"],
                "test_id": test_id,
                "command_id": "ownership-command",
                "state": "implemented",
                "source_path": "tests/ownership_test.py",
                "source_sha256": source_sha256,
                "distinct_reason": f"{scenario}: {observable}",
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
                case("R1.P1.MATCH.POS", "Matching owner", "positive", "matching owner is admitted", "unittest::tests.ownership_test.OwnershipTest.test_match_positive"),
                case("R1.P1.MATCH.NEG", "Matching owner", "negative", "missing owner is rejected", "unittest::tests.ownership_test.OwnershipTest.test_match_negative"),
                case("R1.P1.DIFFERENT.POS", "Different owner", "positive", "different owner keeps its own resource", "unittest::tests.ownership_test.OwnershipTest.test_different_positive"),
                case("R1.P1.DIFFERENT.NEG", "Different owner", "negative", "different owner is rejected", "unittest::tests.ownership_test.OwnershipTest.test_different_negative"),
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
        different_negative = "unittest::tests.ownership_test.OwnershipTest.test_different_negative"
        by_test = graph.select(test_ids=[different_negative])
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
        self.assertEqual(different_negative, different["test_id"])
        self.assertEqual("not_loaded", different["latest_observed_status"])
        with self.assertRaisesRegex(evidence.MatrixError, "changed path has no evidence mapping"):
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
        ):
            with self.subTest(message=message):
                original = copy.deepcopy(self.manifest)
                mutation(self.manifest)
                self.write_manifest()
                with self.assertRaisesRegex(evidence.MatrixError, message):
                    self.graph()
                self.manifest = original

    def test_multi_scenario_test_requires_scenario_specific_reason(self) -> None:
        self.manifest["cases"][2]["test_id"] = "unittest::tests.ownership_test.OwnershipTest.test_match_positive"
        self.manifest["cases"][2]["distinct_reason"] = "generic shared test reason"
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "multi-scenario test"):
            self.graph()

    def test_multi_scenario_test_accepts_scenario_specific_reasons(self) -> None:
        shared_test = "unittest::tests.ownership_test.OwnershipTest.test_match_positive"
        self.manifest["cases"][2]["test_id"] = shared_test
        self.manifest["cases"][2]["distinct_reason"] = (
            "Different owner: proves the independent rejection branch"
        )
        self.write_manifest()
        graph = self.graph()
        self.assertEqual(
            ["R1.P1.DIFFERENT.POS", "R1.P1.MATCH.POS"],
            graph.select(test_ids=[shared_test])["cases"],
        )

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
        self.manifest["commands"][0]["argv"] = [
            sys.executable, "-m", "unittest", "-v",
            "tests.ownership_test.OwnershipTest.test_match_positive",
        ]
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "missing.json")
        self.assertEqual("incomplete", report["status"])
        self.assertEqual("missing", report["cases"]["R1.P1.DIFFERENT.NEG"]["status"])

        self.manifest["commands"][0]["argv"] = [
            sys.executable, "-m", "unittest", "-v", "tests.absent_test",
        ]
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "failed.json")
        self.assertEqual("failed", report["status"])
        self.assertNotEqual(0, report["commands"][0]["exit_code"])

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
        cargo = "test positive ... ok\ntest negative ... FAILED\ntest negative ... ok\n"
        self.assertEqual({
            "ownership::positive": "pass", "ownership::negative": "fail",
        }, evidence.parse_cargo_events(cargo, "ownership"))

    def test_unittest_observer_preserves_skip_expected_failure_and_python_versions(self) -> None:
        raw = "\n".join((
            "test_ok (pkg.Case.test_ok) ... ok",
            "test_skip (pkg.Case.test_skip) ... skipped 'reason'",
            "test_expected (pkg.Case.test_expected) ... expected failure",
            "test_unexpected (pkg.Case.test_unexpected) ... unexpected success",
            "test_old (pkg.Case) ... ok",
            "test_noisy (pkg.Case.test_noisy) ... child process output",
            "still child output",
            "ok",
        ))
        self.assertEqual({
            "unittest::pkg.Case.test_ok": "pass",
            "unittest::pkg.Case.test_skip": "skip",
            "unittest::pkg.Case.test_expected": "skip",
            "unittest::pkg.Case.test_unexpected": "fail",
            "unittest::pkg.Case.test_old": "pass",
            "unittest::pkg.Case.test_noisy": "pass",
        }, evidence.parse_unittest_events(raw))

    def test_node_tap_observer_preserves_pass_fail_and_skip(self) -> None:
        observed = evidence.parse_node_tap_events(
            "ok 1 - accepts valid GMX account\n"
            "not ok 2 - rejects mismatched account\n"
            "ok 3 - funded stage case # SKIP no authority\n"
        )
        self.assertEqual("pass", observed["node::accepts valid GMX account"])
        self.assertEqual("fail", observed["node::rejects mismatched account"])
        self.assertEqual("skip", observed["node::funded stage case"])

    def test_command_markers_cannot_prove_behavioral_cases(self) -> None:
        command = self.manifest["commands"][0]
        command.update(
            runner="command",
            expected_markers=[case["test_id"] for case in self.manifest["cases"]],
        )
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "requires a typed test observer"):
            self.graph()

        for case in self.manifest["cases"]:
            case["state"] = "planned"
            case["substitution"] = {"classification": "UNDECIDED"}
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(
            graph, graph.select(all_cases=True), self.root / "planned-markers.json",
        )
        self.assertEqual("incomplete", report["status"])
        self.assertTrue(all(row["status"] == "planned" for row in report["cases"].values()))

    def test_skipped_or_expected_failure_case_is_nonpassing(self) -> None:
        source = self.root / "tests" / "ownership_test.py"
        original_source = source.read_text()
        for decorator in ("@unittest.skip('fixture')", "@unittest.expectedFailure"):
            with self.subTest(decorator=decorator):
                source.write_text(original_source.replace(
                    "    def test_match_positive(self):",
                    f"    {decorator}\n    def test_match_positive(self):",
                ))
                digest = evidence.sha256_bytes(source.read_bytes())
                for case in self.manifest["cases"]:
                    case["source_sha256"] = digest
                self.write_manifest()
                graph = self.graph()
                report = evidence.run_selection(
                    graph, graph.select(all_cases=True),
                    self.root / f"skip-{decorator.split('.')[-1].split('(')[0]}.json",
                )
                self.assertNotEqual("passed", report["status"])
                self.assertNotEqual("passed", report["cases"]["R1.P1.MATCH.POS"]["status"])
                source.write_text(original_source)

    def test_identity_whitespace_cannot_remove_cases_or_raise_keyerror(self) -> None:
        for field in ("property_id", "command_id"):
            with self.subTest(field=field):
                original = copy.deepcopy(self.manifest)
                self.manifest["cases"][0][field] += " "
                self.write_manifest()
                with self.assertRaisesRegex(evidence.MatrixError, "surrounding whitespace"):
                    self.graph()
                self.manifest = original

    def test_case_dependencies_select_and_invalidate_only_the_declared_case(self) -> None:
        decision = self.root / "docs" / "decision.md"
        decision.parent.mkdir()
        decision.write_text("v1\n")
        self.manifest["cases"][0]["invalidation_dependencies"].append("docs/decision.md")
        self.write_manifest()
        graph = self.graph()
        selected = graph.select(changed_paths=["docs/decision.md"])
        self.assertEqual(["R1.P1.MATCH.POS"], selected["cases"])

        output = self.root / "dependency-result.json"
        report = evidence.run_selection(graph, selected, output)
        self.assertEqual("passed", report["status"])
        self.assertEqual(
            "passed",
            graph.describe(selected, [output])["nodes"]["cases"]["R1.P1.MATCH.POS"]["latest_observed_status"],
        )
        decision.write_text("v2\n")
        self.assertEqual(
            "stale",
            graph.describe(selected, [output])["nodes"]["cases"]["R1.P1.MATCH.POS"]["latest_observed_status"],
        )

    def test_delta_parser_ignores_removed_renamed_and_fenced_examples(self) -> None:
        spec = self.change_root / "specs" / "ownership" / "spec.md"
        spec.write_text(SPEC + """
## REMOVED Requirements
### Requirement: Legacy owner cache

## RENAMED Requirements
- FROM: `Old owner`
- TO: `New owner`

```markdown
### Requirement: Example only
#### Scenario: Not real
```
""")
        parsed = evidence.parse_delta_specs(self.change_root)
        self.assertEqual([("ownership", "Preserve exact ownership")], list(parsed))

    def test_nonbehavioral_change_without_manifest_is_not_required(self) -> None:
        change = "nonbehavioral"
        spec = self.root / "openspec" / "changes" / change / "specs" / "legacy" / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(
            "# Spec Delta\n\n## REMOVED Requirements\n\n"
            "### Requirement: Removed behavior\n\n"
            "#### Scenario: Historical only\n- **WHEN** removed\n- **THEN** absent\n",
            encoding="utf-8",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = evidence.main([
                "--root", str(self.root), "--change", change, "validate",
            ])
        self.assertEqual(0, status)
        self.assertEqual("not_required", json.loads(output.getvalue())["status"])

    def test_policy_environment_and_unavailable_cwd_fail_before_execution(self) -> None:
        self.manifest["commands"][0]["env"] = {"GOPROXY": "https://example.invalid"}
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "may not override execution policy"):
            self.graph()

        self.manifest["commands"][0]["env"] = {}
        self.manifest["commands"][0]["cwd"] = "missing-directory"
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "cwd is unavailable"):
            self.graph()

    def test_execution_tuple_deduplicates_observation_variants_and_go_json(self) -> None:
        duplicate = copy.deepcopy(self.manifest["commands"][0])
        duplicate["id"] = "duplicate-observer"
        duplicate["expected_markers"] = ["unused-marker"]
        self.manifest["commands"].append(duplicate)
        self.manifest["cases"][1]["command_id"] = "duplicate-observer"
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "duplicate command definition"):
            self.graph()

        go = {"runner": "go-test-json", "argv": ["go", "test", "./x"]}
        go_json = {"runner": "go-test-json", "argv": ["go", "test", "-json", "./x"]}
        self.assertEqual(evidence.command_key(go), evidence.command_key(go_json))

    def test_path_globs_have_recursive_and_separator_aware_semantics(self) -> None:
        self.assertTrue(evidence.path_glob_matches("scripts/test_x.py", "scripts/**/*test*.py"))
        self.assertTrue(evidence.path_glob_matches("scripts/deep/test_x.py", "scripts/**/*test*.py"))
        self.assertFalse(evidence.path_glob_matches("src/deep/x.py", "src/*.py"))
        self.assertTrue(evidence.path_glob_matches("src/x.py", "src/*.py"))

    def test_source_path_must_own_test_and_polarities_need_independent_tests(self) -> None:
        original = copy.deepcopy(self.manifest)
        unrelated = self.root / "docs" / "unrelated.md"
        unrelated.parent.mkdir()
        unrelated.write_text("not a test\n")
        self.manifest["cases"][0]["source_path"] = "docs/unrelated.md"
        self.manifest["cases"][0]["source_sha256"] = evidence.sha256_bytes(unrelated.read_bytes())
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "does not own exact test identity"):
            self.graph()

        self.manifest = original
        self.manifest["cases"][1]["test_id"] = self.manifest["cases"][0]["test_id"]
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "independent positive and negative"):
            self.graph()

    def test_generic_review_contract_text_is_rejected(self) -> None:
        case = self.manifest["cases"][0]
        case["setup"] = f"Execute the exact {case['scenario']} scenario at owner."
        self.write_manifest()
        with self.assertRaisesRegex(evidence.MatrixError, "concrete fixture or boundary"):
            self.graph()

    def test_timeout_kills_process_group_and_keeps_complete_output(self) -> None:
        pid_path = self.root / "grandchild.pid"
        code = (
            "import pathlib,subprocess,time; "
            f"p=subprocess.Popen(['{sys.executable}','-c','import time; time.sleep(30)']); "
            f"pathlib.Path({str(pid_path)!r}).write_text(str(p.pid)); time.sleep(30)"
        )
        self.manifest["commands"][0]["argv"] = [sys.executable, "-c", code, "unittest"]
        self.manifest["commands"][0]["timeout_seconds"] = 0.2
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "timeout.json")
        self.assertEqual("incomplete", report["status"])
        self.assertEqual("timed_out", report["commands"][0]["status"])
        pid = int(pid_path.read_text())
        for _ in range(20):
            result = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True)
            if result.returncode != 0 or not result.stdout.strip() or result.stdout.strip().startswith("Z"):
                break
            time.sleep(0.05)
        else:
            self.fail("timed-out command left its grandchild alive")
        self.assertTrue(Path(report["commands"][0]["stdout_artifact"]).is_file())

    def test_large_output_has_complete_artifact_beyond_preview(self) -> None:
        size = 70 * 1024
        self.manifest["commands"][0]["argv"] = [
            sys.executable, "-c", f"print('x'*{size})", "unittest",
        ]
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "large.json")
        command = report["commands"][0]
        self.assertTrue(command["stdout_truncated"])
        self.assertGreater(Path(command["stdout_artifact"]).stat().st_size, 64 * 1024)

    def test_observer_reads_exact_identity_beyond_preview(self) -> None:
        code = (
            "import sys,unittest; "
            "sys.stderr.write('x'*(70*1024)+'\\n'); "
            "sys.argv=['unittest','-v','tests.ownership_test']; "
            "unittest.main(module=None)"
        )
        self.manifest["commands"][0]["argv"] = [sys.executable, "-c", code, "unittest"]
        self.write_manifest()
        graph = self.graph()
        report = evidence.run_selection(graph, graph.select(all_cases=True), self.root / "late.json")
        self.assertEqual("passed", report["status"])
        self.assertTrue(report["commands"][0]["stderr_truncated"])
        self.assertEqual(
            "passed", report["cases"]["R1.P1.DIFFERENT.NEG"]["status"],
        )

    def test_manifest_and_output_cannot_escape_change_or_repository(self) -> None:
        outside = self.root.parent / "outside-verification.json"
        outside.write_text(json.dumps(self.manifest))
        with self.assertRaisesRegex(evidence.MatrixError, "inside the selected change"):
            evidence.EvidenceGraph(self.root, self.change, outside)

        graph = self.graph()
        with self.assertRaisesRegex(evidence.MatrixError, "refusing to overwrite"):
            output = self.root / "exists.json"
            output.write_text("{}")
            evidence.run_selection(graph, graph.select(all_cases=True), output)

    def test_git_provenance_unknown_and_clean_requirement_are_explicit(self) -> None:
        state = evidence.git_state(self.root)
        self.assertEqual("unknown", state["status"])
        graph = self.graph()
        report = evidence.run_selection(
            graph, graph.select(all_cases=True), self.root / "clean.json", require_clean=True,
        )
        self.assertEqual("incomplete", report["status"])
        self.assertEqual("provenance_blocked", report["cases"]["R1.P1.MATCH.POS"]["status"])

    def test_requested_selectors_and_evidence_fingerprints_are_recorded(self) -> None:
        graph = self.graph()
        selection = graph.select(property_ids=["R1.P1"])
        requested = {"properties": ["R1.P1"], "all": False}
        report = evidence.run_selection(
            graph, selection, self.root / "selectors.json", requested_selectors=requested,
        )
        self.assertEqual(requested, report["requested_selectors"])
        self.assertRegex(report["cases"]["R1.P1.MATCH.POS"]["evidence_fingerprint"], r"^[0-9a-f]{64}$")

    def test_shared_routes_require_incremental_and_final_evidence_execution(self) -> None:
        root = Path(__file__).resolve().parents[1]
        apply = (root / "scripts" / "integration_templates" / "apply.md").read_text(encoding="utf-8")
        verify = (root / "scripts" / "integration_templates" / "verify.md").read_text(encoding="utf-8")
        check = (root / "scripts" / "integration_templates" / "check.md").read_text(encoding="utf-8")
        explore = (root / "scripts" / "integration_templates" / "explore.md").read_text(encoding="utf-8")
        makefile = (root / "Makefile").read_text(encoding="utf-8")
        config = (root / "openspec" / "config.yaml").read_text(encoding="utf-8")
        self.assertIn("verification.json", apply)
        self.assertIn("affected", apply)
        self.assertIn("smallest directly invalidated", apply)
        self.assertIn("iteration case set once", apply)
        self.assertIn("verification.json", verify)
        self.assertIn("exact observed pass/fail/skip/missing", verify)
        self.assertIn("Reuse still-valid green", verify)
        self.assertIn("complete iteration set once", verify)
        self.assertIn("spec-tests", check)
        self.assertIn("run --all", check)
        for route in (explore, check):
            self.assertIn("exact repository search", route)
            self.assertIn("semantic Context", route)
            self.assertIn("JetBrains-index", route)
            self.assertIn("discovery.json", route)
        self.assertIn("scripts/discovery_ledger.py", makefile)
        self.assertIn("run --all --require-clean", makefile)
        self.assertIn("verification.json", config)
        self.assertIn("smallest directly invalidated cases", config)
        self.assertIn("complete iteration case set once", config)
        self.assertNotIn("GOTOOLCHAIN=local", (root / "scripts" / "local_verify.py").read_text(encoding="utf-8"))
        self.assertNotIn("GOTOOLCHAIN='local'", (root / "scripts" / "rehearse_flow.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
