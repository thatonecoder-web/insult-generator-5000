export const SEVERITY_LABELS = [
  "Gentle nudge",
  "Mild tease",
  "Cheeky jab",
  "Sharp remark",
  "Proper insult",
  "Stinging",
  "Cutting",
  "Savage",
  "Brutal",
  "Scorched earth",
];

export function severityLabel(level) {
  return SEVERITY_LABELS[Math.min(10, Math.max(1, level)) - 1];
}
