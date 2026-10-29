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
- G1c: add immutable prospective prediction, shared explanation-language and observer-feedback contracts linked to G1b provenance.
- G1d: add actionable knowledge-gap and contribution records linked to exact claims, requests and acceptance criteria.
- G1e: separate environmental knowledge intake from task inputs and authorized control; retain candidate-update lineage.
- G4d: implement a single-process persistent experiment/surprise backlog with deduplication, leases, bounded retries and stop/wake-up conditions before distributed delegation.
- G2a: build sandboxed, versioned generator execution with explicit costs, limits and seeds.
- G2: generic typed transform grammar and method-generation portfolio, with identity/random baselines.
- G3: independent utility scoring and evidence-gated reusable observation-method registry.
- G4a: competence-progress curriculum scheduler with a preregistered frozen evaluation suite.

**Stop condition:** do not expand into full music reconstruction until generic transforms and accumulated methods demonstrate positive transfer on multiple disjoint synthetic signal/mechanism families.

## Predictive interaction and external explanation

The architecture's section 11 makes external communication and reproducibility
part of the discovery loop. These are planned contracts, not implemented
capabilities. Integrate them with existing ledgers and execution paths.

| Stage | Work | Dependencies and acceptance |
|---|---|---|
| G1c | Prediction, explanation-language and observer-feedback records | G1b/G2a provenance; commit prediction before outcome; preserve claim and contract versions |
| G3b | Portable executable claim package and reproduction runner | Stable program/runtime digests; reproduce in a fresh process without private state; reject tampering |
| G4b | Faithful explanations in an observer-agreed vocabulary | G3b; expand abstractions on request; assess comprehension independently of claim correctness |
| G6b | Diagnose surprise and select experiments from external feedback | G6/G6a plus calibrated prediction scores; distinguish noise, execution failure, misunderstanding and model failure |
| G10b | Independent reproduction and mastery assessment | Separate same-code replay, independent implementation, new external observations and formal proof |

Record successful and failed reproduction attempts. Empirical agreement is not
universal proof, and understandable explanations do not by themselves establish
accuracy. Keep explanation fidelity, observer comprehension, reproduction,
predictive calibration, transfer and cost as separate metrics. Freeze learning
and explanation adaptation during held-out evaluation, or explicitly report
online adaptation with a separate untouched evaluation set.

## Collaborative gap resolution

Section 12 extends observer feedback into shared discovery. Expose supported
understanding, surprise and unresolved uncertainty; accept attributed knowledge
and inspiration as candidates; combine tested partial programs and explanations.

| Stage | Work | Dependencies and acceptance |
|---|---|---|
| G1d | Knowledge-gap/help-request and contribution schemas | G1c; immutable claim links, provenance, acceptance criteria and external-knowledge attribution |
| G4c | Negotiated gap clarification and candidate interpretation | G4b; preserve source meaning, request clarification, distinguish suggestions from validated evidence |
| G5b | Shared claim/gap graph and typed program composition | G3b/G5; dependency and unit compatibility; end-to-end tests; retain competing explanations |
| G6c | Bounded collaborative experimentation | G6b plus execution limits; no evidence-free cycles; matched total-cost single-system controls |
| G10c | Collaborative reproduction and mastery assessment | G10b; evidence-lineage independence, transfer and explicit remaining gaps |

Parallel work is optional and justified by task structure and measured outcomes.
A participant's confidence or agreement is not independent evidence; disclose
shared models/data and deduplicate copied results. Report partial progress and
unresolved gaps instead of forcing consensus or claiming complete understanding.

## Environmental knowledge and efficient work coordination

Section 13 adds external partial explanations, programs, tools and experiment
packages as candidate knowledge updates through an interface distinct from task
input and authorized control. Intake never implies execution or adoption.

| Stage | Work | Dependencies and acceptance |
|---|---|---|
| G1e | Environmental intake and candidate-update contracts | G1c/G1d; task/control separation, source and evidence lineage |
| G3c | Isolated baseline/candidate trials and reversible adoption | Existing registry plus G3b; scoped gain, regressions, costs and dependent revalidation |
| G4d | Persistent backlog of experiments, surprises and unresolved gaps | G1d/G1e; bounded scheduler, duplicate reuse, leases, stop criteria and explicit reopening reasons |
| G6d | Shared experiments and bounded delegated work | G3b/G5b/G4d; no circular evidence or ancestor redispatch; one parent budget and end-to-end validation |
| G10d | External-knowledge and collaboration efficiency experiments | Matched total-cost controls; distinguish supplied knowledge, independent evidence and autonomous discovery |

Implement the backlog locally before adding distributed transport. Preserve
scoped negative results and useful unresolved work; repeat only when conditions
change or a bounded stochastic replication protocol requires it. Consolidate
duplicate items, detect circular citations and retain explicit wake-up conditions
for blocked/deferred experiments. Estimated usefulness guides scheduling but
does not count as measured learning gain.
