import shutil
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def interpreter_for_venv() -> str | None:
    """Return an interpreter that can create a virtual environment.

    In a frozen build ``sys.executable`` is the polyinit binary itself, so
    using it would run ``polyinit -m venv``. Fall back to a real interpreter
    from PATH, and return None when the machine has none.
    """
    if not getattr(sys, "frozen", False):
        return sys.executable

    for name in ("python3", "python"):
        found = shutil.which(name)
        if found:
            return found

    return None


def create_virtualenv(root: Path) -> bool:
    """Create a .venv in ``root``.

    Returns False when no interpreter capable of creating one is available,
    which is not an error worth failing the whole project over.
    """
    interpreter = interpreter_for_venv()
    if interpreter is None:
        return False

    run([interpreter, "-m", "venv", ".venv"], root)
    return True


def init_git(root: Path) -> None:
    run(["git", "init"], root)