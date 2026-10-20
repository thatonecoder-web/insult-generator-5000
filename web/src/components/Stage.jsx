import { posAbbreviation } from "../lib/format.js";
import { primaryRegister } from "../lib/registers.js";
import { groupParts } from "../lib/sentence.js";
import Anatomy from "./Anatomy.jsx";
import Icon from "./Icon.jsx";

const HEADINGS = {
  casual: "Just saying",
  formal: "Correspondence",
  archaic: "A Proclamation",
  academic: "Abstract",
  legal: "Exhibit A",
  vulgar: "Uncensored",
};

function Word({ unit, index, entry, tipId, onOpenEntry }) {
  const style = { "--i": index };
  if (entry === null) {
    return (
      <span className="word" style={style}>
        {unit.text}
      </span>
    );
  }
  return (
    <span className={`word word--group word--${primaryRegister(entry)}`} style={style}>
      <button
        type="button"
        className="word__entry"
        aria-describedby={tipId}
        onClick={() => onOpenEntry(entry)}
      >
        {unit.text}
        <span className="tip" id={tipId} aria-hidden="true">
          <b>{entry.term}</b> <i>{posAbbreviation(entry.part_of_speech)}</i>
          <span>{entry.meaning_or_nuance}</span>
        </span>
      </button>
      {unit.tail}
    </span>
  );
}

export default function Stage({
  result,
  status,
  error,
  isSaved,
  conceptsById,
  onAgain,
  onCopy,
  onShare,
  onToggleSave,
  onOpenEntry,
  onClearConcept,
}) {
  const register = result?.register ?? "any";
  const loading = status === "loading";

  return (
    <article className={`stage stage--${register}${loading ? " is-loading" : ""}`}>
      <div className="stage__chrome">
        <span className="stage__label">{HEADINGS[register] ?? "Your insult"}</span>
        {result ? (
          <span className="stage__register">
            <span className={`dot dot--${register}`} aria-hidden="true" />
            {register}
          </span>
        ) : null}
      </div>

      <div className="stage__body">
        {status === "error" ? (
          <div className="stage__error" role="alert">
            <p>{error}</p>
            {onClearConcept ? (
              <button type="button" className="btn btn--ghost btn--sm" onClick={onClearConcept}>
                Clear the concept
              </button>
            ) : null}
          </div>
        ) : result ? (
          <p
            className="stage__text"
            key={`${result.seed}-${result.text}`}
            aria-live="polite"
            aria-atomic="true"
          >
            {groupParts(result.parts).map((unit, index) => (
              <Word
                key={index}
                unit={unit}
                index={index}
                entry={unit.entry === null ? null : result.entries[unit.entry]}
                tipId={`tip-${result.seed}-${index}`}
                onOpenEntry={onOpenEntry}
              />
            ))}
          </p>
        ) : (
          <p className="stage__placeholder">Forging…</p>
        )}
      </div>

      <div className="stage__actions">
        <button type="button" className="btn btn--primary" onClick={onAgain} disabled={loading}>
          <Icon name="dice" size={18} /> Forge another
          <kbd>Space</kbd>
        </button>
        <button type="button" className="btn btn--ghost" onClick={onCopy} disabled={!result}>
          <Icon name="copy" size={18} /> Copy
        </button>
        <button type="button" className="btn btn--ghost" onClick={onShare} disabled={!result}>
          <Icon name="link" size={18} /> Share
        </button>
        <button
          type="button"
          className={`btn btn--ghost${isSaved ? " is-active" : ""}`}
          onClick={onToggleSave}
          disabled={!result}
          aria-pressed={isSaved}
        >
          <Icon name="star" size={18} /> {isSaved ? "Saved" : "Save"}
        </button>
      </div>

      {result ? (
        <Anatomy result={result} conceptsById={conceptsById} onOpenEntry={onOpenEntry} />
      ) : null}
    </article>
  );
}
