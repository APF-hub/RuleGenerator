"""Platform P2: conservative SQLite compatibility, integrity and backup utilities.

Existing databases have legacy unversioned operator tables and an M68 ledger.
No destructive migrations or silent schema upgrades are performed here.
"""
import sqlite3
from pathlib import Path

KNOWN_TABLES={
    "functional_operators":{"name","definition","evidence","status"},
    "operators":{"name","body","args","output","evidence","status"},
    "failures":{"scope","candidate","reason"},
    "rg_metadata":{"key","value"},
    "rg_evidence":{"id","kind","scope","candidate","payload","created_at"},
    "reconstruction_experiments":{"id","adapter","observation_sha256",
                                  "program","loss","evaluations","budget","created_at"},
}
EVIDENCE_VERSION=1

def inspect_database(connection):
    """Read-only schema check; fail closed on incompatible known tables."""
    tables={row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    for table,required in KNOWN_TABLES.items():
        if table in tables:
            actual={row[1] for row in connection.execute("PRAGMA table_info("+table+")")}
            if not required<=actual:
                raise ValueError("incompatible schema: "+table)
    if "rg_evidence" in tables and "rg_metadata" not in tables:
        raise ValueError("evidence metadata missing")
    if "rg_metadata" in tables:
        row=connection.execute(
            "SELECT value FROM rg_metadata WHERE key='schema_version'").fetchone()
        if row is None or row[0]!=str(EVIDENCE_VERSION):
            raise ValueError("unsupported evidence schema version")
    check=connection.execute("PRAGMA quick_check").fetchone()
    if check is None or check[0]!="ok":
        raise ValueError("database integrity check failed")
    return {"integrity":"ok","evidence_schema_version":
            EVIDENCE_VERSION if "rg_metadata" in tables else None,
            "known_tables":sorted(tables.intersection(KNOWN_TABLES))}

def backup_database(source,destination):
    """Create consistent SQLite snapshot; never overwrite a destination."""
    src=Path(source)
    dst=Path(destination)
    if not src.is_file():raise FileNotFoundError(src)
    if dst.exists():raise FileExistsError(dst)
    if src.resolve()==dst.resolve():raise ValueError("source and destination match")
    dst.parent.mkdir(parents=True,exist_ok=True)
    # URI read-only mode prevents implicit creation of missing source databases.
    with sqlite3.connect(src.resolve().as_uri()+"?mode=ro",uri=True) as origin:
        inspect_database(origin)
        try:
            with sqlite3.connect(dst) as target:
                origin.backup(target)
                inspect_database(target)
        except BaseException:
            dst.unlink(missing_ok=True)
            raise
    return str(dst)

def restore_database(snapshot,destination):
    """Restore to a NEW database path only, retaining snapshot unchanged."""
    return backup_database(snapshot,destination)
