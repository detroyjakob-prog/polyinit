import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def create_virtualenv(root: Path) -> None:
    run([sys.executable, "-m", "venv", ".venv"], root)


def init_git(root: Path) -> None:
    run(["git", "init"], root)
