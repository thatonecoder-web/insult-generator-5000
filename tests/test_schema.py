import json
from importlib.resources import files
from typing import Any

import pytest

from insultgen import validation
from insultgen.models import (
    ARCHAICNESS_MAX,
    ARCHAICNESS_MIN,
    FORMALITY_MAX,
    FORMALITY_MIN,
    SEVERITY_MAX,
    SEVERITY_MIN,
    VULGARITY_MAX,
    VULGARITY_MIN,
    NounClass,
    PartOfSpeech,
    Polarity,
    Register,
    ReviewFlag,
    Target,
)


@pytest.fixture(scope="module")
def schema() -> dict[str, Any]:
    text = files("insultgen").joinpath("data/vocabulary.schema.json").read_text(encoding="utf-8")
    loaded = json.loads(text)
    assert isinstance(loaded, dict)
    return loaded


def test_top_level_fields_match_validator(schema: dict[str, Any]) -> None:
    assert set(schema["required"]) == set(validation.TOP_LEVEL_FIELDS)
    assert set(schema["properties"]) == set(validation.TOP_LEVEL_FIELDS)
    assert schema["properties"]["schema_version"]["const"] == validation.SCHEMA_VERSION


def test_entry_fields_match_validator(schema: dict[str, Any]) -> None:
    entry = schema["$defs"]["entry"]
    assert set(entry["required"]) == set(validation.ENTRY_REQUIRED_FIELDS)
    expected = set(validation.ENTRY_REQUIRED_FIELDS) | set(validation.ENTRY_OPTIONAL_FIELDS)
    assert set(entry["properties"]) == expected
    assert entry["additionalProperties"] is False


def test_concept_fields_match_validator(schema: dict[str, Any]) -> None:
    concept = schema["$defs"]["concept"]
    assert set(concept["required"]) == set(validation.CONCEPT_REQUIRED_FIELDS)
    expected = set(validation.CONCEPT_REQUIRED_FIELDS) | set(validation.CONCEPT_OPTIONAL_FIELDS)
    assert set(concept["properties"]) == expected


def test_enums_match_models(schema: dict[str, Any]) -> None:
    props = schema["$defs"]["entry"]["properties"]
    assert props["part_of_speech"]["enum"] == [m.value for m in PartOfSpeech]
    assert props["register"]["items"]["enum"] == [m.value for m in Register]
    assert props["polarity"]["enum"] == [m.value for m in Polarity]
    assert props["review_flags"]["items"]["enum"] == [m.value for m in ReviewFlag]
    assert props["noun_class"]["enum"] == [m.value for m in NounClass]
    assert props["targets"]["items"]["enum"] == [m.value for m in Target]


def test_numeric_ranges_match_models(schema: dict[str, Any]) -> None:
    props = schema["$defs"]["entry"]["properties"]
    ranges = {
        "severity": (SEVERITY_MIN, SEVERITY_MAX),
        "formality": (FORMALITY_MIN, FORMALITY_MAX),
        "vulgarity": (VULGARITY_MIN, VULGARITY_MAX),
        "archaicness": (ARCHAICNESS_MIN, ARCHAICNESS_MAX),
    }
    for name, (low, high) in ranges.items():
        assert (props[name]["minimum"], props[name]["maximum"]) == (low, high)
