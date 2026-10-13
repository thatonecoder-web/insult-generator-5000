"""Generator entry point. Sentence construction is not implemented yet."""

from __future__ import annotations

from insultgen.generation.selection import filter_entries
from insultgen.models import GeneratedInsult, GenerationParameters, Vocabulary, VocabularyEntry


class InsultGenerator:
    """Builds insults from a vocabulary.

    Only candidate selection exists today. Grammar and template selection,
    sentence assembly and output validation are tracked in ``docs/roadmap.md``.
    """

    def __init__(self, vocabulary: Vocabulary) -> None:
        self._vocabulary = vocabulary

    @property
    def vocabulary(self) -> Vocabulary:
        return self._vocabulary

    def candidates(self, parameters: GenerationParameters) -> list[VocabularyEntry]:
        """Entries eligible for ``parameters`` (register, severity and concept filters)."""
        return filter_entries(self._vocabulary.entries, parameters)

    def generate(self, parameters: GenerationParameters) -> GeneratedInsult:
        """Generate one insult. Not implemented yet."""
        raise NotImplementedError("sentence generation is not implemented yet; see docs/roadmap.md")
