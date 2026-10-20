import { useEffect, useRef } from "react";
import { posAbbreviation } from "../lib/format.js";
import { primaryRegister } from "../lib/registers.js";

const FLAG_NOTES = {
  obscure: "Rare. Many readers will need a dictionary.",
  obsolete: "No longer in use. The generator only uses it in the archaic register.",
  regional: "Mainly used in particular regions or dialects.",
  disputed: "Its accuracy or usage is contested.",
  sensitive: "Its origin or other senses may offend. The generator never uses it.",
};

const SCORES = [
  ["severity", "Severity", "How harshly it lands as an insult"],
  ["formality", "Formality", "From slang to formal prose"],
  ["vulgarity", "Vulgarity", "From clean to crude"],
  ["archaicness", "Archaicness", "From current to obsolete"],
];

function describeKind(entry) {
  if (entry.noun_class) return `${entry.part_of_speech} · ${entry.noun_class}`;
  if (entry.part_of_speech === "adjective" && entry.targets?.length) {
    return `adjective · describes ${entry.targets.map((t) => (t === "thing" ? "arguments" : "people")).join(" and ")}`;
  }
  return entry.part_of_speech;
}

export default function EntryDialog({ entry, conceptsById, onClose, onAim }) {
  const dialog = useRef(null);

  useEffect(() => {
    const node = dialog.current;
    if (!node) return;
    if (entry && !node.open) node.showModal();
    if (!entry && node.open) node.close();
  }, [entry]);

  const name = (id) => conceptsById[id]?.name ?? id;

  return (
    <dialog
      ref={dialog}
      className="dialog"
      aria-labelledby="dialog-title"
      onClose={onClose}
      onClick={(event) => {
        if (event.target === dialog.current) dialog.current.close();
      }}
    >
      {entry ? (
        <div className="dialog__panel">
          <button
            type="button"
            className="icon-button dialog__close"
            onClick={() => dialog.current.close()}
            aria-label="Close"
          >
            ×
          </button>
          <p className="dialog__kind">{describeKind(entry)}</p>
          <h3 id="dialog-title" className={`dialog__term dialog__term--${primaryRegister(entry)}`}>
            {entry.term}
            <span>{posAbbreviation(entry.part_of_speech)}</span>
          </h3>
          <ul className="pills">
            {entry.register.map((register) => (
              <li key={register} className={`pill pill--${register}`}>
                {register}
              </li>
            ))}
          </ul>

          <p className="dialog__meaning">{entry.meaning_or_nuance}</p>
          <p className="dialog__notes">{entry.usage_notes}</p>

          {entry.polarity === "positive" ? (
            <p className="callout">
              A positive word. It only works as an insult when negated: <i>“devoid of {entry.term}”</i>.
            </p>
          ) : null}

          <dl className="scores">
            {SCORES.map(([key, label, hint]) => (
              <div key={key} className="score" title={hint}>
                <dt>{label}</dt>
                <dd>
                  <span className="meter" style={{ "--v": entry[key] / 10 }} />
                  <b>{entry[key]}</b>
                </dd>
              </div>
            ))}
          </dl>

          <div className="dialog__concepts">
            <h4>Concepts</h4>
            <ul className="chips">
              <li className="chip chip--primary">{name(entry.primary_concept)}</li>
              {entry.secondary_concepts.map((id) => (
                <li key={id} className="chip">
                  {name(id)}
                </li>
              ))}
            </ul>
            <h4>Pairs well with</h4>
            <ul className="chips">
              {entry.compatible_concepts
                .filter(
                  (id) => id !== entry.primary_concept && !entry.secondary_concepts.includes(id),
                )
                .map((id) => (
                  <li key={id} className="chip chip--quiet">
                    {name(id)}
                  </li>
                ))}
            </ul>
          </div>

          {entry.review_flags?.length ? (
            <ul className="flags">
              {entry.review_flags.map((flag) => (
                <li key={flag}>
                  <b>{flag}</b> {FLAG_NOTES[flag]}
                </li>
              ))}
            </ul>
          ) : null}

          <div className="dialog__footer">
            <button
              type="button"
              className="btn btn--primary"
              onClick={() => {
                dialog.current.close();
                onAim(entry.primary_concept);
              }}
            >
              Aim the forge at {name(entry.primary_concept)}
            </button>
          </div>
        </div>
      ) : null}
    </dialog>
  );
}
