import { useEffect, useState } from "react";
import Icon from "./Icon.jsx";

const LINKS = [
  ["forge", "Forge"],
  ["lexicon", "Lexicon"],
  ["map", "The Map"],
  ["how", "How it works"],
];

export default function Header({ theme, onToggleTheme }) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header className={`header${scrolled ? " header--scrolled" : ""}`}>
      <a className="brand" href="#top" aria-label="Insult Generator 5000, back to top">
        <span className="brand__mark">
          <Icon name="flame" size={18} />
        </span>
        <span className="brand__name">
          Insult Generator <b>5000</b>
        </span>
      </a>
      <nav className="header__nav" aria-label="Sections">
        {LINKS.map(([id, label]) => (
          <a key={id} href={`#${id}`}>
            {label}
          </a>
        ))}
      </nav>
      <button
        className="icon-button"
        type="button"
        onClick={onToggleTheme}
        aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      >
        <Icon name={theme === "dark" ? "sun" : "moon"} size={18} />
      </button>
    </header>
  );
}
