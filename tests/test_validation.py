from typing import Any

import pytest

from insultgen.validation import validate_dataset


def _messages(raw: object) -> list[str]:
    return [str(issue) for issue in validate_dataset(raw)]


def _assert_issue(raw: object, fragment: str) -> None:
    messages = _messages(raw)
    assert any(fragment in message for message in messages), messages


def test_minimal_dataset_is_valid(minimal_raw: dict[str, Any]) -> None:
    assert validate_dataset(minimal_raw) == []


def test_top_level_must_be_an_object() -> None:
    _assert_issue([], "top level must be a JSON object")


def test_schema_version_is_checked(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["schema_version"] = 99
    _assert_issue(minimal_raw, "schema_version")


def test_unknown_top_level_field(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["extras"] = []
    _assert_issue(minimal_raw, "unknown top-level field")


def test_missing_required_field(minimal_raw: dict[str, Any]) -> None:
    del minimal_raw["entries"][0]["usage_notes"]
    _assert_issue(minimal_raw, "missing required field 'usage_notes'")


def test_unknown_entry_field(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["colour"] = "blue"
    _assert_issue(minimal_raw, "unknown field 'colour'")


@pytest.mark.parametrize("value", [0, 11, -3, 5.5, "5", True, None])
def test_invalid_severity_values(minimal_raw: dict[str, Any], value: object) -> None:
    minimal_raw["entries"][0]["severity"] = value
    _assert_issue(minimal_raw, "severity")


@pytest.mark.parametrize("field", ["formality", "vulgarity", "archaicness"])
def test_other_scores_are_range_checked(minimal_raw: dict[str, Any], field: str) -> None:
    minimal_raw["entries"][0][field] = 11
    _assert_issue(minimal_raw, field)


def test_invalid_register_value(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["register"] = ["formal", "pirate"]
    _assert_issue(minimal_raw, "register contains invalid values")


def test_empty_register_list(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["register"] = []
    _assert_issue(minimal_raw, "register must be a non-empty list")


def test_duplicate_register_values(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["register"] = ["formal", "formal"]
    _assert_issue(minimal_raw, "register contains duplicates")


def test_invalid_part_of_speech(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["part_of_speech"] = "interjection"
    _assert_issue(minimal_raw, "part_of_speech")


def test_duplicate_entries_are_detected(minimal_raw: dict[str, Any]) -> None:
    clone = dict(minimal_raw["entries"][0])
    clone["term"] = "OBTUSE"
    minimal_raw["entries"].append(clone)
    _assert_issue(minimal_raw, "duplicate of entries[0]")


def test_same_term_with_different_part_of_speech_is_allowed(
    minimal_raw: dict[str, Any],
) -> None:
    clone = dict(minimal_raw["entries"][0])
    clone["part_of_speech"] = "noun"
    del clone["targets"]
    clone["noun_class"] = "person"
    minimal_raw["entries"].append(clone)
    assert validate_dataset(minimal_raw) == []


def test_unknown_primary_concept(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["primary_concept"] = "nope"
    _assert_issue(minimal_raw, "primary_concept 'nope' does not exist")


def test_unknown_secondary_and_compatible_concepts(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["secondary_concepts"] = ["nope"]
    minimal_raw["entries"][0]["compatible_concepts"] = ["nada"]
    messages = _messages(minimal_raw)
    assert any("secondary_concepts references unknown concept 'nope'" in m for m in messages)
    assert any("compatible_concepts references unknown concept 'nada'" in m for m in messages)


def test_secondary_must_not_repeat_primary(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["secondary_concepts"] = ["stupidity"]
    _assert_issue(minimal_raw, "must not repeat primary_concept")


def test_duplicate_concept_id(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["concepts"].append(dict(minimal_raw["concepts"][0]))
    _assert_issue(minimal_raw, "duplicate concept id")


def test_concept_ids_must_be_snake_case(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["concepts"][2]["id"] = "Bad Id"
    _assert_issue(minimal_raw, "lowercase snake_case")


def test_concept_relations_must_resolve(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["concepts"][0]["related"] = ["nope", "stupidity"]
    messages = _messages(minimal_raw)
    assert any("related concept 'nope' does not exist" in m for m in messages)
    assert any("cannot be related to itself" in m for m in messages)


def test_vulgar_register_requires_vulgarity(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["register"] = ["vulgar"]
    _assert_issue(minimal_raw, "vulgar register requires vulgarity")


def test_archaic_register_requires_archaicness(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["register"] = ["archaic"]
    minimal_raw["entries"][0]["archaicness"] = 0
    _assert_issue(minimal_raw, "archaic register requires archaicness")


@pytest.mark.parametrize("other", ["formal", "academic", "legal"])
def test_incompatible_register_combinations(minimal_raw: dict[str, Any], other: str) -> None:
    minimal_raw["entries"][0]["register"] = [other, "vulgar"]
    minimal_raw["entries"][0]["vulgarity"] = 5
    _assert_issue(minimal_raw, "incompatible register combination")


def test_positive_entries_must_have_low_severity(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][2]["severity"] = 6
    _assert_issue(minimal_raw, "positive-polarity entries must have severity")


def test_invalid_polarity_and_flags(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["polarity"] = "sideways"
    minimal_raw["entries"][1]["review_flags"] = ["spicy"]
    messages = _messages(minimal_raw)
    assert any("polarity" in m for m in messages)
    assert any("review_flags" in m for m in messages)


def test_whitespace_is_flagged(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["term"] = "obtuse "
    _assert_issue(minimal_raw, "leading or trailing whitespace")


def test_all_problems_are_reported_together(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["severity"] = 0
    minimal_raw["entries"][1]["primary_concept"] = "nope"
    minimal_raw["entries"][2]["register"] = []
    assert len(validate_dataset(minimal_raw)) >= 3


def test_non_object_entries_do_not_crash(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"].append("not an object")
    _assert_issue(minimal_raw, "must be an object")


def test_noun_class_is_only_valid_on_nouns(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["noun_class"] = "person"
    _assert_issue(minimal_raw, "noun_class is only valid on nouns")


def test_targets_are_only_valid_on_adjectives(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][1]["targets"] = ["person"]
    _assert_issue(minimal_raw, "targets is only valid on adjectives")


def test_invalid_noun_class_and_targets(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][1]["noun_class"] = "animal"
    minimal_raw["entries"][0]["targets"] = ["person", "robot"]
    messages = _messages(minimal_raw)
    assert any("noun_class must be one of" in m for m in messages)
    assert any("targets contains invalid values" in m for m in messages)


def test_empty_targets_are_allowed(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["targets"] = []
    assert validate_dataset(minimal_raw) == []


def test_attributive_only_must_be_true_on_an_adjective(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["attributive_only"] = True
    assert validate_dataset(minimal_raw) == []
    minimal_raw["entries"][0]["attributive_only"] = False
    _assert_issue(minimal_raw, "attributive_only must be true")
    minimal_raw["entries"][0]["attributive_only"] = True
    minimal_raw["entries"][1]["attributive_only"] = True
    _assert_issue(minimal_raw, "attributive_only is only valid on adjectives")
