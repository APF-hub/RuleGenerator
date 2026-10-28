# M74: canonical functional vocabulary — first implementation

The new `rulegen.functional.Core` provides a constrained, typed, pure
functional language for constructing executable explanations from observations.

## Initial vocabulary tiers

- `algebra`: numeric arithmetic, comparison, equality, literals, lexical
  binding, lambdas, application, conditionals and typed nonempty lists.
- `math`: algebra plus sin, cos, exp and sqrt.
- `functional`: math plus map and fold.

Programs are JSON-serializable ASTs. They cannot import modules, access files,
perform IO, mutate state, or execute arbitrary Python source. A step budget
limits evaluation. The interpreter is a research prototype, not a hardened
security sandbox for adversarial programs.

Definitions are themselves typed ASTs. `validate_definition` checks the
declared signature before making an operator callable in that Core instance.
**This is manual definition registration, not learned discovery or evidence
based promotion.** In particular, `wave` in the tests is an illustrative
manually supplied definition, not a learned oscillator.

## Remaining integration work

1. Integrate this language into the existing canonical `rulegen.engine.Registry`
   without maintaining parallel registries and incompatible ASTs.
2. Build typed search over expressions and typed parameterized abstractions.
3. Learn abstractions from recurring structures in independently discovered
   programs, not from manually seeded domain labels.
4. Maintain separate candidate, validated and promoted states with evidence
   and held-out generalization tests.
5. Benchmark cold versus accumulated library search across numerical,
   structured and temporal observations.
6. Add numeric tolerance, floating-point safeguards, structural canonicalization
   and cost accounting; current equality is exact and literal types are simple.
7. Integrate M73 audio hypothesis compilers as optional reference baselines,
   not as learned operators.

Capability tests: `tests/test_functional_core.py`.
