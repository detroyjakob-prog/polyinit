import contextlib
import subprocess
from pathlib import Path

import typer
from rich.console import Console

from ..generator import generate_project, validate_project_name
from ..system import create_virtualenv, init_git
from ..ui import ask_config, confirm_config, show_banner, show_success

console = Console()


def create_command(
    name: str | None = typer.Argument(
        None,
        help="Project name. If omitted, polyinit asks interactively.",
    ),
) -> None:
    """Interactively create a new project."""
    show_banner()

    config = ask_config(name)

    if config is None:
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit()

    if not validate_project_name(config.name):
        console.print(
            "[bold red]✗ Invalid project name.[/bold red] "
            "Use letters, numbers, '-' or '_' and start with a letter."
        )
        raise typer.Exit(code=1)

    root = Path(config.name)

    if root.exists():
        console.print(
            f"[bold red]✗ Directory already exists:[/bold red] {root}"
        )
        raise typer.Exit(code=1)

    if not confirm_config(config):
        console.print("[yellow]Cancelled.[/yellow]")
        raise typer.Exit()

    steps: list[str] = []

    try:
        root.mkdir()

        steps.extend(generate_project(config, root))

        if config.virtualenv:
            if create_virtualenv(root):
                steps.append("Created virtual environment")
            else:
                console.print(
                    "[yellow]Skipped the virtual environment:[/yellow] "
                    "no Python interpreter found to create one with. "
                    "Install Python and run "
                    "[cyan]python -m venv .venv[/cyan] inside the project."
                )

        if config.git:
            init_git(root)
            steps.append("Initialized Git")

        show_success(root, steps)

    except ValueError as exc:
        if root.exists():
            # Only remove an empty directory created by this run.
            with contextlib.suppress(OSError):
                root.rmdir()

        console.print(f"[bold red]✗ {exc}[/bold red]")
        raise typer.Exit(code=1) from exc

    except subprocess.CalledProcessError as exc:
        console.print(
            "[bold red]✗ A system command failed.[/bold red] "
            "Check that the required tool is installed."
        )
        raise typer.Exit(code=1) from exc
