import sqlite3
import tempfile
import unittest
from pathlib import Path
from rulegen.database_lifecycle import inspect_database,backup_database,restore_database
from rulegen.functional_registry import FunctionalRegistry

def candidate():
    return {"status":"candidate","name":"inc",
            "definition":{"params":[{"name":"x","type":["Int"]}],
                          "return_type":["Int"],
                          "body":{"op":"call","name":"+",
                                  "args":[{"op":"var","name":"x"},
                                          {"op":"literal","value":1}]}}}

class DatabaseLifecycleTests(unittest.TestCase):
    def test_snapshot_restore_and_operator_reuse(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"source.db"
            snapshot=Path(d)/"snapshot.db"
            restored=Path(d)/"restored.db"
            with FunctionalRegistry(source,tier="algebra") as registry:
                registry.promote(candidate(),[([1],2)],[([4],5)])
                self.assertEqual(inspect_database(registry.db)["integrity"],"ok")
            backup_database(source,snapshot)
            restore_database(snapshot,restored)
            with FunctionalRegistry(restored,tier="algebra") as registry:
                self.assertIn("inc",registry.active())
                self.assertEqual(registry.evidence_ledger.count("validation"),1)
                self.assertEqual(registry.core().execute(
                    {"op":"call","name":"inc","args":[{"op":"literal","value":6}]}),7)
            with self.assertRaises(FileExistsError):
                restore_database(snapshot,restored)

    def test_unknown_version_rejected_without_modification(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"old.db"
            with FunctionalRegistry(path) as registry:
                registry.db.execute("UPDATE rg_metadata SET value='999' WHERE key='schema_version'")
                registry.db.commit()
                with self.assertRaises(ValueError):
                    inspect_database(registry.db)
            with self.assertRaises(ValueError):
                backup_database(path,Path(d)/"copy.db")
            self.assertFalse((Path(d)/"copy.db").exists())

    def test_malformed_table_rejected(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE functional_operators(name TEXT)")
            with self.assertRaises(ValueError):
                inspect_database(db)

    def test_legacy_unversioned_database_supported(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE operators(name TEXT,body TEXT,args TEXT,output TEXT,evidence TEXT,status TEXT)")
            self.assertIsNone(inspect_database(db)["evidence_schema_version"])

if __name__=="__main__":unittest.main()
