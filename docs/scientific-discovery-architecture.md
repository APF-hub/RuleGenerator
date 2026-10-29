# General scientific discovery and learned observation methods

**Status:** Research architecture and experimental roadmap; not an implemented or validated general discovery engine.  
**Scope:** Domain-independent observation, representation, operator, program and search-policy discovery.  
**Motivating stress test:** Explain and reconstruct musical recordings from observations, while also supporting unrelated physical, symbolic and temporal systems.

## 1. Objective and epistemic contract

Given observations `D`, seek executable, compact, predictive explanatory models `M` that can generate or reconstruct observations and generalize to independent measurements. Do **not** equate reconstruction with identification of a unique true causal mechanism. Distinct generative histories may be observationally indistinguishable. Preserve competing hypotheses, uncertainty, provenance and falsifying evidence.

A practical multi-objective score includes predictive and reconstruction error, model description length, execution/search cost and calibrated predictive uncertainty. Evaluate these separately; never reward unsupported certainty. Report symbolic equivalence only when proved, empirical agreement only when tested.

A model may contain symbolic programs, numerical parameters, stochastic latent variables, stateful dynamics and compositional mechanisms. Existing typed AST synthesis remains a bounded symbolic kernel, not the complete scientific discovery architecture.

## 2. General learning loop

```text
Raw observations + measurement metadata + experimental controls
  -> observation-method portfolio (existing and proposed methods)
  -> candidate representations / features / latent states
  -> hypothesis and operator generators
  -> adaptive search-policy portfolio
  -> typed program synthesis + numerical estimation + simulation
  -> predictions / reconstructions
  -> independent validation, residuals, counterexamples
  -> active selection of new observations and interventions
  -> evidence-gated registries of methods, representations, operators,
     abstractions, programs and search policies
  -> repeat, preserving alternatives and negative evidence
```

The engine should learn **how to observe**, **how to represent**, **which operators to construct**, **how to compose explanations**, **which experiments to perform**, and **how to allocate search effort**. No domain-specific generator AST or hidden answer may enter feature extraction or evaluation.

## 3. Observation methods are first-class learnable objects

An observation method is an executable, versioned transformation from an observation and its measurement context to a new observation or representation. This can be a filter, resampling, projection, time-windowing, differencing, normalization, coordinate change, aggregation, decomposition, nonlinear transform, learned encoder, or an active measurement protocol. Methods may be composed into pipelines and reused across domains when type and measurement contracts permit.

**Method contract:**

- `method_id`, version, source/code digest, authorship or generation lineage.
- Input/output types, units, dimensions, sampling assumptions, time base, calibration and validity domain.
- Parameters, deterministic seed or stochastic distribution, compute and memory costs.
- Information-loss and invertibility declarations; known invariances and failure modes.
- Training-data and provenance dependencies, privacy and licensing constraints.
- Executable transform, optional inverse/decoder, tests, and evidence references.
- Measured utility, uncertainty, robustness, out-of-distribution behavior and admission state.

Raw observations must remain immutable and traceable. Transformations create derived artifacts with a complete parent-and-parameter lineage. No derived view should be treated as independent evidence of its parent.

### 3.1 Discovery by controlled data play

The system should actively explore transformations of the same input:

1. **Generate candidates** from a typed grammar of composable observation operations; learn new operators through constrained program induction and validated abstraction.
2. **Apply safely** in a bounded sandbox with unit/type checks, execution limits and deterministic seeds.
3. **Evaluate usefulness** using independent predictive tasks, reconstruction with a decoder where appropriate, stability, compression, transfer, identifiability and cost.
4. **Compare against controls** including identity, random features, simpler transforms and shuffled labels, using the same data and compute budgets.
5. **Select informative probes** or interventions that distinguish hypotheses and expose where a representation fails.
6. **Promote and reuse** only when a method improves held-out performance beyond controls and passes robustness and provenance checks.

Candidate transforms must not be scored only on their ability to fit the observations on which they were generated. Complexity reduction alone can discard scientifically essential information. Transform pipelines may be lossy; never assert reversibility without a tested inverse.

### 3.2 General representation utility

For transformation `T`, representation `z=T(x)`, model `M`, and held-out observations `D_test`, consider a Pareto frontier of:

