#!/usr/bin/env python3
"""Prove no stale "turns flow" licence survives in the workflow or its consumers.

Scans every tracked text file for wording that could license stopping, deferring
or asking for a decision outside the three allowed stops. A hit is accepted only
when the same line states the new rule (not-a-stop / never-a-blocker / no-partial
/ exactly-three / decision-the-artifacts-cannot-answer); everything else is
reported as a finding so it must be removed or explicitly justified.

Usage: python3 -B scripts/flow_alignment_scan.py [root ...]
Exit code: 0 when no unjustified hit remains, 1 otherwise.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

BANNED = {
    "turn-as-stop": re.compile(r"\bturn\b", re.I),
    "session-as-stop": re.compile(r"fresh session|separate session|next session", re.I),
    "context-as-limit": re.compile(r"context (window|budget)|working memory limit|effort budget", re.I),
    "pause": re.compile(r"\bpaused?\b|\bpausing\b", re.I),
    "defer": re.compile(r"\bdefer(red|ral)?\b", re.I),
    "handoff-as-stop": re.compile(r"hand ?off", re.I),
    "vague-blocker": re.compile(r"genuine blocker|blocker remains", re.I),
    "stage-stop": re.compile(r"stop at a chosen stage|stop at any stage|chosen stage", re.I),
    "partial-accepted": re.compile(r"partial (landing|fix|result)s? (is|are) (acceptable|accepted)|accept (a |the )?partial", re.I),
    "ask-out-of-scope": re.compile(r"ask (the )?user (for|whether|if)", re.I),
    "budget-stop": re.compile(r"exhausted budget|budget (is )?exhaust", re.I),
}

# A hit is allowed when the same line restates the new default.
ALLOW = re.compile(
    r"not a stop|never a blocker|no partial|exactly three|three stop|"
    r"cannot answer|artifacts do not|does not create stop|resumes? from the recorded|"
    r"continue in the next turn|reporting progress rather than declaring|"
    r"absolute DONE|DONE — no partials|no partials",
    re.I,
)

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "testdata"}
# Historical change records quote the old wording; the ledger names removed
# phrases; local_verify.py uses "pause"/"cont" as CLI verbs. None are live rules.
SKIP_PREFIXES = ("openspec/changes/",)
SKIP_FILES = {"docs/flow-alignment-ledger.md", "scripts/flow_alignment_scan.py"}
# Context-dependent markers that are technical terms, not flow licences.
TECHNICAL = re.compile(
    r"\bturn (each|contracts|rows|it|them|the|a|into|incomplete)\b|fuzz handoff|"
    r"\bdefer [a-z]|retry budget|role handoffs|without .*handoff|Completion and handoff|"
    r"handoff boundaries|handoff\b.*artifact|\bpause\b.*\{|\"pause\"",
    re.I,
)
CLI_VERB = re.compile(r'"pause"|"cont"|\bpause\b.*\{"')
TEXT_SUFFIX = {".md", ".py", ".yaml", ".yml", ".json", ".txt", ".sh", ".toml", ".cfg", ".mdc"}


def tracked_files(root: pathlib.Path) -> list[pathlib.Path]:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True
        ).stdout.splitlines()
    except Exception:
        return [p for p in root.rglob("*") if p.is_file()]

    files = []
    for rel in out:
        p = root / rel
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIX:
            continue
        rel = str(p.relative_to(root))
        if rel in SKIP_FILES or rel.startswith(SKIP_PREFIXES):
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        files.append(p)
    return files


JUSTIFIED = [
    ("runtime/GC term", re.compile(r"pause/assist|paused parallel|Paused parallel test|panic/defer/error", re.I)),
    ("internal skill routing", re.compile(r"hand off to|diagnostic handoff", re.I)),
    ("authorized handoff artifact", re.compile(r"handoff\.md|explicit handoff|For explicit handoffs", re.I)),
    ("negated ceremony", re.compile(r"role handoff|without requiring|do not impose|No fixed checkpoint count|do not impose a separate", re.I)),
    ("evidence batching guidance", re.compile(r"verification, pause or handoff|handoff boundaries", re.I)),
    ("negated ceremony", re.compile(r"not a (separate )?handoff|stage is not a handoff|is not a h", re.I)),
    ("missing external prerequisite", re.compile(r"deferral reason|missing prerequisite", re.I)),
    ("test-concept handoff", re.compile(r"regression handoff|fuzz handoff", re.I)),
    ("verb 'turn'", re.compile(r"\bturn (an|incomplete|it|the|a|each|contracts|rows|them|into|an L1)\b", re.I)),
    ("runtime GC term", re.compile(r"pause/latency|pause/assist|GC CPU/assists", re.I)),
    ("authorized handoff artifact", re.compile(r"authorizes a handoff|task authorizes", re.I)),
    ("verb 'turn' (wrapped)", re.compile(r"do not turn|must not turn|can turn|\bturn$", re.I)),
]


def classify(line: str) -> str | None:
    for label, regex in JUSTIFIED:
        if regex.search(line):
            return label
    return None


def scan(root: pathlib.Path) -> tuple[int, list[tuple[str, int, str, str]], list[tuple[str, str, int, str]]]:
    findings = []
    justified = []
    scanned = 0
    for path in tracked_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        scanned += 1
        lines = text.splitlines()
        # Allow when the surrounding paragraph states the new default, so rules
        # wrapped across lines are recognised instead of re-reported.
        block_of = {}
        block_start = 0
        for i, line in enumerate(lines):
            if not line.strip():
                block_start = i + 1
            block_of[i] = block_start
        blocks = {}
        for i, start in block_of.items():
            blocks.setdefault(start, []).append(lines[i])
        allowed_blocks = {
            start for start, body in blocks.items() if ALLOW.search(" ".join(body))
        }
        for lineno, line in enumerate(lines, start=1):
            if CLI_VERB.search(line) or TECHNICAL.search(line):
                continue
            for name, regex in BANNED.items():
                if regex.search(line) and block_of[lineno - 1] not in allowed_blocks:
                    label = classify(line)
                    if label:
                        justified.append((label, name, lineno, f"{path.relative_to(root)}:{lineno}"))
                    else:
                        findings.append((name, lineno, str(path.relative_to(root)), line.strip()[:150]))
    return scanned, findings, justified


def main(argv: list[str]) -> int:
    roots = [pathlib.Path(a).resolve() for a in argv[1:]] or [pathlib.Path(".").resolve()]
    total_findings = 0
    for root in roots:
        scanned, findings, justified = scan(root)
        total_findings += len(findings)
        print(f"== {root}")
        print(f"   files scanned: {scanned}   hard findings: {len(findings)}   justified technical markers: {len(justified)}")
        for label, name, lineno, where in justified:
            print(f"   justified [{label}] {where} ({name})")
        for name, lineno, rel, line in findings[:40]:
            print(f"   [{name}] {rel}:{lineno}: {line}")
        if len(findings) > 40:
            print(f"   ... {len(findings) - 40} more")
    print("RESULT:", "clean — no unjustified stale flow wording" if total_findings == 0 else f"{total_findings} findings to remove or justify")
    return 0 if total_findings == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
