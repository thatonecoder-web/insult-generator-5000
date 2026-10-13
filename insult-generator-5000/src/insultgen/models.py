"""Typed domain models shared by the data, generation and CLI layers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

SEVERITY_MIN = 1
SEVERITY_MAX = 10
FORMALITY_MIN = 1
FORMALITY_MAX = 10
VULGARITY_MIN = 0
VULGARITY_MAX = 10
ARCHAICNESS_MIN = 0
ARCHAICNESS_MAX = 10


class Register(StrEnum):
    """Linguistic registers supported by the generator."""

    CASUAL = "casual"
    FORMAL = "formal"
    ARCHAIC = "archaic"
    ACADEMIC = "academic"
    LEGAL = "legal"
    VULGAR = "vulgar"


class PartOfSpeech(StrEnum):
    """Grammatical categories a grammar engine can build on."""

    NOUN = "noun"
    ADJECTIVE = "adjective"
    VERB = "verb"
    ADVERB = "adverb"


class Polarity(StrEnum):
    """Whether a word is an insult component on its own.

    ``POSITIVE`` entries (e.g. "perspicacity") only work as insults when negated
    or otherwise manipulated ("you lack perspicacity").
    """

    PEJORATIVE = "pejorative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"


class ReviewFlag(StrEnum):
    """Markers for entries that deserve a human second look."""

    OBSCURE = "obscure"
    OBSOLETE = "obsolete"
    REGIONAL = "regional"
    DISPUTED = "disputed"
    SENSITIVE = "sensitive"


INCOMPATIBLE_REGISTER_PAIRS: frozenset[frozenset[Register]] = frozenset(
    {
        frozenset({Register.FORMAL, Register.VULGAR}),
        frozenset({Register.ACADEMIC, Register.VULGAR}),
        frozenset({Register.LEGAL, Register.VULGAR}),
    }
)


def check_range(name: str, value: int, low: int, high: int) -> None:
    """Raise ``ValueError`` unless ``low <= value <= high``."""
    if not low <= value <= high:
        raise ValueError(f"{name} must be between {low} and {high}, got {value}")


@dataclass(frozen=True, slots=True)
class Concept:
    """A semantic concept (e.g. ``stupidity``) that groups related vocabulary."""

    id: str
    name: str
    description: str
    related: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class VocabularyEntry:
    """One lexical entry with the metadata the generator filters on."""

    term: str
    part_of_speech: PartOfSpeech
    primary_concept: str
    secondary_concepts: tuple[str, ...]
    register: frozenset[Register]
    severity: int
    formality: int
    vulgarity: int
    archaicness: int
    meaning_or_nuance: str
    usage_notes: str
    compatible_concepts: tuple[str, ...]
    polarity: Polarity = Polarity.PEJORATIVE
    review_flags: tuple[ReviewFlag, ...] = ()

    def __post_init__(self) -> None:
        if not self.term.strip():
            raise ValueError("term must not be empty")
        if not self.register:
            raise ValueError("register must contain at least one value")
        check_range("severity", self.severity, SEVERITY_MIN, SEVERITY_MAX)
        check_range("formality", self.formality, FORMALITY_MIN, FORMALITY_MAX)
        check_range("vulgarity", self.vulgarity, VULGARITY_MIN, VULGARITY_MAX)
        check_range("archaicness", self.archaicness, ARCHAICNESS_MIN, ARCHAICNESS_MAX)


@dataclass(frozen=True, slots=True)
class Vocabulary:
    """A validated dataset: concepts by id plus all entries."""

    concepts: Mapping[str, Concept]
    entries: tuple[VocabularyEntry, ...]


@dataclass(frozen=True, slots=True)
class GenerationParameters:
    """User-facing inputs to the generator. ``None`` means "no constraint"."""

    register: Register | None = None
    severity: int | None = None
    concept: str | None = None
    seed: int | None = None

    def __post_init__(self) -> None:
        if self.severity is not None:
            check_range("severity", self.severity, SEVERITY_MIN, SEVERITY_MAX)


@dataclass(frozen=True, slots=True)
class GeneratedInsult:
    """The result of one generation run, with provenance for debugging."""

    text: str
    parameters: GenerationParameters
    entries: tuple[VocabularyEntry, ...]
    template_id: str | None = None
