"""Framework-independent request handling for the web API.

The HTTP layer (``server.py``) only moves bytes; everything that decides what a request
means lives here, so it can be tested without sockets.
"""

from __future__ import annotations

import threading
from collections import Counter
from typing import Any

from insultgen import __version__
from insultgen.generation import GenerationError, InsultGenerator
from insultgen.generation.engine import MAX_BATCH, SEED_LIMIT
from insultgen.generation.templates import FRAMES
from insultgen.loader import load_vocabulary
from insultgen.models import (
    SEVERITY_MAX,
    SEVERITY_MIN,
    GeneratedInsult,
    GenerationParameters,
    Polarity,
    Register,
    Vocabulary,
    VocabularyEntry,
)

REQUEST_FIELDS = ("register", "severity", "concept", "seed", "count")
WORKABLE_SEEDS = 24


class ApiError(Exception):
    """A client error with an HTTP status code and a message safe to show to users."""

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def entry_to_json(entry: VocabularyEntry) -> dict[str, Any]:
    """Serialize an entry using the same field names as the dataset file."""
    data: dict[str, Any] = {
        "term": entry.term,
        "part_of_speech": entry.part_of_speech.value,
        "primary_concept": entry.primary_concept,
        "secondary_concepts": list(entry.secondary_concepts),
        "register": sorted(r.value for r in entry.register),
        "severity": entry.severity,
        "formality": entry.formality,
        "vulgarity": entry.vulgarity,
        "archaicness": entry.archaicness,
        "meaning_or_nuance": entry.meaning_or_nuance,
        "usage_notes": entry.usage_notes,
        "compatible_concepts": list(entry.compatible_concepts),
    }
    if entry.noun_class is not None:
        data["noun_class"] = entry.noun_class.value
    if entry.part_of_speech.value == "adjective":
        data["targets"] = sorted(t.value for t in entry.targets)
    if entry.attributive_only:
        data["attributive_only"] = True
    if entry.polarity is not Polarity.PEJORATIVE:
        data["polarity"] = entry.polarity.value
    if entry.review_flags:
        data["review_flags"] = [flag.value for flag in entry.review_flags]
    return data


def insult_to_json(result: GeneratedInsult) -> dict[str, Any]:
    """Serialize a generated insult. ``parts[].entry`` indexes into ``entries``."""
    parts: list[dict[str, Any]] = []
    next_index = 0
    for part in result.parts:
        entry_index = None
        if part.entry is not None:
            entry_index = next_index
            next_index += 1
        parts.append({"text": part.text, "slot": part.slot, "entry": entry_index})

    requested = result.parameters
    return {
        "text": result.text,
        "register": result.register.value if result.register else None,
        "concept": result.concept,
        "seed": result.seed,
        "template_id": result.template_id,
        "template_text": result.template_text,
        "severity_tolerance": result.severity_tolerance,
        "requested": {
            "register": requested.register.value if requested.register else None,
            "severity": requested.severity,
            "concept": requested.concept,
            "seed": requested.seed,
        },
        "parts": parts,
        "entries": [entry_to_json(entry) for entry in result.entries],
    }


class InsultService:
    """Answers API requests for one loaded vocabulary."""

    def __init__(self, vocabulary: Vocabulary | None = None) -> None:
        self._vocabulary = vocabulary if vocabulary is not None else load_vocabulary()
        self._generator = InsultGenerator(self._vocabulary)
        self._meta: dict[str, Any] | None = None
        self._lock = threading.Lock()

    def vocabulary_payload(self) -> dict[str, Any]:
        """Every concept and entry, for the lexicon explorer."""
        return {
            "concepts": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "related": list(c.related),
                }
                for c in self._vocabulary.concepts.values()
            ],
            "entries": [entry_to_json(entry) for entry in self._vocabulary.entries],
        }

    def meta(self) -> dict[str, Any]:
        """Dataset statistics and which concepts each register can actually build."""
        with self._lock:
            if self._meta is None:
                self._meta = self._build_meta()
            return self._meta

    def generate(self, payload: object) -> dict[str, Any]:
        """Validate a request body, generate, and return the serialized results."""
        parameters, count = _parse_request(payload)
        try:
            results = self._generator.generate_batch(parameters, count)
        except GenerationError as error:
            raise ApiError(422, str(error)) from error
        return {"results": [insult_to_json(result) for result in results]}

    def _build_meta(self) -> dict[str, Any]:
        entries = self._vocabulary.entries
        by_register = Counter(r for e in entries for r in e.register)
        by_pos = Counter(e.part_of_speech.value for e in entries)
        primary = Counter(e.primary_concept for e in entries)
        registers = []
        for register in Register:
            registers.append(
                {
                    "id": register.value,
                    "entries": by_register[register],
                    "concepts": self._workable_concepts(register),
                }
            )
        return {
            "version": __version__,
            "counts": {
                "entries": len(entries),
                "concepts": len(self._vocabulary.concepts),
                "frames": len(FRAMES),
                "by_part_of_speech": dict(by_pos),
            },
            "registers": registers,
            "concepts": [
                {"id": c.id, "name": c.name, "entries": primary[c.id]}
                for c in self._vocabulary.concepts.values()
            ],
            "limits": {"severity": [SEVERITY_MIN, SEVERITY_MAX], "max_count": MAX_BATCH},
        }

    def _workable_concepts(self, register: Register) -> list[str]:
        workable = []
        for concept_id in self._vocabulary.concepts:
            for seed in range(WORKABLE_SEEDS):
                parameters = GenerationParameters(register=register, concept=concept_id, seed=seed)
                try:
                    self._generator.generate(parameters)
                except GenerationError:
                    continue
                workable.append(concept_id)
                break
        return workable


def _parse_request(payload: object) -> tuple[GenerationParameters, int]:
    if not isinstance(payload, dict):
        raise ApiError(400, "request body must be a JSON object")
    unknown = sorted(set(payload) - set(REQUEST_FIELDS))
    if unknown:
        raise ApiError(400, f"unknown field(s): {', '.join(unknown)}")

    register: Register | None = None
    if payload.get("register") is not None:
        try:
            register = Register(payload["register"])
        except ValueError:
            allowed = ", ".join(r.value for r in Register)
            raise ApiError(400, f"register must be one of: {allowed}") from None

    severity = payload.get("severity")
    if severity is not None and (
        not _is_int(severity) or not SEVERITY_MIN <= severity <= SEVERITY_MAX
    ):
        raise ApiError(400, f"severity must be an integer from {SEVERITY_MIN} to {SEVERITY_MAX}")

    concept = payload.get("concept")
    if concept is not None and not isinstance(concept, str):
        raise ApiError(400, "concept must be a string")

    seed = payload.get("seed")
    if seed is not None and (not _is_int(seed) or not 0 <= seed < SEED_LIMIT):
        raise ApiError(400, f"seed must be an integer from 0 to {SEED_LIMIT - 1}")

    count = payload.get("count", 1)
    if not _is_int(count) or not 1 <= count <= MAX_BATCH:
        raise ApiError(400, f"count must be an integer from 1 to {MAX_BATCH}")

    return GenerationParameters(register, severity, concept, seed), count


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)
