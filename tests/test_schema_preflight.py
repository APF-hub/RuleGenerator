import sqlite3
import tempfile
import unittest
from pathlib import Path
from rulegen.engine import Registry
from rulegen.functional_registry import FunctionalRegistry

class SchemaPreflightTests(unittest.TestCase):
    def test_unsupported_evidence_version_rejected_before_registry_writes(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"bad.db"
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE rg_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
                db.execute("INSERT INTO rg_metadata VALUES('schema_version','999')")
            for factory in (Registry,FunctionalRegistry):
                with self.assertRaises(ValueError):
                    factory(path)
            with sqlite3.connect(path) as db:
                names={row[0] for row in db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertNotIn("operators",names)
                self.assertNotIn("functional_operators",names)
                self.assertEqual(db.execute(
                    "SELECT value FROM rg_metadata WHERE key='schema_version'"
                ).fetchone()[0],"999")

    def test_both_backends_initialize_fresh_database(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"fresh.db"
            with Registry(path) as legacy:
                self.assertEqual(legacy.active(),{})
            with FunctionalRegistry(path) as functional:
                self.assertEqual(functional.active(),{})
                self.assertEqual(functional.evidence_ledger.count(),0)

if __name__=="__main__":unittest.main()
