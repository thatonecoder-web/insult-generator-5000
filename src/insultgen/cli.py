"""Command-line interface."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from insultgen import __version__
from insultgen.generation import GenerationError, InsultGenerator
from insultgen.generation.engine import MAX_BATCH
from insultgen.loader import load_raw, load_vocabulary
from insultgen.models import SEVERITY_MAX, SEVERITY_MIN, GenerationParameters, Register
from insultgen.server import make_server
from insultgen.service import InsultService
from insultgen.validation import validate_dataset

EXIT_OK = 0
EXIT_FAILURE = 1


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


def _count(value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"count must be an integer, got {value!r}") from None
    if not 1 <= number <= MAX_BATCH:
        raise argparse.ArgumentTypeError(f"count must be between 1 and {MAX_BATCH}, got {number}")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="insultgen", description="Algorithmic English insult generator."
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="COMMAND")

    generate = commands.add_parser("generate", help="generate one or more insults")
    generate.add_argument("--register", choices=[r.value for r in Register])
    generate.add_argument("--severity", type=_severity, metavar=f"{SEVERITY_MIN}-{SEVERITY_MAX}")
    generate.add_argument("--concept", help="semantic concept id, e.g. 'stupidity'")
    generate.add_argument("--seed", type=int, help="seed for reproducible output")
    generate.add_argument("--count", type=_count, default=1, help=f"how many (1-{MAX_BATCH})")
    generate.set_defaults(handler=_run_generate)

    serve = commands.add_parser("serve", help="serve the web interface and JSON API")
    serve.add_argument("--host", default="127.0.0.1", help="interface to bind (default: local)")
    serve.add_argument("--port", type=int, default=8000, help="port to listen on")
    serve.add_argument("--web-dir", type=Path, help="built web interface (default: web/dist)")
    serve.set_defaults(handler=_run_serve)

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
    generator = InsultGenerator(load_vocabulary())
    try:
        results = generator.generate_batch(parameters, args.count)
    except GenerationError as error:
        print(f"insultgen: {error}", file=sys.stderr)
        return EXIT_FAILURE
    for result in results:
        print(result.text)
    return EXIT_OK


def _run_serve(args: argparse.Namespace) -> int:
    web_dir = args.web_dir or Path(os.environ.get("INSULTGEN_WEB_DIR", "web/dist"))
    service = InsultService()
    service.meta()  # computed once here so the first page load is instant
    try:
        server = make_server(args.host, args.port, service, web_dir)
    except OSError as error:
        print(f"insultgen: cannot listen on {args.host}:{args.port}: {error}", file=sys.stderr)
        return EXIT_FAILURE

    host, port = server.server_address[:2]
    print(f"Serving on http://{host}:{port}  (Ctrl+C to stop)")
    if not (web_dir / "index.html").is_file():
        print(
            f"Note: no built web interface found at {web_dir}; only the API is available.\n"
            "Build it with: cd web && npm install && npm run build",
            file=sys.stderr,
        )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()
    return EXIT_OK


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
