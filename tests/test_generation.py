import pytest

from insultgen.generation import GenerationError, InsultGenerator, filter_entries
from insultgen.generation.templates import FRAMES, attributive_slots
from insultgen.models import (
    GenerationParameters,
    Polarity,
    Register,
    ReviewFlag,
    Vocabulary,
    VocabularyEntry,
)


def _terms(entries: list[VocabularyEntry]) -> list[str]:
    return [entry.term for entry in entries]


def test_no_constraints_keeps_everything_in_order(minimal_vocabulary: Vocabulary) -> None:
    result = filter_entries(minimal_vocabulary.entries, GenerationParameters())
    assert _terms(result) == ["obtuse", "dolt", "humility"]


def test_register_filter(minimal_vocabulary: Vocabulary) -> None:
    params = GenerationParameters(register=Register.ARCHAIC)
    assert _terms(filter_entries(minimal_vocabulary.entries, params)) == ["dolt"]


def test_severity_filter_uses_tolerance(minimal_vocabulary: Vocabulary) -> None:
    params = GenerationParameters(severity=6)
    assert _terms(filter_entries(minimal_vocabulary.entries, params)) == ["obtuse", "dolt"]
    exact = filter_entries(minimal_vocabulary.entries, params, severity_tolerance=0)
    assert _terms(exact) == ["dolt"]


def test_concept_filter_matches_primary_and_secondary(minimal_vocabulary: Vocabulary) -> None:
    params = GenerationParameters(concept="ignorance")
    assert _terms(filter_entries(minimal_vocabulary.entries, params)) == ["obtuse"]
    params = GenerationParameters(concept="stupidity")
    assert _terms(filter_entries(minimal_vocabulary.entries, params)) == ["obtuse", "dolt"]


def test_constraints_combine(minimal_vocabulary: Vocabulary) -> None:
    params = GenerationParameters(register=Register.FORMAL, severity=5, concept="stupidity")
    assert _terms(filter_entries(minimal_vocabulary.entries, params)) == ["obtuse"]


def test_no_match_returns_empty_list(minimal_vocabulary: Vocabulary) -> None:
    params = GenerationParameters(register=Register.LEGAL)
    assert filter_entries(minimal_vocabulary.entries, params) == []


def test_filtering_is_deterministic(minimal_vocabulary: Vocabulary) -> None:
    params = GenerationParameters(severity=5)
    first = filter_entries(minimal_vocabulary.entries, params)
    assert first == filter_entries(minimal_vocabulary.entries, params)


def test_generator_candidates_use_the_filter(minimal_vocabulary: Vocabulary) -> None:
    generator = InsultGenerator(minimal_vocabulary)
    params = GenerationParameters(register=Register.CASUAL)
    assert _terms(generator.candidates(params)) == ["dolt"]
    assert generator.vocabulary is minimal_vocabulary


def _params(**kwargs: object) -> GenerationParameters:
    return GenerationParameters(**kwargs)  # type: ignore[arg-type]


def test_same_seed_gives_the_same_insult(bundled_generator: InsultGenerator) -> None:
    params = _params(register=Register.FORMAL, severity=5, seed=42)
    first = bundled_generator.generate(params)
    assert first.text == bundled_generator.generate(params).text
    assert first.seed == 42


def test_different_seeds_give_variety(bundled_generator: InsultGenerator) -> None:
    texts = {bundled_generator.generate(_params(severity=5, seed=s)).text for s in range(30)}
    assert len(texts) >= 25


def test_result_is_self_consistent(bundled_generator: InsultGenerator) -> None:
    template_ids = {frame.id for frame in FRAMES}
    for seed in range(60):
        result = bundled_generator.generate(_params(seed=seed))
        assert result.text == "".join(part.text for part in result.parts)
        assert result.template_id in template_ids
        assert result.text[0].isupper()
        assert result.text[-1] in ".!?"
        assert result.register is not None
        assert result.entries == tuple(p.entry for p in result.parts if p.entry is not None)
        assert len({e.term for e in result.entries}) == len(result.entries)


def test_every_register_and_severity_can_be_generated(bundled_generator: InsultGenerator) -> None:
    for register in Register:
        for severity in range(1, 11):
            for seed in range(5):
                params = _params(register=register, severity=severity, seed=seed)
                assert bundled_generator.generate(params).register is register


def test_requested_register_is_respected(bundled_generator: InsultGenerator) -> None:
    for register in Register:
        for seed in range(20):
            result = bundled_generator.generate(_params(register=register, seed=seed))
            assert all(register in entry.register for entry in result.entries)