- Predictive log loss or task-appropriate error of `M(z)` on `D_test`.
- Reconstruction error of `decode(z)` where reconstruction is an actual requirement.
- Compression / minimum description length of `T` + `M` + residuals.
- Stability to known nuisance transformations, and sensitivity to scientifically relevant changes.
- Improvement on **new tasks, unseen compositions and withheld mechanism families**.
- Total cost of discovering, executing and maintaining `T` and `M`.

A feature is useful if it improves downstream scientific explanation or prediction under controlled evaluation, not merely because it correlates with a label in the discovery set.

### 3.3 Concrete generic examples (not hardcoded search policies)

| Observation | Candidate transform | Possible discovered feature | Independent test |
|---|---|---|---|
| Numerical series | Finite difference | Constant increment or acceleration | Future points, altered initial conditions |
| Time series | Lag embedding / autocorrelation | Periodic or delayed dependence | New windows, shifted phase |
| Multichannel measurements | Linear projection / source separation | Shared latent sources | New mixtures and sensor layouts |
| Images | Multiscale decomposition | Repeated spatial patterns | New scales and orientations |
| Audio | Windowing + spectral transform | Harmonic trajectories and transients | Unseen notes, instruments and mixes |
| Events | Interval encoding | Recurring timing structure | New event sequences |

These are examples of *candidate method families* available to a generic grammar. They must not become oracle rules selected by a hidden benchmark family label.

## 4. Search policy generators, not example-specific policies

Represent a search policy as an executable strategy over typed partial hypotheses, observed residuals, evidence, candidate representations, current vocabulary and remaining resources. Policy actions include:

- Propose/compose observation transforms or latent representations.
- Expand a typed program hole; introduce a reusable operator or abstraction.
- Fit continuous parameters; refine a stochastic model.
- Request an observation, counterexample or experiment.
- Reallocate budget, resume a frontier or abandon an unproductive hypothesis.

Generate policies by transforming prior policies, combining exploration strategies and fitting context-conditioned ranking/portfolio models. Train on task histories **disjoint from evaluation tasks**. Preserve nonzero exploration and a bounded exhaustive fallback where feasible. Empirical heuristic failure must affect ranking, not logically prune a valid hypothesis. Sound constraint-derived contradictions may prune.

Learn general search statistics such as reduction in held-out error per compute, type compatibility, novelty, uncertainty and transfer, not memorized associations such as 'pair swap -> pair/snd/fst'. Search-policy generation and feature-method generation should share an evidence registry but retain distinct promotion criteria.

## 5. Hierarchical explanations and active science

Discover local invariants -> mechanisms -> reusable compositions -> hierarchical systems -> generative theories. Reuse validated components without rebuilding their internals on every task. Store dependency graphs and counterexamples. Maintain alternative explanations when data do not identify a unique mechanism.

Select new experiments by expected information gain or expected improvement in model discrimination, with explicit costs and safety constraints. Passive reconstruction is not causal discovery. Interventions and controlled measurements provide stronger evidence; where they are unavailable, report observational equivalence classes.

## 6. Music as a difficult, long-horizon benchmark

Progress from single synthesized oscillators to modulated signals, overlapping sources, repeated events, multi-instrument passages and finally real recordings. Candidate explanations may involve pitch and timing events, score structure, harmonic relationships, instrument/timbre models, lyrics and phonemes, voice characteristics, effects, samples and mixing. They should be executable and render audio for comparison.

Evaluate **separately**: waveform/spectral/perceptual reconstruction; transcription accuracy; rhythm/harmony/structure; source attribution; sample identity; vocal/lyric content; uncertainty and evidence for each. A perceptually close reconstruction cannot establish exact original instruments, samples, voice identities or production history. Respect copyright, consent and voice/privacy constraints; use licensed or synthetic training and evaluation material.

The engine must not depend on being handed musical concepts. General transforms and mechanisms should be discoverable and transferable to unrelated signals. Domain adapters provide data acquisition, units, execution and measurement, not privileged hidden answers.

## 7. Benchmark and evidence protocol

