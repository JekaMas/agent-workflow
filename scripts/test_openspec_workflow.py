"""Real OpenSpec CLI integration over explicitly synthetic repository fixtures.

These disposable projects prove local workflow mechanics only. They are not
Smart Example implementation, production, external-service, or readiness proof.
No product change is created or archived, and the archive command is never run.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


WRAPPER = Path(__file__).with_name("local_verify.py").resolve()
PROJECT_CONFIG = Path(os.environ.get("LOCAL_VERIFY_PROJECT_CONFIG", str(WRAPPER.parent.parent / "openspec" / "config.yaml")))
CHANGE = "workflow-mechanics"
CONTEXT = "This disposable project verifies local workflow mechanics only."
PROPOSAL_RULE = "State the local evidence boundary in the proposal."
ARTIFACT_RULES = {
    "proposal": PROPOSAL_RULE,
    "specs": "Describe observable behavior in the local fixture specification.",
    "design": "Describe the disposable fixture ownership in the design.",
    "tasks": "Give each fixture task an explicit verification statement.",
}
APPLY_GUIDANCE = "Record local checks separately from operational readiness."
ARCHIVE_GUIDANCE = "Retain unresolved verification work before archival."

PROPOSAL = """# Proposal

## Why

This disposable fixture establishes observable local workflow mechanics without
claiming product implementation, external-service, or readiness evidence.

## What Changes

- Add one workflow mechanics capability for this isolated fixture.

## Capabilities

### New Capabilities

- workflow-mechanics: local validation fixture behavior.

### Modified Capabilities

None.

## Impact

Only this disposable fixture is affected.
"""

DESIGN = """# Design

## Context

An isolated integration fixture exercises the real installed OpenSpec CLI.

## Decisions

Keep every generated file inside the temporary project.
"""

SPEC = """# Spec Delta

## Purpose

Provide observable fixture behavior for local OpenSpec workflow validation
without claiming Smart Example implementation or operational readiness.

## ADDED Requirements

### Requirement: Report local validation outcome

The fixture SHALL report whether its local validation succeeded.

#### Scenario: Valid fixture

