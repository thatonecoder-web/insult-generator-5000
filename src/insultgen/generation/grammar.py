"""Small grammar helpers for assembling sentences."""

from __future__ import annotations

import re

_AN_PREFIXES = ("hon", "hour", "heir")
_A_BEFORE_VOWEL = re.compile(r"^(eu|one|once|use|usu|uti|ubi|unic|unif|unil|unio|uniq|unit|univ)")


def indefinite_article(word: str) -> str:
    """Return "a" or "an" for ``word`` using spelling and a few common exceptions."""
    lowered = word.strip().lower()
    if not lowered or not lowered[0].isalpha():
        return "a"
    if lowered.startswith(_AN_PREFIXES):
        return "an"
    if _A_BEFORE_VOWEL.match(lowered):
        return "a"
    return "an" if lowered[0] in "aeiou" else "a"


def capitalize_first(text: str) -> str:
    """Upper-case the first character only, leaving the rest untouched."""
    return text[:1].upper() + text[1:]