Use preregistered suites with generated mechanisms withheld from the learner, disjoint train/validation/test observations, distinct unseen rules, unseen compositions and withheld families. Include noise, missing data, nuisance transformations, confounders and non-identifiable cases. Benchmark against identity, fixed handcrafted features, size-first search, random search, and a compute-matched feature/policy learner.

Track: success/failure categories, candidate/generated counts, wall time, CPU, peak memory, discovery/acquisition cost, method-execution cost, predictive generalization, reconstruction quality, complexity, confidence calibration, cross-task transfer and amortized reuse. Compare **matched total budgets**, not merely equal per-target search limits. Freeze learned policy and feature registry during held-out evaluation; report multi-seed distributions and uncertainty intervals.

A discovered method must not be promoted based solely on performance on the tasks used to invent or tune it. Register negative transfer and regression cases, and allow rollback. Require reproducible artifact hashes and provenance-linked evidence.

## 8. Implementation milestones and acceptance gates

| Milestone | Deliverable | Gate |
|---|---|---|
| G1 | Typed observation, transformation, representation and provenance APIs | Round-trip lineage, units, bounded execution and reproducibility tests |
| G2 | Generic transformation grammar and observation-method candidate generator | Produce diverse valid candidates without reading ground-truth programs |
| G3 | Representation-utility evaluation and reusable method registry | Held-out gain vs identity/random/handcrafted controls; rollback |
| G4 | Search-policy generator and experience registry | Learned policy beats fixed baselines on unseen tasks at matched compute |
| G5 | Hierarchical operator/program discovery and abstraction reuse | Demonstrated positive amortized transfer on unseen compositions |
| G6 | Residual-guided refinement and active observation/experiment choice | Better discrimination or predictive accuracy per unit cost |
| G7 | Continuous, stochastic and multimodal observation adapters | Validated signals/time series and audio execution contracts |
| G8 | Synthetic generative audio discovery | Reconstruct withheld mechanisms with calibrated ambiguity |
| G9 | Real music explanatory reconstruction | Independent transcription and reconstruction metrics |
| G10 | Cross-domain scientific discovery | Transfer of methods and search policies to withheld domains |

**Near-term engineering priority:** Implement G1–G3 before adding music-specific transcription. Start with immutable observations, a typed transform DSL, generic transform generation, residual/predictive utility scoring and a persistent evidence-gated method registry. Then compare learned observation methods against fixed transforms on disjoint generated signal families.

## 9. Relationship to existing RuleGenerator

Retain the current typed AST interpreter, bounded search, discovery/admission, failure accounting, generated-task benchmarks and provenance machinery as a symbolic kernel. The current F1–F4 feature heuristics and operator-frequency policy are *prototypes*, not proof of domain-independent meta-learning. Their arithmetic/pair-specific feature shortcuts should not be the architecture's long-term dependency.

Explicitly separate **observation-method learning**, **feature/representation learning**, **operator/program learning**, and **search-policy learning**. Each produces versioned reusable artifacts with evidence, dependency graphs and rollback. This design is a research hypothesis; empirical validation must precede claims of general scientific discovery.

## 10. Autonomous generative experimentation and developmental curricula

**Architectural requirement:** The engine must be able to generate new experimental data, tasks, worlds, interventions and measurement procedures to learn how to discover models. This is distinct from fitting an external dataset. Generated experiments may train observation methods, feature detectors, operators, programs and search policies, and may probe the behavior of competing hypotheses.

### 10.1 Experimental objects and provenance

An experiment specification is an executable, versioned object containing:

- A generator program or simulator, its dependency digests, types, units, assumptions and validity limits.
- Variables, controllable factors, initial/boundary conditions, distributions, noise and interventions.
- Observation methods, sampling and measurement settings; available ground truth and what remains latent.
- Random seed, deterministic replay requirements, resource and safety limits.
- A declared goal: exploration, training, falsification, validation, robustness, or transfer.
- Split assignments and complete provenance lineage linking synthetic outputs to the generating mechanism.
- Evaluation protocol, costs, results, failures and subsequent changes in discovery competence.

Generated data is evidence **of the generator's behavior**, not independent confirmation that its mechanism is true in nature. Model-generated training data cannot be promoted as real-world validation of that same model. Preserve immutable external observations and isolate synthetic evidence from independent measurements.

