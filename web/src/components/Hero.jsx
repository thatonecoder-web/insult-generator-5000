import { useMemo } from "react";
import { primaryRegister } from "../lib/registers.js";
import Icon from "./Icon.jsx";

const TICKER_SIZE = 34;

const SPECIMENS = [
  { register: "archaic", label: "A Proclamation", text: "Thou art a craven knave!", x: "2%", y: "0px", r: "-5deg", d: "0s" },
  { register: "formal", label: "Correspondence", text: "One cannot help observing that you are obtuse.", x: "20%", y: "92px", r: "3deg", d: "-2s" },
  { register: "casual", label: "Just saying", text: "You absolute dimwit.", x: "0%", y: "206px", r: "-3deg", d: "-4s" },
  { register: "legal", label: "Exhibit A", text: "Objection: the claim is frivolous and vexatious.", x: "22%", y: "290px", r: "4deg", d: "-1s" },
  { register: "academic", label: "Abstract", text: "To call that argument reductive would be generous.", x: "2%", y: "408px", r: "-2deg", d: "-3s" },
  { register: "vulgar", label: "Uncensored", text: "Shut up, you @#$%!", x: "20%", y: "512px", r: "-4deg", d: "-5s" },
];

/** A deterministic, tasteful sample of the vocabulary for the decorative ticker. */
function tickerWords(entries) {
  const pool = entries.filter(
    (entry) =>
      !entry.register.includes("vulgar") &&
      !(entry.review_flags ?? []).includes("sensitive") &&
      entry.polarity !== "positive" &&
      entry.term.length <= 14,
  );
  const step = Math.max(1, Math.floor(pool.length / TICKER_SIZE));
  return pool.filter((_, index) => index % step === 0).slice(0, TICKER_SIZE);
}

export default function Hero({ meta, entries }) {
  const words = useMemo(() => tickerWords(entries), [entries]);

  return (
    <section className="hero" id="top">
      <p className="eyebrow">
        <span className="pulse" aria-hidden="true" />
        {meta.counts.entries} words · {meta.counts.concepts} concepts · {meta.registers.length}{" "}
        registers
      </p>
      <h1 className="hero__title">
        <span className="hero__line">Insult</span>
        <span className="hero__line">Generator</span>
        <span className="hero__line hero__line--accent">5000</span>
      </h1>
      <p className="hero__lede">
        Grammar-aware, register-tuned and severity-calibrated. Every sentence is{" "}
        <em>built</em>, never shuffled.
      </p>
      <div className="hero__cta">
        <a className="btn btn--primary" href="#forge">
          Start forging <Icon name="arrow" size={18} />
        </a>
        <a className="btn btn--ghost" href="#lexicon">
          Browse the lexicon
        </a>
      </div>
      <div className="hero__stack" aria-hidden="true">
        {SPECIMENS.map((card) => (
          <div
            key={card.register}
            className={`specimen specimen--${card.register}`}
            style={{ "--x": card.x, "--y": card.y, "--r": card.r, "--d": card.d }}
          >
            <span className="specimen__label">{card.label}</span>
            <p>{card.text}</p>
          </div>
        ))}
      </div>
      <div className="ticker" aria-hidden="true">
        <div className="ticker__track">
          {[0, 1].map((copy) =>
            words.map((entry) => (
              <span
                key={`${copy}-${entry.term}-${entry.part_of_speech}`}
                className={`ticker__word ticker__word--${primaryRegister(entry)}`}
              >
                {entry.term}
              </span>
            )),
          )}
        </div>
      </div>
    </section>
  );
}
