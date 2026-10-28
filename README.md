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
