# Security policy

## Supported versions

This project is in initial development (0.x). Only the latest release on `main` receives fixes.

## Scope

insultgen is a local library and command-line tool. It makes no network requests, runs no
subprocesses, and uses no `eval` or `pickle`. Realistic concerns include:

- Handling of untrusted vocabulary files (`insultgen validate-data --path ...`).
- Dependency or packaging problems.

## Reporting a vulnerability

Please do not open a public issue for security problems.

Use GitHub's private vulnerability reporting ("Security" tab, then "Report a vulnerability") once
it is enabled for the repository. If that is unavailable, contact the maintainers at
[CONTACT METHOD TO BE ADDED BEFORE PUBLIC RELEASE].

Include the version, steps to reproduce, and the impact you expect. We aim to acknowledge
reports within a week and to share a fix timeline after triage.

## Content concerns

Offensive or inappropriate dataset entries are not security issues. Report them as a normal
issue using the vocabulary proposal template.
