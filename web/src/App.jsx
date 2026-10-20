import { useCallback, useEffect, useMemo, useState } from "react";
import { getMeta, getVocabulary } from "./api.js";
import EntryDialog from "./components/EntryDialog.jsx";
import Footer from "./components/Footer.jsx";
import Forge from "./components/Forge.jsx";
import Header from "./components/Header.jsx";
import Hero from "./components/Hero.jsx";
import HowItWorks from "./components/HowItWorks.jsx";
import Lexicon from "./components/Lexicon.jsx";
import { ToastProvider } from "./components/Toast.jsx";
import WordMap from "./components/WordMap.jsx";
import { useTheme } from "./hooks.js";

function useBootstrap() {
  const [state, setState] = useState({ status: "loading" });
  const load = useCallback(() => {
    setState({ status: "loading" });
    Promise.all([getMeta(), getVocabulary()])
      .then(([meta, vocabulary]) => setState({ status: "ready", meta, vocabulary }))
      .catch((error) => setState({ status: "error", message: error.message }));
  }, []);
  useEffect(load, [load]);
  return [state, load];
}

function Splash({ message, onRetry }) {
  return (
    <div className="splash" role={onRetry ? "alert" : "status"}>
      <div className="splash__mark" aria-hidden="true" />
      <p>{message}</p>
      {onRetry ? (
        <button type="button" className="btn btn--primary" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}

export default function App() {
  const [theme, toggleTheme] = useTheme();
  const [boot, reload] = useBootstrap();
  const [dialogEntry, setDialogEntry] = useState(null);
  const [aim, setAim] = useState(null);

  const vocabulary = boot.status === "ready" ? boot.vocabulary : null;
  const conceptsById = useMemo(
    () => (vocabulary ? Object.fromEntries(vocabulary.concepts.map((c) => [c.id, c])) : {}),
    [vocabulary],
  );

  if (boot.status === "loading") return <Splash message="Sharpening the vocabulary…" />;
  if (boot.status === "error") return <Splash message={boot.message} onRetry={reload} />;

  const { meta } = boot;
  return (
    <ToastProvider>
      <Header theme={theme} onToggleTheme={toggleTheme} />
      <main>
        <Hero meta={meta} entries={vocabulary.entries} />
        <Forge
          meta={meta}
          concepts={vocabulary.concepts}
          conceptsById={conceptsById}
          onOpenEntry={setDialogEntry}
          aim={aim}
        />
        <Lexicon
          entries={vocabulary.entries}
          concepts={vocabulary.concepts}
          conceptsById={conceptsById}
          onOpenEntry={setDialogEntry}
        />
        <WordMap entries={vocabulary.entries} onOpenEntry={setDialogEntry} />
        <HowItWorks meta={meta} />
      </main>
      <Footer meta={meta} />
      <EntryDialog
        entry={dialogEntry}
        conceptsById={conceptsById}
        onClose={() => setDialogEntry(null)}
        onAim={(concept) => setAim({ concept, nonce: Date.now() })}
      />
    </ToastProvider>
  );
}
