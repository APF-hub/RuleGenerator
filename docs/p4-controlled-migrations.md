# P4 controlled migrations

Platform schema history is independent from evidence schema v1. The read-only plan_migrations reports current, target and pending versions. apply_migrations requires an idle connection and explicitly creates the platform history table in a single transaction. Existing operator data is unchanged. No migrations execute automatically.

Upgrade procedure: stop writers; take and retain a SQLite snapshot; inspect and plan; explicitly apply; verify and reopen the registry; restore to a new path if necessary.

Only the v0-to-v1 metadata baseline exists. Downgrades, live multi-process upgrades and external backup retention remain future work.
