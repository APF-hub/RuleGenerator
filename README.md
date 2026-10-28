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


## M65 canonical source import — VERIFIED (2026-10-28)

The exact M63 Python source files and tests have now been imported into GitHub. Git blob SHA-1 values were compared against local M63 files: **9/9 matched**, including the package initializer, all five implementation modules, two test modules, and pyproject.toml. The incompatible transitional `tests/test_package.py` was removed.

Local source validation: `python -m unittest discover -s tests -v` completed **9/9 passing** before import; warnings about unclosed SQLite connections remain. CI now explicitly tests the canonical package on Python 3.11 and 3.12, plus the legacy standalone tests. **Remote CI status has not yet been confirmed.**

The imported implementation includes scoped empirical mismatch caching, goal-directed typed-hole enumeration, persisted operators and a persistent exploration portfolio. **Still not integrated:** durable mid-search checkpoints, proof-based nogoods from M58, one unified evidence schema, and portfolio rewards driven by real synthesis trials. These remain separate acceptance criteria; exact source parity does not imply all historical functionality is integrated.


## M66: durable search sessions (2026-10-28)

Added `rulegen/session.py` and `tests/test_m66.py` directly to the canonical GitHub repository. `synthesize_resumable` stores a transactional cursor and matched program in SQLite; search identity includes observations, depth, reuse flag, primitive type signatures and active learned operator definitions. A restart resumes candidate **evaluation** without rechecking earlier candidates. Rebuilding the enumerator still costs O(previously generated candidates).

**Local regression:** 12/12 tests passed (nine prior, three new). Existing SQLite connection warnings remain. Remote CI not yet verified. This is durable typed-hole search continuation, not M58's proof-based nogood integration or a unified evidence database.


## M67: Real synthesis trials and database lifecycle

Added `rulegen/trials.py`, `tests/test_m67.py` and `benchmarks/real_trials.py`. Each allocation choice now triggers a real bounded typed-hole synthesis attempt, with independent held-out validation; only validated solutions count as observed reward. The trial runner records actual candidate executions, program and selected direction. This is **not** a simulation.

Reproduce with `PYTHONPATH=. python benchmarks/real_trials.py`. On the local four-task smoke benchmark (depths 1/3/5, up to 12 checks per task, seed 11):

| Policy | Held-out tasks solved | Candidate executions |
| --- | ---: | ---: |
| Adaptive | 2/4 | 20 |
| Round-robin | 2/4 | 20 |
| Seeded random | 2/4 | 15 |

**There is no demonstrated adaptive advantage.** Costs are realized rather than equal, and trials use fresh registries to prevent cross-policy leakage. The workload is too small to support general conclusions.

Added a type-soundness regression: an identity body cannot be admitted as `a -> b`. Fixed zero-budget session cursor reporting. Added SQLite context management and fallback finalizers. **Local 18/18 tests passed with ResourceWarnings treated as errors**. Remote GitHub CI remains unverified.

Next: independent held-out multi-task suites, common evidence schema, sound nogoods, and efficient resumable frontiers.


## M68: Verified type nogoods, versioned evidence, longitudinal benchmark

New canonical modules:
- `rulegen/evidence.py`: versioned SQLite evidence ledger (`rg_metadata`, `rg_evidence`) attached to each `Registry`. Evidence kinds: `type_proof`, `empirical_failure`, `validation`, `search_trial`.
- `tests/test_m68.py`: five tests for proof rechecking, context isolation, persistence, empirical/proof separation, and schema compatibility.
- `benchmarks/longitudinal.py`: cold versus warm-library evaluation over three held-out swap tasks; acquisition and marginal reuse are reported separately.

**Soundness rule:** only a fresh, independent typecheck that demonstrates a contradiction may prune based on a recorded `type_proof`. Empirical observation mismatches are stored but cannot be promoted into global logical nogoods. A proof's context includes input type, required type, and active operator definitions. This is a first, deliberately narrow proof mechanism, not the full M58 CSP solver.

**Verification boundary:** the M68 files were committed to GitHub, but this session has not independently executed the GitHub checkout or verified its Actions workflow. Do not infer green CI from successful GitHub commits. The new longitudinal benchmark has been added but no results are claimed until executed. Previous locally verified milestone: M67, 18/18 tests.

Run:
```bash
python -m pip install -e .
python -m unittest discover -s tests -v
PYTHONPATH=. python benchmarks/longitudinal.py
```

Outstanding: full unified schema migration for older tables, serializable search frontier, actual longitudinal results with diverse negative controls, remote CI verification.


### M68 executed results (2026-10-28)

The local M68 test suite ran with `python -W error::ResourceWarning -m unittest discover -s tests -v`: **23 passed, 0 failed** in 0.626 s.

The actual longitudinal benchmark `PYTHONPATH=. python benchmarks/longitudinal.py` was executed. Reproducible output is committed in `benchmarks/m68_results.json`:

| Metric | Primitive-only (cold) | Learned swap (warm) |
| --- | ---: | ---: |
| Three task candidate checks | 25 | 3 |
| Held-out validation passes | 1/3 | 3/3 |
| Initial operator acquisition checks | — | 17 |
| Total checks including acquisition | 25 | 20 |

The learned swap operator was admitted after 17 candidate checks. All three subsequent tasks were solved with one candidate evaluation each. The cold search overfit two of the three training sets; this is why validation passes differ.

**Limitations:** three closely related swap tasks, one deterministic split per task, small search space, no wall-clock or memory measurements. This establishes a reproducible positive transfer example, not general cumulative-learning superiority. GitHub workflow status was queried for commit `085af51a`, but the connector returned no pull-request-triggered runs; **remote CI is still unverified**.


## M69: Matched-budget transfer evaluation (2026-10-28)

Added `rulegen/evaluation.py`, `tests/test_m69.py` and `benchmarks/m69_summary.json`. Run `python -W error::ResourceWarning -m unittest discover -s tests -v` and `python -m rulegen.evaluation` (or `from rulegen.evaluation import evaluate; evaluate(budget=40,depth=5,seeds=(0,1,2))`).

**Local execution:** 26/26 regression tests passed. Nine tasks (three swap-related, six unrelated controls) repeated in three seeded orders. Equal per-task maximum of 40 candidate evaluations:

| Metric | Cold | Warm |
| --- | ---: | ---: |
| Task trials | 27 | 27 |
| Held-out validations | 21 | 27 |
| Candidate checks | 300 | 147 |
| Acquisition checks | 0 | 51 |
| Checks including acquisition | 300 | 198 |
| Related validations | 6/9 | 9/9 |
| Unrelated validations | 15/18 | 18/18 |

The 51% marginal check reduction and 34% including acquisition are **specific to this fixed task suite**. Shuffling order does not provide independent statistical replications. Cold and warm each use fresh databases per task; the learned operator is copied from a separately validated acquisition. Timing is instrumentation-dependent and does not include setup/acquisition. Search enumeration and typechecking cost are not counted as candidate evaluations. Remote GitHub CI remains unverified.

**Next:** independent task generation, more diverse task families, negative transfer stress with many irrelevant operators, per-run peak RSS and search-generation cost, fixed *total* computational budgets, and statistical uncertainty intervals.
