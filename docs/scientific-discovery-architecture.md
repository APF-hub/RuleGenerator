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

## 11. Predictive interaction, shared explanations and independent reproduction

**Architectural requirement:** The system must expose its current knowledge as
predictions and executable explanations that an external observer can inspect,
understand, challenge and reproduce. Internal reconstruction success alone does
not establish communicable understanding or mastery. This is a proposed
capability contract, not implemented behavior.

### 11.1 Predict before observing, then investigate surprise

Given available input/context, the system records a versioned prediction from
its current model before obtaining the target outcome. The record includes
model/library digests, input and observation-method identities, assumptions,
predicted values or distributions, uncertainty, units, validity scope, and the
declared comparison metric. If the outcome is already available during fitting,
label the result reconstruction or retrospective fit rather than a prospective
prediction.

On receiving an outcome, compare it with the recorded prediction and retain
both. Surprise is a discrepancy relative to the predictive distribution and
measurement model, not simply raw error. Use proper predictive scores where
applicable, and distinguish stochastic variation, measurement failure,
distribution shift and a potentially missing mechanism. Check measurement
integrity before changing explanatory rules; surprising noise must not become
an unlimited source of curiosity reward.

A match provides scoped supporting evidence; a mismatch triggers diagnosis,
alternative hypotheses, observation-method changes or an informative experiment.
Small routine errors need not trigger expensive search. Prioritize reducible
uncertainty, hypothesis discrimination, learning progress and cost; retain
exploration of unfamiliar phenomena. Never silently revise an earlier prediction
after seeing its outcome. Model revisions require a new version and evaluation
on new or reserved observations.

### 11.2 Agree an explanation language with the observer

An external observer may be a person or another machine. Establish a versioned
communication contract containing:

- Observer goal, relevant expertise, preferred language, notation and granularity.
- Typed vocabulary, definitions, units, coordinate/time conventions and assumptions.
- Accepted executable format, interpreter/runtime semantics and available tools.
- Requested claim scope, evidence standard, error metric and numeric tolerances.
- A procedure to request clarification, expand a term or reject an unsupported claim.

Use an executable core with audience-specific renderings such as equations,
structured programs, annotated audio events, diagrams or plain-language accounts.
A learned abstraction may be introduced as a new term only with its definition,
dependencies and examples; expand it to accepted primitives on request. Language
negotiation must not require the observer to supply the hidden generating rules.

Generate explanations from the actual model and execution trace. A simpler
explanation must declare approximations and measured fidelity to that model.
Do not substitute a plausible narrative for the mechanism that produced the
prediction. Changing vocabulary or presentation must not silently change the
underlying claim. Observer comprehension feedback may improve communication
without providing evidence that the physical or mathematical claim is true.

### 11.3 Export a reproducible claim package

Each published prediction or explanation should reference a portable,
content-addressed package with:

1. Claim/prediction identity, creation order and model/library/version digests.
2. Input artifacts or a declared access procedure, provenance and measurement context.
3. Executable program, parameters and expanded definitions or pinned dependencies.
4. Runtime/environment specification, seeds and resource requirements.
5. Expected outputs, comparison procedure, numeric tolerances and known limits.
6. Evidence, counterexamples, alternative explanations and uncertainty.
7. Explicit status: conjectured, observed agreement, independently reproduced,
   or formally proved under named assumptions.

A minimal external runner should execute the exported program without access to
the discovery system's private mutable state. Report unavailable dependencies,
restricted inputs or failed checks as incomplete reproduction rather than
success. Validate hashes and environment compatibility before execution; use
bounded execution for received artifacts. Reproduction costs count in total
discovery costs.

Distinguish replay of the same artifact from an independently implemented
replication and from validation against new external measurements. Record which
occurred. Reproducing a waveform or image establishes the declared rendering
claim within tolerance, not the unique original instruments, scene or causal
history. Formal claims require a machine-checkable certificate and a named
checker/assumption set; empirical matches must not be presented as universal
proofs.

