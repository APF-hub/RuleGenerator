# RuleGenerator engineering charter

## Mission and boundaries

RuleGenerator is a platform for discovering, validating, persisting and
reusing interpretable programs from observations. Research outcomes guide
investment; they are not automatically supported product behavior.

### Track P — Platform engineering (release-gating)

Owns package/runtime policy, interfaces, storage, migrations, resource limits,
error contracts, security, deterministic reproducibility, telemetry and CI.
Acceptance: backward compatibility or documented migration, deterministic
capability tests, failure handling, supported Python 3.12 and reviewable PR.
A benchmark improvement is not required.

### Track C — Learning capabilities (release-gating when promoted)

Owns typed execution, synthesis, abstraction, evidence validation, operator
lifecycle and reuse. Acceptance: specification, integration with shared
platform interfaces, adversarial/negative tests, bounded execution, provenance
semantics and regression tests. An operator cannot be called learned merely
because it was manually defined. Capability contracts should be domain-neutral
where feasible.

### Track E — Experiments (non-gating)

Owns hypotheses, datasets, baselines, budgets, controls, seeds, outcomes,
statistical uncertainty and failure analysis. Store reproducible experiment
scripts and reports under `experiments/` or `benchmarks/`. Experiments may
fail without blocking releases. A positive result is not an accepted
capability. Promotion requires a separate C/P change with durable tests.

## Decision and evidence flow

1. Research question -> E experiment protocol and preregistered success metric.
2. Run and archive results with code revision, dataset fingerprints and costs.
3. Review threats to validity and transfer/generalization.
4. Propose capability change (C) or platform change (P) with explicit contract.
5. Review API/storage impacts, implement tests, pass CI, merge through PR.
6. Update roadmap with evidence and decision, not just performance headlines.

## Platform stabilization priorities

P0: one supported Python runtime (3.12), reliable PR CI, documented contracts.
P1: atomic operator promotion/evidence writes; SQLite schema migration strategy.
P2: resource limits, bounded search, deterministic execution and error contracts.
P3: typed backend adapters, provenance integration, structured telemetry.
P4: reproducible build/dependency policy, release versioning and compatibility.
P5: observability, integration tests and documented recovery paths.

## Architectural constraints

The legacy and functional ASTs remain separate until semantic parity is proven.
Shared protocol/facade is not equivalent to a unified engine. M78-M81 are
integration foundations, not evidence that cumulative transfer is solved.
Do not rewrite or delete historical experimental evidence to simplify CI.
