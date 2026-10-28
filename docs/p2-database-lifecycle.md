# P2 platform: database lifecycle baseline

`rulegen.database_lifecycle` provides:

- `inspect_database(connection)`: checks known-table column contracts,
  supported M68 evidence schema version (1), and SQLite quick integrity.
  It is read-only and never upgrades a database.
- `backup_database(source,destination)`: uses SQLite's online backup API
  for a consistent snapshot, including WAL-backed source databases.
- `restore_database(snapshot,destination)`: restores only to a new path,
  preserving the snapshot and refusing to overwrite existing data.

The regression suite checks operator and evidence preservation across
snapshot/restore, legacy unversioned operator-table compatibility, malformed
schemas, and unsupported evidence versions.

## Operator runbook

1. Stop writes when practical, or use the SQLite online snapshot API.
2. Back up the source to a **new** path; retain an independent copy.
3. Validate the backup and restore it to a new test path.
4. Reopen the restored registry and confirm active operators and evidence.
5. Never replace a live database file in place while connections are open.

## Remaining platform gates

This milestone is a **compatibility and recovery baseline**, not a migration
framework. No automatic schema migrations, schema-history table, cross-version
upgrade path, encryption, retention policy, external backup scheduling,
or multi-process writer coordination are implemented. Database file permissions
and operational backup retention remain operator responsibilities.
