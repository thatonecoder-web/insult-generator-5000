"""Print a quality-control summary of the vocabulary dataset.

Usage: python scripts/dataset_report.py [--path PATH]
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from insultgen.loader import load_vocabulary
from insultgen.models import Polarity, Register, ReviewFlag

LOWEST_CONCEPTS_SHOWN = 8


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, help="dataset to report on (default: bundled)")
    args = parser.parse_args(argv)

    vocabulary = load_vocabulary(args.path)
    entries = vocabulary.entries

    print(f"Unique entries:       {len(entries)}")
    print(f"Semantic concepts:    {len(vocabulary.concepts)}")
    print(f"Multi-register:       {sum(len(e.register) > 1 for e in entries)}")
    print(f"Positive polarity:    {sum(e.polarity is Polarity.POSITIVE for e in entries)}")

    print("\nEntries per register (an entry counts once per register it carries):")
    by_register = Counter(r for e in entries for r in e.register)
    for register in Register:
        print(f"  {register.value:<9}{by_register[register]:>4}")

    print("\nEntries per part of speech:")
    for pos, count in sorted(Counter(e.part_of_speech.value for e in entries).items()):
        print(f"  {pos:<10}{count:>4}")

    by_concept = Counter(e.primary_concept for e in entries)
    print(f"\nLeast-populated concepts (by primary concept, lowest {LOWEST_CONCEPTS_SHOWN}):")
    counts = sorted((by_concept[c], c) for c in vocabulary.concepts)
    for count, concept in counts[:LOWEST_CONCEPTS_SHOWN]:
        print(f"  {concept:<26}{count:>3}")

    print("\nEntries flagged for manual review:")
    for flag in ReviewFlag:
        terms = sorted(e.term for e in entries if flag in e.review_flags)
        print(f"  {flag.value} ({len(terms)}): {', '.join(terms) if terms else '-'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
