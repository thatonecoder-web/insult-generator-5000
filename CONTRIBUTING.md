# Contributing

Thanks for helping. This project is at an early stage, so small, focused changes are easiest to review.

## Development setup

```bash
git clone <your fork>
cd insult-generator-5000
python -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Python 3.12 or newer is required.

## Branches and commits

- Branch from `main`: `feature/<short-name>`, `fix/<short-name>`, or `vocab/<short-name>`.
- Keep commits focused, with an imperative subject line under about 72 characters
  ("Add legal-register entries for obstruction").
- Add a line under `[Unreleased]` in `CHANGELOG.md` for any user-visible change.

## Testing requirements

Before opening a pull request, all of these must pass:

```bash
python -m pytest
python -m ruff check .
python -m mypy
```

If you changed anything under `web/`, also run:

```bash
cd web && npm install && npm test && npm run build
```

The browser test in `web/e2e/` is optional but worth running for interface changes.

New behaviour needs tests. Tests must be small and deterministic: no network, no wall-clock
time, no unseeded randomness.

## Adding vocabulary

1. Read [docs/vocabulary-guidelines.md](docs/vocabulary-guidelines.md). It lists what the
   dataset excludes (slurs, sexual content, invented words).
2. Add entries to `src/insultgen/data/vocabulary.json`, following [docs/data-schema.md](docs/data-schema.md).
3. Give every noun a `noun_class` and every adjective its `targets` (see the guidelines).
4. Run `insultgen validate-data` and `python -m pytest`, then generate some sentences with
   your words and read them.
5. In the pull request, mention anything uncertain (register, severity, accuracy).

## Code style

- PEP 8, enforced by Ruff (line length 100). Type hints everywhere; mypy runs in strict mode.
- Standard library first. Do not add a dependency without discussing it in an issue.
- Prefer small modules and plain functions. No global mutable state. Use `pathlib`.
- Comments and docstrings should explain why or what is not obvious, not restate the code.

## Pull requests

Describe what changed and why, link the issue, and tick the checklist in the template.
Maintainers may ask for changes to keep the dataset consistent.

By participating you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
