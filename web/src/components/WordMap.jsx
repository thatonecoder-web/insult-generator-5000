import { useMemo, useState } from "react";
import { useReveal } from "../hooks.js";
import { REGISTERS, primaryRegister } from "../lib/registers.js";

const AXES = [
  { id: "formality", label: "Formality", min: 1, max: 10, low: "slang", high: "formal" },
  { id: "severity", label: "Severity", min: 1, max: 10, low: "mild", high: "savage" },
  { id: "archaicness", label: "Archaicness", min: 0, max: 10, low: "current", high: "obsolete" },
  { id: "vulgarity", label: "Vulgarity", min: 0, max: 10, low: "clean", high: "crude" },
];
const WIDTH = 1000;
const HEIGHT = 560;
const MARGIN = { left: 70, right: 28, top: 24, bottom: 62 };

function jitter(term, salt) {
  let hash = 2166136261;
  for (const char of term + salt) {
    hash ^= char.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return ((hash >>> 0) % 1000) / 1000 - 0.5;
}

const DOMAIN_PADDING = 0.7;

function scale(value, axis, from, to) {
  const low = axis.min - DOMAIN_PADDING;
  const high = axis.max + DOMAIN_PADDING;
  return from + ((value - low) / (high - low)) * (to - from);
}

export default function WordMap({ entries, onOpenEntry }) {
  const sectionRef = useReveal();
  const [xId, setXId] = useState("formality");
  const [yId, setYId] = useState("severity");
  const [hidden, setHidden] = useState([]);
  const [hover, setHover] = useState(null);

  const xAxis = AXES.find((axis) => axis.id === xId);
  const yAxis = AXES.find((axis) => axis.id === yId);

  const points = useMemo(
    () =>
      entries.map((entry) => ({
        entry,
        register: primaryRegister(entry),
        x: scale(entry[xId] + jitter(entry.term, "x") * 0.75, xAxis, MARGIN.left, WIDTH - MARGIN.right),
        y: scale(entry[yId] + jitter(entry.term, "y") * 0.75, yAxis, HEIGHT - MARGIN.bottom, MARGIN.top),
      })),
    [entries, xId, yId, xAxis, yAxis],
  );

  const ticks = (axis) => Array.from({ length: axis.max - axis.min + 1 }, (_, index) => axis.min + index);

  const showTip = (event, point) => {
    const box = event.currentTarget.closest(".map__plot").getBoundingClientRect();
    const dot = event.currentTarget.getBoundingClientRect();
    setHover({
      entry: point.entry,
      left: dot.left - box.left + dot.width / 2,
      top: dot.top - box.top,
    });
  };

  return (
    <section className="section map reveal" id="map" ref={sectionRef}>
      <header className="section__head">
        <p className="eyebrow">03 · The Map of Malice</p>
        <h2>Every word, plotted.</h2>
        <p className="section__lede">
          Slide the axes to see how the vocabulary spreads. Formal words cluster at one end, crude
          ones at the other, and the harshest sit where you would expect them to.
        </p>
      </header>

      <div className="panel map__panel">
        <div className="map__controls">
          {[
            ["Across", xId, setXId],
            ["Up", yId, setYId],
          ].map(([label, value, setter]) => (
            <label key={label} className="mini-field">
              <span>{label}</span>
              <span className="select">
                <select value={value} onChange={(event) => setter(event.target.value)}>
                  {AXES.map((axis) => (
                    <option key={axis.id} value={axis.id}>
                      {axis.label}
                    </option>
                  ))}
                </select>
              </span>
            </label>
          ))}
          <div className="chipset" role="group" aria-label="Show registers">
            {REGISTERS.map((register) => {
              const off = hidden.includes(register.id);
              return (
                <button
                  key={register.id}
                  type="button"
                  className={`filter-chip filter-chip--${register.id}${off ? "" : " is-on"}`}
                  aria-pressed={!off}
                  onClick={() =>
                    setHidden(off ? hidden.filter((id) => id !== register.id) : [...hidden, register.id])
                  }
                >
                  <span className={`dot dot--${register.id}`} aria-hidden="true" />
                  {register.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="map__plot" onMouseLeave={() => setHover(null)}>
          <svg
            viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
            role="img"
            aria-label={`Scatter plot of ${entries.length} words by ${xAxis.label.toLowerCase()} and ${yAxis.label.toLowerCase()}. The lexicon above offers the same words as a keyboard-friendly list.`}
          >
            {ticks(xAxis).map((tick) => {
              const x = scale(tick, xAxis, MARGIN.left, WIDTH - MARGIN.right);
              return (
                <g key={`x${tick}`} className="map__tick">
                  <line x1={x} x2={x} y1={MARGIN.top} y2={HEIGHT - MARGIN.bottom} />
                  <text x={x} y={HEIGHT - MARGIN.bottom + 22} textAnchor="middle">
                    {tick}
                  </text>
                </g>
              );
            })}
            {ticks(yAxis).map((tick) => {
              const y = scale(tick, yAxis, HEIGHT - MARGIN.bottom, MARGIN.top);
              return (
                <g key={`y${tick}`} className="map__tick">
                  <line x1={MARGIN.left} x2={WIDTH - MARGIN.right} y1={y} y2={y} />
                  <text x={MARGIN.left - 14} y={y + 4} textAnchor="end">
                    {tick}
                  </text>
                </g>
              );
            })}
            <text className="map__axis" x={(MARGIN.left + WIDTH - MARGIN.right) / 2} y={HEIGHT - 12} textAnchor="middle">
              {xAxis.low} ← {xAxis.label.toLowerCase()} → {xAxis.high}
            </text>
            <text
              className="map__axis"
              transform={`translate(18 ${(MARGIN.top + HEIGHT - MARGIN.bottom) / 2}) rotate(-90)`}
              textAnchor="middle"
            >
              {yAxis.low} ← {yAxis.label.toLowerCase()} → {yAxis.high}
            </text>

            {points.map((point) => (
              <circle
                key={`${point.entry.term}-${point.entry.part_of_speech}`}
                className={`map__dot dot--${point.register}${hidden.includes(point.register) ? " is-hidden" : ""}`}
                r="6"
                style={{ transform: `translate(${point.x}px, ${point.y}px)` }}
                onMouseEnter={(event) => showTip(event, point)}
                onClick={() => onOpenEntry(point.entry)}
              />
            ))}
          </svg>

          {hover ? (
            <div className="map__tip" style={{ left: hover.left, top: hover.top }} role="presentation">
              <b>{hover.entry.term}</b>
              <span>{hover.entry.meaning_or_nuance}</span>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
}
