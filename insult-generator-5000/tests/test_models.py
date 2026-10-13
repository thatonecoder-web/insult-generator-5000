import dataclasses
from typing import Any

import pytest

from insultgen.models import (
    INCOMPATIBLE_REGISTER_PAIRS,
    GenerationParameters,
    PartOfSpeech,
    Register,
    VocabularyEntry,
)


def _entry(**overrides: Any) -> VocabularyEntry:
    values: dict[str, Any] = {
        "term": "obtuse",
        "part_of_speech": PartOfSpeech.ADJECTIVE,
        "primary_concept": "stupidity",
        "secondary_concepts": (),
        "register": frozenset({Register.FORMAL}),
        "severity": 5,
        "formality": 8,
        "vulgarity": 0,
        "archaicness": 1,
        "meaning_or_nuance": "slow to understand",
        "usage_notes": "n/a",
        "compatible_concepts": ("stupidity",),
    }
    values.update(overrides)
    return VocabularyEntry(**values)


def test_registers_are_exactly_the_six_supported() -> None:
    assert {r.value for r in Register} == {
        "casual",
        "formal",
        "archaic",
        "academic",
        "legal",
        "vulgar",
    }


def test_register_parses_from_string() -> None:
    assert Register("academic") is Register.ACADEMIC


def test_invalid_register_value_is_rejected() -> None:
    with pytest.raises(ValueError):
        Register("pirate")


@pytest.mark.parametrize("severity", [0, 11, -1])
def test_entry_rejects_out_of_range_severity(severity: int) -> None:
    with pytest.raises(ValueError, match="severity"):
        _entry(severity=severity)


@pytest.mark.parametrize("field", ["formality", "vulgarity", "archaicness"])
def test_entry_rejects_out_of_range_scores(field: str) -> None:
    with pytest.raises(ValueError, match=field):
        _entry(**{field: 11})


def test_entry_requires_a_register() -> None:
    with pytest.raises(ValueError, match="register"):
        _entry(register=frozenset())


def test_entry_requires_a_term() -> None:
    with pytest.raises(ValueError, match="term"):
        _entry(term="  ")


def test_entry_is_immutable() -> None:
    entry = _entry()
    with pytest.raises(dataclasses.FrozenInstanceError):
        entry.severity = 9  # type: ignore[misc]


@pytest.mark.parametrize("severity", [0, 11])
def test_parameters_reject_invalid_severity(severity: int) -> None:
    with pytest.raises(ValueError, match="severity"):
        GenerationParameters(severity=severity)


@pytest.mark.parametrize("severity", [None, 1, 10])
def test_parameters_accept_valid_severity(severity: int | None) -> None:
    assert GenerationParameters(severity=severity).severity == severity


def test_vulgar_cannot_pair_with_formal_registers() -> None:
    assert frozenset({Register.FORMAL, Register.VULGAR}) in INCOMPATIBLE_REGISTER_PAIRS
