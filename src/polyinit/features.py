"""Feature definitions shared by the prompts and the generator.

Keeping this in one place is what stops the UI from offering a combination
the generator cannot honour.
"""

# Feature label -> languages that support it.
LANGUAGE_FEATURES: dict[str, tuple[str, ...]] = {
    "git": ("python", "javascript", "typescript", "rust", "go", "markdown"),
    "readme": ("python", "javascript", "typescript", "rust", "go", "markdown"),
    "virtualenv": ("python",),
    "pytest": ("python",),
    "ruff": ("python",),
}

# Features enabled by default, per feature name.
DEFAULT_ENABLED: frozenset[str] = frozenset(
    {"git", "readme", "virtualenv"}
)

# Human readable labels used in the interactive checkbox.
FEATURE_LABELS: dict[str, str] = {
    "git": "Git",
    "readme": "README",
    "virtualenv": "Virtual environment",
    "pytest": "Pytest",
    "ruff": "Ruff",
}


def supports(language: str, feature: str) -> bool:
    """Return whether ``feature`` applies to ``language``."""
    languages = LANGUAGE_FEATURES.get(feature)
    if languages is None:
        return False

    return language.strip().lower() in languages


def features_for(language: str) -> list[str]:
    """Return the feature names available for ``language``, in prompt order."""
    order = ["git", "readme", "virtualenv", "pytest", "ruff"]
    return [name for name in order if supports(language, name)]


def is_default_enabled(feature: str) -> bool:
    """Return whether a feature is pre-selected in the prompt."""
    return feature in DEFAULT_ENABLED