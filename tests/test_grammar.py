import pytest

from insultgen.generation.grammar import capitalize_first, indefinite_article


@pytest.mark.parametrize(
    ("word", "article"),
    [
        ("obtuse", "an"),
        ("dolt", "a"),
        ("ill-advised", "an"),
        ("Janus-faced", "a"),
        ("ne'er-do-well", "a"),
        ("honest", "an"),
        ("hour", "an"),
        ("hubristic", "a"),
        ("usurious", "a"),
        ("unicorn", "a"),
        ("euphemism", "a"),
        ("one-sided", "a"),
        ("uninformed", "an"),
        ("unkempt", "an"),
        ("umbrella", "an"),
        ("ad hoc", "an"),
        ("", "a"),
        ("'tis", "a"),
    ],
)
def test_indefinite_article(word: str, article: str) -> None:
    assert indefinite_article(word) == article


@pytest.mark.parametrize(
    ("text", "expected"),
    [("hello there", "Hello there"), ("Hello", "Hello"), ("", ""), ("a thing", "A thing")],
)
def test_capitalize_first(text: str, expected: str) -> None:
    assert capitalize_first(text) == expected
