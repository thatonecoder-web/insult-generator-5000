from typing import Any

import pytest

from insultgen.loader import load_raw, parse_vocabulary
from insultgen.models import Vocabulary


@pytest.fixture
def minimal_raw() -> dict[str, Any]:
    """A tiny valid dataset. A fresh copy per test, so tests may mutate it."""
    return {
        "schema_version": 1,
        "concepts": [
            {
                "id": "stupidity",
                "name": "Stupidity",
                "description": "Low intelligence.",
                "related": ["ignorance"],
            },
            {
                "id": "ignorance",
                "name": "Ignorance",
                "description": "Lack of knowledge.",
                "related": ["stupidity"],
            },
            {
                "id": "arrogance",
                "name": "Arrogance",
                "description": "Overbearing pride.",
                "related": [],
            },
        ],
        "entries": [
            {
                "term": "obtuse",
                "part_of_speech": "adjective",
                "primary_concept": "stupidity",
                "secondary_concepts": ["ignorance"],
                "register": ["formal"],
                "severity": 5,
                "formality": 8,
                "vulgarity": 0,
                "archaicness": 1,
                "meaning_or_nuance": "slow to understand",
                "usage_notes": "Fits people and arguments.",
                "compatible_concepts": ["stupidity", "ignorance"],
            },
            {
                "term": "dolt",
                "part_of_speech": "noun",
                "primary_concept": "stupidity",
                "secondary_concepts": [],
                "register": ["archaic", "casual"],
                "severity": 6,
                "formality": 4,
                "vulgarity": 0,
                "archaicness": 4,
                "meaning_or_nuance": "a stupid person",
                "usage_notes": "Short and punchy.",
                "compatible_concepts": ["stupidity"],
            },
            {
                "term": "humility",
                "part_of_speech": "noun",
                "primary_concept": "arrogance",
                "secondary_concepts": [],
                "register": ["formal"],
                "severity": 1,
                "formality": 7,
                "vulgarity": 0,
                "archaicness": 0,
                "meaning_or_nuance": "a modest view of one's own importance",
                "usage_notes": "Positive term; works via negation.",
                "compatible_concepts": ["arrogance"],
                "polarity": "positive",
                "review_flags": ["disputed"],
            },
        ],
    }


@pytest.fixture
def minimal_vocabulary(minimal_raw: dict[str, Any]) -> Vocabulary:
    return parse_vocabulary(minimal_raw)


@pytest.fixture(scope="session")
def bundled_raw() -> dict[str, Any]:
    raw = load_raw()
    assert isinstance(raw, dict)
    return raw