- **WHEN** the valid fixture is inspected
- **THEN** the local validation reports success
"""


def child_environment() -> dict[str, str]:
    """Use installed tools without inheriting credentials or enabling telemetry."""
    environment = {
        key: os.environ[key]
        for key in ("PATH", "HOME", "USER", "TMPDIR", "XDG_CONFIG_HOME", "XDG_DATA_HOME")
        if key in os.environ
    }
    environment.update(
        OPENSPEC_TELEMETRY="0",
        DO_NOT_TRACK="1",
        OPENSPEC_NO_UPDATE_CHECK="1",
    )
    return environment


class OpenSpecWorkflowIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("OPENSPEC_BIN") or shutil.which("openspec")
        if not configured:
            raise RuntimeError("OpenSpec 1.13.1 is required; integration checks were not run")
        cls.tool = str(Path(configured).absolute())
        if not Path(cls.tool).is_file():
            raise RuntimeError(f"OpenSpec executable is unavailable: {cls.tool}")

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="openspec-workflow-integration-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.change = self.root / "openspec" / "changes" / CHANGE
        self.result_number = 0

    def project(self, *, populated: bool = True, complete: bool = True) -> None:
        (self.root / "openspec" / "specs").mkdir(parents=True)
        self.change.mkdir(parents=True)
        rules = "".join(
            f"  {artifact}:\n    - {json.dumps(rule)}\n"
            for artifact, rule in ARTIFACT_RULES.items()
        )
        config = (
            "schema: spec-driven\n"
            f"context: {json.dumps(CONTEXT)}\n"
            "rules:\n"
            f"{rules}"
            "operations:\n"
            "  apply:\n"
            "    guidance:\n"
            f"      - {json.dumps(APPLY_GUIDANCE)}\n"
            "  archive:\n"
            "    guidance:\n"
            f"      - {json.dumps(ARCHIVE_GUIDANCE)}\n"
        )
        (self.root / "openspec" / "config.yaml").write_text(config, encoding="utf-8")
        (self.change / ".openspec.yaml").write_text(
            "schema: spec-driven\ncreated: 2026-09-20\n", encoding="utf-8"
        )
        if not populated:
            return
        (self.change / "proposal.md").write_text(PROPOSAL, encoding="utf-8")
        (self.change / "design.md").write_text(DESIGN, encoding="utf-8")
        marker = "x" if complete else " "
        (self.change / "tasks.md").write_text(
            "# Tasks\n\n## 1. Validation\n\n"
            f"- [{marker}] 1.1 Define the fixture and verify strict native validation succeeds.\n",
            encoding="utf-8",
        )
        capability = self.change / "specs" / "workflow-mechanics"
        capability.mkdir(parents=True)
        (capability / "spec.md").write_text(SPEC, encoding="utf-8")

    def native(self, *arguments: str) -> dict:
        result = subprocess.run(
            [self.tool, *arguments],
            cwd=self.root,
            env=child_environment(),
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr[-1500:])
        return json.loads(result.stdout)

    def verify(
        self, *, change: str = CHANGE, require_complete: bool = False,
        require_guidance: bool = False,
    ) -> tuple[int, dict]:
        self.result_number += 1
        output = self.root / "evidence" / f"result-{self.result_number}.json"
        command = [
            sys.executable, "-B", str(WRAPPER), "openspec",
            "--cwd", str(self.root), "--change", change,
            "--scope", f"openspec/changes/{change}/proposal.md",
            "--output", str(output), "--timeout", "30", "--tool", self.tool,
        ]
        if require_complete:
            command.append("--require-tasks-complete")
        if require_guidance:
            command.append("--require-project-guidance")
        result = subprocess.run(
            command,
            cwd=self.root,
            env=child_environment(),
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        self.assertTrue(output.is_file(), result.stderr[-1500:])
        return result.returncode, json.loads(output.read_text(encoding="utf-8"))

    def assert_rejected(self, result: tuple[int, dict]) -> dict:
        code, manifest = result
        self.assertNotEqual(code, 0, manifest)
        self.assertNotEqual(manifest["status"], "passed", manifest)
        return manifest

    def test_valid_complete_change_passes_local_boundary(self) -> None:
        self.project()
        code, manifest = self.verify(require_complete=True, require_guidance=True)
        self.assertEqual(code, 0, manifest)
        self.assertEqual(manifest["status"], "passed", manifest)

    def test_missing_change_is_rejected(self) -> None:
        self.project()
        self.assert_rejected(self.verify(change="missing-change"))

    def test_empty_change_is_rejected(self) -> None:
        self.project(populated=False)
        self.assert_rejected(self.verify())

    def test_malformed_delta_is_rejected(self) -> None:
        self.project()
        delta = self.change / "specs" / "workflow-mechanics" / "spec.md"
        delta.write_text(
            SPEC.replace("#### Scenario: Valid fixture", "### Scenario: Invalid heading"),
            encoding="utf-8",
        )
        self.assert_rejected(self.verify())

    def test_empty_task_list_is_not_completion(self) -> None:
        self.project()
        (self.change / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        status = self.native("status", "--change", CHANGE, "--json")
        self.assertTrue(status["isComplete"])
        self.assert_rejected(self.verify(require_complete=True))

    def test_artifact_completion_does_not_allow_incomplete_task_closure(self) -> None:
        self.project(complete=False)
        before = {str(p.relative_to(self.root)): p.read_bytes()
                  for p in (self.root / "openspec").rglob("*") if p.is_file()}
        status = self.native("status", "--change", CHANGE, "--json")
        self.assertTrue(status["isComplete"])
        self.assertTrue(status["isPlanningComplete"])
        apply = self.native("instructions", "apply", "--change", CHANGE, "--json")
        self.assertEqual(apply["progress"], {"total": 1, "complete": 0, "remaining": 1})
        self.assertEqual(apply["state"], "ready")
        code, structural = self.verify()
        self.assertEqual(code, 0, structural)
        self.assertEqual(structural["status"], "passed", structural)
        closure = self.assert_rejected(self.verify(require_complete=True))
        self.assertEqual(closure["status"], "incomplete_tasks", closure)
        after = {str(p.relative_to(self.root)): p.read_bytes()
                 for p in (self.root / "openspec").rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertFalse((self.root / "openspec" / "changes" / "archive").exists())

    def test_project_inputs_reach_native_artifact_apply_and_archive_instructions(self) -> None:
        self.project()
        for artifact, rule in ARTIFACT_RULES.items():
            with self.subTest(artifact=artifact):
                instructions = self.native(
                    "instructions", artifact, "--change", CHANGE, "--json"
                )
                self.assertEqual(instructions["context"], CONTEXT)
                self.assertEqual(instructions["rules"], [rule])
        for operation, guidance in (("apply", APPLY_GUIDANCE), ("archive", ARCHIVE_GUIDANCE)):
            with self.subTest(operation=operation):
                instructions = self.native(
                    "instructions", operation, "--change", CHANGE, "--json"
                )
                self.assertEqual(instructions["changeName"], CHANGE)
                self.assertEqual(instructions["context"], CONTEXT)
                self.assertEqual(instructions["operationGuidance"], [guidance])
                self.assertNotIn("rules", instructions)
                self.assertEqual(Path(instructions["root"]["path"]), self.root)

    def test_missing_project_guidance_is_rejected_when_required(self) -> None:
        self.project()
        (self.root / "openspec" / "config.yaml").write_text(
            "schema: spec-driven\n", encoding="utf-8"
        )
        self.assert_rejected(self.verify(require_guidance=True))

    def test_repository_config_delivers_required_guidance_in_disposable_project(self) -> None:
        self.project()
        (self.root / "openspec" / "config.yaml").write_bytes(PROJECT_CONFIG.read_bytes())
        code, manifest = self.verify(require_complete=True, require_guidance=True)
        self.assertEqual(code, 0, manifest)
        self.assertEqual(manifest["status"], "passed", manifest)

    def test_wrong_typed_operation_guidance_is_rejected_when_required(self) -> None:
        self.project()
        config = self.root / "openspec" / "config.yaml"
        text = config.read_text(encoding="utf-8")
        old = f"  archive:\n    guidance:\n      - {json.dumps(ARCHIVE_GUIDANCE)}\n"
        self.assertIn(old, text)
        config.write_text(
            text.replace(old, "  archive:\n    guidance: not-a-list\n"), encoding="utf-8"
        )
        self.assert_rejected(self.verify(require_guidance=True))


if __name__ == "__main__":
    unittest.main()
