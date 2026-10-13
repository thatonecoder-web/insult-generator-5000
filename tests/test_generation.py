import pytest

from insultgen.generation import InsultGenerator, filter_entries
from insultgen.models import GenerationParameters, Register, Vocabulary, VocabularyEntry


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


def test_generate_is_not_implemented_yet(minimal_vocabulary: Vocabulary) -> None:
    generator = InsultGenerator(minimal_vocabulary)
    with pytest.raises(NotImplementedError):
        generator.generate(GenerationParameters())
