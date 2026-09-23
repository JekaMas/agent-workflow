"""Bounded process execution with process-group cleanup and complete artifacts."""

from __future__ import annotations

import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time


PREVIEW_BYTES = 64 * 1024


def run_process(
    command: list[str],
    cwd: Path,
    env: dict[str, str],
    timeout: float,
    artifact_prefix: Path | None = None,
) -> dict[str, object]:
    """Run one command without leaking descendants or truncating retained output."""

    started = time.monotonic()
    prefix = artifact_prefix or Path(tempfile.mkdtemp(prefix="local-verify-")) / "process"
    prefix.parent.mkdir(parents=True, exist_ok=True)
    stdout_path = Path(f"{prefix}.stdout.log")
    stderr_path = Path(f"{prefix}.stderr.log")
    status = "exited"
    exit_code: int | None = None
    with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=env,
                stdout=stdout_file,
                stderr=stderr_file,
                start_new_session=True,
            )
            try:
                exit_code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                status = "timed_out"
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                exit_code = process.wait()
        except OSError as error:
            status = "unavailable"
            stderr_file.write(str(error).encode())

    result: dict[str, object] = {
        "command": command,
        "exit_code": exit_code,
        "status": status,
        "duration_seconds": time.monotonic() - started,
    }
    for stream, path in (("stdout", stdout_path), ("stderr", stderr_path)):
        with path.open("rb") as source:
            preview = source.read(PREVIEW_BYTES)
        result[stream] = preview.decode("utf-8", errors="replace")
        result[f"{stream}_artifact"] = str(path.resolve())
        result[f"{stream}_truncated"] = path.stat().st_size > PREVIEW_BYTES
    return result
