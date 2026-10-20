const LEADING_PUNCTUATION = /^[.,;:!?)\u201d\u2019]+/;

/**
 * Turn the API's parts into display units. Punctuation that follows a vocabulary word is
 * attached to it, so a line can never wrap in front of a ";" or ".".
 */
export function groupParts(parts) {
  const units = [];
  for (const part of parts) {
    const previous = units[units.length - 1];
    if (part.entry === null && previous && previous.entry !== null) {
      const match = part.text.match(LEADING_PUNCTUATION);
      if (match) {
        previous.tail += match[0];
        const rest = part.text.slice(match[0].length);
        if (rest) units.push({ text: rest, slot: null, entry: null, tail: "" });
        continue;
      }
    }
    units.push({ text: part.text, slot: part.slot, entry: part.entry, tail: "" });
  }
  return units;
}
