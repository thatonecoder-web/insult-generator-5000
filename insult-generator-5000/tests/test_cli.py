import json
from pathlib import Path
from typing import Any

import pytest

from insultgen import __version__
from insultgen.cli import EXIT_FAILURE, EXIT_NOT_IMPLEMENTED, EXIT_OK, main


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


def test_generate_is_a_clearly_marked_placeholder(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["generate"]) == EXIT_NOT_IMPLEMENTED
    assert "not implemented yet" in capsys.readouterr().err


def test_generate_parses_options(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["generate", "--register", "legal", "--severity", "6", "--seed", "3"])
    err = capsys.readouterr().err
    assert code == EXIT_NOT_IMPLEMENTED
    assert "Register.LEGAL" in err
    assert "severity=6" in err
    assert "seed=3" in err


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
