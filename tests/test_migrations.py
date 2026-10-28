import sqlite3
import tempfile
import unittest
from pathlib import Path
from rulegen.functional_registry import FunctionalRegistry
from rulegen.migrations import apply_migrations,plan_migrations
from rulegen.database_lifecycle import backup_database

class MigrationTests(unittest.TestCase):
    def test_explicit_migration_idempotent_and_preserves_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"operators.db"
            with FunctionalRegistry(source) as lib:
                lib.evidence_ledger.append("validation","test",{"id":1},{"ok":True})
                before=plan_migrations(lib.db)
                self.assertEqual(before["pending"],[1])
                self.assertEqual(apply_migrations(lib.db)["pending"],[])
                self.assertEqual(apply_migrations(lib.db)["pending"],[])
                self.assertEqual(lib.evidence_ledger.count(),1)
            backup_database(source,Path(d)/"backup.db")
            with FunctionalRegistry(source) as lib:
                self.assertEqual(plan_migrations(lib.db)["current"],1)
                self.assertEqual(lib.evidence_ledger.count(),1)

    def test_transaction_failure_rolls_back(self):
        with sqlite3.connect(":memory:") as db:
            # An unsupported evidence version must fail without migration side effects.
            db.execute("CREATE TABLE rg_metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)")
            db.execute("INSERT INTO rg_metadata VALUES('schema_version','999')")
            with self.assertRaises(ValueError):
                apply_migrations(db)
            self.assertNotIn("rg_platform_schema",
                {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")})

    def test_future_version_rejected(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE rg_platform_schema(version INTEGER PRIMARY KEY,applied_at TEXT NOT NULL)")
            db.execute("INSERT INTO rg_platform_schema VALUES(2,'now')")
            db.commit()
            with self.assertRaises(ValueError):plan_migrations(db)

    def test_migration_requires_idle_connection(self):
        with sqlite3.connect(":memory:") as db:
            db.execute("CREATE TABLE t(x)")
            db.execute("INSERT INTO t VALUES(1)")
            with self.assertRaises(RuntimeError):apply_migrations(db)
            db.rollback()

if __name__=="__main__":unittest.main()
