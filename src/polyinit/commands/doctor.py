"""Environment checks for polyinit and the tools its templates rely on."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

console = Console()

# Tools polyinit itself shells out to.
BASE_TOOLS: tuple[str, ...] = ("git",)

# Tools the generated projects need, grouped by language.
LANGUAGE_TOOLS: dict[str, tuple[str, ...]] = {
    "python": ("python", "pip", "pytest", "ruff", "uv"),
    "javascript": ("node", "npm"),
    "typescript": ("node", "npm", "tsc"),
    "rust": ("cargo", "rustc"),
    "go": ("go",),
}

OPTIONAL_TOOLS: dict[str, tuple[str, ...]] = {
    "javascript": ("yarn", "pnpm"),
    "typescript": ("bun",),
}


def _python_version() -> str:
    return ".".join(str(part) for part in sys.version_info[:3])


def _tool_row(name: str) -> tuple[str, str, str]:
    path = shutil.which(name)
    return name, "✓" if path else "✗", path or "Not found in PATH"


def _check_sources(package_root: Path) -> list[tuple[str, str]]:
    """Compile every shipped module without writing bytecode to disk.

    Returns a list of ``(module, error)`` pairs, empty when all modules are
    valid.
    """
    for pyfile in sorted(package_root.rglob("*.py")):
        relative = pyfile.relative_to(package_root)

        if "templates" in relative.parts:
            continue

        try:
            source = pyfile.read_text(encoding="utf-8")
            compile(source, str(pyfile), "exec")
        except (OSError, SyntaxError, ValueError) as exc:
            return [(str(relative), str(exc))]

    return []


def doctor_command() -> None:
    """Check installed tools and validate the polyinit installation."""
    console.print("[bold cyan]polyinit doctor[/bold cyan]\n")

    environment = Table(title="Environment")
    environment.add_column("Item")
    environment.add_column("Value")
    environment.add_row("python", _python_version())
    environment.add_row("polyinit", sys.executable)
    console.print(environment)
    console.print()

    table = Table(title="Tool Check")
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Path/Info")

    table.add_row("python", "✓", sys.executable)

    for name in BASE_TOOLS:
        table.add_row(*_tool_row(name))

    for language, tools in LANGUAGE_TOOLS.items():
        for tool in tools:
            name, status, path = _tool_row(tool)
            table.add_row(f"{language}:{name}", status, path)

    for language, tools in OPTIONAL_TOOLS.items():
        for tool in tools:
            name, _, path = _tool_row(tool)
            table.add_row(
                f"{language}:{name}",
                "optional",
                path or "Not found in PATH",
            )

    console.print(table)
    console.print()

    package_root = Path(__file__).resolve().parent.parent
    failures = _check_sources(package_root)

    if failures:
        for name, detail in failures:
            console.print(f"[red]✗[/red] {name}: {detail}")
        raise typer.Exit(code=1)

    console.print("[green]✓[/green] All polyinit modules compile successfully")
    console.print("\n[green]Doctor check complete![/green]")