# Release and recovery operations (P14 baseline)

## Supported runtime and CI
Python 3.12 only (as declared in `pyproject.toml`). The CI workflow runs unit tests, builds an sdist and wheel, and checks package metadata. CI uses read-only repository permissions, a ten-minute job timeout, and cancels superseded runs on the same ref. These are build checks, **not** proof of a reproducible, byte-for-byte deterministic release.

## Operator database safety
Before schema changes, stop writers, take a SQLite-consistent snapshot using `backup_database(source, snapshot)`, and run `inspect_database` against the snapshot. Never copy a live SQLite file with a plain filesystem copy when WAL activity may be present. Restore using `restore_database(snapshot, new_destination)`; this intentionally refuses to overwrite existing destinations. Confirm both registries reopen and evidence counts match expectations before switching consumers to the new database path.

A failed startup transaction should roll back registry and evidence table creation; do not manually delete a database to recover from an initialization error. Preserve the original database for diagnosis.

## Release gates
1. Confirm pull-request CI is successful at the exact head commit.
2. Review changes and explicit migration/backward compatibility impact.
3. Squash-merge; verify main-branch CI separately when available.
4. Record source commit, package version, artifact hashes and runtime Python version in the release record.
5. Perform restore/reopen rehearsal for persistence-affecting releases.

## Outstanding
Dependency versions are not fully pinned; build tooling is installed from current indexes. No artifact signing, SBOM, supply-chain attestation, cross-platform isolated-worker parity or enforced repository branch protection is claimed. The process-isolated synthesis runner is POSIX-only. Release automation must not publish artifacts without an explicit release gate.
