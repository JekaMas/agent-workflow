"""Consumer admission fixtures for the requirement-evidence graph wrapper."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPOSITORY = Path(__file__).resolve().parents[1]
SCRIPT = REPOSITORY / "scripts" / "evidence_graph_check.py"
OWN_CHANGE = "require-executable-requirement-test-matrices"


def call(root: Path, change: str, operation: str, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(SCRIPT), "--root", str(root), "--change", change, operation, *arguments],
        capture_output=True, text=True, check=False)


def payload(process: subprocess.CompletedProcess) -> dict:
    for text in (process.stdout.strip(), process.stderr.strip()):
        if text.startswith("{"):
            return json.JSONDecoder().raw_decode(text)[0]
        if text.splitlines() and text.splitlines()[-1].startswith("{"):
            return json.loads(text.splitlines()[-1])

    raise AssertionError(f"no payload in stdout or stderr; stderr: {process.stderr.strip()}")


class EvidenceGraphCheckTest(unittest.TestCase):
    def test_validate_delegates_to_the_shared_graph(self) -> None:
        process = call(REPOSITORY, OWN_CHANGE, "validate")

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("passed", payload(process)["status"])

    def test_query_reaches_the_shared_executor(self) -> None:
        process = call(REPOSITORY, OWN_CHANGE, "query", "--requirements", "R1")

        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual("R1", payload(process)["requested_selectors"]["requirements"][0])

    def transition_fixture(self, directory: str) -> Path:
        root = Path(directory)
        (root / "openspec" / "changes" / "legacy-change").mkdir(parents=True)
        (root / ".agents").mkdir()
        (root / ".agents" / "evidence-transition.json").write_text(
            json.dumps({"schema": 1, "reason": "fixture", "changes": ["legacy-change"]}), encoding="utf-8")

        return root

    def test_recorded_transition_gap_passes_validation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            validation = call(self.transition_fixture(directory), "legacy-change", "validate")

        self.assertEqual(0, validation.returncode, validation.stderr)
        self.assertEqual("transition_gap", payload(validation)["evidence_graph"])

    def test_recorded_transition_gap_cannot_claim_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            refusal = call(self.transition_fixture(directory), "legacy-change", "ready")

        self.assertEqual(1, refusal.returncode)
        self.assertEqual("transition_gap", payload(refusal)["evidence_graph"])

    def test_unrecorded_change_without_a_graph_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "openspec" / "changes" / "unknown-change").mkdir(parents=True)
            (root / ".agents").mkdir()
            (root / ".agents" / "evidence-transition.json").write_text(
                json.dumps({"schema": 1, "reason": "fixture", "changes": ["another-change"]}), encoding="utf-8")

            process = call(root, "unknown-change", "validate")

        self.assertEqual(1, process.returncode)
        self.assertEqual("missing", payload(process)["evidence_graph"])

    def test_unknown_change_directory_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            process = call(Path(directory), "absent-change", "validate")

        self.assertEqual(2, process.returncode)
        self.assertIn("unknown change", process.stderr)

    def test_unknown_selector_is_refused_by_the_shared_executor(self) -> None:
        process = call(REPOSITORY, OWN_CHANGE, "query", "--properties", "R9.P9")

        self.assertNotEqual(0, process.returncode)
        self.assertEqual("invalid", payload(process)["status"])


if __name__ == "__main__":
    unittest.main()
