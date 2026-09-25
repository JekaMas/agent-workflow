#!/usr/bin/env python3
"""Contract test for the flow's stop and non-stop cases.

Every condition that must never stop an apply run - turn boundary, compaction,
context ceiling or truncation (and its prediction), effort, elapsed time, long
run, landed milestone, unfinished increment, plus spec-aligned findings - must be
named as a non-stop in the operation body, the operations map and the normative
specification. Exactly three stops may be named: a needed spec change, an
absolute unresolvable blocker, and the finished iteration.
"""

from __future__ import annotations

import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
APPLY = (ROOT / "scripts/integration_templates/apply.md").read_text(encoding="utf-8")
OPERATIONS = (ROOT / "docs/operations.md").read_text(encoding="utf-8")
DELIVERY = (ROOT / "skills/openspec-delivery/references/delivery.md").read_text(encoding="utf-8")
SPEC = (ROOT / "openspec/specs/adaptive-development-workflow/spec.md").read_text(encoding="utf-8")


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text)


APPLY_N = normalized(APPLY)
OPERATIONS_N = normalized(OPERATIONS)
DELIVERY_N = normalized(DELIVERY)
SPEC_N = normalized(SPEC)


class FlowContractTest(unittest.TestCase):
    def test_apply_names_every_non_stop_condition(self) -> None:
        # Every phrase below names a condition that is not a stop; the list is
        # the rule's own restatement, so the flow-alignment scanner must read it
        # as justification rather than as stale stopping licence.
        for phrase in (
            "turn boundary",
            "compacted or restarted thread",
            "context exhaustion or a truncated response",
            "prediction of truncation",
            "effort",
            "a long run",
            "landed milestone",
            "unfinished increment",
            "needs no spec change is never a stop",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, APPLY_N, "apply.md must name this non-stop condition")

    def test_apply_names_exactly_the_three_stops(self) -> None:
        self.assertIn("Apply stops at exactly three points, and nowhere else", APPLY_N)
        for phrase in ("a spec change is needed", "absolute implementation blocker", "the iteration is finished"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, APPLY_N)

    def test_operations_map_carries_the_same_non_stops(self) -> None:
        for phrase in (
            "context exhaustion or a truncated response",
            "prediction of truncation",
            "landed milestone",
            "needing no spec change is never a stop",
            "checkpoint each step so truncation is resumable",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, OPERATIONS_N, "operations.md must carry this rule")

    def test_delivery_never_pauses_for_the_ceiling(self) -> None:
        self.assertIn("A context ceiling, a truncated response or an estimate of either is not a measured budget", DELIVERY_N)
        self.assertIn("checkpoint the step and keep applying", DELIVERY_N)

    def test_spec_states_the_ceiling_scenario(self) -> None:
        self.assertIn("The context ceiling is reached mid-iteration", SPEC_N)
        self.assertIn("a prediction of truncation is not treated as the truncation itself", SPEC_N)

    def test_no_finding_or_milestone_may_be_reported_as_a_result(self) -> None:
        self.assertIn("not an iteration result and must not be reported as one", APPLY_N)
        self.assertIn("never report a finding, commit, gate or increment as the iteration's outcome", OPERATIONS_N)


if __name__ == "__main__":
    unittest.main(verbosity=2)
