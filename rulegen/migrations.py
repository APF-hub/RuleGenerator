"""P4: explicit, non-destructive, transactionally applied platform migrations.

This version track is independent of the M68 evidence schema version.
No migration runs implicitly when a registry is opened.
"""
import sqlite3
from .database_lifecycle import inspect_database

PLATFORM_VERSION=1

def _version(connection):
    tables={row[0] for row in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    if "rg_platform_schema" not in tables:return 0
    cols={row[1] for row in connection.execute("PRAGMA table_info(rg_platform_schema)")}
    if cols!={"version","applied_at"}:
        raise ValueError("incompatible platform migration table")
    rows=connection.execute("SELECT version FROM rg_platform_schema ORDER BY version").fetchall()
    if not rows or rows!=[(v,) for v in range(1,rows[-1][0]+1)]:
        raise ValueError("invalid platform migration history")
    if rows[-1][0]>PLATFORM_VERSION:
        raise ValueError("future platform schema version")
    return rows[-1][0]

def plan_migrations(connection):
    """Inspect only; no schema or metadata mutations."""
    inspect_database(connection)
    current=_version(connection)
    return {"current":current,"target":PLATFORM_VERSION,
            "pending":list(range(current+1,PLATFORM_VERSION+1))}

def apply_migrations(connection):
    """Apply explicitly with atomic rollback on failure.

    Caller must back up the database before invoking this function.
    This API deliberately refuses to join an existing write transaction.
    """
    if connection.in_transaction:
        raise RuntimeError("migration requires an idle connection")
    plan=plan_migrations(connection)
    if not plan["pending"]:return plan
    connection.execute("BEGIN IMMEDIATE")
    try:
        # v1: metadata-only baseline. Existing operator and evidence tables
        # remain untouched and retain their original versions.
        connection.execute("""CREATE TABLE rg_platform_schema(
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
        connection.execute("INSERT INTO rg_platform_schema(version) VALUES (1)")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    return plan_migrations(connection)
