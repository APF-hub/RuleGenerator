# Scientific discovery implementation roadmap

Status: staged implementation plan, not a claim of achieved general scientific discovery. See [scientific-discovery-architecture.md](scientific-discovery-architecture.md) for research principles.

| Order | Milestone | Required implementation | Acceptance evidence |
|---|---|---|---|
| 1 | G1 observation contracts | Typed observations, immutable lineage, method identity, versioned synthetic experiment specs, isolated splits | Deterministic replay, type rejection, distinct splits, no generator oracle leakage |
| 2 | G2a execution and provenance | Sandboxed generators, reproducible simulator parameters, content-addressed artifacts, immutable evaluator-only ground truth | Replay and negative tests, limits, generator digest verification |
| 3 | G2 transform grammar | Typed, bounded generic observation-transform composition and mutation; baseline transform library | Generated valid methods on multiple observation kinds; no hidden labels |
| 4 | G3 method evaluation and registry | Identity/random controls, predictive and reconstruction utility, versioned admission, rollback | Positive held-out transfer at matched compute |
| 5 | G2b/G3a experimental worlds | Mechanism, perturbation, noise and intervention generators; novelty/validity checks | Detect duplicates, trivial tasks, leakage and distribution collapse |
| 6 | G4/G4a policy and curriculum generation | Search-action DSL, learned policies, competence map, controlled exploration | Frozen policy beats random/fixed controls on unseen tasks |
| 7 | G5 hierarchical mechanism discovery | Typed holes, operator invention, numerical fitting, abstraction reuse | Verified reuse and amortized improvement on unseen compositions |
| 8 | G6 active discovery | Residual modeling, alternative hypotheses, informative experiments | Better hypothesis discrimination per cost |
| 9 | G7/G8 continuous signals and synthetic audio | Signal observation adapters, differentiable/numerical execution, synthetic audio benchmarks | Unseen-mechanism reconstruction and calibrated ambiguity |
| 10 | G9/G10 external scientific evaluation | Real audio and unrelated scientific domains, independent observations | Cross-domain transfer, reproducible external validation |

## Engineering sequencing

G1 should integrate with existing `rulegen.experiments` ledger and the current synthesis kernel rather than duplicate it. The first implementation adds `rulegen.observation_contracts` as a minimal API; it is not yet a persistent provenance store, sandbox or discovery algorithm.

For every experiment, isolate the learner-facing observations from evaluator-only generating programs, simulator identity and ground truth. Never treat synthetic agreement as external scientific validation. Preserve independent tests, counterexamples, provenance and total compute costs.

Each algorithmic milestone requires three matched-budget controls: existing size-first synthesis, an equivalent system without accumulated experience, and a simple random/fixed policy. Freeze feature/method registries and search policies during evaluation; split by mechanism and composition, not only by example rows.

## Immediate next PRs

- G1b: integrate observation contracts with the existing experiment ledger; enforce content hashes and replay; prevent split leakage.
- G2a: build sandboxed, versioned generator execution with explicit costs, limits and seeds.
- G2: generic typed transform grammar and method-generation portfolio, with identity/random baselines.
- G3: independent utility scoring and evidence-gated reusable observation-method registry.
- G4a: competence-progress curriculum scheduler with a preregistered frozen evaluation suite.

**Stop condition:** do not expand into full music reconstruction until generic transforms and accumulated methods demonstrate positive transfer on multiple disjoint synthetic signal/mechanism families.