### 11.4 External feedback closes the learning loop

The observer can report reproducibility outcomes, comprehension difficulties,
alternative explanations and counterexamples. Link each feedback record to the
exact claim, package, explanation and communication-contract versions. Record
observer role, environment, attempted procedure, actual outputs, tolerances,
evidence origin and any reproduction independence.

Route feedback according to its meaning:

- Execution/reproduction failure -> artifact, dependency, runtime or semantic diagnosis.
- Misunderstanding -> vocabulary negotiation or explanation revision.
- New conflicting observation -> prediction diagnosis and model/measurement experiments.
- Successful replication -> scoped evidence for the reproduced claim.
- New question or proposed intervention -> candidate experiment, with its own cost.

Self-play role agreement is synthetic/internal feedback; never relabel it as an
independent external confirmation. Communication optimization must not reward
persuasiveness, approval or verbosity as substitutes for accuracy. Separate
comprehension, faithfulness, reproducibility, predictive calibration and transfer
metrics. An observer can understand a wrong explanation or reproduce a wrong
model; preserve those distinct outcomes.

The loop becomes: input/context -> recorded prediction and explanation ->
outcome comparison -> surprise or agreement -> targeted experiment ->
versioned knowledge revision -> exported explanation/program -> external
reproduction and comprehension feedback -> further investigation.

Trust should be supported by an inspectable history of successful predictions,
faithful explanations, independent reproduction and openly retained failures.
Mastery remains scoped to tested conditions, including changed inputs and
interventions; observer approval alone cannot establish it.

### 11.5 Implementation and acceptance gates

| Milestone | Deliverable | Acceptance evidence |
|---|---|---|
| G1c | Prediction, communication-contract and observer-feedback schemas linked to provenance | Predictions immutable after outcome; units/versions checked; feedback tied to exact claims |
| G3b | Exported executable explanation/claim package and minimal reproduction runner | Fresh-process execution without private state; missing/tampered dependencies rejected; tolerances reported |
| G4b | Audience-adaptive explanation and clarification protocol | Faithful expansion to agreed vocabulary; separately measured comprehension and correctness |
| G6b | Surprise diagnosis and external-feedback-driven experiment selection | Noise controls, recorded alternatives, independent predictive improvement at matched cost |
| G10b | Independent reproduction and task-mastery evaluation | Separate replay, independent implementation, new measurements and proof outcomes; scoped trust report |

Implement G1c alongside G1b/G2a record integration, then G3b once program and
runtime identities can be exported reliably. G4b depends on faithful program
rendering; G6b depends on prediction scoring and experiment selection. Use
explicit evaluator-only feedback during frozen tests; observer feedback used for
training cannot also count as untouched held-out evaluation. No new general
synthesis engine is required by this extension.

## 12. Communicating knowledge gaps and collaborative discovery

**Architectural requirement:** Expose the current explanation, its unresolved
gaps and the evidence needed to address them in the agreed observer language.
A person or another system may contribute knowledge, experience, analogies,
measurements, experiments or partial programs. Participants may address different
aspects and compose a shared explanatory program through validated interfaces.
This is a proposed distributed capability, not an implemented agent network.

### 12.1 A knowledge-gap report is an actionable scientific object

For each unresolved issue, publish a versioned report referencing the exact
prediction, explanation, observation and evidence records. Include:

- What is currently explained, the supported scope and the remaining residual.
- The predicted outcome/distribution and observed outcome, with units, uncertainty,
  comparison metric and the location/time/conditions of the discrepancy.
- Known limitations, missing observations and alternative hypotheses.
- A diagnosis status: unexamined, suspected measurement error, irreducible noise,
  representation limitation, model conflict, missing mechanism or unresolved
  identifiability. These are hypotheses until tested.
- Prior attempts and counterexamples, unresolved dependencies, resource limits
  and why the issue matters for the task.
- A concrete help request: clarify a concept, suggest a mechanism, supply a
  measurement, design a discriminating test, implement a component or reproduce
  a result.
