export default function ConceptSelect({ value, onChange, concepts, available }) {
  const sorted = [...concepts].sort((a, b) => a.name.localeCompare(b.name));
  return (
    <div className="field">
      <label className="field__label" htmlFor="concept">
        Aim at
      </label>
      <div className="select">
        <select id="concept" value={value} onChange={(event) => onChange(event.target.value)}>
          <option value="">Any concept</option>
          {sorted.map((concept) => {
            const enabled = available.has(concept.id);
            return (
              <option key={concept.id} value={concept.id} disabled={!enabled}>
                {concept.name}
                {enabled ? "" : " (not in this register)"}
              </option>
            );
          })}
        </select>
      </div>
      <p className="field__hint">
        {available.size} of {concepts.length} concepts work with this register.
      </p>
    </div>
  );
}
