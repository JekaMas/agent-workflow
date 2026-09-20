"""Synthetic parser/process fixtures; no Go/Rust product test or live service runs."""

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import local_verify as verify


def events(*rows):
    return "\n".join(json.dumps(row) for row in rows)


def go_events(result="pass"):
    return events(
        {"Action": "start", "Package": "example/p"},
        {"Action": "run", "Package": "example/p", "Test": "TestCancel"},
        {"Action": result, "Package": "example/p", "Test": "TestCancel"},
        {"Action": "pass", "Package": "example/p"},
    )


class LocalVerifyTest(unittest.TestCase):
    def test_proof_summaries_require_nonempty_success(self):
        passing = {
            'kani': 'VERIFICATION:- SUCCESSFUL\nComplete - 1 successfully verified harnesses, 0 failures, 1 total.',
            'verus': 'verification results:: 1 verified, 0 errors',
            'gobra': 'Gobra found 1 methods and functions.\n0 specified members of the package under verification are trusted or abstract.\nGobra found 0 errors.'}
        for kind, raw in passing.items():
            with self.subTest(kind=kind):
                self.assertEqual('passed', verify.proof_result(kind, raw)[0])
                self.assertEqual('incomplete', verify.proof_result(kind, '')[0])
                self.assertEqual('incomplete', verify.proof_result(kind, raw.replace('1 ', '0 '))[0])
        self.assertEqual('incomplete', verify.proof_result('kani', passing['kani'] + '\n- Status: FAILURE')[0])
        self.assertEqual('incomplete', verify.proof_result('verus', passing['verus'] + '\nverification results:: 0 verified, 1 errors')[0])
        self.assertEqual('incomplete', verify.proof_result('gobra', passing['gobra'] + '\nGobra found 1 errors.')[0])
        self.assertEqual('incomplete', verify.proof_result('gobra', passing['gobra'].replace('0 specified', '1 specified'))[0])

    def test_proof_process_failure_and_stale_source_cannot_pass(self):
        for condition in ('failed', 'stale', 'empty', 'unavailable', 'timed_out'):
            with self.subTest(condition=condition), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                source = root / 'target.rs'
                source.write_text('source')
                output = root / 'result.json'
                def process(command, cwd, env, timeout, prefix=None):
                    version = '--version' in command
                    if not version and condition == 'stale': source.write_text('changed')
                    return {'command':command, 'status': condition if not version and condition in ('unavailable','timed_out') else 'exited',
                            'exit_code': 1 if not version and condition == 'failed' else 0,
                            'stdout':'pinned' if version else '' if condition == 'empty' else 'verification results:: 1 verified, 0 errors', 'stderr':''}
                with patch.object(verify, 'run_process', side_effect=process), contextlib.redirect_stdout(io.StringIO()):
                    code = verify.main(['verus','--cwd',str(root),'--scope','target.rs','--proof-target','target.rs',
                                        '--tool','verus','--expect-version','pinned','--output',str(output)])
                self.assertNotEqual(code, 0)
                self.assertNotEqual(json.loads(output.read_text())['status'], 'passed')

    def test_proof_failures_keep_property_setup_unknown_and_unsupported_distinct(self):
        cases = [
            ('kani', 'VERIFICATION:- FAILED\n- Status: FAILURE', 'property_violation'),
            ('verus', 'error: postcondition not satisfied', 'property_violation'),
            ('gobra', 'Postcondition might not hold.', 'property_violation'),
            ('verus', 'error[E0425]: cannot find value', 'harness_or_environment'),
            ('kani', 'error: Failed to invoke goto-cc', 'harness_or_environment'),
            ('kani', 'VERIFICATION:- UNKNOWN', 'solver_unknown'),
            ('gobra', 'unsupported construct in selected target', 'unsupported'),
            ('verus', 'unrecognized diagnostic', 'unclassified_failure'),
        ]
        for kind, raw, expected in cases:
            with self.subTest(kind=kind, raw=raw):
                self.assertEqual(expected, verify.proof_failure(kind, raw))

    def test_completed_go_test_is_selected_evidence(self):
        status, details = verify.go_result(go_events())
        self.assertEqual("passed", status)
        self.assertEqual(1, details["tests"])
        self.assertEqual(1, details["pass"])

    def test_go_failure_cannot_be_overwritten_by_later_pass(self):
        raw = go_events("fail") + "\n" + go_events()
        self.assertEqual("failed", verify.go_result(raw)[0])

    def test_go_skips_cannot_be_overwritten_by_later_pass(self):
        status, details = verify.go_result(go_events("skip") + "\n" + go_events())
        self.assertEqual("required_skipped", status)
        self.assertEqual(["example/p::TestCancel"], details["skipped_tests"])
        self.assertEqual(1, details["skip"])
        package_skip = events({"Action": "start", "Package": "example/p"}, {"Action": "skip", "Package": "example/p"})
        status, details = verify.go_result(package_skip + "\n" + go_events())
        self.assertEqual("required_skipped", status)
        self.assertEqual(["example/p"], details["skipped_packages"])

    def test_unknown_go_actions_cannot_hide_in_passing_stream(self):
        for extra in ({"Action": "mystery", "Package": "example/p"},
                      {"Action": "mystery", "Package": "example/p", "Test": "TestCancel"}):
            with self.subTest(extra=extra):
                status, details = verify.go_result(go_events() + "\n" + events(extra))
                self.assertEqual("incomplete", status)
                self.assertEqual(1, details["malformed_lines"])

    def test_duplicate_active_go_identities_are_incomplete(self):
        for duplicate in ({"Action": "start", "Package": "example/p"},
                          {"Action": "run", "Package": "example/p", "Test": "TestCancel"}):
            rows = [json.loads(line) for line in go_events().splitlines()]
            rows.insert(2, duplicate)
            with self.subTest(duplicate=duplicate):
                status, details = verify.go_result(events(*rows))
                self.assertEqual("incomplete", status)
                self.assertEqual(1, details["malformed_lines"])

    def test_go_parallel_lifecycle_and_output_are_supported(self):
        raw = events(
            {"Action": "start", "Package": "example/p"},
            {"Action": "run", "Package": "example/p", "Test": "TestParallel"},
            {"Action": "output", "Package": "example/p", "Test": "TestParallel", "Output": "fixture"},
            {"Action": "pause", "Package": "example/p", "Test": "TestParallel"},
            {"Action": "cont", "Package": "example/p", "Test": "TestParallel"},
            {"Action": "pass", "Package": "example/p", "Test": "TestParallel"},
            {"Action": "output", "Package": "example/p", "Output": "ok"},
            {"Action": "pass", "Package": "example/p"},
        )
        self.assertEqual("passed", verify.go_result(raw)[0])

    def test_orphan_go_pause_and_cont_are_incomplete(self):
        for action in ("pause", "cont"):
            extra = {"Action": action, "Package": "example/p", "Test": "TestAbsent"}
            with self.subTest(action=action):
                self.assertEqual("incomplete", verify.go_result(go_events() + "\n" + events(extra))[0])

    def test_package_failure_without_test_rows_is_failure(self):
        raw = events({"Action": "fail", "Package": "example/p"})
        self.assertEqual("failed", verify.go_result(raw)[0])

    def test_empty_or_malformed_go_stream_is_incomplete(self):
        for raw in ("", "not-json", "[]", "null", '{"Action":"pass"}'):
            with self.subTest(raw=raw):
                self.assertEqual("incomplete", verify.go_result(raw)[0])

    def test_go_zero_selection_and_skip_are_not_pass(self):
        no_tests = events({"Action": "start", "Package": "example/p"}, {"Action": "pass", "Package": "example/p"})
        self.assertEqual("no_tests", verify.go_result(no_tests)[0])
        status, details = verify.go_result(go_events("skip"))
        self.assertEqual("required_skipped", status)
        self.assertEqual(["example/p::TestCancel"], details["skipped_tests"])

    def test_partial_go_stream_keeps_unfinished_identity(self):
        raw = events({"Action": "start", "Package": "example/p"}, {"Action": "run", "Package": "example/p", "Test": "TestCancel"})
        status, details = verify.go_result(raw)
        self.assertEqual("incomplete", status)
        self.assertEqual([("example/p", "TestCancel")], details["unfinished_tests"])

    def test_passing_package_cannot_hide_an_empty_or_missing_selected_package(self):
        empty_package = events({"Action": "start", "Package": "example/empty"}, {"Action": "pass", "Package": "example/empty"})
        self.assertEqual("no_tests", verify.go_result(go_events() + "\n" + empty_package)[0])
        self.assertEqual("incomplete", verify.go_result(go_events(), {"example/p", "example/missing"})[0])

    def test_native_package_skip_without_tests_is_no_tests(self):
        empty_package = events({"Action": "start", "Package": "example/empty"}, {"Action": "skip", "Package": "example/empty", "Output": "? example/empty [no test files]"})
        status, details = verify.go_result(go_events() + "\n" + empty_package, {"example/p", "example/empty"})
        self.assertEqual("no_tests", status)
        self.assertEqual(["example/empty"], details["packages_without_tests"])

    def test_orphan_terminal_events_are_incomplete(self):
        raw = events({"Action": "pass", "Package": "example/p", "Test": "TestCancel"}, {"Action": "pass", "Package": "example/p"})
        self.assertEqual("incomplete", verify.go_result(raw)[0])

    def test_openspec_requires_exact_named_selection_root_and_counts(self):
        cwd = Path.cwd().resolve()
        valid = {"items": [{"id": "workflow", "type": "change", "valid": True}],
                 "summary": {"totals": {"items": 1, "passed": 1, "failed": 0}},
                 "root": {"path": str(cwd)}}
        self.assertEqual("passed", verify.openspec_result(json.dumps(valid), cwd, "workflow")[0])
        for expected, update in (
            ("no_selection", {"items": []}),
            ("wrong_root", {"root": {"path": str(cwd / "another-root")}}),
            ("wrong_selection", {"items": [{"id": "other", "type": "change", "valid": True}]}),
            ("failed", {"summary": {"totals": {"items": 0, "passed": 0, "failed": 0}}}),
        ):
            with self.subTest(expected=expected):
                self.assertEqual(expected, verify.openspec_result(json.dumps({**valid, **update}), cwd, "workflow")[0])

    def test_bad_openspec_json_is_not_success(self):
        for raw in ("", "not-json", "[]", "null", "{}"):
            with self.subTest(raw=raw):
                self.assertEqual("invalid_output", verify.openspec_result(raw, Path.cwd(), "workflow")[0])

    def test_artifact_is_complete_is_not_task_completion(self):
        raw = json.dumps({"isComplete": True, "changeName": "workflow"})
        self.assertEqual("invalid_output", verify.task_result(raw, Path.cwd(), "workflow")[0])

    def test_static_routes_do_not_launch_cargo_tests_or_install_tools(self):
        for kind in ("cargo-fmt", "cargo-clippy"):
            args = verify.parser().parse_args([kind, "--cwd", ".", "--scope", "privy_gateway", "--output", "unused.json"])
            version, commands = verify.command_plan(args)
            self.assertEqual(["cargo", "fmt" if kind == "cargo-fmt" else "clippy", "--version"], version)
            self.assertNotIn("test", commands[0][1])
            self.assertNotIn("install", commands[0][1])
            if kind == "cargo-clippy":
                self.assertIn("--locked", commands[0][1])
                self.assertIn("--offline", commands[0][1])

    def test_go_routes_require_explicit_packages_and_selector(self):
        common = ["go-test", "--cwd", ".", "--scope", "application", "--output", "unused.json"]
        for extra in ([], ["--package", ""], ["--package", "./application", "--test", "Test"]):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                verify.command_plan(verify.parser().parse_args(common + extra))
        args = verify.parser().parse_args(common + ["--package", "./application", "--test", "^TestCancel$", "--race"])
        _, commands = verify.command_plan(args)
        self.assertEqual(["go", "list", "-f", "{{.ImportPath}}", "./application"], commands[0][1])
        self.assertEqual(["go", "test", "-json", "-count=1", "-timeout", "120s", "-run", "^TestCancel$", "-race", "./application"], commands[1][1])

    def test_subtest_selectors_are_rejected_before_any_child(self):
        for selector in ("^TestParent$/^Known$", "^TestParent$/^Absent$"):
            with self.subTest(selector=selector), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "check.json"
                with patch.object(verify, "run_process") as process, contextlib.redirect_stdout(io.StringIO()):
                    code = verify.main(["go-test", "--cwd", temporary, "--scope", ".", "--output", str(output), "--package", "./example", "--test", selector])
                process.assert_not_called()
                self.assertEqual(1, code)
                report = json.loads(output.read_text())
                self.assertEqual("invalid_configuration", report["status"])
                self.assertIn("exact leaf selection", report["reason"])

    def test_make_preserves_literal_selector_anchor_without_running_recipe(self):
        makefile = (Path(__file__).resolve().parents[1] / "Makefile").read_text()
        recipe = makefile.split("\nverify-go-test:\n", 1)[1].split("\n\n", 1)[0]
        result = subprocess.run(["make", "-f", "-", "-n", "verify-go-test", "VERIFY_TEST=^TestCancel$"],
                                input="verify-go-test:\n" + recipe + "\n", text=True, capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("--test '^TestCancel$'", result.stdout)

    def test_timeout_must_be_finite_positive_before_any_child(self):
        for timeout in ("nan", "inf", "-inf", "0", "-1"):
            with self.subTest(timeout=timeout), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "check.json"
                with patch.object(verify, "run_process") as process, contextlib.redirect_stdout(io.StringIO()):
                    code = verify.main(["cargo-fmt", "--cwd", temporary, "--scope", ".", "--output", str(output), "--timeout=" + timeout])
                process.assert_not_called()
                self.assertEqual(1, code)
                def reject_nonfinite(value):
                    self.fail(f"invalid JSON numeric constant: {value}")
                report = json.loads(output.read_text(), parse_constant=reject_nonfinite)
                self.assertEqual("invalid_configuration", report["status"])
                self.assertIn("finite positive", report["reason"])

    def test_child_environment_disables_rustup_auto_install_without_global_mutation(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ, {"RUSTUP_AUTO_INSTALL": "1"}):
            output = Path(temporary) / "check.json"
            version = {"command": ["cargo", "fmt", "--version"], "status": "exited", "exit_code": 1,
                       "stdout": "", "stderr": "fixture unavailable", "duration_seconds": 0}
            with patch.object(verify, "run_process", return_value=version) as process, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, verify.main(["cargo-fmt", "--cwd", temporary, "--scope", ".", "--output", str(output)]))
            child_env = process.call_args.args[2]
            self.assertEqual("0", child_env["RUSTUP_AUTO_INSTALL"])
            self.assertEqual("true", child_env["CARGO_NET_OFFLINE"])
            self.assertEqual("1", os.environ["RUSTUP_AUTO_INSTALL"])

    def test_native_process_failure_retains_exit_and_output(self):
        result = verify.run_process([sys.executable, "-c", 'print("fixture failed"); raise SystemExit(7)'], Path.cwd(), os.environ.copy(), 5)
        self.assertEqual(7, result["exit_code"])
        self.assertIn("fixture failed", result["stdout"])

    def test_native_process_timeout_is_explicit(self):
        result = verify.run_process([sys.executable, "-c", "import time; time.sleep(10)"], Path.cwd(), os.environ.copy(), 0.05)
        self.assertEqual("timed_out", result["status"])
        self.assertNotEqual(0, result["exit_code"])

    def test_noisy_process_has_bounded_preview_and_complete_file(self):
        size = verify.PREVIEW_BYTES * 3
        result = verify.run_process([sys.executable, "-c", f"import sys; sys.stdout.write('x' * {size})"], Path.cwd(), os.environ.copy(), 5)
        self.assertEqual(verify.PREVIEW_BYTES, len(result["stdout"]))
        self.assertTrue(result["stdout_truncated"])
        self.assertEqual(size, Path(result["stdout_artifact"]).stat().st_size)

    def test_missing_executable_writes_unavailable_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "check.json"
            with contextlib.redirect_stdout(io.StringIO()):
                code = verify.main(["openspec", "--cwd", temporary, "--scope", "openspec", "--change", "workflow", "--output", str(output), "--tool", str(Path(temporary) / "absent")])
            report = json.loads(output.read_text())
            self.assertNotEqual(0, code)
            self.assertEqual("unavailable", report["status"])
            self.assertTrue(Path(report["steps"][0]["stderr_artifact"]).is_file())

    def test_existing_result_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "check.json"
            retained = '{"status":"failed","retained":true}\n'
            output.write_text(retained)
            with patch.object(verify, "run_process") as process, contextlib.redirect_stderr(io.StringIO()):
                code = verify.main(["openspec", "--cwd", temporary, "--scope", "openspec", "--change", "workflow", "--output", str(output)])
            self.assertEqual(2, code)
            process.assert_not_called()
            self.assertEqual(retained, output.read_text())

    def test_output_directory_keeps_every_failed_invocation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "evidence"
            arguments = ["openspec", "--cwd", temporary, "--scope", "openspec", "--change", "workflow", "--output-dir", str(output_dir), "--tool", str(Path(temporary) / "absent")]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(1, verify.main(arguments))
                self.assertEqual(1, verify.main(arguments))
            reports = list(output_dir.glob("*/result.json"))
            self.assertEqual(2, len(reports))
            for path in reports:
                report = json.loads(path.read_text())
                self.assertEqual("unavailable", report["status"])
                self.assertTrue(Path(report["steps"][0]["stderr_artifact"]).is_file())

    def test_nonzero_child_cannot_be_overridden_by_success_looking_json(self):
        """Synthetic process double checks wrapper status precedence, not Go behavior."""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "check.json"
            outputs = [
                {"command": ["go", "version"], "status": "exited", "exit_code": 0, "stdout": "go version fixture", "stderr": "", "duration_seconds": 0},
                {"command": ["go", "list"], "status": "exited", "exit_code": 0, "stdout": "example/p\n", "stderr": "", "duration_seconds": 0},
                {"command": ["go", "test"], "status": "exited", "exit_code": 7, "stdout": go_events(), "stderr": "", "duration_seconds": 0},
            ]
            with patch.object(verify, "run_process", side_effect=outputs), contextlib.redirect_stdout(io.StringIO()):
                code = verify.main(["go-test", "--cwd", temporary, "--scope", "application", "--output", str(output), "--package", "./application", "--test", "^TestCancel$"])
            self.assertNotEqual(0, code)
            report = json.loads(output.read_text())
            self.assertEqual("failed", report["status"])
            self.assertEqual(7, report["steps"][-1]["exit_code"])


if __name__ == "__main__":
    unittest.main()
