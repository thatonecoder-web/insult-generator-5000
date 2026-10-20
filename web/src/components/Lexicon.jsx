import { useDeferredValue, useMemo, useState } from "react";
import { useReveal } from "../hooks.js";
import { DEFAULT_FILTERS, SORTS, activeFilterCount, filterEntries } from "../lib/filters.js";
import { posAbbreviation } from "../lib/format.js";
import { REGISTERS, primaryRegister } from "../lib/registers.js";
import Icon from "./Icon.jsx";

const PAGE_SIZE = 48;
const PARTS_OF_SPEECH = ["noun", "adjective", "verb"];

function toggle(list, value) {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value];
}

function Card({ entry, conceptsById, onOpen }) {
  const register = primaryRegister(entry);
  return (
    <li>
      <button
        type="button"
        className={`card card--${register}`}
        onClick={() => onOpen(entry)}
        aria-label={`${entry.term}, ${entry.part_of_speech}. ${entry.meaning_or_nuance}`}
      >
        <span className="card__top">
          <span className="card__term">{entry.term}</span>
          <span className="card__pos">{posAbbreviation(entry.part_of_speech)}</span>
        </span>
        <span className="card__meaning">{entry.meaning_or_nuance}</span>
        <span className="card__foot">
          <span className="card__regs" aria-hidden="true">
            {entry.register.map((r) => (
              <span key={r} className={`dot dot--${r}`} />
            ))}
          </span>
          <span className="card__concept">{conceptsById[entry.primary_concept]?.name}</span>
          <span className="meter meter--sm" style={{ "--v": entry.severity / 10 }} aria-hidden="true" />
        </span>
      </button>
    </li>
  );
}

export default function Lexicon({ entries, concepts, conceptsById, onOpenEntry }) {
  const sectionRef = useReveal();
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const [shown, setShown] = useState(PAGE_SIZE);
  const deferred = useDeferredValue(filters);

  const matches = useMemo(() => filterEntries(entries, deferred), [entries, deferred]);
  const sortedConcepts = useMemo(
    () => [...concepts].sort((a, b) => a.name.localeCompare(b.name)),
    [concepts],
  );
  const active = activeFilterCount(filters);

  const update = (patch) => {
    setFilters((previous) => ({ ...previous, ...patch }));
    setShown(PAGE_SIZE);
  };

  return (
    <section className="section lexicon reveal" id="lexicon" ref={sectionRef}>
      <header className="section__head">
        <p className="eyebrow">02 · The Lexicon</p>
        <h2>{entries.length} words, sorted by hand.</h2>
        <p className="section__lede">
          Every word carries its register, its heat, and the nuance that separates it from its
          near-synonyms. Click any card for the full entry.
        </p>
      </header>

      <div className="filters panel">
        <div className="search">
          <Icon name="search" size={18} />
          <input
            type="search"
            className="input input--bare"
            placeholder="Search words and meanings"
            aria-label="Search the lexicon"
            value={filters.query}
            onChange={(event) => update({ query: event.target.value })}
          />
        </div>

        <div className="filters__row">
          <div className="chipset" role="group" aria-label="Filter by register">
            {REGISTERS.map((register) => (
              <button
                key={register.id}
                type="button"
                className={`filter-chip filter-chip--${register.id}${
                  filters.registers.includes(register.id) ? " is-on" : ""
                }`}
                aria-pressed={filters.registers.includes(register.id)}
                onClick={() => update({ registers: toggle(filters.registers, register.id) })}
              >
                <span className={`dot dot--${register.id}`} aria-hidden="true" />
                {register.label}
              </button>
            ))}
          </div>
          <div className="chipset" role="group" aria-label="Filter by part of speech">
            {PARTS_OF_SPEECH.map((pos) => (
              <button
                key={pos}
                type="button"
                className={`filter-chip${filters.partsOfSpeech.includes(pos) ? " is-on" : ""}`}
                aria-pressed={filters.partsOfSpeech.includes(pos)}
                onClick={() => update({ partsOfSpeech: toggle(filters.partsOfSpeech, pos) })}
              >
                {pos}s
              </button>
            ))}
          </div>
        </div>

        <div className="filters__row filters__row--fields">
          <label className="mini-field">
            <span>Concept</span>
            <span className="select">
              <select value={filters.concept} onChange={(event) => update({ concept: event.target.value })}>
                <option value="">All concepts</option>
                {sortedConcepts.map((concept) => (
                  <option key={concept.id} value={concept.id}>
                    {concept.name}
                  </option>
                ))}
              </select>
            </span>
          </label>
          <label className="mini-field">
            <span>Sort</span>
            <span className="select">
              <select value={filters.sort} onChange={(event) => update({ sort: event.target.value })}>
                {SORTS.map((sort) => (
                  <option key={sort.id} value={sort.id}>
                    {sort.label}
                  </option>
                ))}
              </select>
            </span>
          </label>
          <div className="mini-field mini-field--range">
            <span>
              Severity {filters.severity[0]}–{filters.severity[1]}
            </span>
            <div className="range-pair">
              <input
                type="range"
                min="1"
                max="10"
                aria-label="Minimum severity"
                value={filters.severity[0]}
                onChange={(event) =>
                  update({ severity: [Math.min(Number(event.target.value), filters.severity[1]), filters.severity[1]] })
                }
              />
              <input
                type="range"
                min="1"
                max="10"
                aria-label="Maximum severity"
                value={filters.severity[1]}
                onChange={(event) =>
                  update({ severity: [filters.severity[0], Math.max(Number(event.target.value), filters.severity[0])] })
                }
              />
            </div>
          </div>
        </div>

        <div className="filters__foot">
          <p aria-live="polite">
            <b>{matches.length}</b> of {entries.length} words
          </p>
          {active ? (
            <button type="button" className="link-button" onClick={() => update(DEFAULT_FILTERS)}>
              Clear {active} filter{active > 1 ? "s" : ""}
            </button>
          ) : null}
        </div>
      </div>

      {matches.length ? (
        <>
          <ul className="grid">
            {matches.slice(0, shown).map((entry) => (
              <Card
                key={`${entry.term}-${entry.part_of_speech}`}
                entry={entry}
                conceptsById={conceptsById}
                onOpen={onOpenEntry}
              />
            ))}
          </ul>
          {shown < matches.length ? (
            <div className="grid__more">
              <button type="button" className="btn btn--ghost" onClick={() => setShown(shown + PAGE_SIZE)}>
                Show {Math.min(PAGE_SIZE, matches.length - shown)} more
                <Icon name="down" size={16} />
              </button>
            </div>
          ) : null}
        </>
      ) : (
        <p className="empty">No words match those filters. Try loosening one.</p>
      )}
    </section>
  );
}
