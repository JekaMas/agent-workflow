"""Opt-in native Cargo adapter checks using a disposable dependency-free crate.

The fixture proves formatter/Clippy exit handling only. No gateway code, tests,
credentials, registry downloads or live services are used.
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cargo-tool", default="cargo")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = {key: os.environ[key] for key in ("PATH", "HOME", "TMPDIR", "RUSTUP_HOME", "CARGO_HOME") if key in os.environ}
    env.update(PYTHONDONTWRITEBYTECODE="1", CARGO_NET_OFFLINE="true")
    cases = [
        ("bad-format", "cargo-fmt", "pub fn empty(xs:&[u8])->bool{xs.is_empty()}\n", "failed"),
        ("formatted", "cargo-fmt", "pub fn empty(xs: &[u8]) -> bool {\n    xs.is_empty()\n}\n", "passed"),
        ("clippy-warning", "cargo-clippy", "pub fn empty(xs: &[u8]) -> bool {\n    xs.len() == 0\n}\n", "failed"),
        ("clippy-clean", "cargo-clippy", "pub fn empty(xs: &[u8]) -> bool {\n    xs.is_empty()\n}\n", "passed"),
    ]
    results = []
    with tempfile.TemporaryDirectory(prefix="local-verify-real-cargo-") as directory:
        root = Path(directory)
        (root / "src").mkdir()
        (root / "Cargo.toml").write_text('[package]\nname = "workflow-fixture"\nversion = "0.1.0"\nedition = "2021"\n')
        (root / "Cargo.lock").write_text('version = 4\n\n[[package]]\nname = "workflow-fixture"\nversion = "0.1.0"\n')
        for name, kind, source, expected in cases:
            (root / "src" / "lib.rs").write_text(source)
            record = output / f"{name}.json"
            command = [sys.executable, "-B", str(WRAPPER), kind, "--cwd", str(root),
                       "--scope", "src/lib.rs", "--manifest", "Cargo.toml",
                       "--tool", args.cargo_tool, "--output", str(record), "--timeout", "60"]
            process = subprocess.run(command, env=env, capture_output=True, text=True, timeout=90)
            observed = json.loads(record.read_text()) if record.is_file() else {}
            status = observed.get("status", "missing_result")
            correct = status == expected and process.returncode == (0 if expected == "passed" else 1)
            results.append({"case": name, "expected": expected, "observed": status,
                            "wrapper_exit": process.returncode, "matched": correct,
                            "artifact": str(record)})
    result = {"status": "passed" if all(item["matched"] for item in results) else "failed",
              "claim": "native Cargo over a synthetic dependency-free crate; adapter behavior only",
              "cases": results}
    (output / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
