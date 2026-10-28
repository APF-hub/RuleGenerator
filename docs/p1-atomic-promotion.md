# P1 platform integrity: atomic functional operator promotion

Functional operator admission and its M68 validation event are now committed
in a **single SQLite transaction**. An error inserting evidence rolls back
the operator insertion. The public `Evidence.append()` remains a standalone
transactional API; `append_in_transaction()` requires a transaction already
owned by its caller and never commits independently.

The platform regression suite injects an SQLite failure into evidence
insertion, verifies no active operator or validation event remains, then
retries and checks persistence across database restart.

## Scope and outstanding work

This protects *new functional promotions* through `FunctionalRegistry.promote`.
It does not retroactively repair old databases or guarantee atomicity for
legacy `Registry.admit`, which currently stores operator evidence in its
operator row. It does not provide general schema migrations, multi-process
concurrency control, independent provenance attestation or backup/recovery.
The evidence schema remains version 1. Those are separate platform gates.

A successful research experiment is not a substitute for these platform
invariants. See `docs/engineering-charter.md`.
