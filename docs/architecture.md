# Architecture

The system is a pipeline. Each layer has one job and depends only on the layers below it.

```
web/ (React)
   |  HTTP + JSON
server.py -> service.py ----+
cli.py ---------------------+--> generation/ --> loader.py --> validation.py
                                      |               |               |
                                      +---------------+---------------+--> models.py
```

## Layers

**Domain (`models.py`).** Frozen dataclasses (`Concept`, `VocabularyEntry`, `Vocabulary`,
`GenerationParameters`, `GeneratedInsult`, `InsultPart`) and `StrEnum`s (`Register`,
`PartOfSpeech`, `Polarity`, `ReviewFlag`, `NounClass`, `Target`). Range checks live here, so an
invalid object cannot exist.

**Data (`loader.py`, `data/`).** Reads JSON, validates it, and converts it to typed models. The
bundled dataset lives inside the package so an installed wheel can find it through
`importlib.resources`, with no hard-coded paths.

**Validation (`validation.py`).** Works on the raw JSON structure and returns every problem at
once. Standard library only. It checks types, ranges, enums, unknown fields, duplicates, concept
cross-references and consistency rules (for example `vulgar` requires `vulgarity >= 1`, and
`noun_class` is only valid on nouns). `data/vocabulary.schema.json` mirrors the field list for
editors; a test keeps the two in agreement.

**Generation (`generation/`).**

- `templates.py`: sentence frames. A frame is text with typed slots, e.g.
  `"You are {a adj1} {person}."`. Slot kinds are person adjective, thing adjective, either,
  person noun, abstract noun, positive ("lack") noun, and a fixed set of target nouns
  (argument, claim, position, theory). `attributive_slots()` works out which adjective slots sit
  directly before a noun.
- `grammar.py`: indefinite article agreement and capitalization.
- `engine.py`: `InsultGenerator`. See below.
- `selection.py`: simple register, severity and concept filtering over the vocabulary.

**Service (`service.py`).** Framework-independent request handling: validates request bodies,
serializes entries and results, and computes which concepts each register can build. Raises
`ApiError` with an HTTP status. Tested without sockets.

**Server (`server.py`).** A thin standard-library HTTP layer: routing, gzip, security headers,
static files with path-traversal protection and single-page-app fallback.

**CLI (`cli.py`).** A thin `argparse` layer over the generator, the server and the validator.

## The generator

1. **Register.** The requested one, or the non-vulgar registers in a seeded random order. With no
   register given, each is tried in turn until one can build a sentence.
2. **Frames.** Frames written for the register are tried before generic ones (they are weighted
   four to one), in a seeded random order.
3. **Severity window.** Words within a tolerance of the target severity are considered first. The
   tolerance widens (1, 2, 3, 5, then unconstrained) only if no frame can be filled.
4. **Slot filling**, in the order slots appear in the sentence. Candidates must match the slot
   kind and register, must not already be used in the sentence, must not be `sensitive` (or
   `obsolete`, outside the archaic register), and `attributive_only` adjectives only fill slots
   that directly precede a noun. They are chosen by weighted random draw: closer to the target
   severity is better, and words whose concept is the anchor concept or related to it weigh six
   times as much. If a concept was requested, the first vocabulary slot must have it as a primary
   or secondary concept; otherwise the first word chosen becomes the anchor.
5. **Assembly.** Articles are chosen from the following word, the first letter is capitalized,
   and the sentence is checked: no unfilled placeholders, closing punctuation present, no
   repeated word.

Output is deterministic for a given vocabulary, parameters and seed. A batch uses consecutive
seeds, so it is reproducible too.

## Grammar annotations

Grammar is data, not code. Three optional entry fields tell the generator where a word fits:

- `noun_class`: `person` ("dolt"), `abstract` (mass nouns such as "balderdash" and "villainy",
  plus positive words used as "devoid of ..."), or `thing` (countable non-persons; not yet used).
- `targets`: whether an adjective describes `person`, `thing` (arguments, claims), or both.
  An empty list means no current frame can use it.
- `attributive_only`: adjectives that only work before a noun ("bloody", "damned").

The dataset tests require every noun and adjective to be annotated.

## Design decisions

- **Standard library only** at runtime. Dev tools and the front end are the only dependencies.
- **Concepts are named for the insult side of an axis** (`stupidity`, not `intelligence`).
  Positive words such as *perspicacity* live in the concept they negate, marked
  `polarity: positive`, and only appear in "devoid of ..." frames.
- **`compatible_concepts` always includes the entry's primary concept** (tested).
- **Immutable models, no global state.**
- **Honest failure.** If no sentence fits, the generator raises `GenerationError` and the
  interfaces say so, rather than quietly returning something off-spec.

## Deviation from the suggested layout

The dataset is inside the package (`src/insultgen/data/`), not a top-level `data/` directory,
because files outside `src/` are not included in an installed wheel.
