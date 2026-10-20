import assert from "node:assert/strict";
import { test } from "node:test";
import { SEED_LIMIT, decodeState, encodeState, posAbbreviation, shareUrl } from "../src/lib/format.js";
import { primaryRegister } from "../src/lib/registers.js";
import { SEVERITY_LABELS, severityLabel } from "../src/lib/severity.js";

test("posAbbreviation", () => {
  assert.equal(posAbbreviation("noun"), "n.");
  assert.equal(posAbbreviation("adjective"), "adj.");
  assert.equal(posAbbreviation("other"), "other");
});

test("state round-trips through the URL fragment", () => {
  const state = { register: "legal", severity: 6, concept: "deception", seed: 42 };
  assert.deepEqual(decodeState(`#${encodeState(state)}`), state);
});

test("empty state encodes to a bare fragment", () => {
  assert.equal(encodeState({ register: null, severity: null, concept: null, seed: null }), "forge?");
});

test("seed zero survives the round trip", () => {
  const encoded = encodeState({ register: null, severity: null, concept: null, seed: 0 });
  assert.equal(decodeState(`#${encoded}`).seed, 0);
});

test("decodeState rejects bad values instead of trusting the URL", () => {
  const bad = decodeState("#forge?register=pirate&severity=11&concept=Bad%20Id&seed=-5");
  assert.deepEqual(bad, { register: null, severity: null, concept: null, seed: null });
  assert.equal(decodeState(`#forge?seed=${SEED_LIMIT}`).seed, null);
  assert.equal(decodeState("#forge?severity=5.5").severity, null);
});

test("decodeState ignores unrelated fragments", () => {
  assert.deepEqual(decodeState("#lexicon"), { register: null, severity: null, concept: null, seed: null });
  assert.deepEqual(decodeState(""), { register: null, severity: null, concept: null, seed: null });
});

test("shareUrl builds an absolute link", () => {
  const url = shareUrl({ origin: "https://example.test", pathname: "/" }, { register: "formal", severity: 3 });
  assert.equal(url, "https://example.test/#forge?register=formal&severity=3");
});

test("every severity level has a label", () => {
  assert.equal(SEVERITY_LABELS.length, 10);
  for (let level = 1; level <= 10; level += 1) assert.ok(severityLabel(level));
  assert.equal(severityLabel(0), SEVERITY_LABELS[0]);
  assert.equal(severityLabel(99), SEVERITY_LABELS[9]);
});

test("primaryRegister prefers the most specific register", () => {
  assert.equal(primaryRegister({ register: ["casual", "archaic"] }), "archaic");
  assert.equal(primaryRegister({ register: ["formal", "casual"] }), "formal");
  assert.equal(primaryRegister({ register: ["casual", "vulgar"] }), "vulgar");
});
