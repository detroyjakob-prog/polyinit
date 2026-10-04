from pathlib import Path

import pytest

from pinit.commands.run import (
    LANGUAGE_MANAGERS,
    _read_pyproject,
    detect_language,
)


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("pyproject.toml", "python"),
        ("setup.py", "python"),
        ("Cargo.toml", "rust"),
        ("go.mod", "go"),
        ("tsconfig.json", "typescript"),
        ("package.json", "javascript"),
        ("index.md", "markdown"),
    ],
)
def test_detects_language(tmp_path: Path, filename: str, expected: str):
    (tmp_path / filename).write_text("")
    assert detect_language(tmp_path) == expected


def test_detects_typescript_over_javascript(tmp_path: Path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "tsconfig.json").write_text("{}")
    assert detect_language(tmp_path) == "typescript"


def test_returns_none_for_empty_directory(tmp_path: Path):
    assert detect_language(tmp_path) is None


def test_every_language_has_managers():
    for language in LANGUAGE_MANAGERS:
        assert LANGUAGE_MANAGERS[language]


def test_read_pyproject_handles_missing_file(tmp_path: Path):
    assert _read_pyproject(tmp_path) == {}


def test_read_pyproject_handles_invalid_toml(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("not [ valid")
    assert _read_pyproject(tmp_path) == {}


def test_read_pyproject_parses_entry_points(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "demo"\n\n'
        '[project.scripts]\ndemo = "demo.main:main"\n'
    )

    data = _read_pyproject(tmp_path)

    assert data["project"]["scripts"]["demo"] == "demo.main:main"