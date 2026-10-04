import typer
from rich.console import Console
from rich.table import Table

from ..templates import list_templates

console = Console()


def templates_command() -> None:
    """List all installed project templates."""
    templates = list_templates()

    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        raise typer.Exit()

    table = Table(title="Available Templates")
    table.add_column("Language")
    table.add_column("Project Types")

    for language, project_types in templates.items():
        table.add_row(language, ", ".join(project_types))

    console.print(table)