### 10.2 Generic experiment-generation actions

Use a typed experiment grammar with domain adapters, not a hand-authored set of music-specific lessons. Search actions include:

1. Sample new parameter combinations, input conditions, perturbations and noise models.
2. Compose or mutate existing executable mechanisms and observation procedures.
3. Construct counterexamples and adversarial cases for competing hypotheses.
4. Vary resolution, sampling, measurement noise, missingness and sensor placement.
5. Generate interventions that distinguish observationally equivalent hypotheses when possible.
6. Produce out-of-distribution compositions and cross-family transfer tasks.
7. Propose simpler subproblems, curriculum transitions or new environment simulators.
8. Execute, measure, compare and persist outcomes in a sandbox.

Generators themselves can be proposed, evaluated, revised and retained as reusable artifacts. Keep generator quality distinct from solver performance. A generator that produces trivial, repetitive or misleading tasks must not earn high utility merely because its own tasks are solved easily.

### 10.3 Competence-progress curriculum

Allocate experiments by estimated **improvement in future capability per unit cost**, not by raw success rate or synthetic data volume. Candidate objectives include predictive/reconstruction improvement on independent tasks, new reusable abstraction discovery, discrimination between hypotheses, calibration improvement and cross-family transfer. Track uncertainty and novelty; reserve exploration for under-tested task families and alternative generators.

Use a competence map indexed by observable task properties (dimensions, time dependence, compositional depth, noise, number of latent factors, identifiability and required representation changes), rather than hidden generator-family labels. Maintain prerequisites and transferable skills, but allow revisiting simpler experiments when harder tasks expose missing foundations.

Prevent reward hacking: hold out independent evaluation suites; freeze curricula/policies during tests; measure total compute, generator construction cost and negative transfer. Include random curricula, fixed complexity curricula, passive training and no-synthetic-data controls.

### 10.4 Generative model-discovery cycle

```text
Existing hypotheses / methods / policies
  -> propose experimental world or perturbation
  -> execute generator, recording mechanism and provenance
  -> observe through one or more candidate observation methods
  -> discover / fit explanatory programs without access to generator AST
  -> compare with known synthetic mechanism and held-out generated cases
  -> evaluate transfer on separate generators and real observations
  -> revise representations, operators, hypotheses, policy and curriculum
  -> evidence-gated registration of reusable discoveries
```

For real-world scientific claims, require external evidence or actual interventions. The known synthetic ground truth may be used by the **evaluator** but never by the learner or feature-selection policy at test time. Counterexample generation must not silently leak expected answers into the discovery inputs.

### 10.5 Progressive audio illustration, not a domain-specific policy

A general generator could first create simple periodic signals, then mixtures, modulation, transients, event sequences and hierarchical compositions. The learner should discover and reuse observation transforms and mechanisms across stages. Real music is evaluated independently, with separate scores for waveform fidelity, transcription, source attribution and explanatory uncertainty. Success on synthetic audio alone does not imply real-recording reconstruction or exact source identification.

### 10.6 Implementation extension and acceptance gates

| Milestone | Deliverable | Acceptance gate |
|---|---|---|
| G2a | Typed synthetic experiment and dataset provenance API | Deterministic replay, immutable lineage, split isolation and resource bounds |
| G2b | Generic mechanism/perturbation/intervention generator | Diverse experiments without access to target answers; validity checks |
| G3a | Generator quality and curriculum competence registry | Detect triviality, duplicates, distribution collapse and misleading synthetic data |
| G4a | Adaptive competence-progress experiment scheduler | Beats matched-compute random/fixed curricula on frozen unseen tasks |
| G6a | Hypothesis-discriminating synthetic and real experiment proposals | Improves calibrated discrimination while preserving evidence provenance |
| G8a | Progressive synthetic audio generative benchmark | Demonstrates transfer to unseen mechanisms and independently sampled recordings |

**Implementation order:** Couple G1 observation contracts with G2a experiment provenance before training from synthetic data; then implement generic perturbation and mechanism composition, frozen independent evaluation, and adaptive curricula. Do not claim validated autonomous scientific discovery before cross-domain external tests.
