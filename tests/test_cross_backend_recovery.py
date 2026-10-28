"""P13: persisted state, restoration and cross-backend isolation."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rulegen.database_lifecycle import backup_database, restore_database, inspect_database
from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry
from rulegen.isolated_synthesis import synthesize_functional_isolated


def increment():
    return {"status":"candidate","name":"inc",
            "definition":{"params":[{"name":"x","type":["Int"]}],
                          "return_type":["Int"],
                          "body":{"op":"call","name":"+",
                                  "args":[{"op":"var","name":"x"},
                                          {"op":"literal","value":1}]}}}


class CrossBackendRecoveryTests(unittest.TestCase):
    def test_recover_both_registries_and_reuse_without_worker_db_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            original=Path(tmp)/"original.db"
            snapshot=Path(tmp)/"snapshot.db"
            restored=Path(tmp)/"restored.db"
            with Registry(original) as legacy:
                self.assertEqual(legacy.active(),{})
            with FunctionalRegistry(original,tier="algebra") as functional:
                functional.promote(increment(),[([1],2)],[([5],6)])
                definitions=functional.active()
                self.assertEqual(functional.evidence_ledger.count("validation"),1)
            backup_database(original,snapshot)
            restore_database(snapshot,restored)
            with Registry(restored) as legacy:
                self.assertEqual(legacy.active(),{})
            with FunctionalRegistry(restored,tier="algebra") as functional:
                self.assertEqual(functional.active(),definitions)
                self.assertEqual(functional.evidence_ledger.count("validation"),1)
                self.assertEqual(inspect_database(functional.db)["integrity"],"ok")
                result=synthesize_functional_isolated(
                    [({"x":3},4),({"x":7},8)],tier="algebra",
                    budget=100,max_nodes=2,definitions=functional.active())
                self.assertIsNotNone(result["program"])

    def test_failed_schema_initialization_preserves_existing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"library.db"
            with FunctionalRegistry(path,tier="algebra") as functional:
                functional.promote(increment(),[([1],2)],[([5],6)])
            from rulegen.evidence import Evidence
            with patch.object(Evidence,"__init__",side_effect=sqlite3.OperationalError("injected")):
                with self.assertRaises(sqlite3.OperationalError):
                    Registry(path)
            with FunctionalRegistry(path,tier="algebra") as functional:
                self.assertIn("inc",functional.active())
                self.assertEqual(functional.evidence_ledger.count("validation"),1)
            with sqlite3.connect(path) as db:
                self.assertIsNone(db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='operators'").fetchone())
