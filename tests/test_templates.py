from pathlib import Path

import pytest

from polyinit.features import features_for, supports
from polyinit.generator import generate_project, validate_project_name
from polyinit.models import ProjectConfig
from polyinit.templates import (
    available_languages,
    available_types,
    get_template_dir,
    list_templates,
    render_template,
)


def make_config(**overrides) -> ProjectConfig:
    defaults = {
        "name": "demo",
        "language": "Python",
        "project_type": "CLI",
        "git": False,
        "virtualenv": False,
        "pytest": True,
        "ruff": True,
        "readme": True,
    }
    defaults.update(overrides)
    return ProjectConfig(**defaults)


class TestTemplateDiscovery:
    def test_languages_are_listed(self):
        languages = available_languages()
        assert "python" in languages
        assert "rust" in languages

    def test_types_are_listed_per_language(self):
        assert "cli" in available_types("Python")
        assert available_types("Go") == ["cli", "library", "web-api"]

    def test_unknown_language_has_no_types(self):
        assert available_types("cobol") == []

    def test_every_listed_template_directory_exists(self):
        for language, types in list_templates().items():
            for project_type in types:
                assert get_template_dir(language, project_type).is_dir()

    def test_language_lookup_is_case_insensitive(self):
        assert available_types("python") == available_types("Python")


class TestFeatureSupport:
    def test_python_supports_python_only_features(self):
        assert supports("python", "pytest")
        assert supports("python", "ruff")
        assert not supports("rust", "pytest")
        assert not supports("go", "ruff")

    def test_virtualenv_is_python_only(self):
        assert features_for("Python") == [
            "git",
            "readme",
            "virtualenv",
            "pytest",
            "ruff",
        ]
        assert "virtualenv" not in features_for("Rust")

    def test_unknown_feature_is_never_supported(self):
        assert not supports("python", "nonsense")


class TestProjectNameValidation:
    @pytest.mark.parametrize("name", ["demo", "my-project", "my_project", "a1"])
    def test_valid_names(self, name):
        assert validate_project_name(name)

    @pytest.mark.parametrize("name", ["", "1demo", "-demo", "my project", "a/b"])
    def test_invalid_names(self, name):
        assert not validate_project_name(name)


class TestRendering:
    def test_placeholders_are_substituted_in_paths_and_content(self, tmp_path):
        template_dir = get_template_dir("Python", "CLI")
        render_template(template_dir, tmp_path, "my-app")

        package = tmp_path / "src" / "my_app"
        assert package.is_dir()
        assert (package / "main.py").exists()

        pyproject = (tmp_path / "pyproject.toml").read_text()
        assert "{{project_name}}" not in pyproject
        assert "{{package_name}}" not in pyproject
        assert 'name = "my-app"' in pyproject

    def test_hyphens_become_underscores_in_package_names(self, tmp_path):
        render_template(get_template_dir("Python", "CLI"), tmp_path, "a-b-c")
        assert (tmp_path / "src" / "a_b_c" / "__init__.py").exists()


class TestGeneration:
    def test_rejects_unavailable_combination(self, tmp_path):
        config = make_config(language="Python", project_type="Document")

        with pytest.raises(ValueError, match="No template exists"):
            generate_project(config, tmp_path)

    def test_error_lists_available_types(self, tmp_path):
        config = make_config(language="Markdown", project_type="CLI")

        with pytest.raises(ValueError, match="document"):
            generate_project(config, tmp_path)

    def test_readme_flag_removes_readme(self, tmp_path):
        generate_project(make_config(readme=False), tmp_path)
        assert not (tmp_path / "README.md").exists()

    def test_readme_flag_keeps_readme(self, tmp_path):
        generate_project(make_config(readme=True), tmp_path)
        assert (tmp_path / "README.md").exists()

    def test_pytest_flag_controls_tests_and_config(self, tmp_path):
        generate_project(make_config(pytest=False), tmp_path)

        assert not (tmp_path / "tests").exists()

        pyproject = (tmp_path / "pyproject.toml").read_text()
        assert "tool.pytest.ini_options" not in pyproject
        assert '"pytest>=' not in pyproject

    def test_pytest_flag_keeps_tests_and_config(self, tmp_path):
        generate_project(make_config(pytest=True), tmp_path)

        assert (tmp_path / "tests" / "test_main.py").exists()

        pyproject = (tmp_path / "pyproject.toml").read_text()
        assert "tool.pytest.ini_options" in pyproject
        assert '"pytest>=' in pyproject

    def test_ruff_flag_controls_ruff_config(self, tmp_path):
        generate_project(make_config(ruff=False), tmp_path)

        pyproject = (tmp_path / "pyproject.toml").read_text()
        assert "tool.ruff" not in pyproject
        assert '"ruff>=' not in pyproject

    def test_pyproject_survives_with_every_optional_feature_off(self, tmp_path):
        generate_project(
            make_config(pytest=False, ruff=False, readme=False),
            tmp_path,
        )

        pyproject = tmp_path / "pyproject.toml"
        assert pyproject.exists()

        text = pyproject.read_text()
        assert "[project]" in text
        assert "[project.scripts]" in text
        assert "[build-system]" in text

    def test_steps_report_what_happened(self, tmp_path):
        steps = generate_project(
            make_config(pytest=False, readme=False),
            tmp_path,
        )

        joined = " | ".join(steps)
        assert "Generated" in joined
        assert "README.md" in joined
        assert "tests/" in joined

    def test_non_python_templates_keep_their_tests(self, tmp_path):
        generate_project(
            make_config(
                language="JavaScript",
                project_type="CLI",
                pytest=False,
                ruff=False,
            ),
            tmp_path,
        )

        # The pytest/ruff flags are Python only, so a JS project keeps its
        # own test suite.
        assert (tmp_path / "tests" / "cli.test.js").exists()


class TestAllTemplatesGenerate:
    @pytest.mark.parametrize(
        ("language", "project_type"),
        [
            (language, project_type)
            for language, types in list_templates().items()
            for project_type in types
        ],
    )
    def test_template_generates_cleanly(
        self,
        language: str,
        project_type: str,
        tmp_path: Path,
    ):
        config = make_config(
            language=language,
            project_type=project_type,
            pytest=True,
            ruff=True,
        )

        generate_project(config, tmp_path)

        assert any(tmp_path.iterdir())

        for path in tmp_path.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                assert "{{project_name}}" not in text
                assert "{{package_name}}" not in text