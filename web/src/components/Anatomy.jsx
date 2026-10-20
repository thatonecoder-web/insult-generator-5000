import { posAbbreviation } from "../lib/format.js";
import { primaryRegister } from "../lib/registers.js";

const SLOT_LABELS = {
  adj: "adjective",
  person: "person noun",
  abstract: "abstract noun",
  lack: "positive noun, negated",
  thing: "target noun",
};

function slotLabel(slot) {
  return SLOT_LABELS[slot.replace(/\d+$/, "")] ?? "word";
}

export default function Anatomy({ result, conceptsById, onOpenEntry }) {
  const tolerance = result.severity_tolerance;
  const requested = result.requested;
  const entryParts = result.parts.filter((part) => part.entry !== null);

  return (
    <details className="anatomy">
      <summary>
        <span>Anatomy of this insult</span>
        <span className="anatomy__hint">See how it was built</span>
      </summary>
      <ol className="anatomy__steps">
        <li>
          <h4>Parameters</h4>
          <p>
            Register <b>{result.register}</b>
            {requested.register ? "" : " (chosen for you)"}.{" "}
            {requested.severity ? (
              <>
                Severity target <b>{requested.severity}</b>
                {tolerance === null
                  ? ", relaxed until a sentence fit."
                  : `, words within ±${tolerance}.`}
              </>
            ) : (
              "No severity target."
            )}{" "}
            Concept <b>{conceptsById[result.concept]?.name ?? "any"}</b>
            {requested.concept ? "" : " (anchored on the first word)"}.
          </p>
        </li>
        <li>
          <h4>Frame</h4>
          <p className="anatomy__frame">
            {result.template_text.split(/(\{[^}]+\})/).map((chunk, index) =>
              chunk.startsWith("{") ? (
                <code key={index}>{chunk}</code>
              ) : (
                <span key={index}>{chunk}</span>
              ),
            )}
          </p>
          <p className="anatomy__meta">
            Template <code>{result.template_id}</code> · seed <code>{result.seed}</code>
          </p>
        </li>
        <li>
          <h4>Vocabulary</h4>
          <ul className="anatomy__words">
            {entryParts.map((part) => {
              const entry = result.entries[part.entry];
              return (
                <li key={part.slot}>
                  <button type="button" onClick={() => onOpenEntry(entry)}>
                    <span className={`dot dot--${primaryRegister(entry)}`} aria-hidden="true" />
                    <b>{entry.term}</b>
                    <span className="anatomy__slot">
                      {part.slot} · {slotLabel(part.slot)}
                    </span>
                    <span className="anatomy__tags">
                      {posAbbreviation(entry.part_of_speech)} ·{" "}
                      {conceptsById[entry.primary_concept]?.name} · severity {entry.severity}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </li>
        <li>
          <h4>Checks passed</h4>
          <p>
            Every word fits its slot, the article agrees, no word repeats, no sensitive terms,
            and the sentence is correctly punctuated.
          </p>
        </li>
      </ol>
    </details>
  );
}