- Acceptance criteria and an executable minimal reproducer where available.

Surprise measures unexpected outcomes under a particular model; it does not
measure every knowledge gap. The system may have broad uncertainty or multiple
indistinguishable explanations without experiencing a surprising outcome.
Report those gaps too. Describe measured model discrepancies rather than
asserting a subjective experience of surprise or introspective certainty.

### 12.2 Contributions become testable candidates

Allow contributions in the negotiated vocabulary, with source, authorship,
version, assumptions, intended scope and dependencies. Preserve a natural-language
suggestion and its proposed executable interpretation as linked but distinct
artifacts. Seek clarification when their meaning is ambiguous, and expose that
interpretation for correction before claiming it implements the suggestion.

External knowledge may seed a hypothesis or method without being counted as
autonomously discovered. Record whether a claim is externally supplied,
internally generated, derived from prior knowledge or experimentally supported.
Expertise and analogy guide search; they are not execution results or formal
proofs. Keep contributed private knowledge within its declared access scope.

Evaluate contributions against the original gap and reserved tests. A proposed
solution may close, narrow, split or invalidate a gap; report the evidence and
remaining limitations. Retain rejected alternatives and useful negative results.
Do not silently erase the prediction that motivated the contribution.

### 12.3 Decompose work and compose explanations

Use a shared graph of claims, gaps, experiments, artifacts and dependencies.
Assign bounded subproblems with explicit input/output types, units, assumptions,
resource limits and required evidence. Roles can include proposer, representation
investigator, program synthesizer, experiment designer, critic and reproducer;
roles do not require separate model instances.

Different participants may develop competing explanations or solve independent
parts. Before integration, check representation/semantic compatibility, units,
sampling conventions, uncertainty assumptions and dependency versions. Validate
each component, then run end-to-end tests on the composed program; locally
successful components can fail together. Attribute improvement and costs to
their evidence lineage.

Keep conflicting claims explicit until discriminating evidence is available.
Agreement among participants does not establish truth. Repeated citations or
copies of one result are one evidence lineage, not independent replications.
Systems sharing a model, dataset or runtime may share failure modes; disclose
these dependencies when reporting independent confirmation.

Use explicit ownership/version checks for shared artifact updates. Bound work
and stop duplicate or cyclic requests that produce no new evidence. Unproductive
collaboration must return an unresolved-gap report, not recurse indefinitely.
Communication overhead, reproduction and integration costs are part of the
discovery budget. Track whether collaboration improves outcomes over a matched
single-system baseline; additional participants alone are not an improvement.

### 12.4 Collaborative output and acceptance gates

The shared result consists of a versioned executable explanation and task-solving
program, its component/dependency graph, evidence, contributor provenance,
external reproduction reports and remaining gaps. Mastery reports remain scoped
to tested capabilities. Better communication and a clearer unresolved question
can be valuable intermediate outcomes even before a solution is found.

| Milestone | Deliverable | Acceptance evidence |
|---|---|---|
| G1d | Versioned knowledge-gap and contribution contracts | Reports reference exact predictions/claims; supplied knowledge and derived evidence distinguished |
| G4c | Observer dialogue that turns gaps and suggestions into testable work | Faithful translation, clarification handling and contribution attribution |
| G5b | Shared claim/gap graph and typed partial-program composition | Component compatibility, conflict preservation, dependency invalidation and end-to-end reproduction |
| G6c | Bounded collaborative experiment coordination | No evidence-free request cycles; cost accounting; improved gap resolution against matched controls |
| G10c | Independent collaborative mastery evaluation | Traceable contributions, correlated-evidence controls, transfer and reproducibility on external tasks |

Implement G1d alongside G1c, reuse the existing provenance and registry mechanisms,
and add G4c after the observer language/feedback contract works. G5b/G6c follow
portable reproduction and bounded task execution. No external messages or work
dispatch are performed merely by introducing these contracts; actual interaction
requires the relevant user-authorized channel.
