export const DEFAULT_FILTERS = {
  query: "",
  registers: [],
  partsOfSpeech: [],
  concept: "",
  severity: [1, 10],
  sort: "term",
};

export const SORTS = [
  { id: "term", label: "A to Z" },
  { id: "severity-desc", label: "Harshest first" },
  { id: "severity-asc", label: "Mildest first" },
  { id: "formality-desc", label: "Most formal" },
  { id: "archaicness-desc", label: "Most archaic" },
];

const COMPARATORS = {
  term: (a, b) => a.term.localeCompare(b.term, "en", { sensitivity: "base" }),
  "severity-desc": (a, b) => b.severity - a.severity || COMPARATORS.term(a, b),
  "severity-asc": (a, b) => a.severity - b.severity || COMPARATORS.term(a, b),
  "formality-desc": (a, b) => b.formality - a.formality || COMPARATORS.term(a, b),
  "archaicness-desc": (a, b) => b.archaicness - a.archaicness || COMPARATORS.term(a, b),
};

export function filterEntries(entries, filters) {
  const query = filters.query.trim().toLowerCase();
  const [minSeverity, maxSeverity] = filters.severity;

  const matches = entries.filter((entry) => {
    if (entry.severity < minSeverity || entry.severity > maxSeverity) return false;
    if (filters.registers.length && !entry.register.some((r) => filters.registers.includes(r))) {
      return false;
    }
    if (filters.partsOfSpeech.length && !filters.partsOfSpeech.includes(entry.part_of_speech)) {
      return false;
    }
    if (
      filters.concept &&
      entry.primary_concept !== filters.concept &&
      !entry.secondary_concepts.includes(filters.concept)
    ) {
      return false;
    }
    if (query) {
      const haystack = `${entry.term} ${entry.meaning_or_nuance}`.toLowerCase();
      if (!haystack.includes(query)) return false;
    }
    return true;
  });

  return matches.sort(COMPARATORS[filters.sort] ?? COMPARATORS.term);
}

export function activeFilterCount(filters) {
  let count = 0;
  if (filters.query.trim()) count += 1;
  if (filters.registers.length) count += 1;
  if (filters.partsOfSpeech.length) count += 1;
  if (filters.concept) count += 1;
  if (filters.severity[0] !== 1 || filters.severity[1] !== 10) count += 1;
  return count;
}
