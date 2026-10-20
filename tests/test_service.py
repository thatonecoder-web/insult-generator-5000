from typing import Any

import pytest

from insultgen.generation.templates import FRAMES
from insultgen.loader import load_vocabulary
from insultgen.models import Register
from insultgen.service import ApiError, InsultService, entry_to_json


@pytest.fixture(scope="module")
def service() -> InsultService:
    return InsultService()


def _normalised(raw_entry: dict[str, Any]) -> dict[str, Any]:
    entry = dict(raw_entry)
    entry["register"] = sorted(entry["register"])
    if "targets" in entry:
        entry["targets"] = sorted(entry["targets"])
    return entry


def test_entry_serialisation_is_lossless(bundled_raw: dict[str, Any]) -> None:
    vocabulary = load_vocabulary()
    for raw, entry in zip(bundled_raw["entries"], vocabulary.entries, strict=True):
        assert entry_to_json(entry) == _normalised(raw), raw["term"]


def test_vocabulary_payload(service: InsultService) -> None:
    payload = service.vocabulary_payload()
    vocabulary = load_vocabulary()
    assert len(payload["entries"]) == len(vocabulary.entries)
    assert [c["id"] for c in payload["concepts"]] == list(vocabulary.concepts)
    assert set(payload["concepts"][0]) == {"id", "name", "description", "related"}


def test_meta(service: InsultService) -> None:
    meta = service.meta()
    vocabulary = load_vocabulary()
    concept_ids = set(vocabulary.concepts)
    assert meta["counts"]["entries"] == len(vocabulary.entries)
    assert meta["counts"]["concepts"] == len(concept_ids)
    assert meta["counts"]["frames"] == len(FRAMES)
    assert sum(meta["counts"]["by_part_of_speech"].values()) == len(vocabulary.entries)
    assert [r["id"] for r in meta["registers"]] == [r.value for r in Register]
    for register in meta["registers"]:
        assert register["concepts"]
        assert set(register["concepts"]) <= concept_ids
    assert meta["limits"] == {"severity": [1, 10], "max_count": 50}
    assert service.meta() is meta


def test_meta_workable_concepts_really_work(service: InsultService) -> None:
    meta = service.meta()
    for register in meta["registers"]:
        workable = set(register["concepts"])
        unworkable = [c["id"] for c in meta["concepts"] if c["id"] not in workable]
        for concept in sorted(workable)[:3]:
            hits = 0
            for seed in range(24):
                try:
                    service.generate({"register": register["id"], "concept": concept, "seed": seed})
                    hits += 1
                except ApiError:
                    pass
            assert hits, (register["id"], concept)
        if unworkable:
            with pytest.raises(ApiError) as excinfo:
                service.generate({"register": register["id"], "concept": unworkable[0], "seed": 0})
            assert excinfo.value.status == 422


def test_generate_result_shape(service: InsultService) -> None:
    body = service.generate({"register": "formal", "severity": 6, "concept": None, "seed": 7})
    (result,) = body["results"]
    assert result["register"] == "formal"
    assert result["seed"] == 7
    assert result["requested"] == {
        "register": "formal",
        "severity": 6,
        "concept": None,
        "seed": 7,
    }
    assert result["text"] == "".join(part["text"] for part in result["parts"])
    entry_indices = [p["entry"] for p in result["parts"] if p["entry"] is not None]
    assert entry_indices == list(range(len(result["entries"])))
    for part in result["parts"]:
        if part["entry"] is not None:
            assert result["entries"][part["entry"]]["term"] == part["text"]


def test_generate_count(service: InsultService) -> None:
    body = service.generate({"count": 3, "seed": 10})
    assert [r["seed"] for r in body["results"]] == [10, 11, 12]


def test_generate_accepts_an_empty_request(service: InsultService) -> None:
    assert len(service.generate({})["results"]) == 1


@pytest.mark.parametrize(
    "payload",
    [
        [],
        "text",
        None,
        {"register": "pirate"},
        {"register": 5},
        {"severity": 0},
        {"severity": 11},
        {"severity": "5"},
        {"severity": True},
        {"severity": 5.5},
        {"seed": -1},
        {"seed": 2**31},
        {"seed": "1"},
        {"count": 0},
        {"count": 51},
        {"count": "2"},
        {"count": True},
        {"concept": 5},
        {"colour": "red"},
    ],
)
def test_generate_rejects_invalid_requests(service: InsultService, payload: object) -> None:
    with pytest.raises(ApiError) as excinfo:
        service.generate(payload)
    assert excinfo.value.status == 400


def test_unknown_concept_is_unprocessable(service: InsultService) -> None:
    with pytest.raises(ApiError) as excinfo:
        service.generate({"concept": "nope"})
    assert excinfo.value.status == 422
    assert "unknown concept" in excinfo.value.message
