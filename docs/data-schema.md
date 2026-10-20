# Data schema

The dataset is one JSON file with three top-level keys: `schema_version` (currently `1`),
`concepts`, and `entries`. `src/insultgen/data/vocabulary.schema.json` is the machine-readable
form; `insultgen validate-data` is the authoritative check.

## Concept

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | lowercase snake_case, unique |
| `name` | string | display name |
| `description` | string | what the concept covers |
| `related` | list of concept ids | optional; must exist, must not include itself |

## Entry

| Field | Type | Notes |
| --- | --- | --- |
| `term` | string | no leading or trailing whitespace |
| `part_of_speech` | `noun`, `adjective`, `verb`, `adverb` | |
| `primary_concept` | concept id | the main semantic home |
| `secondary_concepts` | list of concept ids | must not repeat the primary |
| `register` | non-empty list of registers | `casual`, `formal`, `archaic`, `academic`, `legal`, `vulgar` |
| `severity` | integer 1-10 | how harsh the word is as an insult |
| `formality` | integer 1-10 | 1 = slang, 10 = highly formal |
| `vulgarity` | integer 0-10 | 0 = none |
| `archaicness` | integer 0-10 | 0 = current, 10 = obsolete |
| `meaning_or_nuance` | string | what it means and how it differs from near-synonyms |
| `usage_notes` | string | grammatical constraints, connotation, cautions |
| `compatible_concepts` | list of concept ids | concepts this word can sensibly be paired with |
| `noun_class` | `person`, `abstract`, `thing` | nouns only; optional in the schema, required by the dataset tests |
| `targets` | list of `person`, `thing` | adjectives only; what the adjective can describe; required by the dataset tests |
| `attributive_only` | `true` | adjectives only; the word only works before a noun ("bloody") |
| `polarity` | `pejorative` (default), `neutral`, `positive` | optional |
| `review_flags` | list of `obscure`, `obsolete`, `regional`, `disputed`, `sensitive` | optional |

An entry is unique by (`term`, `part_of_speech`), case-insensitively.

## Validation rules beyond types

- Every concept id referenced must exist.
- `vulgar` requires `vulgarity >= 1`; `archaic` requires `archaicness >= 1`.
- `vulgar` cannot be combined with `formal`, `academic` or `legal`.
- `positive` polarity requires `severity <= 2`.
- `noun_class` only on nouns; `targets` and `attributive_only` only on adjectives.
- No unknown fields at any level.

## Conventions the test suite also checks (bundled dataset only)

- Each entry's `compatible_concepts` includes its `primary_concept`.
- Terms are unique across the whole file, regardless of part of speech.
- Every concept is the primary concept of at least one entry.
- Each register has at least 75 entries.
- Every noun has a `noun_class`; every adjective declares its `targets`.
- Positive nouns are `abstract`.

## Choosing grammar annotations

- `person`: a noun you can say "You are a ___" about. `abstract`: a mass noun ("That is ___").
  `thing`: anything else.
- `targets`: ask whether "You are ___" works (`person`) and whether "That argument is ___" works
  (`thing`). Many adjectives work for both. If neither does, use an empty list.
- `attributive_only`: use it when "You are ___" is ungrammatical but "You ___ git" is fine.
