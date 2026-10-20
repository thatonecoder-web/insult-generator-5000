"""Generation layer: vocabulary selection and sentence construction."""

from insultgen.generation.engine import GenerationError, InsultGenerator
from insultgen.generation.selection import filter_entries

__all__ = ["GenerationError", "InsultGenerator", "filter_entries"]
