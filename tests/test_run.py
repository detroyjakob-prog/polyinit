import shutil
import sys
from pathlib import Path

import pytest

from polyinit.commands.run import (
    LANGUAGE_MANAGERS,
    _read_pyproject,
    detect_language,
)
from polyinit.system import create_virtualenv, interpreter_for_venv


class TestVenvInterpreter:
    def test_uses_sys_executable_when_not_frozen(self):
        assert interpreter_for_venv() == sys.executable

    def test_frozen_build_never_returns_the_binary(self, monkeypatch):
        """A frozen sys.executable is polyinit, not a Python interpreter."""
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "executable", "/usr/local/bin/polyinit")
        monkeypatch.setattr(shutil, "which", lambda name: None)

        assert interpreter_for_venv() is None

    def test_frozen_build_falls_back_to_path(self, monkeypatch):
        monkeypatch.setattr(sys, "frozen", True, raising=False)
        monkeypatch.setattr(sys, "executable", "/usr/local/bin/polyinit")
        monkeypatch.setattr(
            shutil, "which", lambda name: f"/usr/bin/{name}"
        )

        assert interpreter_for_venv() == "/usr/bin/python3"

    def test_create_virtualenv_reports_failure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "polyinit.system.interpreter_for_venv", lambda: None
        )

        assert create_virtualenv(tmp_path) is False
        assert not (tmp_path / ".venv").exists()

    def test_create_virtualenv_uses_the_interpreter(
        self, tmp_path, monkeypatch
    ):
        seen: list[list[str]] = []

        monkeypatch.setattr(
            "polyinit.system.run",
            lambda command, cwd: seen.append(command),
        )

        assert create_virtualenv(tmp_path) is True
        assert seen == [[sys.executable, "-m", "venv", ".venv"]]


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