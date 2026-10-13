"""Vocabulary selection: narrow the dataset to entries that fit the parameters."""

from __future__ import annotations

from collections.abc import Iterable

from insultgen.models import GenerationParameters, VocabularyEntry

DEFAULT_SEVERITY_TOLERANCE = 1


def filter_entries(
    entries: Iterable[VocabularyEntry],
    parameters: GenerationParameters,
    *,
    severity_tolerance: int = DEFAULT_SEVERITY_TOLERANCE,
) -> list[VocabularyEntry]:
    """Return entries matching every constraint set on ``parameters``.

    Order follows the input order, so results are deterministic. Constraints:

    * ``register``: the entry must be tagged with that register.
    * ``severity``: the entry's severity must be within ``severity_tolerance``.
    * ``concept``: the concept must be the entry's primary or a secondary concept.
    """
    selected: list[VocabularyEntry] = []
    for entry in entries:
        if parameters.register is not None and parameters.register not in entry.register:
            continue
        if (
            parameters.severity is not None
            and abs(entry.severity - parameters.severity) > severity_tolerance
        ):
            continue
        if parameters.concept is not None and parameters.concept not in (
            entry.primary_concept,
            *entry.secondary_concepts,
        ):
            continue
        selected.append(entry)
    return selected
