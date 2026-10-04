"""Run a generated project.

The runner is derived from what is actually on disk (entry points in
``pyproject.toml``, ``Cargo.toml``, ``go.mod``, ``package.json``) rather than
from a hardcoded guess, so it stays correct as templates change.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console

console = Console()

# Language -> package managers offered for it.
LANGUAGE_MANAGERS: dict[str, list[str]] = {
    "python": ["venv", "uv", "pip"],
    "javascript": ["npm", "yarn", "pnpm", "node"],
    "typescript": ["npm", "yarn", "pnpm", "bun"],
    "rust": ["cargo"],
    "go": ["go"],
    "markdown": ["default"],
}

# Files that identify a project, checked in order of specificity.
LANGUAGE_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("python", ("pyproject.toml", "setup.py", "setup.cfg")),
    ("rust", ("Cargo.toml",)),
    ("go", ("go.mod",)),
    ("typescript", ("tsconfig.json",)),
    ("javascript", ("package.json",)),
    ("markdown", ("index.md",)),
)


def detect_language(project_path: Path) -> str | None:
    """Best-effort detection of the project's language."""
    for language, markers in LANGUAGE_MARKERS:
        if any((project_path / marker).exists() for marker in markers):
            return language

    return None


def _read_pyproject(project_path: Path) -> dict:
    import tomllib

    pyproject = project_path / "pyproject.toml"
    if not pyproject.exists():
        return {}

    try:
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _python_command(
    project_path: Path,
    manager: str,
) -> tuple[list[str], dict[str, str]]:
    """Return the interpreter prefix and environment for a Python project."""
    env = {**os.environ}
    src = project_path / "src"
    if src.is_dir():
        existing = env.get("PYTHONPATH")
        env["PYTHONPATH"] = (
            f"{src}{os.pathsep}{existing}" if existing else str(src)
        )

    if manager == "uv":
        return ["uv", "run", "python"], env

    if manager == "venv":
        venv_python = project_path / ".venv" / "bin" / "python"
        if venv_python.exists():
            return [str(venv_python)], env
        console.print(
            "[yellow]No .venv found, falling back to the current "
            "interpreter.[/yellow]"
        )

    return [sys.executable], env


def _run_python(project_path: Path, manager: str) -> int:
    data = _read_pyproject(project_path)
    project = data.get("project", {})

    interpreter, env = _python_command(project_path, manager)

    scripts = project.get("scripts") or {}
    if scripts:
        target = next(iter(scripts.values()))
        module = str(target).split(":")[0]
        command = [*interpreter, "-m", module]
        return _execute(command, project_path, env)

    dependencies = " ".join(project.get("dependencies") or [])
    if "fastapi" in dependencies:
        package = str(project.get("name", project_path.name)).replace("-", "_")
        command = [
            *interpreter,
            "-m",
            "uvicorn",
            f"{package}.main:app",
            "--reload",
        ]
        return _execute(command, project_path, env)

    console.print(
        "[yellow]This is a library, so it has no entry point to run.[/yellow]\n"
        f"Run its tests instead: [cyan]{interpreter[0]} -m pytest[/cyan]"
    )
    return 1


def _package_json(project_path: Path) -> dict:
    manifest = project_path / "package.json"
    if not manifest.exists():
        return {}

    try:
        return json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _run_node(project_path: Path, manager: str, language: str) -> int:
    if language == "typescript" and manager == "bun":
        return _execute(["bun", "run", "src/index.ts"], project_path)

    if language == "typescript":
        build = ["tsc"]
        if manager in {"npm", "yarn", "pnpm"}:
            run_build = [manager, "run", "build"]
        else:
            run_build = build

        code = _execute(run_build, project_path)
        if code != 0:
            return code

    if manager == "node":
        return _execute(["node", "src/index.js"], project_path)

    if manager == "bun":
        return _execute(["bun", "run", "src/index.ts"], project_path)

    return _execute([manager, "start"], project_path)


def _execute(
    command: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
) -> int:
    console.print(f"[cyan]Running:[/cyan] {' '.join(command)}")
    try:
        return subprocess.run(command, cwd=cwd, env=env).returncode
    except FileNotFoundError:
        console.print(
            f"[bold red]✗ Command not found:[/bold red] {command[0]}"
        )
        return 127


def run_command(
    language: str | None = typer.Argument(
        None, help="Project language. Detected automatically when omitted."
    ),
    package_manager: str | None = typer.Argument(
        None, help="Package manager or runner to use."
    ),
) -> None:
    """Run the project in the current directory."""
    project_path = Path.cwd()

    if language is None:
        language = detect_language(project_path)

    if language is None:
        console.print(
            "[bold red]✗ Could not detect the project type.[/bold red]\n"
            "Pass a language explicitly: "
            "[cyan]pinit run python[/cyan]"
        )
        raise typer.Exit(code=1)

    language = language.lower()

    if language not in LANGUAGE_MANAGERS:
        supported = ", ".join(sorted(LANGUAGE_MANAGERS))
        console.print(
            f"[bold red]✗ Unknown language:[/bold red] {language}\n"
            f"Supported: {supported}"
        )
        raise typer.Exit(code=1)

    if package_manager is None:
        if language == "markdown":
            package_manager = "default"
        else:
            import questionary

            package_manager = questionary.select(
                "Which package manager/runner?",
                choices=LANGUAGE_MANAGERS[language],
            ).ask()

        if package_manager is None:
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit()

    package_manager = package_manager.lower()

    if language == "python":
        code = _run_python(project_path, package_manager)
    elif language in {"javascript", "typescript"}:
        code = _run_node(project_path, package_manager, language)
    elif language == "rust":
        code = _execute(["cargo", "run"], project_path)
    elif language == "go":
        code = _execute(["go", "run", "."], project_path)
    else:
        console.print(
            f"[green]Open[/green] {project_path / 'README.md'} "
            "in a markdown viewer."
        )
        return

    raise typer.Exit(code=code)