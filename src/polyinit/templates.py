import re
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"


def normalize(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def get_template_dir(language: str, project_type: str) -> Path:
    return TEMPLATES_DIR / normalize(language) / normalize(project_type)


def template_exists(language: str, project_type: str) -> bool:
    return get_template_dir(language, project_type).is_dir()


def available_languages() -> list[str]:
    """Return the template languages that ship with polyinit, sorted."""
    if not TEMPLATES_DIR.exists():
        return []

    return sorted(
        item.name
        for item in TEMPLATES_DIR.iterdir()
        if item.is_dir()
    )


def available_types(language: str) -> list[str]:
    """Return the project types available for ``language``, sorted.

    The templates directory is the single source of truth, so a combination
    the UI offers is always a combination that can actually be generated.
    """
    language_dir = TEMPLATES_DIR / normalize(language)

    if not language_dir.is_dir():
        return []

    return sorted(
        item.name
        for item in language_dir.iterdir()
        if item.is_dir()
    )


def list_templates() -> dict[str, list[str]]:
    """Return every language mapped to its available project types."""
    return {
        language: available_types(language)
        for language in available_languages()
    }


def render_template(
    template_dir: Path,
    destination: Path,
    project_name: str,
) -> None:
    package_name = re.sub(r"[^a-zA-Z0-9_]", "_", project_name.replace("-", "_"))

    def substitute(value: str) -> str:
        value = value.replace("{{project_name}}", project_name)
        return value.replace("{{package_name}}", package_name)

    for source in template_dir.rglob("*"):
        relative = source.relative_to(template_dir)

        # Placeholders are substituted in path segments too, so template
        # directories such as src/{{package_name}} are renamed on render.
        target = destination / Path(
            *(substitute(part) for part in relative.parts)
        )

        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)

        content = substitute(source.read_text(encoding="utf-8"))

        target.write_text(content, encoding="utf-8")
