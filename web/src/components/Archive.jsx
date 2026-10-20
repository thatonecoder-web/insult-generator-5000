import { useState } from "react";
import Icon from "./Icon.jsx";

function Row({ item, onRestore, onRemove }) {
  return (
    <li className="archive__row">
      <button type="button" className="archive__item" onClick={() => onRestore(item)}>
        <span className={`dot dot--${item.register}`} aria-hidden="true" />
        <span className="archive__text">{item.text}</span>
      </button>
      {onRemove ? (
        <button
          type="button"
          className="icon-button icon-button--sm"
          onClick={() => onRemove(item)}
          aria-label={`Remove "${item.text}" from saved`}
        >
          <Icon name="close" size={14} />
        </button>
      ) : null}
    </li>
  );
}

export default function Archive({ history, saved, onRestore, onRemoveSaved }) {
  const [tab, setTab] = useState("recent");
  const items = tab === "recent" ? history : saved;

  return (
    <section className="archive" aria-label="Previous insults">
      <div className="archive__tabs" role="tablist">
        {[
          ["recent", `Recent (${history.length})`],
          ["saved", `Hall of Fame (${saved.length})`],
        ].map(([id, label]) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={tab === id}
            className={tab === id ? "is-active" : ""}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>
      {items.length ? (
        <ul className="archive__list">
          {items.map((item) => (
            <Row
              key={`${item.seed}-${item.text}`}
              item={item}
              onRestore={onRestore}
              onRemove={tab === "saved" ? onRemoveSaved : null}
            />
          ))}
        </ul>
      ) : (
        <p className="archive__empty">
          {tab === "recent"
            ? "Nothing yet. Forge something."
            : "Star an insult to keep it here, even after you close the tab."}
        </p>
      )}
    </section>
  );
}
