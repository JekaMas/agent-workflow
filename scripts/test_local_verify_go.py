"""Opt-in real Go adapter experiment over disposable, synthetic local packages.

No Smart package or dependency is loaded. These cases prove event/exit handling,
not product behavior, race freedom or deployment readiness.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


WRAPPER = Path(__file__).with_name("local_verify.py").resolve()
TEST_SOURCE = """package sample
import "testing"
func TestPass(t *testing.T) {}
func TestFail(t *testing.T) { t.Fatal("deliberate local adapter witness") }
func TestSkip(t *testing.T) { t.Skip("deliberate required-case skip") }
func TestParent(t *testing.T) { t.Run("Present", func(t *testing.T) {}) }
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--go-tool", default="go")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = {key: os.environ[key] for key in ("PATH", "HOME", "TMPDIR") if key in os.environ}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    cases = [
        ("passing", "^TestPass$", ["./sample"], "passed"),
        ("failing", "^TestFail$", ["./sample"], "failed"),
        ("skipped", "^TestSkip$", ["./sample"], "required_skipped"),
        ("zero-selection", "^TestAbsent$", ["./sample"], "no_tests"),
        ("partial-package-selection", "^TestPass$", ["./sample", "./empty"], "no_tests"),
        ("parent-all-children", "^TestParent$", ["./sample"], "passed"),
        ("unsupported-missing-child", "^TestParent$/^Absent$", ["./sample"], "invalid_configuration"),
        ("unsupported-present-child", "^TestParent$/^Present$", ["./sample"], "invalid_configuration"),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="local-verify-real-go-") as directory:
        root = Path(directory)
        (root / "go.mod").write_text("module example.test/workflowfixture\n\ngo 1.20\n")
        (root / "sample").mkdir()
        (root / "sample" / "sample_test.go").write_text(TEST_SOURCE)
        (root / "empty").mkdir()
        (root / "empty" / "empty.go").write_text("package empty\n")
        for name, selector, packages, expected in cases:
            record = output / f"{name}.json"
            command = [sys.executable, "-B", str(WRAPPER), "go-test", "--cwd", str(root),
                       "--scope", ".", "--tool", args.go_tool, "--test", selector,
                       "--output", str(record), "--timeout", "60"]
            for package in packages:
                command.extend(["--package", package])
            process = subprocess.run(command, env=env, capture_output=True, text=True, timeout=150)
            observed = json.loads(record.read_text()) if record.is_file() else {}
            status = observed.get("status", "missing_result")
            correct = status == expected and process.returncode == (0 if expected == "passed" else 1)
            results.append({"case": name, "expected": expected, "observed": status,
                            "wrapper_exit": process.returncode, "matched": correct,
                            "artifact": str(record)})
    result = {"status": "passed" if all(item["matched"] for item in results) else "failed",
              "claim": "real Go over synthetic disposable packages; adapter behavior only",
              "cases": results}
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
