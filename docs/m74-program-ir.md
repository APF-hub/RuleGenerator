# M74: Portable typed program documents (first integration slice)

## Goal

Learn from observations and produce a compact **human-readable, executable
program**, not a copied observation. The program must execute from a known
operator catalog, a small configuration and execution context.

## Implemented

`rulegen/programs.py` introduces a JSON-safe expression IR:

- `number(value)`: finite numeric literal;
- `config(name)`: named numeric parameter supplied at execution;
- `call(operator, *arguments)`: typed composition;
- `Catalog.register(name, input_types, output_type, implementation)`:
  external operator implementations, not embedded source code;
- `Catalog.infer`, `execute`, `encode`, `decode`:
  validation, execution and portable serialization;
- `audio_catalog()`: `oscillator`, `mix`, `gate`, `silence`;
- `audio_sines_program` and `audio_events_program`:
  compile existing M70 and M73 hypothesis tuples to the new IR.

The program describes **how to synthesize a signal**; no observed waveform
samples are serialized into the program. Parameters can be abstracted as
configuration references, allowing the same program to reproduce different
inputs without storing raw audio.

Example:

```python
from rulegen.programs import audio_catalog, call, config, number, encode

program = call("oscillator",config("frequency"),config("amplitude"),number(0))
catalog = audio_catalog()
print(encode(program))
samples = catalog.execute(program,{"frequency":440,"amplitude":0.4},
                          rate=8000,length=8000)
```

## Explicit limits and next milestones

This is a **first IR slice**, not yet a unified cumulative learner.
The existing `rulegen.engine` typed symbolic AST and `Registry` remain
separate. Existing search adapters still propose tuples, which are compiled
to the portable IR **after** discovery. Learned operators are not yet
promoted automatically into a persistent shared typed registry. The catalog
currently provides audio primitives only. Configuration is numeric and
programs have no abstract lambda, loops or conditionals.

M74 follow-up: introduce one shared operator type system and persist
declarative program definitions and evidence in the canonical registry.
M75: propose and evaluate typed IR refinements directly; meter proposal
and execution costs. M76: abstract recurring subprograms across multiple
independent observations, validate on held-out inputs and promote reusable
operators with measured warm/cold gains.

Capability tests live in `tests/test_program_documents.py`.
