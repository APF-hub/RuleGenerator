# M81: provenance and acquisition accounting

`rulegen.provenance.Observation` records a caller-supplied source ID, split,
inputs and expected output. `verify_splits` rejects source-ID reuse and
identical inputs across train, validation and test splits, and emits a stable
manifest digest. **Source IDs are declarations, not independently verified
attestations**; related or duplicated upstream material may still leak.

`acquisition_report` separates proposal, validation and downstream search
checks. These are *reported check counts*, not measured CPU time and not
automatically instrumented execution. Callers must supply counts collected
from the actual algorithms; no zero-cost learning assumption is allowed.

The existing M69 evaluation remains the historical baseline. Next integrate
provenance manifests into operator promotion, instrument actual proposal and
validation operations, and rerun matched **total** budget transfer benchmarks
with negative controls. This milestone provides prerequisites rather than
claiming measured cumulative-learning gains.
