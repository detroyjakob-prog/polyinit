import typer
from rich.console import Console

from .commands.create import create_command
from .commands.doctor import doctor_command
from .commands.run import run_command
from .commands.templates import templates_command

app = typer.Typer(
    name="polyinit",
    help="Create project skeletons from the terminal.",
    no_args_is_help=True,
)
console = Console()

app.command(name="create")(create_command)
app.command(name="templates")(templates_command)
app.command(name="doctor")(doctor_command)
app.command(name="run")(run_command)


@app.command()
def version() -> None:
    """Show the polyinit version."""
    from . import __version__
    console.print(f"polyinit {__version__}")
