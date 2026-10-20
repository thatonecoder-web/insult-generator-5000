import json
from pathlib import Path
from typing import Any

import pytest

from insultgen import __version__
from insultgen.cli import EXIT_FAILURE, EXIT_OK, main


def test_validate_data_accepts_the_bundled_dataset(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["validate-data"]) == EXIT_OK
    assert capsys.readouterr().out.startswith("OK:")


def test_validate_data_reports_problems(
    tmp_path: Path, minimal_raw: dict[str, Any], capsys: pytest.CaptureFixture[str]
) -> None:
    minimal_raw["entries"][0]["severity"] = 11
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(minimal_raw), encoding="utf-8")
    assert main(["validate-data", "--path", str(path)]) == EXIT_FAILURE
    assert "1 validation issue(s) found." in capsys.readouterr().err


def test_validate_data_handles_missing_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main(["validate-data", "--path", str(tmp_path / "nope.json")]) == EXIT_FAILURE
    assert "Could not read dataset" in capsys.readouterr().err


def test_validate_data_handles_invalid_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    assert main(["validate-data", "--path", str(path)]) == EXIT_FAILURE
    assert "Could not read dataset" in capsys.readouterr().err


def test_generate_prints_an_insult(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["generate", "--register", "legal", "--severity", "6", "--seed", "3"]) == EXIT_OK
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 1
    assert out[0][-1] in ".!?"


def test_generate_is_reproducible_with_a_seed(capsys: pytest.CaptureFixture[str]) -> None:
    main(["generate", "--seed", "11", "--count", "4"])
    first = capsys.readouterr().out
    main(["generate", "--seed", "11", "--count", "4"])
    assert capsys.readouterr().out == first
    assert len(first.strip().splitlines()) == 4


def test_generate_reports_unknown_concepts(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["generate", "--concept", "nope"]) == EXIT_FAILURE
    assert "unknown concept" in capsys.readouterr().err


@pytest.mark.parametrize("count", ["0", "51", "many"])
def test_generate_rejects_invalid_counts(count: str) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["generate", "--count", count])
    assert excinfo.value.code == 2


@pytest.mark.parametrize("severity", ["0", "11", "high"])
def test_generate_rejects_invalid_severity(severity: str) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["generate", "--severity", severity])
    assert excinfo.value.code == 2


def test_generate_rejects_invalid_register() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["generate", "--register", "pirate"])
    assert excinfo.value.code == 2


def test_a_command_is_required() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out
