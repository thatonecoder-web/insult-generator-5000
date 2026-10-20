import { REGISTER_IDS } from "./registers.js";

export const SEED_LIMIT = 2 ** 31;

const POS_ABBREVIATIONS = { noun: "n.", adjective: "adj.", verb: "v.", adverb: "adv." };

export function posAbbreviation(partOfSpeech) {
  return POS_ABBREVIATIONS[partOfSpeech] ?? partOfSpeech;
}

/** Encode forge settings as a URL fragment such as "forge?register=legal&severity=6". */
export function encodeState({ register, severity, concept, seed }) {
  const params = new URLSearchParams();
  if (register) params.set("register", register);
  if (severity) params.set("severity", String(severity));
  if (concept) params.set("concept", concept);
  if (seed !== null && seed !== undefined) params.set("seed", String(seed));
  return `forge?${params.toString()}`;
}

/** Parse a fragment produced by encodeState. Invalid or missing values become null. */
export function decodeState(hash) {
  const empty = { register: null, severity: null, concept: null, seed: null };
  const text = (hash ?? "").replace(/^#/, "");
  if (!text.startsWith("forge?")) return empty;

  const params = new URLSearchParams(text.slice("forge?".length));
  const register = params.get("register");
  const severity = Number(params.get("severity"));
  const seed = Number(params.get("seed"));
  const concept = params.get("concept");

  return {
    register: REGISTER_IDS.includes(register) ? register : null,
    severity: Number.isInteger(severity) && severity >= 1 && severity <= 10 ? severity : null,
    concept: concept && /^[a-z][a-z0-9_]*$/.test(concept) ? concept : null,
    seed:
      params.get("seed") !== null && Number.isInteger(seed) && seed >= 0 && seed < SEED_LIMIT
        ? seed
        : null,
  };
}

export function shareUrl(location, state) {
  return `${location.origin}${location.pathname}#${encodeState(state)}`;
}
