# RuleGenerator

Research prototypes for cumulative, observation-driven program and rule synthesis.

## M58: Persistent contradiction learning

M58 introduces a finite-constraint search engine that persists compact, sound nogoods, search-ordering evidence, and resumable frontiers. A nogood records a partial assignment proven incompatible with a constraint clause; it does **not** store every execution path.

The implementation and reproducible tests are packaged separately as `rule-discovery-m58.zip` in the ChatGPT project conversation. This repository is being bootstrapped; the archive is the complete M58 source of record until it is imported here.

**Status:** Prototype, not general program synthesis. Does not yet infer musical programs from raw audio or invent generic operators.

### Principles

- No domain-specific structure hints in training examples.
- Promote learned rules only with independent validation.
- Keep measured error, runtime, memory, candidate checks and storage separate.
- Prune only with proven contradictions; empirical failures affect ordering, not admissibility.
- Scope semantic deduplication to observations and invalidate on changed evidence.
- Persist search frontiers and learned knowledge across sessions.
- Benchmark cumulative acquisition + reuse cost against matched controls.

### Planned integration

1. Typed partial-program constraint states.
2. Cross-task reusable, independently validated abstractions.
3. Learned search policy with exploration and controlled ablations.
4. Generic audio-to-program induction using elementary primitives.
5. Multi-seed held-out tests, CI and durable versioned rule registry.


## M61: Autonomous operator discovery (2026-10-28)

Run `python -m unittest -v test_m61_discovery.py` and `python m61_discovery.py`.

M61 searches for an operator body from input/output examples, then derives and validates a polymorphic signature. It can discover pair swapping from integer/Boolean observations and validate it on list/Boolean pairs. This is **restricted combinator synthesis**, not invention of arbitrary algorithms or type constructors.

The separate downloadable M61 research archive contains the full local M60 synthesizer, a more extensive M61 benchmark, and six passing local tests. The GitHub version is a smaller, registry-compatible implementation; GitHub tests are not yet verified in CI.

**Measured local research benchmark:** 17 discovery evaluations; target baseline 17; target with learned operator 1; acquisition plus one reuse 18. Thus there is no net benefit after a single reuse. More repeated targets and full cost accounting are needed.

### Engineering priorities
1. Consolidate the separate M55–M61 prototypes into one tested package.
2. Fix typed-hole propagation, fresh polymorphic variable handling, and observation-scoped negative knowledge.
3. Add continuous integration, benchmark manifests and reproducible environment.
4. Learn recursive and higher-order abstractions and type constructors without task-specific hints.
5. Evaluate on diverse held-out programs and raw audio, including negative controls.


## M62: Consolidation and research allocation

M62 local archive packages the fuller M60–M61 typed synthesizer as `rulegen.engine` and `rulegen.discovery`, adds `rulegen.portfolio`, a `pyproject.toml`, and four passing local integration tests. **It does not yet integrate all M55–M59 prototypes.** The GitHub repo contains `m62_portfolio.py` as a standalone version of the new scheduling mechanism; the full consolidated package is in the M62 downloadable archive pending source import.

**Decision principle:** A discovered operator's acquisition cost is sunk when deciding marginal reuse. Research allocation tracks historical exploration cost and independently validated outcomes; it never assigns speculative future value to a discovery.

The scheduler reserves every Nth decision for the least-funded research direction; otherwise it favours directions with measured validated improvement per cost, and tries untested directions. This is an auditable heuristic, not an optimal bandit. Held-out comparability and fixed-budget baselines are still needed.

Next: migrate the full consolidated package to GitHub, enable CI, integrate scoped failure learning and typed holes, and run matched-budget longitudinal benchmarks.


## M63: Goal-directed typed holes and allocation controls

The M63 local archive adds `rulegen.typedholes` (top-down type-constraint propagation) and `rulegen.benchmark` (deterministic adaptive/round-robin/random allocation controls). Nine local tests pass. In a deliberately favorable **simulated** 30-trial allocation experiment, adaptive achieved validated gain 45 vs round-robin 30 and random 29, all at cost 60. These are **not** observed real-synthesis improvements.

A Python CI workflow is now in this repository. **Release blocker:** the full canonical package is not yet imported; see issue #1. The standalone GitHub code and the local M63 archive are not yet equivalent. Do not interpret CI on the standalone modules as validation of the local consolidated package.


## M64 repository consolidation (2026-10-28)

A pip-installable `rulegen/` package and package-level tests now exist **in GitHub**, alongside the existing M58, M60, M61 and M62 standalone implementations. Run:

```bash
python -m pip install -e .
python -m unittest discover -v
```

Package modules: `engine` (compatibility export of M60 registry/type kernel), `discovery` (M61 discovery), `typedholes` (goal-type-filtered enumeration), `portfolio` (M62 measured allocation), `benchmark` (equal-budget simulated policy replay).

**Integration caveats:** this is a transitional canonical package, not a verbatim import of the M63 local archive. The M63 local archive's nine tests passed independently, but the GitHub package tests have not yet been run by the connected GitHub CI. The M58 scoped nogood engine remains separate and is not used by typed-hole synthesis; the portfolio uses simulated outcomes rather than real synthesis trials; checkpointing and validated admission are not unified. The M60 registry currently permits user-supplied operators and M61 discovery is restricted to pair combinators.

No claim of complete functionality or green remote CI is made until those end-to-end integrations are demonstrated.
