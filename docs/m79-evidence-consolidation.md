# M79: shared evidence ledger (incremental integration)

FunctionalRegistry now initializes the original M68 `Evidence` ledger on the
same SQLite connection. Successful functional promotions append a `validation`
event with a definition digest, train/validation counts and digests, and
`provenance: unverified`. This is empirical validation, **not** a logical
proof and cannot authorize permanent pruning. Rejected candidates do not
produce successful validation events.

The original `rg_evidence` schema and proof verification behavior are
unchanged; older databases are initialized on first open. The existing
`functional_operators.evidence` column remains for compatibility.

This is **shared evidence storage**, not a unified operator lifecycle or
automated provenance verification. Historical evidence is not retroactively
backfilled. A subsequent milestone should use a single transaction for
promotion and ledger append and introduce provenance attestations and
acquisition-cost measurements before making cross-task learning claims.
