# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## Conventions

Add every change under `[Unreleased]` while developing, in one of these groups:

- **Added**: new features
- **Changed**: changes to existing behaviour
- **Deprecated**: features that will be removed
- **Removed**: features removed in this release
- **Fixed**: bug fixes
- **Security**: vulnerability fixes

On release, rename `[Unreleased]` to the version and date, and add a fresh empty `[Unreleased]`.
Version 0.1.0 is an initial development release; it is not feature-complete.

## [Unreleased]

### Added

- Initial repository structure
- Core package architecture
- Vocabulary data schema
- Dataset validation infrastructure
- Initial testing infrastructure
- CLI skeleton
- Development tooling
- Documentation
- Template-based insult generator: typed sentence frames (58, organized by register), article
  agreement, seeded and reproducible, with severity and concept steering
- Grammar annotations in the dataset: `noun_class`, `targets` and `attributive_only`
- `insultgen generate` (with `--count` and `--seed`) and `insultgen serve`
- JSON API (`/api/generate`, `/api/vocabulary`, `/api/meta`, `/api/health`) on a standard-library
  HTTP server, with a framework-independent service layer
- React web interface in `web/`: register-themed result stage, lexicon explorer, vocabulary
  map, shareable links, light and dark themes
- Front-end unit tests and an optional end-to-end browser test
