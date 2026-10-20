import { REGISTERS } from "../lib/registers.js";

export default function RegisterPicker({ value, onChange, entriesByRegister }) {
  return (
    <fieldset className="field">
      <legend className="field__label">Register</legend>
      <div className="tiles">
        <label className={`tile tile--any${value === null ? " is-selected" : ""}`}>
          <input
            type="radio"
            name="register"
            checked={value === null}
            onChange={() => onChange(null)}
          />
          <span className="tile__specimen">Any</span>
          <span className="tile__name">Surprise me</span>
          <span className="tile__blurb">A voice of its own choosing</span>
        </label>
        {REGISTERS.map((register) => (
          <label
            key={register.id}
            className={`tile tile--${register.id}${value === register.id ? " is-selected" : ""}`}
          >
            <input
              type="radio"
              name="register"
              checked={value === register.id}
              onChange={() => onChange(register.id)}
            />
            <span className="tile__specimen">{register.specimen}</span>
            <span className="tile__name">{register.label}</span>
            <span className="tile__blurb">{register.blurb}</span>
            {entriesByRegister?.[register.id] ? (
              <span className="tile__count">{entriesByRegister[register.id]} words</span>
            ) : null}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
