# M78 salvage and consolidation: architecture decision

## What was salvaged

- `rulegen/engine.py`: original typed synthesis, operator execution, persistent SQLite Registry.
- `rulegen/typedholes.py`: goal-directed type pruning and scoped failure evidence.
- `rulegen/evidence.py`: versioned evidence ledger; only rechecked type contradictions count as logical pruning proofs.
- `rulegen/experiments.py`: observation reconstruction experiment store.
- `rulegen/evaluation.py` and `experiments/test_m69_evaluation.py`: historical acquisition-aware matched-evaluation-budget methodology, including negative controls.
- `rulegen/reconstruct.py`, audio/residual adapters: observation-to-program reconstruction path.
- M74–M77 functional AST, anti-unification, evidence-gated persistence and bounded reuse synthesis.

**Do not delete or rewrite these modules solely to unify them.** Historical benchmarks are evidence, not new CI acceptance thresholds.

## Implemented now

`rulegen/learning_protocol.py` provides one result envelope for the existing legacy enumerator, legacy goal-directed enumerator and functional enumerator. It records backend identity, observation fingerprint, evaluation budget, checks, solved state, program and explicit acquisition cost (unknown unless supplied). Cold and warm runs share evaluation budgets. Their search spaces are **not equivalent**, so cross-backend check counts cannot be interpreted as a controlled speedup.

## Architecture decision

The canonical shared layer is **experiment protocol and evidence semantics**, not a forced AST conversion. Existing type systems differ: the legacy engine has polymorphic tuple constructors, while the functional core supports real numbers, lexical closures and math. Unchecked translation would be unsound. Preserve both evaluators behind explicit backend boundaries until a typed conversion with roundtrip and semantic-equivalence tests exists.

Next:
1. Route functional promotion evidence through a shared versioned ledger without changing legacy proof semantics.
2. Add stable program/observation digests and provenance for train/validation splits; disjoint argument vectors alone do not prove independence.
3. Make acquisition cost measurable at the source, not supplied after the fact.
4. Reuse M69 evaluation controls and negative controls for multi-task functional learning. Match total budgets and report solved tasks, search cost, acquisition cost, and transfer.
5. Evaluate whether AST dialect consolidation is warranted based on semantic parity tests, rather than introducing a third language.

## Important constraints

- No learned-operator success claim without held-out evidence and provenance.
- Never count empirical failures as permanent logical proofs.
- A common metrics envelope is **not** a unified execution engine.
- Python 3.12 is the sole supported CI runtime; fix stale docs separately.
