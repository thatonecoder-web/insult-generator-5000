"""Dataset validation.

Works on the raw JSON structure so that *every* problem in a file can be
reported at once, instead of failing on the first bad entry. The same field
names and enums are mirrored in ``data/vocabulary.schema.json`` (checked by
the test suite) for editor support.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from insultgen.models import (
    ARCHAICNESS_MAX,
    ARCHAICNESS_MIN,
    FORMALITY_MAX,
    FORMALITY_MIN,
    INCOMPATIBLE_REGISTER_PAIRS,
    SEVERITY_MAX,
    SEVERITY_MIN,
    VULGARITY_MAX,
    VULGARITY_MIN,
    PartOfSpeech,
    Polarity,
    Register,
    ReviewFlag,
)

SCHEMA_VERSION = 1

TOP_LEVEL_FIELDS = ("schema_version", "concepts", "entries")
CONCEPT_REQUIRED_FIELDS = ("id", "name", "description")
CONCEPT_OPTIONAL_FIELDS = ("related",)
ENTRY_REQUIRED_FIELDS = (
    "term",
    "part_of_speech",
    "primary_concept",
    "secondary_concepts",
    "register",
    "severity",
    "formality",
    "vulgarity",
    "archaicness",
    "meaning_or_nuance",
    "usage_notes",
    "compatible_concepts",
)
ENTRY_OPTIONAL_FIELDS = ("polarity", "review_flags")

MAX_POSITIVE_SEVERITY = 2

_CONCEPT_ID = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """A single problem found in a dataset."""

    location: str
    message: str

    def __str__(self) -> str:
        return f"{self.location}: {self.message}"


def validate_dataset(raw: object) -> list[ValidationIssue]:
    """Return every problem found in ``raw``; an empty list means the data is valid."""
    if not isinstance(raw, dict):
        return [ValidationIssue("$", "top level must be a JSON object")]

    issues: list[ValidationIssue] = []

    for key in raw:
        if key not in TOP_LEVEL_FIELDS:
            issues.append(ValidationIssue("$", f"unknown top-level field {key!r}"))
    if raw.get("schema_version") != SCHEMA_VERSION:
        found = raw.get("schema_version")
        issues.append(ValidationIssue("schema_version", f"must be {SCHEMA_VERSION}, got {found!r}"))

    concept_ids = _validate_concepts(raw.get("concepts"), issues)
    _validate_entries(raw.get("entries"), concept_ids, issues)
    return issues


def _validate_concepts(raw: object, issues: list[ValidationIssue]) -> set[str]:
    if not isinstance(raw, list) or not raw:
        issues.append(ValidationIssue("concepts", "must be a non-empty list"))
        return set()

    seen: set[str] = set()
    pending_related: list[tuple[str, str, str]] = []

    for index, item in enumerate(raw):
        location = f"concepts[{index}]"
        if not isinstance(item, dict):
            issues.append(ValidationIssue(location, "must be an object"))
            continue

        _check_keys(item, CONCEPT_REQUIRED_FIELDS, CONCEPT_OPTIONAL_FIELDS, location, issues)

        concept_id = _text(item, "id", location, issues)
        _text(item, "name", location, issues)
        _text(item, "description", location, issues)

        if concept_id is not None:
            location = f"concepts[{index}] ({concept_id})"
            if not _CONCEPT_ID.match(concept_id):
                issues.append(ValidationIssue(location, "id must be lowercase snake_case"))
            if concept_id in seen:
                issues.append(ValidationIssue(location, "duplicate concept id"))
            seen.add(concept_id)

            related = _text_list(item, "related", location, issues)
            for target in related or []:
                pending_related.append((location, concept_id, target))

    for location, concept_id, target in pending_related:
        if target == concept_id:
            issues.append(ValidationIssue(location, "concept cannot be related to itself"))
        elif target not in seen:
            issues.append(ValidationIssue(location, f"related concept {target!r} does not exist"))

    return seen


def _validate_entries(raw: object, concept_ids: set[str], issues: list[ValidationIssue]) -> None:
    if not isinstance(raw, list) or not raw:
        issues.append(ValidationIssue("entries", "must be a non-empty list"))
        return

    seen: dict[tuple[str, str], int] = {}

    for index, item in enumerate(raw):
        location = f"entries[{index}]"
        if not isinstance(item, dict):
            issues.append(ValidationIssue(location, "must be an object"))
            continue

        term = _text(item, "term", location, issues)
        if term is not None:
            location = f"entries[{index}] ({term})"
        _check_keys(item, ENTRY_REQUIRED_FIELDS, ENTRY_OPTIONAL_FIELDS, location, issues)

        pos = _choice(item, "part_of_speech", PartOfSpeech, location, issues)
        if term is not None and pos is not None:
            key = (term.casefold(), pos)
            if key in seen:
                first = seen[key]
                message = f"duplicate of entries[{first}] (same term and part of speech)"
                issues.append(ValidationIssue(location, message))
            else:
                seen[key] = index

        _validate_entry_body(item, concept_ids, location, issues)


def _validate_entry_body(
    item: dict[str, Any], concept_ids: set[str], location: str, issues: list[ValidationIssue]
) -> None:
    primary = _text(item, "primary_concept", location, issues)
    if primary is not None and primary not in concept_ids:
        issues.append(ValidationIssue(location, f"primary_concept {primary!r} does not exist"))

    secondary = _text_list(item, "secondary_concepts", location, issues)
    _check_concept_refs(secondary, "secondary_concepts", concept_ids, location, issues)
    if secondary is not None:
        if primary is not None and primary in secondary:
            message = "secondary_concepts must not repeat primary_concept"
            issues.append(ValidationIssue(location, message))
        _check_unique(secondary, "secondary_concepts", location, issues)

    compatible = _text_list(item, "compatible_concepts", location, issues)
    _check_concept_refs(compatible, "compatible_concepts", concept_ids, location, issues)
    if compatible is not None:
        _check_unique(compatible, "compatible_concepts", location, issues)

    registers = _choice_list(item, "register", Register, location, issues, allow_empty=False)

    severity = _integer(item, "severity", SEVERITY_MIN, SEVERITY_MAX, location, issues)
    _integer(item, "formality", FORMALITY_MIN, FORMALITY_MAX, location, issues)
    vulgarity = _integer(item, "vulgarity", VULGARITY_MIN, VULGARITY_MAX, location, issues)
    archaicness = _integer(item, "archaicness", ARCHAICNESS_MIN, ARCHAICNESS_MAX, location, issues)

    _text(item, "meaning_or_nuance", location, issues)
    _text(item, "usage_notes", location, issues)

    polarity = Polarity.PEJORATIVE.value
    if "polarity" in item:
        polarity = _choice(item, "polarity", Polarity, location, issues) or polarity
    if "review_flags" in item:
        _choice_list(item, "review_flags", ReviewFlag, location, issues, allow_empty=True)

    if registers is None:
        return

    chosen = set(registers)
    if Register.VULGAR.value in chosen and vulgarity is not None and vulgarity < 1:
        message = "vulgar register requires vulgarity of at least 1"
        issues.append(ValidationIssue(location, message))
    if Register.ARCHAIC.value in chosen and archaicness is not None and archaicness < 1:
        message = "archaic register requires archaicness of at least 1"
        issues.append(ValidationIssue(location, message))
    for pair in INCOMPATIBLE_REGISTER_PAIRS:
        if {r.value for r in pair} <= chosen:
            names = " + ".join(sorted(r.value for r in pair))
            message = f"incompatible register combination: {names}"
            issues.append(ValidationIssue(location, message))
    if (
        polarity == Polarity.POSITIVE.value
        and severity is not None
        and severity > MAX_POSITIVE_SEVERITY
    ):
        message = f"positive-polarity entries must have severity <= {MAX_POSITIVE_SEVERITY}"
        issues.append(ValidationIssue(location, message))


def _check_keys(
    item: dict[str, Any],
    required: tuple[str, ...],
    optional: tuple[str, ...],
    location: str,
    issues: list[ValidationIssue],
) -> None:
    for key in required:
        if key not in item:
            issues.append(ValidationIssue(location, f"missing required field {key!r}"))
    for key in item:
        if key not in required and key not in optional:
            issues.append(ValidationIssue(location, f"unknown field {key!r}"))


def _text(
    item: dict[str, Any], key: str, location: str, issues: list[ValidationIssue]
) -> str | None:
    value = item.get(key)
    if key not in item:
        return None
    if not isinstance(value, str) or not value.strip():
        issues.append(ValidationIssue(location, f"{key} must be a non-empty string"))
        return None
    if value != value.strip():
        issues.append(ValidationIssue(location, f"{key} has leading or trailing whitespace"))
    return value


def _text_list(
    item: dict[str, Any], key: str, location: str, issues: list[ValidationIssue]
) -> list[str] | None:
    if key not in item:
        return None
    value = item[key]
    if not isinstance(value, list) or not all(isinstance(v, str) and v for v in value):
        issues.append(ValidationIssue(location, f"{key} must be a list of non-empty strings"))
        return None
    return value


def _integer(
    item: dict[str, Any],
    key: str,
    low: int,
    high: int,
    location: str,
    issues: list[ValidationIssue],
) -> int | None:
    if key not in item:
        return None
    value = item[key]
    if isinstance(value, bool) or not isinstance(value, int):
        issues.append(ValidationIssue(location, f"{key} must be an integer"))
        return None
    if not low <= value <= high:
        message = f"{key} must be between {low} and {high}, got {value}"
        issues.append(ValidationIssue(location, message))
        return None
    return value


def _choice(
    item: dict[str, Any], key: str, enum: type[Any], location: str, issues: list[ValidationIssue]
) -> str | None:
    if key not in item:
        return None
    value = item[key]
    allowed = [member.value for member in enum]
    if not isinstance(value, str) or value not in allowed:
        issues.append(ValidationIssue(location, f"{key} must be one of {allowed}, got {value!r}"))
        return None
    return value


def _choice_list(
    item: dict[str, Any],
    key: str,
    enum: type[Any],
    location: str,
    issues: list[ValidationIssue],
    *,
    allow_empty: bool,
) -> list[str] | None:
    if key not in item:
        return None
    value = item[key]
    allowed = [member.value for member in enum]
    if not isinstance(value, list) or (not value and not allow_empty):
        issues.append(ValidationIssue(location, f"{key} must be a non-empty list"))
        return None
    bad = [v for v in value if not isinstance(v, str) or v not in allowed]
    if bad:
        message = f"{key} contains invalid values {bad}; allowed: {allowed}"
        issues.append(ValidationIssue(location, message))
        return None
    _check_unique(value, key, location, issues)
    return value


def _check_concept_refs(
    values: list[str] | None,
    key: str,
    concept_ids: set[str],
    location: str,
    issues: list[ValidationIssue],
) -> None:
    for value in values or []:
        if value not in concept_ids:
            issues.append(ValidationIssue(location, f"{key} references unknown concept {value!r}"))


def _check_unique(
    values: list[str], key: str, location: str, issues: list[ValidationIssue]
) -> None:
    if len(set(values)) != len(values):
        issues.append(ValidationIssue(location, f"{key} contains duplicates"))
