import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { generate } from "../api.js";
import { useLocalStorage, useReveal } from "../hooks.js";
import { decodeState, shareUrl } from "../lib/format.js";
import Archive from "./Archive.jsx";
import ConceptSelect from "./ConceptSelect.jsx";
import RegisterPicker from "./RegisterPicker.jsx";
import SeverityDial from "./SeverityDial.jsx";
import Stage from "./Stage.jsx";
import { useToast } from "./Toast.jsx";

const HISTORY_LIMIT = 12;
const AUTO_DELAY_MS = 220;

const itemKey = (item) => `${item.seed}-${item.text}`;

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement("textarea");
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand("copy");
    document.body.removeChild(area);
    return ok;
  }
}

export default function Forge({ meta, concepts, conceptsById, onOpenEntry, aim }) {
  const toast = useToast();
  const sectionRef = useReveal();

  const [register, setRegister] = useState(null);
  const [severity, setSeverity] = useState(5);
  const [concept, setConcept] = useState("");
  const [seedText, setSeedText] = useState("");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [history, setHistory] = useLocalStorage("ig5k.history", []);
  const [saved, setSaved] = useLocalStorage("ig5k.saved", []);

  const controller = useRef(null);
  const ready = useRef(false);

  const available = useMemo(() => {
    if (register) {
      return new Set(meta.registers.find((r) => r.id === register)?.concepts ?? []);
    }
    const union = new Set();
    for (const r of meta.registers) {
      if (r.id !== "vulgar") r.concepts.forEach((id) => union.add(id));
    }
    return union;
  }, [meta, register]);

  const entriesByRegister = useMemo(
    () => Object.fromEntries(meta.registers.map((r) => [r.id, r.entries])),
    [meta],
  );

  const run = useCallback(
    async (settings) => {
      controller.current?.abort();
      const current = new AbortController();
      controller.current = current;
      setStatus("loading");
      try {
        const data = await generate(settings, current.signal);
        const item = data.results[0];
        setResult(item);
        setError("");
        setStatus("ready");
        setHistory((previous) =>
          [item, ...previous.filter((entry) => itemKey(entry) !== itemKey(item))].slice(
            0,
            HISTORY_LIMIT,
          ),
        );
      } catch (failure) {
        if (failure.name === "AbortError") return;
        setError(failure.message);
        setStatus("error");
      }
    },
    [setHistory],
  );

  const currentSettings = useCallback(
    (overrides = {}) => ({
      register,
      severity,
      concept: concept || null,
      seed: seedText.trim() === "" ? null : Number(seedText),
      ...overrides,
    }),
    [register, severity, concept, seedText],
  );

  // First load: honour a shared link, otherwise forge something straight away.
  useEffect(() => {
    const shared = decodeState(window.location.hash);
    const hasShared = Object.values(shared).some((value) => value !== null);
    if (hasShared) {
      setRegister(shared.register);
      setSeverity(shared.severity ?? 5);
      setConcept(shared.concept ?? "");
      setSeedText(shared.seed === null ? "" : String(shared.seed));
      run({ ...shared, severity: shared.severity ?? 5 });
      document.getElementById("forge")?.scrollIntoView();
    } else {
      run({ register: null, severity: 5, concept: null, seed: null });
    }
    const timer = window.setTimeout(() => {
      ready.current = true;
    }, 0);
    return () => window.clearTimeout(timer);
  }, [run]);

  // Regenerate shortly after any control changes, so the stage always matches the dials.
  useEffect(() => {
    if (!ready.current) return undefined;
    const timer = window.setTimeout(() => run(currentSettings()), AUTO_DELAY_MS);
    return () => window.clearTimeout(timer);
    // Only the controls should trigger this, not the identity of the callbacks.
  }, [register, severity, concept, seedText]);

  // "Aim the forge at this concept" from the lexicon dialog.
  useEffect(() => {
    if (!aim) return;
    if (register && !meta.registers.find((r) => r.id === register)?.concepts.includes(aim.concept)) {
      setRegister(null);
    }
    setConcept(aim.concept);
    document.getElementById("forge")?.scrollIntoView({ behavior: "smooth" });
  }, [aim]);

  const forgeAgain = useCallback(() => {
    run(currentSettings({ seed: seedText.trim() === "" ? null : Number(seedText) }));
  }, [run, currentSettings, seedText]);

  useEffect(() => {
    const onKey = (event) => {
      if (event.code === "Space" && event.target === document.body) {
        event.preventDefault();
        forgeAgain();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [forgeAgain]);

  const chooseRegister = (next) => {
    setRegister(next);
    if (concept) {
      const pool = next
        ? meta.registers.find((r) => r.id === next)?.concepts ?? []
        : meta.registers.flatMap((r) => r.concepts);
      if (!pool.includes(concept)) setConcept("");
    }
  };

  const isSaved = result ? saved.some((item) => itemKey(item) === itemKey(result)) : false;

  const restore = (item) => {
    setResult(item);
    setStatus("ready");
    setError("");
    document.getElementById("forge")?.scrollIntoView({ behavior: "smooth" });
  };

  const onCopy = async () => {
    if (result && (await copyText(result.text))) toast("Copied to clipboard");
  };

  const onShare = async () => {
    if (!result) return;
    const link = shareUrl(window.location, {
      register: result.requested.register,
      severity: result.requested.severity,
      concept: result.requested.concept,
      seed: result.seed,
    });
    if (await copyText(link)) toast("Link copied. It recreates this exact insult.");
  };

  const onToggleSave = () => {
    if (!result) return;
    setSaved((previous) =>
      isSaved
        ? previous.filter((item) => itemKey(item) !== itemKey(result))
        : [result, ...previous],
    );
    toast(isSaved ? "Removed from the Hall of Fame" : "Saved to the Hall of Fame");
  };

  return (
    <section className="section forge reveal" id="forge" ref={sectionRef}>
      <header className="section__head">
        <p className="eyebrow">01 · The Forge</p>
        <h2>Choose your weapon.</h2>
        <p className="section__lede">
          Pick a voice, set how hard it lands, and aim it. The sentence is rebuilt as you turn the
          dials.
        </p>
      </header>

      <div className="forge__grid">
        <div className="panel controls">
          <RegisterPicker
            value={register}
            onChange={chooseRegister}
            entriesByRegister={entriesByRegister}
          />
          <SeverityDial value={severity} onChange={setSeverity} />
          <ConceptSelect
            value={concept}
            onChange={setConcept}
            concepts={concepts}
            available={available}
          />
          <details className="advanced">
            <summary>Advanced</summary>
            <div className="field">
              <label className="field__label" htmlFor="seed">
                Seed
              </label>
              <input
                id="seed"
                className="input"
                inputMode="numeric"
                pattern="[0-9]*"
                placeholder="Random every time"
                value={seedText}
                onChange={(event) => setSeedText(event.target.value.replace(/\D/g, "").slice(0, 10))}
              />
              <p className="field__hint">
                The same settings and seed always give the same insult. Leave empty for variety.
              </p>
            </div>
          </details>
        </div>

        <div className="forge__stage">
          <Stage
            result={result}
            status={status}
            error={error}
            isSaved={isSaved}
            conceptsById={conceptsById}
            onAgain={forgeAgain}
            onCopy={onCopy}
            onShare={onShare}
            onToggleSave={onToggleSave}
            onOpenEntry={onOpenEntry}
            onClearConcept={concept ? () => setConcept("") : null}
          />
          <Archive
            history={history}
            saved={saved}
            onRestore={restore}
            onRemoveSaved={(item) =>
              setSaved((previous) => previous.filter((entry) => itemKey(entry) !== itemKey(item)))
            }
          />
        </div>
      </div>
    </section>
  );
}
