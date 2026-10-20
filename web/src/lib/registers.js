export const REGISTERS = [
  { id: "casual", label: "Casual", blurb: "Everyday and unfiltered", specimen: "dimwit" },
  { id: "formal", label: "Formal", blurb: "Polished and restrained", specimen: "obtuse" },
  { id: "archaic", label: "Archaic", blurb: "Shakespeare would blush", specimen: "knave" },
  { id: "academic", label: "Academic", blurb: "Footnotes included", specimen: "sophistry" },
  { id: "legal", label: "Legal", blurb: "Admissible in court", specimen: "frivolous" },
  { id: "vulgar", label: "Vulgar", blurb: "Not safe for work", specimen: "@#$%!" },
];

export const REGISTER_IDS = REGISTERS.map((register) => register.id);

// Most specific first: used to pick one display colour for an entry with several registers.
const PRECEDENCE = ["vulgar", "legal", "archaic", "academic", "formal", "casual"];

export function primaryRegister(entry) {
  return PRECEDENCE.find((id) => entry.register.includes(id)) ?? entry.register[0];
}
