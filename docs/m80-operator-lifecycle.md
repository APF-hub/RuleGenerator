# M80: shared operator lifecycle facade

`OperatorLibrary(path, backend="legacy"|"functional", tier="math")`
standardizes `admit(name, definition, training, validation)`,
`active()`, `status(name)`, and `retire(name)`. Native type checking
and native AST formats remain authoritative. Neither backend receives
unverified operators from the other.

Legacy definitions have `body`, `args`, `out`; functional definitions
have `body`, `params`, `return_type`. The facade deliberately does not
perform AST translation or pretend their admission criteria are identical.
The functional backend requires disjoint input vectors; the legacy backend
currently requires nonempty train/validation but does not enforce that
disjointness. Results differ: functional admission returns evidence metadata,
legacy admission returns a boolean.

This is an incremental lifecycle interface, not yet a unified persistence
schema, autonomous learning loop, or comparable evidence quality. Next:
strengthen the legacy validation split gate, establish source provenance,
measure acquisition cost, and migrate callers to the facade with
semantic-equivalence tests before considering backend consolidation.
