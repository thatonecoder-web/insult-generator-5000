"""Generator: fills typed sentence frames with vocabulary entries."""

from __future__ import annotations

import dataclasses
import random
import re
import secrets

from insultgen.generation.grammar import capitalize_first, indefinite_article
from insultgen.generation.selection import filter_entries
from insultgen.generation.templates import (
    FRAMES,
    PLACEHOLDER,
    THING_NOUNS,
    Frame,
    SlotKind,
    attributive_slots,
)
from insultgen.models import (
    GeneratedInsult,
    GenerationParameters,
    InsultPart,
    NounClass,
    PartOfSpeech,
    Polarity,
    Register,
    ReviewFlag,
    Target,
    Vocabulary,
    VocabularyEntry,
)

SEED_LIMIT = 2**31
SEVERITY_TOLERANCES: tuple[int | None, ...] = (1, 2, 3, 5, None)
SPECIFIC_FRAME_WEIGHT = 4
RELATED_CONCEPT_WEIGHT = 6
MAX_BATCH = 50

_ATTRIBUTIVE_SLOTS = {frame.id: attributive_slots(frame) for frame in FRAMES}
_RANDOM_REGISTERS = tuple(r for r in Register if r is not Register.VULGAR)
_SENTENCE_END = re.compile(r"[.!?]$")


class GenerationError(Exception):
    """Raised when no sentence can be built for the requested parameters."""


def _adjective(entry: VocabularyEntry, *targets: Target) -> bool:
    return (
        entry.part_of_speech is PartOfSpeech.ADJECTIVE
        and entry.polarity is not Polarity.POSITIVE
        and set(targets) <= entry.targets
    )


def _noun(entry: VocabularyEntry, noun_class: NounClass, *, positive: bool) -> bool:
    return (
        entry.part_of_speech is PartOfSpeech.NOUN
        and entry.noun_class is noun_class
        and (entry.polarity is Polarity.POSITIVE) == positive
    )


