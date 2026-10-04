import re
from pathlib import Path

from .edits import remove_paths, strip_pyproject_feature
from .models import ProjectConfig
from .templates import available_types, get_template_dir, render_template


def validate_project_name(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", name))


def generate_project(config: ProjectConfig, root: Path) -> list[str]:
    if not template_exists(config.language, config.project_type):
        supported = ", ".join(available_types(config.language)) or "none"
        raise ValueError(
            f"No template exists for "
            f"{config.language} / {config.project_type}. "
            f"Available types: {supported}."
        )

    template_dir = get_template_dir(
        config.language,
        config.project_type,
    )

    render_template(
        template_dir=template_dir,
        destination=root,
        project_name=config.name,
    )

    steps = [
        f"Generated {config.language} {config.project_type} template"
    ]

    steps.extend(_apply_features(config, root))

    return steps


def template_exists(language: str, project_type: str) -> bool:
    from .templates import template_exists as _exists

    return _exists(language, project_type)


def _apply_features(config: ProjectConfig, root: Path) -> list[str]:
    """Remove the pieces of the rendered template the user opted out of."""
    steps: list[str] = []
    is_python = config.language.strip().lower() == "python"

    if not config.readme:
        removed = remove_paths(root, ["README.md"])
        if removed:
            steps.append("Skipped README.md")

    if is_python:
        if not config.pytest:
            removed = remove_paths(root, ["tests"])
            if removed:
                steps.append("Removed tests/")

        if not config.pytest or not config.ruff or not config.readme:
            # pyproject.toml still carries the package definition, build
            # backend and script entry point, so the file always stays.
            strip_pyproject_feature(
                root / "pyproject.toml",
                pytest=config.pytest,
                ruff=config.ruff,
                readme=config.readme,
            )

    return steps