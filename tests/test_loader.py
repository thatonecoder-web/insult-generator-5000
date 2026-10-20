import json
from pathlib import Path
from typing import Any

import pytest

from insultgen.loader import DatasetError, load_raw, load_vocabulary, parse_vocabulary
from insultgen.models import NounClass, PartOfSpeech, Polarity, Register, ReviewFlag, Target


def test_bundled_dataset_loads() -> None:
    vocabulary = load_vocabulary()
    assert len(vocabulary.entries) >= 500
    assert 50 <= len(vocabulary.concepts) <= 70


def test_load_from_explicit_path(tmp_path: Path, minimal_raw: dict[str, Any]) -> None:
    path = tmp_path / "vocab.json"
    path.write_text(json.dumps(minimal_raw), encoding="utf-8")
    assert len(load_vocabulary(path).entries) == 3


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_raw(tmp_path / "nope.json")


def test_entries_are_converted_to_typed_values(minimal_raw: dict[str, Any]) -> None:
    vocabulary = parse_vocabulary(minimal_raw)
    obtuse, dolt, humility = vocabulary.entries
    assert obtuse.part_of_speech is PartOfSpeech.ADJECTIVE
    assert dolt.register == frozenset({Register.ARCHAIC, Register.CASUAL})
    assert obtuse.polarity is Polarity.PEJORATIVE
    assert obtuse.review_flags == ()
    assert humility.polarity is Polarity.POSITIVE
    assert humility.review_flags == (ReviewFlag.DISPUTED,)
    assert vocabulary.concepts["stupidity"].related == ("ignorance",)
    assert obtuse.targets == frozenset({Target.PERSON, Target.THING})
    assert obtuse.noun_class is None
    assert dolt.noun_class is NounClass.PERSON
    assert dolt.targets == frozenset()
    assert obtuse.attributive_only is False


def test_invalid_dataset_raises_with_all_issues(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["severity"] = 11
    minimal_raw["entries"][1]["register"] = ["pirate"]
    with pytest.raises(DatasetError) as excinfo:
        parse_vocabulary(minimal_raw)
    assert len(excinfo.value.issues) == 2
    assert "2 validation issue" in str(excinfo.value)


def test_attributive_only_is_loaded(minimal_raw: dict[str, Any]) -> None:
    minimal_raw["entries"][0]["attributive_only"] = True
    assert parse_vocabulary(minimal_raw).entries[0].attributive_only is True
