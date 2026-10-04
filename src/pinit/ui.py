import questionary
from questionary import Choice
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .features import (
    FEATURE_LABELS,
    features_for,
    is_default_enabled,
)
from .models import ProjectConfig
from .templates import available_languages, available_types

console = Console()

# Directory names differ from how they read best in a prompt.
TYPE_LABELS = {
    "cli": "CLI",
    "web-api": "Web API",
    "document": "Document",
}


def show_banner() -> None:
    console.print(
        Panel(
            "Let's create your project!",
            title="Project Init",
            border_style="cyan",
        )
    )


def ask_config(name: str | None = None) -> ProjectConfig | None:
    if name is None:
        name = questionary.text(
            "Project name:",
            validate=lambda value: bool(value.strip())
            or "Please enter a project name.",
        ).ask()

    if name is None:
        return None

    language = questionary.select(
        "What language?",
        choices=_language_choices(),
    ).ask()

    if language is None:
        return None

    # Types are derived from the templates that actually ship, so every
    # combination offered here can be generated.
    types = available_types(language)
    project_type = questionary.select(
        "What type of project?",
        choices=_type_choices(types),
    ).ask()

    if project_type is None:
        return None

    features = features_for(language)
    choices = _feature_choices(features)

    selected = questionary.checkbox(
        "Features:",
        choices=choices,
        instruction="Use ↑/↓ to move, Space to select, Enter to continue",
    ).ask()

    if selected is None:
        return None

    # questionary returns the values of the chosen entries, which default to
    # their titles.
    chosen = set(selected)

    def enabled(feature: str) -> bool:
        return FEATURE_LABELS[feature] in chosen

    return ProjectConfig(
        name=name.strip(),
        language=language,
        project_type=project_type,
        git=enabled("git"),
        virtualenv=enabled("virtualenv"),
        pytest=enabled("pytest"),
        ruff=enabled("ruff"),
        readme=enabled("readme"),
    )


def _language_choices() -> list[str]:
    return [
        language.capitalize()
        for language in available_languages()
    ]


def _type_choices(types: list[str]) -> list[str]:
    return [TYPE_LABELS.get(item, item.replace("-", " ").title()) for item in types]


def _feature_choices(features: list[str]) -> list[Choice]:
    return [
        Choice(
            FEATURE_LABELS[feature],
            checked=is_default_enabled(feature),
        )
        for feature in features
    ]


def confirm_config(config: ProjectConfig) -> bool:
    table = Table(title="Project Summary", show_header=False, box=None)
    table.add_row("Name", config.name)
    table.add_row("Language", config.language)
    table.add_row("Type", config.project_type)

    enabled = {
        "git": config.git,
        "readme": config.readme,
        "virtualenv": config.virtualenv,
        "pytest": config.pytest,
        "ruff": config.ruff,
    }

    for feature in features_for(config.language):
        table.add_row(
            FEATURE_LABELS[feature],
            "yes" if enabled[feature] else "no",
        )

    console.print(table)
    return questionary.confirm("Create this project?", default=True).ask() is True


def show_success(path, steps: list[str]) -> None:
    console.print()
    for step in steps:
        console.print(f"[bold green]✓[/bold green] {step}")

    console.print()
    console.print(
        Panel(
            f"[bold green]🎉 Project created successfully![/bold green]\n\n"
            f"cd {path}",
            border_style="green",
        )
    )
