"""Generate every shipped template into ./generated for CI to build.

Run with ``python -m tests.check_templates``. Each project is generated with
all features enabled so the resulting tree is the full template.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from polyinit.generator import generate_project  # noqa: E402
from polyinit.models import ProjectConfig  # noqa: E402
from polyinit.templates import list_templates  # noqa: E402

OUTPUT = Path("generated")


def generate_all() -> list[Path]:
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)

    roots: list[Path] = []

    for language, project_types in list_templates().items():
        for project_type in project_types:
            root = OUTPUT / language / project_type
            root.mkdir(parents=True)

            config = ProjectConfig(
                name="demo",
                language=language,
                project_type=project_type,
                git=False,
                virtualenv=False,
                pytest=True,
                ruff=True,
                readme=True,
            )
            generate_project(config, root)
            roots.append(root)

    return roots


def main() -> int:
    roots = generate_all()

    for root in roots:
        print(f"generated {root}")

    print(f"\n{len(roots)} projects generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())