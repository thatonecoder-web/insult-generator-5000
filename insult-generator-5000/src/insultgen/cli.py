"""Command-line interface. ``generate`` is a placeholder until the engine exists."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from insultgen import __version__
from insultgen.loader import load_raw
from insultgen.models import SEVERITY_MAX, SEVERITY_MIN, GenerationParameters, Register
from insultgen.validation import validate_dataset

EXIT_OK = 0
EXIT_FAILURE = 1
EXIT_NOT_IMPLEMENTED = 3


def _severity(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"severity must be an integer, got {value!r}") from None
    if not SEVERITY_MIN <= number <= SEVERITY_MAX:
        raise argparse.ArgumentTypeError(
            f"severity must be between {SEVERITY_MIN} and {SEVERITY_MAX}, got {number}"
        )
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="insultgen", description="Algorithmic English insult generator."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    generate = commands.add_parser("generate", help="generate an insult (not implemented yet)")
    generate.add_argument("--register", choices=[r.value for r in Register])
    generate.add_argument("--severity", type=_severity, metavar=f"{SEVERITY_MIN}-{SEVERITY_MAX}")
    generate.add_argument("--concept", help="semantic concept id, e.g. 'stupidity'")
    generate.add_argument("--seed", type=int, help="seed for reproducible output")
    generate.set_defaults(handler=_run_generate)

    validate = commands.add_parser("validate-data", help="validate the vocabulary dataset")
    validate.add_argument("--path", type=Path, help="dataset to check (default: bundled dataset)")
    validate.set_defaults(handler=_run_validate)

    return parser


def _run_generate(args: argparse.Namespace) -> int:
    parameters = GenerationParameters(
        register=Register(args.register) if args.register else None,
        severity=args.severity,
        concept=args.concept,
        seed=args.seed,
    )
    print("insultgen generate: not implemented yet (see docs/roadmap.md).", file=sys.stderr)
    print(f"Parsed parameters: {parameters}", file=sys.stderr)
    return EXIT_NOT_IMPLEMENTED


def _run_validate(args: argparse.Namespace) -> int:
    try:
        raw = load_raw(args.path)
    except (OSError, ValueError) as error:
        print(f"Could not read dataset: {error}", file=sys.stderr)
        return EXIT_FAILURE

    issues = validate_dataset(raw)
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        print(f"{len(issues)} validation issue(s) found.", file=sys.stderr)
        return EXIT_FAILURE

    assert isinstance(raw, dict)
    print(f"OK: {len(raw['entries'])} entries, {len(raw['concepts'])} concepts.")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.handler(args))