def test_vulgar_is_never_chosen_unless_requested(bundled_generator: InsultGenerator) -> None:
    for seed in range(200):
        assert bundled_generator.generate(_params(seed=seed)).register is not Register.VULGAR


def test_severity_steers_the_output(bundled_generator: InsultGenerator) -> None:
    def mean_severity(level: int) -> float:
        results = [
            bundled_generator.generate(_params(register=Register.CASUAL, severity=level, seed=s))
            for s in range(40)
        ]
        scores = [e.severity for r in results for e in r.entries]
        return sum(scores) / len(scores)

    assert mean_severity(2) + 1.5 < mean_severity(8)


def test_sensitive_entries_are_never_used(bundled_generator: InsultGenerator) -> None:
    for register in Register:
        for seed in range(150):
            result = bundled_generator.generate(_params(register=register, seed=seed))
            assert all(ReviewFlag.SENSITIVE not in e.review_flags for e in result.entries)


def test_obsolete_entries_only_appear_in_archaic(bundled_generator: InsultGenerator) -> None:
    for register in Register:
        if register is Register.ARCHAIC:
            continue
        for seed in range(150):
            result = bundled_generator.generate(_params(register=register, seed=seed))
            assert all(ReviewFlag.OBSOLETE not in e.review_flags for e in result.entries)


def test_positive_words_only_appear_in_lack_frames(bundled_generator: InsultGenerator) -> None:
    seen_positive = False
    for register in Register:
        for seed in range(200):
            result = bundled_generator.generate(_params(register=register, seed=seed))
            for part in result.parts:
                if part.entry is not None and part.entry.polarity is Polarity.POSITIVE:
                    seen_positive = True
                    assert part.slot == "lack"
    assert seen_positive


def test_concept_constraint_is_honoured(bundled_generator: InsultGenerator) -> None:
    for seed in range(30):
        params = _params(register=Register.ACADEMIC, concept="flawed_reasoning", seed=seed)
        result = bundled_generator.generate(params)
        first = result.entries[0]
        assert "flawed_reasoning" in (first.primary_concept, *first.secondary_concepts)
        assert result.concept == "flawed_reasoning"


def test_unknown_concept_is_an_error(bundled_generator: InsultGenerator) -> None:
    with pytest.raises(GenerationError, match="unknown concept"):
        bundled_generator.generate(_params(concept="nope"))


def test_unbuildable_settings_raise(minimal_vocabulary: Vocabulary) -> None:
    generator = InsultGenerator(minimal_vocabulary)
    with pytest.raises(GenerationError, match="could not build"):
        generator.generate(_params(register=Register.LEGAL, seed=1))


def test_minimal_vocabulary_can_still_generate(minimal_vocabulary: Vocabulary) -> None:
    generator = InsultGenerator(minimal_vocabulary)
    result = generator.generate(_params(register=Register.FORMAL, seed=1))
    assert {e.term for e in result.entries} <= {"obtuse", "humility"}


def test_batch_is_reproducible_and_uses_consecutive_seeds(
    bundled_generator: InsultGenerator,
) -> None:
    params = _params(register=Register.CASUAL, seed=100)
    batch = bundled_generator.generate_batch(params, 5)
    assert [r.seed for r in batch] == [100, 101, 102, 103, 104]
    assert [r.text for r in batch] == [r.text for r in bundled_generator.generate_batch(params, 5)]


@pytest.mark.parametrize("count", [0, 51, -1])
def test_batch_rejects_bad_counts(bundled_generator: InsultGenerator, count: int) -> None:
    with pytest.raises(ValueError, match="count"):
        bundled_generator.generate_batch(_params(), count)


def test_concept_without_register_tries_every_register(bundled_generator: InsultGenerator) -> None:
    for seed in range(40):
        result = bundled_generator.generate(_params(concept="cowardice", seed=seed))
        assert result.register is not Register.VULGAR
        assert result.concept == "cowardice"


def test_intensifiers_only_appear_before_a_noun(bundled_generator: InsultGenerator) -> None:
    frames = {frame.id: frame for frame in FRAMES}
    seen = 0
    for seed in range(600):
        result = bundled_generator.generate(_params(register=Register.VULGAR, seed=seed))
        assert result.template_id is not None
        slots = attributive_slots(frames[result.template_id])
        for part in result.parts:
            if part.entry is not None and part.entry.attributive_only:
                seen += 1
                assert part.slot in slots, result.text
    assert seen
