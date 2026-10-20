import assert from "node:assert/strict";
import { test } from "node:test";
import { groupParts } from "../src/lib/sentence.js";

const lit = (text) => ({ text, slot: null, entry: null });
const word = (text, entry) => ({ text, slot: "adj1", entry });

test("trailing punctuation attaches to the preceding vocabulary word", () => {
  const units = groupParts([lit("You are not merely "), word("vain", 0), lit("; you are "), word("rude", 1), lit(".")]);
  assert.deepEqual(units.map((u) => [u.text, u.tail]), [
    ["You are not merely ", ""],
    ["vain", ";"],
    [" you are ", ""],
    ["rude", "."],
  ]);
});

test("a literal that starts with a space is left alone", () => {
  const units = groupParts([word("dolt", 0), lit(" indeed")]);
  assert.deepEqual(units.map((u) => [u.text, u.tail]), [["dolt", ""], [" indeed", ""]]);
});

test("a literal that is only punctuation is absorbed completely", () => {
  const units = groupParts([word("knave", 0), lit("!")]);
  assert.equal(units.length, 1);
  assert.equal(units[0].tail, "!");
});

test("the entry index and slot survive grouping", () => {
  const [unit] = groupParts([word("dolt", 3)]);
  assert.equal(unit.entry, 3);
  assert.equal(unit.slot, "adj1");
});

test("multiple punctuation marks stay together", () => {
  const units = groupParts([word("rude", 0), lit("?! Well")]);
  assert.deepEqual(units.map((u) => [u.text, u.tail]), [["rude", "?!"], [" Well", ""]]);
});
