from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts import discovery_ledger


class DiscoveryLedgerTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="discovery-ledger-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.change = "fixture"
        change_root = self.root / "openspec" / "changes" / self.change
        change_root.mkdir(parents=True)
        (change_root / "verification.json").write_text(json.dumps({
            "properties": [{"id": "R1.P1"}],
            "cases": [{"test_id": "example::TestOne"}],
        }))
        self.path = change_root / "discovery.json"
        self.ledger = {
            "schema_version": 1,
            "change": self.change,
            "scope": {"property_ids": ["R1.P1"], "test_ids": ["example::TestOne"]},
            "reviews": [{
                "id": "D1",
                "question": "Find the exact production and proof owners.",
                "property_ids": ["R1.P1"],
                "test_ids": ["example::TestOne"],
                "searches": [
                    {"kind": "exact", "status": "completed", "query": "rg owner", "outcome": "Owner found.", "results": [{"path": "src/owner.go", "line": 4, "classification": "change_candidate", "reason": "Owns behavior."}]},
                    {"kind": "semantic", "status": "completed", "query": "semantic owner", "outcome": "Confirmed owner.", "results": []},
                    {"kind": "jetbrains-index", "status": "unavailable", "query": "references to Owner", "outcome": "No IDE MCP exposed.", "reason": "Capability unavailable in this task.", "results": []},
                ],
                "disposition": "current_change",
                "rationale": "The affected property belongs to this change.",
            }],
        }
        self.write()

    def write(self) -> None:
        self.path.write_text(json.dumps(self.ledger))

    def test_complete_three_lane_discovery_passes(self) -> None:
        result = discovery_ledger.validate(self.root, self.change)
        self.assertEqual("passed", result["status"])
        self.assertEqual(["R1.P1"], result["properties"])

    def test_missing_lane_scope_or_disposition_fails(self) -> None:
        mutations = (
            lambda: self.ledger["reviews"][0]["searches"].pop(),
            lambda: self.ledger["reviews"][0].update(property_ids=[]),
            lambda: self.ledger["reviews"][0].update(disposition="unknown"),
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                original = json.loads(json.dumps(self.ledger))
                mutation()
                self.write()
                with self.assertRaises(discovery_ledger.DiscoveryError):
                    discovery_ledger.validate(self.root, self.change)
                self.ledger = original

    def test_unavailable_exact_search_and_unmapped_identity_fail(self) -> None:
        self.ledger["reviews"][0]["searches"][0].update(status="unavailable", reason="missing")
        self.write()
        with self.assertRaisesRegex(discovery_ledger.DiscoveryError, "exact search must complete"):
            discovery_ledger.validate(self.root, self.change)

        self.ledger["reviews"][0]["searches"][0]["status"] = "completed"
        self.ledger["scope"]["property_ids"] = ["R9.P9"]
        self.write()
        with self.assertRaisesRegex(discovery_ledger.DiscoveryError, "unknown scoped properties"):
            discovery_ledger.validate(self.root, self.change)


if __name__ == "__main__":
    unittest.main()
