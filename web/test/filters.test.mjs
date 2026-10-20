import assert from "node:assert/strict";
import { test } from "node:test";
import { DEFAULT_FILTERS, activeFilterCount, filterEntries } from "../src/lib/filters.js";

const entry = (overrides) => ({
  term: "dolt",
  part_of_speech: "noun",
  primary_concept: "stupidity",
  secondary_concepts: [],
  register: ["casual"],
  severity: 5,
  formality: 3,
  vulgarity: 0,
  archaicness: 2,
  meaning_or_nuance: "a stupid person",
  ...overrides,
});

const ENTRIES = [
  entry({ term: "dolt" }),
  entry({ term: "obtuse", part_of_speech: "adjective", register: ["formal"], severity: 3 }),
  entry({
    term: "knave",
    register: ["archaic"],
    severity: 7,
    primary_concept: "dishonesty",
    secondary_concepts: ["wickedness"],
    meaning_or_nuance: "a dishonest man",
  }),
];

const terms = (list) => list.map((e) => e.term);

test("no filters keeps everything, sorted A to Z", () => {
  assert.deepEqual(terms(filterEntries(ENTRIES, DEFAULT_FILTERS)), ["dolt", "knave", "obtuse"]);
});

test("query matches the term and the meaning, ignoring case", () => {
  assert.deepEqual(terms(filterEntries(ENTRIES, { ...DEFAULT_FILTERS, query: "DISHONEST" })), ["knave"]);
  assert.deepEqual(terms(filterEntries(ENTRIES, { ...DEFAULT_FILTERS, query: "obt" })), ["obtuse"]);
});

test("register filter matches any selected register", () => {
  const filters = { ...DEFAULT_FILTERS, registers: ["formal", "archaic"] };
  assert.deepEqual(terms(filterEntries(ENTRIES, filters)), ["knave", "obtuse"]);
});

test("part of speech filter", () => {
  const filters = { ...DEFAULT_FILTERS, partsOfSpeech: ["adjective"] };
  assert.deepEqual(terms(filterEntries(ENTRIES, filters)), ["obtuse"]);
});

test("concept filter matches primary and secondary concepts", () => {
  assert.deepEqual(terms(filterEntries(ENTRIES, { ...DEFAULT_FILTERS, concept: "wickedness" })), ["knave"]);
  assert.deepEqual(terms(filterEntries(ENTRIES, { ...DEFAULT_FILTERS, concept: "dishonesty" })), ["knave"]);
});

test("severity range is inclusive", () => {
  const filters = { ...DEFAULT_FILTERS, severity: [3, 5] };
  assert.deepEqual(terms(filterEntries(ENTRIES, filters)), ["dolt", "obtuse"]);
});

test("sorting", () => {
  assert.deepEqual(
    terms(filterEntries(ENTRIES, { ...DEFAULT_FILTERS, sort: "severity-desc" })),
    ["knave", "dolt", "obtuse"],
  );
  assert.deepEqual(
    terms(filterEntries(ENTRIES, { ...DEFAULT_FILTERS, sort: "severity-asc" })),
    ["obtuse", "dolt", "knave"],
  );
});

test("filtering does not mutate its input", () => {
  const copy = [...ENTRIES];
  filterEntries(ENTRIES, { ...DEFAULT_FILTERS, sort: "severity-desc" });
  assert.deepEqual(ENTRIES, copy);
});

test("activeFilterCount", () => {
  assert.equal(activeFilterCount(DEFAULT_FILTERS), 0);
  assert.equal(
    activeFilterCount({ ...DEFAULT_FILTERS, query: "x", registers: ["legal"], severity: [2, 10] }),
    3,
  );
});
