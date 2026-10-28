# Testing, experiments, and evidence

RuleGenerator separates **capability contracts** from **research experiments**.

## CI: supported capabilities

GitHub Actions installs the package and runs `python -m unittest discover -s tests -p 'test_*.py' -v` on Python 3.12. These tests protect maintained behavior, including:

- typed AST execution, type checking, and program synthesis;
- independent validation and safe admission of reusable operators;
- persisted registries, evidence, resumable search, and experimental allocation machinery;
- observation adapters, audio rendering, WAV roundtrips, waveform/spectrogram comparison, residual-guided temporal composition, and persisted reconstruction results.

An example may be synthetic, but its regression test stays in CI **only when it verifies a durable supported capability**. Avoid requiring a fixed experimental score, discovery count, or particular learned program unless it is a documented interface guarantee.

## Research experiments: non-gating

Historical or exploratory evaluations belong in `experiments/` or `benchmarks/`, not the CI test discovery directory. They may run manually or in a separate, non-blocking scheduled workflow. Record:

- source revision and configuration, dataset/split and random seeds;
- budgets (candidate evaluations and, where available, CPU/wall-clock costs);
- baseline and candidate metrics, uncertainty, failures and caveats;
- conclusion, follow-up decision, and the reusable capability or regression test that resulted.

Keep evidence and reproducibility instructions when retiring experiment code. Promote only stable, independently validated behavior to `tests/`. Do not treat experiment-specific performance outcomes as universal product guarantees.

## Legacy code

Top-level `test_m*.py` files are retained for historical reproducibility, but are **not** a supported CI compatibility contract. The canonical `rulegen/` package is the maintained implementation. M69 matched-budget transfer evaluation has been moved to `experiments/test_m69_evaluation.py` without changing its assertions.

To run historical experiments manually:

```sh
python -m unittest discover -s experiments -p 'test_*.py' -v
python -m unittest discover -s . -p 'test_m*.py' -v
```

Neither command is a release gate. Failures in retired experimental code should be documented rather than patched solely to keep historical scripts green.
