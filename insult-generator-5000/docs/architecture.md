# Architecture

The system is a pipeline. Each layer has one job and depends only on the layers below it.

```
cli.py ---------> generation/ ---------> loader.py -----> validation.py
                       |                     |                  |
                       +---------------------+------------------+--> models.py
```

## Layers

**Domain (`models.py`).** Frozen dataclasses (`Concept`, `VocabularyEntry`, `Vocabulary`,
`GenerationParameters`, `GeneratedInsult`) and `StrEnum`s (`Register`, `PartOfSpeech`,
`Polarity`, `ReviewFlag`). Range checks live here, so an invalid object cannot exist.

**Data (`loader.py`, `data/`).** Reads JSON, validates it, and converts it to typed models.
The bundled dataset lives inside the package (`src/insultgen/data/`) so an installed wheel
can find it through `importlib.resources`, with no hard-coded paths.

**Validation (`validation.py`).** Works on the raw JSON structure and returns a list of
`ValidationIssue`, so one run reports every problem. It is standard-library only. It checks
types, ranges, enums, unknown fields, duplicates, concept cross-references, and a few
consistency rules (for example `vulgar` requires `vulgarity >= 1`, and `formal` cannot be
combined with `vulgar`). `data/vocabulary.schema.json` mirrors the field list for editors;
a test keeps the two in agreement.

**Generation (`generation/`).** `selection.filter_entries` narrows the vocabulary by register,
severity (within a tolerance) and concept. `InsultGenerator` wraps it; `generate()` raises
`NotImplementedError` until grammar and templates exist. This is where template selection,
compatibility logic and sentence assembly will go.

**CLI (`cli.py`).** A thin `argparse` layer. It parses and validates input and delegates.

## Design decisions

- **Standard library only.** Nothing here needs a framework. Dev tools are the only dependencies.
- **Concepts are named for the insult side of an axis** (`stupidity`, not `intelligence`).
  Positive words such as *perspicacity* live in the concept they negate, marked
  `polarity: positive`, so a generator knows they need negation ("devoid of perspicacity").
- **`compatible_concepts` always includes the entry's primary concept.** Dataset tests enforce this.
- **Immutable models, no global state.** Loading returns values; nothing is cached globally.
- **Determinism.** Selection preserves dataset order; randomness (later) will take an explicit seed.

## Deviation from the suggested layout

The brief suggested a top-level `data/` directory. The dataset is inside the package instead,
because files outside `src/` are not included in an installed wheel, which would break
`insultgen validate-data` for anyone who installs rather than clones.
