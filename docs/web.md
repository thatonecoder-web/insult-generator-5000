# Web interface and API

## Running it

```bash
cd web && npm install && npm run build && cd ..
insultgen serve --port 8000
```

`insultgen serve` serves the built interface from `web/dist` (override with `--web-dir` or the
`INSULTGEN_WEB_DIR` environment variable) and the JSON API under `/api/`. It binds to
`127.0.0.1` by default. Standard library only; no Flask or FastAPI.

For development, `npm run watch` rebuilds on every change. Reload the page after a rebuild.
React 19 and esbuild are the only front-end dependencies.

## What is in the interface

- **Forge**: register tiles, a severity dial, a concept picker, an optional seed. The result
  regenerates as you change a control. Each register has its own visual world for the result: a
  chat bubble (casual), letterpress (formal), parchment (archaic), a lined notebook (academic),
  pleading paper (legal) and a loud sticker (vulgar). Every vocabulary word is clickable.
  Copy, share (a link that recreates the exact insult), save to the Hall of Fame, and an
  "Anatomy" panel showing the parameters, frame and words behind the sentence.
- **Lexicon**: search, filter by register, part of speech, concept and severity, sort, and open
  any entry. "Aim the forge" jumps back to the forge with that concept selected.
- **The Map**: every word plotted by any two of formality, severity, archaicness and vulgarity.
- **How it works**: the pipeline, the grammar guardrails and the dataset statistics.

Light and dark themes (following the system, remembered once toggled), keyboard operable
(Space forges another insult), screen-reader friendly, and `prefers-reduced-motion` is honoured.
History and saved insults live in `localStorage`; nothing is sent anywhere but the local API.

## API

All bodies are JSON. Errors have the form `{"error": "message"}`.

| Method and path | Purpose |
| --- | --- |
| `GET /api/health` | `{"status": "ok", "version": "..."}` |
| `GET /api/meta` | counts, per-register entry counts, and which concepts each register can build |
| `GET /api/vocabulary` | every concept and entry (gzip-compressed when the client accepts it) |
| `POST /api/generate` | generate insults |

`POST /api/generate` accepts any of `register` (one of the six), `severity` (1-10), `concept`
(a concept id), `seed` (0 to 2147483647) and `count` (1-50, default 1). All are optional.

```bash
curl -s localhost:8000/api/generate -H 'Content-Type: application/json' \
  -d '{"register": "formal", "severity": 6, "seed": 7}'
```

Each result has `text`, the resolved `register`, `concept` and `seed`, the `template_id` and
`template_text`, the `requested` parameters, `parts` (the sentence split into literal text and
vocabulary words) and `entries` (the full vocabulary entries used; `parts[].entry` indexes into
it). Status codes: `400` invalid request, `404` unknown path, `413` body over 4 KB, `415`
wrong content type, `422` no insult can be built for those settings.

## Front-end layout

```
web/
  build.mjs          esbuild build (npm run build / npm run watch)
  index.html         HTML shell
  public/            fonts, favicon, theme bootstrap script
  src/
    main.jsx App.jsx api.js hooks.js
    components/      Forge, Stage, Lexicon, WordMap, EntryDialog, ...
    lib/             pure logic: filters, URL state, sentence grouping (unit tested)
    styles/          tokens, base, layout, forge, stage, explore
  test/              node:test unit tests (npm test)
  e2e/journeys.mjs   optional Playwright check of the main journeys
```

## Design notes

- **Tokens first.** Colours, type and radii are CSS variables in `styles/tokens.css`. Each
  register has one hue; any class named like `thing--legal` picks it up as `--reg`.
- **Type.** Lora for display and result text, Poppins for the interface, DejaVu Sans Mono for
  labels. They are bundled as Latin subsets, so there are no third-party requests and the
  server's Content-Security-Policy can be strict (`default-src 'self'`).
- **Sentence display.** The API returns the sentence as parts. The interface attaches trailing
  punctuation to its word so a line can never break before a semicolon or full stop, and keeps
  hover tooltips out of the live region so screen readers hear the sentence, not the glosses.

## Deployment

The built-in server is a convenience for local use. It has no authentication, rate limiting or
TLS. To publish the site, serve `web/dist` from a static host or web server and run the API
behind a production server; `service.py` contains the framework-independent logic to wrap.
