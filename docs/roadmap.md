# Roadmap

Versions follow semantic versioning. Everything before 1.0 may change.

## 0.1.0 (initial development release)

Repository skeleton, typed models, curated vocabulary dataset, validation, tests, CLI skeleton,
CI. No sentence generation.

## 0.2.0: grammar and templates

- Template format and loader (data-driven, validated like the vocabulary).
- Part-of-speech slots, agreement (articles, number), and positive-polarity handling (negation frames).
- Compatibility rules between concepts, registers and constructions.

## 0.3.0: generation

- Weighted, seeded selection so output is reproducible.
- `insultgen generate` produces real output; `--seed` becomes meaningful.
- Output validation: malformed sentences and register clashes are rejected.

## 0.4.0: dataset quality

- Expert review of flagged entries; fill thin concepts; add adverbs.
- More tests for balance across registers and concepts.

## Later

- Optional output formats (JSON), a small Python API guide, and a stable 1.0 interface.
- A licence decision before any public release.
