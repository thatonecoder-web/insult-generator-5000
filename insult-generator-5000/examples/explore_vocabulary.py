"""Load the bundled vocabulary and list candidate entries for a few parameter sets."""

from __future__ import annotations

from insultgen.generation import InsultGenerator
from insultgen.loader import load_vocabulary
from insultgen.models import GenerationParameters, Register

MAX_SHOWN = 10


def main() -> None:
    generator = InsultGenerator(load_vocabulary())
    for register, severity in [(Register.ACADEMIC, 5), (Register.ARCHAIC, 6), (Register.LEGAL, 6)]:
        params = GenerationParameters(register=register, severity=severity, concept="deception")
        terms = [entry.term for entry in generator.candidates(params)]
        print(f"{register.value} / severity {severity} / deception: {terms[:MAX_SHOWN]}")


if __name__ == "__main__":
    main()
