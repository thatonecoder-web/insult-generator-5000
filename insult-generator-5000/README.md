# insult-generator-5000

An algorithmic English insult generator that builds grammatically coherent insults from a
curated, structured vocabulary, rather than gluing random words together.

> **Status: initial development release (0.1.0).** The repository skeleton, data layer,
> validation tooling and test infrastructure exist. **Insult generation itself is not
> implemented yet.** `insultgen generate` is a placeholder.

The repository is `insult-generator-5000`; the Python package and command-line tool are both named
`insultgen`.

## Goals

Generate insults controlled by:

- semantic concept (for example `stupidity`, `hypocrisy`, `cowardice`)
- linguistic register: casual, formal, archaic, academic, legal, vulgar
- severity, formality, vulgarity and archaicness
- part of speech and grammatical structure
- vocabulary compatibility (words must fit the construction they appear in)

The target pipeline:

```
parameters -> concept selection -> vocabulary selection -> register filtering
  -> severity/formality filtering -> grammar/template selection
  -> sentence generation -> validation -> final insult
```

## Current status

| Stage | State |
| --- | --- |
| Vocabulary dataset (629 entries, 63 concepts) | Implemented, needs expert review |
| Dataset loading and validation | Implemented |
| Typed domain models | Implemented |
| Candidate selection (register, severity, concept filters) | Implemented, minimal |
| Grammar/template selection | Not started |
| Sentence generation | Not started |
| Output validation | Not started |
| CLI | `validate-data` works; `generate` is a placeholder |

## Architecture

```
src/insultgen/
  models.py        typed domain models and enums (data/domain layer)
  validation.py    dataset validation, reports every problem at once (validation layer)
  loader.py        loads and validates the dataset into typed models (data layer)
  data/            vocabulary.json and vocabulary.schema.json (packaged with the library)
  generation/      candidate selection now; grammar and sentences later (generation layer)
  cli.py           command-line interface (CLI layer)
```

See [docs/architecture.md](docs/architecture.md) for the reasoning behind these boundaries.

## Installation

Requires Python 3.12 or newer. There are no runtime dependencies.

```bash
git clone <repository url>
cd insult-generator-5000
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Usage

```bash
insultgen --version
insultgen validate-data                      # validate the bundled dataset
insultgen validate-data --path my_vocab.json # validate another file
insultgen generate --register academic --severity 6   # placeholder, exits with code 3
```

`generate` accepts `--register`, `--severity` (1-10), `--concept` and `--seed`. Input is
validated, but no text is generated yet.

To inspect the dataset:

```bash
python scripts/dataset_report.py
python examples/explore_vocabulary.py
```

## Development

```bash
python -m pytest          # run the tests
python -m ruff check .    # lint
python -m mypy            # type check (strict)
```

CI runs these three on every push and pull request.

## Adding vocabulary

Edit `src/insultgen/data/vocabulary.json`, then run `insultgen validate-data` and
`python -m pytest`. The entry format is documented in [docs/data-schema.md](docs/data-schema.md)
and the curation rules in [docs/vocabulary-guidelines.md](docs/vocabulary-guidelines.md).
Please read the guidelines first: the dataset deliberately excludes slurs and sexual content.

## Roadmap

See [docs/roadmap.md](docs/roadmap.md).

## Content note

This project is about the craft of insults, in the tradition of Shakespearean insult
generators. The vocabulary targets conduct and character (stupidity, dishonesty,
cowardice). It deliberately excludes slurs aimed at protected characteristics and sexual
content. The `vulgar` register covers profanity and crude slang as language, not hate speech.

## License

No license has been chosen yet. See [LICENSE](LICENSE).
