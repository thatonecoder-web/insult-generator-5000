import { useEffect, useState } from "react";
import { useReducedMotion, useReveal } from "../hooks.js";
import { REGISTERS } from "../lib/registers.js";

const STEPS = [
  ["Parameters", "Register, severity, concept and an optional seed come in."],
  ["Concept", "A concept anchors the sentence so its words belong together."],
  ["Vocabulary", "Candidates are pulled by part of speech, noun class and what an adjective can describe."],
  ["Register filter", "Only words tagged for the chosen register survive."],
  ["Severity window", "Words near the target are preferred. The window widens only if it must."],
  ["Frame", "A typed sentence frame is chosen. Its slots decide what may fill them."],
  ["Sentence", "Articles agree, then capitals and punctuation are set."],
  ["Validation", "No unfilled slots, no repeated words, no sensitive terms."],
];

const GUARDRAILS = [
  ["Typed slots", "“You are fallacious” cannot happen. Fallacious only describes arguments, so it is never offered for a person."],
  ["Mass and count nouns", "“A balderdash” cannot happen. Mass nouns only appear in frames that take them."],
  ["Negation-aware", "Positive words such as perspicacity only appear in frames like “devoid of …”."],
  ["Reproducible", "The same settings and seed always rebuild the same insult. Share links rely on it."],
  ["Safe defaults", "Sensitive terms are never used, and the vulgar register only appears when you ask for it."],
];

export default function HowItWorks({ meta }) {
  const sectionRef = useReveal();
  const reduced = useReducedMotion();
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    if (reduced || paused) return undefined;
    const timer = window.setInterval(() => setActive((step) => (step + 1) % STEPS.length), 2400);
    return () => window.clearInterval(timer);
  }, [reduced, paused]);

  const mostEntries = Math.max(...meta.registers.map((register) => register.entries));
  const topConcepts = [...meta.concepts].sort((a, b) => b.entries - a.entries).slice(0, 8);
  const mostInConcept = topConcepts[0]?.entries ?? 1;

  return (
    <section className="section how reveal" id="how" ref={sectionRef}>
      <header className="section__head">
        <p className="eyebrow">04 · How it works</p>
        <h2>Built, never shuffled.</h2>
        <p className="section__lede">
          A random word list makes word salad. This engine fills typed sentence frames from a
          curated vocabulary, one stage at a time.
        </p>
      </header>

      <ol
        className="pipeline"
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
      >
        {STEPS.map(([title, text], index) => (
          <li key={title} className={index === active ? "is-active" : ""}>
            <button type="button" onClick={() => setActive(index)} aria-current={index === active}>
              <span className="pipeline__n">{String(index + 1).padStart(2, "0")}</span>
              <b>{title}</b>
              <span>{text}</span>
            </button>
          </li>
        ))}
      </ol>

      <div className="how__cols">
        <div className="panel">
          <h3>Guardrails</h3>
          <ul className="guardrails">
            {GUARDRAILS.map(([title, text]) => (
              <li key={title}>
                <b>{title}</b>
                <span>{text}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="panel">
          <h3>The dataset</h3>
          <p className="stats__lede">
            {meta.counts.entries} entries across {meta.counts.concepts} concepts and{" "}
            {meta.counts.frames} sentence frames.
          </p>
          <ul className="bars" aria-label="Words per register">
            {REGISTERS.map((register) => {
              const entries = meta.registers.find((r) => r.id === register.id).entries;
              return (
                <li key={register.id}>
                  <span>{register.label}</span>
                  <span className="bars__track">
                    <span
                      className={`bars__fill dot--${register.id}`}
                      style={{ "--w": entries / mostEntries }}
                    />
                  </span>
                  <b>{entries}</b>
                </li>
              );
            })}
          </ul>
          <h4>Biggest concepts</h4>
          <ul className="bars" aria-label="Words per concept">
            {topConcepts.map((concept) => (
              <li key={concept.id}>
                <span>{concept.name}</span>
                <span className="bars__track">
                  <span className="bars__fill bars__fill--accent" style={{ "--w": concept.entries / mostInConcept }} />
                </span>
                <b>{concept.entries}</b>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
