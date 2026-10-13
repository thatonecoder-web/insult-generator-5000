"""Generation layer: vocabulary selection and (eventually) sentence construction."""

from insultgen.generation.engine import InsultGenerator
from insultgen.generation.selection import filter_entries

__all__ = ["InsultGenerator", "filter_entries"]