class InsultGenerator:
    """Builds insults from a vocabulary.

    Output is deterministic for a given vocabulary, parameters and seed. Entries flagged
    ``sensitive`` are never used, and ``obsolete`` entries only appear in the archaic register.
    Verbs and adverbs are not used yet.
    """

    def __init__(self, vocabulary: Vocabulary) -> None:
        self._vocabulary = vocabulary
        usable = [e for e in vocabulary.entries if ReviewFlag.SENSITIVE not in e.review_flags]
        self._by_kind: dict[SlotKind, tuple[VocabularyEntry, ...]] = {
            SlotKind.PERSON_ADJECTIVE: tuple(e for e in usable if _adjective(e, Target.PERSON)),
            SlotKind.THING_ADJECTIVE: tuple(e for e in usable if _adjective(e, Target.THING)),
            SlotKind.BOTH_ADJECTIVE: tuple(
                e for e in usable if _adjective(e, Target.PERSON, Target.THING)
            ),
            SlotKind.PERSON_NOUN: tuple(
                e for e in usable if _noun(e, NounClass.PERSON, positive=False)
            ),
            SlotKind.ABSTRACT_NOUN: tuple(
                e for e in usable if _noun(e, NounClass.ABSTRACT, positive=False)
            ),
            SlotKind.LACK_NOUN: tuple(
                e for e in usable if _noun(e, NounClass.ABSTRACT, positive=True)
            ),
        }

    @property
    def vocabulary(self) -> Vocabulary:
        return self._vocabulary

    def candidates(self, parameters: GenerationParameters) -> list[VocabularyEntry]:
        """Entries eligible for ``parameters`` (register, severity and concept filters)."""
        return filter_entries(self._vocabulary.entries, parameters)

    def generate(self, parameters: GenerationParameters) -> GeneratedInsult:
        """Generate one insult, or raise ``GenerationError`` if none can be built."""
        concept = parameters.concept
        if concept is not None and concept not in self._vocabulary.concepts:
            raise GenerationError(f"unknown concept {concept!r}")

        seed = parameters.seed if parameters.seed is not None else secrets.randbelow(SEED_LIMIT)
        rng = random.Random(seed)
        if parameters.register is not None:
            registers = [parameters.register]
        else:
            registers = list(_RANDOM_REGISTERS)
            rng.shuffle(registers)
        tolerances = SEVERITY_TOLERANCES if parameters.severity is not None else (None,)

        for register in registers:
            frames = self._ordered_frames(register, rng)
            for tolerance in tolerances:
                for frame in frames:
                    filled = self._fill(frame, register, parameters, tolerance, rng)
                    if filled is not None:
                        return self._assemble(frame, filled, parameters, register, seed, tolerance)

        raise GenerationError("could not build an insult for these settings; try relaxing them")

    def generate_batch(self, parameters: GenerationParameters, count: int) -> list[GeneratedInsult]:
        """Generate ``count`` insults using consecutive seeds, so the batch is reproducible."""
        if not 1 <= count <= MAX_BATCH:
            raise ValueError(f"count must be between 1 and {MAX_BATCH}, got {count}")
        base = parameters.seed if parameters.seed is not None else secrets.randbelow(SEED_LIMIT)
        return [
            self.generate(dataclasses.replace(parameters, seed=(base + offset) % SEED_LIMIT))
            for offset in range(count)
        ]

    def _ordered_frames(self, register: Register, rng: random.Random) -> list[Frame]:
        remaining = [f for f in FRAMES if not f.registers or register in f.registers]
        ordered: list[Frame] = []
        while remaining:
            weights = [SPECIFIC_FRAME_WEIGHT if f.registers else 1 for f in remaining]
            index = rng.choices(range(len(remaining)), weights=weights)[0]
            ordered.append(remaining.pop(index))
        return ordered

    def _fill(
        self,
        frame: Frame,
        register: Register,
        parameters: GenerationParameters,
        tolerance: int | None,
        rng: random.Random,
    ) -> dict[str, VocabularyEntry | str] | None:
        chosen: dict[str, VocabularyEntry | str] = {}
        used: set[str] = set()
        required = parameters.concept
        attributive = _ATTRIBUTIVE_SLOTS[frame.id]
        context = self._concept_context(required) if required is not None else None

        for name in _slot_order(frame):
            kind = frame.slots[name]
            if kind is SlotKind.THING_NOUN:
                chosen[name] = rng.choice(THING_NOUNS)
                continue

            candidates = [
                e
                for e in self._by_kind[kind]
                if register in e.register
                and e.term not in used
                and _usable_in(e, register)
                and (name in attributive or not e.attributive_only)
                and _within(e, parameters.severity, tolerance)
            ]
            if required is not None:
                candidates = [
                    e
                    for e in candidates
                    if e.primary_concept == required or required in e.secondary_concepts
                ]
                required = None
            if not candidates:
                return None

            weights = [_weight(e, parameters.severity, context) for e in candidates]
            entry = rng.choices(candidates, weights=weights)[0]
            chosen[name] = entry
            used.add(entry.term)
            if context is None:
                context = self._concept_context(entry.primary_concept)

        return chosen

    def _concept_context(self, concept: str) -> frozenset[str]:
        return frozenset({concept, *self._vocabulary.concepts[concept].related})

    def _assemble(
        self,
        frame: Frame,
        chosen: dict[str, VocabularyEntry | str],
        parameters: GenerationParameters,
        register: Register,
        seed: int,
        tolerance: int | None,
    ) -> GeneratedInsult:
        parts: list[InsultPart] = []
        position = 0
        for match in PLACEHOLDER.finditer(frame.text):
            if match.start() > position:
                parts.append(InsultPart(frame.text[position : match.start()]))
            name = match.group(2)
            value = chosen[name]
            word = value.term if isinstance(value, VocabularyEntry) else value
            if match.group(1):
                parts.append(InsultPart(indefinite_article(word) + " "))
            entry = value if isinstance(value, VocabularyEntry) else None
            parts.append(InsultPart(word, slot=name, entry=entry))
            position = match.end()
        if position < len(frame.text):
            parts.append(InsultPart(frame.text[position:]))

        first = parts[0]
        parts[0] = dataclasses.replace(first, text=capitalize_first(first.text))
        text = "".join(part.text for part in parts)
        entries = tuple(part.entry for part in parts if part.entry is not None)
        _check_sentence(text, entries)

        anchor = parameters.concept or (entries[0].primary_concept if entries else None)
        return GeneratedInsult(
            text=text,
            parameters=parameters,
            entries=entries,
            template_id=frame.id,
            template_text=frame.text,
            parts=tuple(parts),
            register=register,
            concept=anchor,
            seed=seed,
            severity_tolerance=tolerance,
        )


def _slot_order(frame: Frame) -> list[str]:
    ordered: list[str] = []
    for _, name in PLACEHOLDER.findall(frame.text):
        if name not in ordered:
            ordered.append(name)
    return ordered


def _usable_in(entry: VocabularyEntry, register: Register) -> bool:
    return ReviewFlag.OBSOLETE not in entry.review_flags or register is Register.ARCHAIC


def _within(entry: VocabularyEntry, severity: int | None, tolerance: int | None) -> bool:
    return severity is None or tolerance is None or abs(entry.severity - severity) <= tolerance


def _weight(entry: VocabularyEntry, severity: int | None, context: frozenset[str] | None) -> float:
    weight = 1.0
    if severity is not None:
        weight /= 1 + abs(entry.severity - severity)
    if context is not None and (
        entry.primary_concept in context or context.intersection(entry.secondary_concepts)
    ):
        weight *= RELATED_CONCEPT_WEIGHT
    return weight


def _check_sentence(text: str, entries: tuple[VocabularyEntry, ...]) -> None:
    if "{" in text or "}" in text:
        raise GenerationError(f"unfilled placeholder in {text!r}")
    if not _SENTENCE_END.search(text):
        raise GenerationError(f"sentence has no closing punctuation: {text!r}")
    terms = [entry.term for entry in entries]
    if len(set(terms)) != len(terms):
        raise GenerationError(f"repeated word in {text!r}")
