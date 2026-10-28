import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry
from rulegen.evidence import Evidence


class AtomicSchemaInitTests(unittest.TestCase):
    def test_failure_rolls_back_legacy_and_functional_tables(self):
        for registry in (Registry, FunctionalRegistry):
            with self.subTest(registry=registry.__name__), tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/"db.sqlite"
                with patch.object(Evidence,"__init__",side_effect=RuntimeError("injected failure")):
                    with self.assertRaisesRegex(RuntimeError,"injected failure"):
                        registry(path)
                with sqlite3.connect(path) as db:
                    tables={r[0] for r in db.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'")}
                    self.assertNotIn("operators",tables)
                    self.assertNotIn("functional_operators",tables)
                    self.assertNotIn("failures",tables)
                with registry(path):
                    pass

    def test_evidence_does_not_commit_caller_transaction(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("BEGIN IMMEDIATE")
            Evidence(db)
            self.assertTrue(db.in_transaction)
            db.rollback()
            tables={r[0] for r in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertNotIn("rg_evidence",tables)
            self.assertNotIn("rg_metadata",tables)

    def test_existing_unrelated_data_survives_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"existing.sqlite"
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE keep(value TEXT)")
                db.execute("INSERT INTO keep VALUES ('preserved')")
            with patch.object(Evidence,"__init__",side_effect=RuntimeError("injected failure")):
                with self.assertRaises(RuntimeError):
                    Registry(path)
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT value FROM keep").fetchone()[0],"preserved")
                self.assertIsNone(db.execute(
                    "SELECT name FROM sqlite_master WHERE name='operators'").fetchone())
