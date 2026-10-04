"""Post-render edits applied to a generated project.

Templates ship in their "everything enabled" form so that they stay valid,
self-contained projects that also work when copied by hand. Features the user
opted out of are removed here, after rendering, rather than being threaded
through every template file as a placeholder.
"""

import re
import shutil
from pathlib import Path


def remove_toml_section(text: str, section: str) -> str:
    """Remove a ``[section]`` block, including its trailing blank line.

    Handles the dotted section names used in ``pyproject.toml`` (for example
    ``tool.pytest.ini_options``) by matching the literal header line.
    """
    pattern = re.compile(
        rf"^\[{re.escape(section)}\][ \t]*\n"
        rf"(?:(?![ \t]*\[)[^\n]*(?:\n|\Z))*",
        re.MULTILINE,
    )
    cleaned = pattern.sub("", text)

    # Collapse the blank line the removed block left behind.
    return re.sub(r"\n{3,}", "\n\n", cleaned)


def remove_toml_list_entries(
    text: str,
    section: str,
    entries: list[str],
) -> str:
    """Drop ``entries`` from the array inside ``section``.

    Used to prune optional dev dependencies. The section is left in place so
    the surrounding table stays well formed.
    """
    block = _find_section(text, section)
    if block is None:
        return text

    start, end = block
    body = text[start:end]

    for entry in entries:
        # Match the whole quoted requirement, including any version
        # specifier, while refusing to match a longer name that merely
        # starts with this one (e.g. "ruff" must not match "ruff-lint").
        body = re.sub(
            rf'^[ \t]*"{re.escape(entry)}'
            rf'(?![A-Za-z0-9_.-])[^"\n]*"[^\n]*(?:\n|\Z)',
            "",
            body,
            flags=re.MULTILINE,
        )

    return text[:start] + body + text[end:]


def _find_section(text: str, section: str) -> tuple[int, int] | None:
    """Return the ``(start, end)`` span of a section's body lines."""
    match = re.search(
        rf"^\[{re.escape(section)}\][ \t]*\n",
        text,
        flags=re.MULTILINE,
    )
    if match is None:
        return None

    start = match.end()

    end = len(text)
    next_section = re.search(r"^[ \t]*\[", text[start:], flags=re.MULTILINE)
    if next_section is not None:
        end = start + next_section.start()

    return start, end


def remove_toml_key(text: str, key: str) -> str:
    """Remove a top-level key assignment such as ``readme = "README.md"``."""
    return re.sub(
        rf'^[ \t]*{re.escape(key)}[ \t]*=.*?(?:\n|\Z)',
        "",
        text,
        flags=re.MULTILINE,
    )


def collapse_empty_arrays(text: str) -> str:
    """Turn ``key = [\\n]`` left behind by pruning back into ``key = []``."""
    return re.sub(
        r"^([ \t]*[A-Za-z0-9_.-]+[ \t]*=)[ \t]*\[\s*\]([ \t]*)$",
        r"\1 []\2",
        text,
        flags=re.MULTILINE,
    )


def remove_paths(root: Path, relative_paths: list[str]) -> list[str]:
    """Delete each path under ``root``, ignoring ones that are absent."""
    removed: list[str] = []

    for relative in relative_paths:
        target = root / relative

        if target.is_dir():
            shutil.rmtree(target)
            removed.append(relative)
        elif target.exists():
            target.unlink()
            removed.append(relative)

    return removed


def strip_pyproject_feature(
    path: Path,
    *,
    pytest: bool,
    ruff: bool,
    readme: bool = True,
) -> None:
    """Remove pytest/ruff/readme wiring from a generated ``pyproject.toml``."""
    if not path.exists():
        return

    text = path.read_text(encoding="utf-8")

    if not pytest:
        text = remove_toml_section(text, "tool.pytest.ini_options")
        text = remove_toml_list_entries(
            text, "project.optional-dependencies", ["pytest"]
        )

    if not ruff:
        text = remove_toml_section(text, "tool.ruff")
        text = remove_toml_section(text, "tool.ruff.lint")
        text = remove_toml_list_entries(
            text, "project.optional-dependencies", ["ruff"]
        )

    if not readme:
        # Leaving the key would make the build backend fail on a missing file.
        text = remove_toml_key(text, "readme")

    text = collapse_empty_arrays(text)

    path.write_text(text.rstrip() + "\n", encoding="utf-8")