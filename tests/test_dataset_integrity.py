from collections import Counter
from typing import Any

from insultgen.models import Register
from insultgen.validation import validate_dataset

MIN_ENTRIES_PER_REGISTER = 75


def test_bundled_dataset_is_valid(bundled_raw: dict[str, Any]) -> None:
    issues = validate_dataset(bundled_raw)
    assert issues == [], "\n".join(str(issue) for issue in issues)


def test_every_concept_has_at_least_one_entry(bundled_raw: dict[str, Any]) -> None:
    used = {entry["primary_concept"] for entry in bundled_raw["entries"]}
    unused = {c["id"] for c in bundled_raw["concepts"]} - used
    assert not unused, sorted(unused)


def test_every_register_is_well_populated(bundled_raw: dict[str, Any]) -> None:
    counts = Counter(r for entry in bundled_raw["entries"] for r in entry["register"])
    for register in Register:
        assert counts[register.value] >= MIN_ENTRIES_PER_REGISTER, (register, counts)


def test_terms_are_unique_across_the_dataset(bundled_raw: dict[str, Any]) -> None:
    terms = [entry["term"].casefold() for entry in bundled_raw["entries"]]
    repeated = [term for term, count in Counter(terms).items() if count > 1]
    assert not repeated, repeated


def test_compatible_concepts_include_the_primary_concept(bundled_raw: dict[str, Any]) -> None:
    missing = [
        entry["term"]
        for entry in bundled_raw["entries"]
        if entry["primary_concept"] not in entry["compatible_concepts"]
    ]
    assert not missing, missing


def test_positive_entries_are_marked_as_such(bundled_raw: dict[str, Any]) -> None:
    positives = [e for e in bundled_raw["entries"] if e.get("polarity") == "positive"]
    assert positives
    assert all("negation" in e["usage_notes"] for e in positives)
