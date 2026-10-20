import { severityLabel } from "../lib/severity.js";
import Icon from "./Icon.jsx";

export default function SeverityDial({ value, onChange }) {
  return (
    <div className="field">
      <label className="field__label" htmlFor="severity">
        Severity
      </label>
      <div className="dial">
        <div className="dial__readout" style={{ "--heat": (value - 1) / 9 }}>
          <span className="dial__number">{value}</span>
          <span className="dial__name">{severityLabel(value)}</span>
          <span className="dial__flames" aria-hidden="true">
            {Array.from({ length: 5 }, (_, index) => (
              <Icon
                key={index}
                name="flame"
                size={16}
                className={index < Math.ceil(value / 2) ? "is-lit" : ""}
              />
            ))}
          </span>
        </div>
        <input
          id="severity"
          className="range range--heat"
          type="range"
          min="1"
          max="10"
          step="1"
          value={value}
          onChange={(event) => onChange(Number(event.target.value))}
          aria-valuetext={`${value} of 10, ${severityLabel(value)}`}
          style={{ "--fill": `${((value - 1) / 9) * 100}%` }}
        />
        <div className="dial__scale" aria-hidden="true">
          <span>Teasing</span>
          <span>Wounding</span>
        </div>
      </div>
    </div>
  );
}
