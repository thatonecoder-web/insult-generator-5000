# Roadmap

Versions follow semantic versioning. Everything before 1.0 may change.

## 0.1.0 (initial development release)

Repository skeleton, typed models, curated vocabulary, validation, tests, CI.

Since then (unreleased): the template-based generator, grammar annotations, the CLI `generate`
command, the JSON API, the React web interface and the `serve` command.

## Next: generator quality

- More frames per register, and frames that use verbs ("You prevaricate, dissemble and call it
  honesty."). Verbs need a transitivity annotation first.
- Use `thing` nouns and adverbs.
- Reduce repetition: remember recent words within a session, and penalize reuse.
- Plural and countability handling, so more frame shapes are safe.

## Next: dataset quality

- Expert review of flagged entries, and a dictionary check of every definition.
- Fill the thin spots: vulgar, legal, academic and archaic cover only 22 to 38 of the 63 concepts.
- A sensitivity review of the register labels.

## Next: web interface

- Batch generation ("give me ten").
- Export and import of the Hall of Fame.
- A static build that runs the generator in the browser (a port or WebAssembly), so the site can
  be hosted without a server.
- Automated visual regression tests.

## Later

- A stable 1.0 interface and a licence decision before any public release.
