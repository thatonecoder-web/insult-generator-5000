"""Loading the vocabulary dataset from disk into typed models."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from importlib.resources import files
from pathlib import Path
from typing import Any, cast

from insultgen.models import (
    Concept,
    NounClass,
    PartOfSpeech,
    Polarity,
    Register,
    ReviewFlag,
    Target,
    Vocabulary,
    VocabularyEntry,
)
from insultgen.validation import ValidationIssue, validate_dataset

BUNDLED_DATASET = "data/vocabulary.json"


class DatasetError(Exception):
    """Raised when a dataset fails validation. ``issues`` lists every problem."""

    def __init__(self, issues: Sequence[ValidationIssue]) -> None:
        self.issues = tuple(issues)
        preview = "; ".join(str(issue) for issue in self.issues[:3])
        more = f" (+{len(self.issues) - 3} more)" if len(self.issues) > 3 else ""
        super().__init__(f"dataset has {len(self.issues)} validation issue(s): {preview}{more}")


def load_raw(path: Path | None = None) -> object:
    """Read the JSON at ``path``, or the dataset bundled with the package."""
    if path is None:
        text = files("insultgen").joinpath(BUNDLED_DATASET).read_text(encoding="utf-8")
    else:
        text = path.read_text(encoding="utf-8")
    return json.loads(text)


def parse_vocabulary(raw: object) -> Vocabulary:
    """Validate ``raw`` and convert it to typed models, or raise ``DatasetError``."""
    issues = validate_dataset(raw)
    if issues:
        raise DatasetError(issues)

    data = cast("dict[str, Any]", raw)
    concepts = {item["id"]: _build_concept(item) for item in data["concepts"]}
    entries = tuple(_build_entry(item) for item in data["entries"])
    return Vocabulary(concepts=concepts, entries=entries)


def load_vocabulary(path: Path | None = None) -> Vocabulary:
    """Load and validate a dataset (the bundled one by default)."""
    return parse_vocabulary(load_raw(path))


def _build_concept(item: Mapping[str, Any]) -> Concept:
    return Concept(
        id=item["id"],
        name=item["name"],
        description=item["description"],
        related=tuple(item.get("related", ())),
    )


def _build_entry(item: Mapping[str, Any]) -> VocabularyEntry:
    return VocabularyEntry(
        term=item["term"],
        part_of_speech=PartOfSpeech(item["part_of_speech"]),
        primary_concept=item["primary_concept"],
        secondary_concepts=tuple(item["secondary_concepts"]),
        register=frozenset(Register(value) for value in item["register"]),
        severity=item["severity"],
        formality=item["formality"],
        vulgarity=item["vulgarity"],
        archaicness=item["archaicness"],
        meaning_or_nuance=item["meaning_or_nuance"],
        usage_notes=item["usage_notes"],
        compatible_concepts=tuple(item["compatible_concepts"]),
        polarity=Polarity(item.get("polarity", Polarity.PEJORATIVE.value)),
        review_flags=tuple(ReviewFlag(value) for value in item.get("review_flags", ())),
        noun_class=NounClass(item["noun_class"]) if "noun_class" in item else None,
        targets=frozenset(Target(value) for value in item.get("targets", ())),
        attributive_only=bool(item.get("attributive_only", False)),
    )
