
import pytest

from pinit.edits import (
    collapse_empty_arrays,
    remove_paths,
    remove_toml_key,
    remove_toml_list_entries,
    remove_toml_section,
    strip_pyproject_feature,
)

SAMPLE = """\
[build-system]
requires = ["hatchling"]

[project]
name = "demo"

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.6.0",
    "httpx>=0.27.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]

[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = ["E", "F"]
"""


class TestRemoveTomlSection:
    def test_removes_target_section(self):
        result = remove_toml_section(SAMPLE, "tool.pytest.ini_options")
        assert "tool.pytest.ini_options" not in result
        assert "[tool.ruff]" in result

    def test_keeps_sibling_content(self):
        result = remove_toml_section(SAMPLE, "tool.pytest.ini_options")
        assert "[build-system]" in result
        assert 'name = "demo"' in result

    def test_removing_nested_section_keeps_parent(self):
        result = remove_toml_section(SAMPLE, "tool.ruff.lint")
        assert "tool.ruff.lint" not in result
        assert "[tool.ruff]" in result

    def test_removing_last_section_leaves_earlier_ones(self):
        result = remove_toml_section(SAMPLE, "tool.ruff.lint")
        assert "select =" not in result
        assert "[tool.ruff]" in result
        assert "line-length = 88" in result

    def test_missing_section_is_noop(self):
        assert remove_toml_section(SAMPLE, "tool.nope") == SAMPLE

    def test_does_not_match_similarly_named_section(self):
        text = "[tool.ruff]\nline-length = 88\n"
        assert remove_toml_section(text, "tool.ruffx") == text


class TestRemoveTomlListEntries:
    def test_removes_single_entry(self):
        result = remove_toml_list_entries(
            SAMPLE, "project.optional-dependencies", ["ruff"]
        )
        assert "ruff>=" not in result
        assert "pytest>=" in result

    def test_removes_multiple_entries(self):
        result = remove_toml_list_entries(
            SAMPLE,
            "project.optional-dependencies",
            ["pytest", "httpx"],
        )
        assert "pytest>=" not in result
        assert "httpx>=" not in result
        assert "ruff>=" in result

    def test_preserves_section_header(self):
        result = remove_toml_list_entries(
            SAMPLE, "project.optional-dependencies", ["pytest", "ruff"]
        )
        assert "[project.optional-dependencies]" in result

    def test_missing_section_is_noop(self):
        assert (
            remove_toml_list_entries(SAMPLE, "project.nope", ["pytest"])
            == SAMPLE
        )

    def test_does_not_match_a_longer_similar_entry(self):
        text = (
            '[project.optional-dependencies]\ndev = [\n'
            '    "ruff-lint>=1.0.0",\n'
            ']\n'
        )

        result = remove_toml_list_entries(
            text, "project.optional-dependencies", ["ruff"]
        )

        assert "ruff-lint>=1.0.0" in result

    def test_matches_bare_entry_without_version(self):
        text = (
            '[project.optional-dependencies]\ndev = [\n'
            '    "pytest",\n'
            ']\n'
        )

        result = remove_toml_list_entries(
            text, "project.optional-dependencies", ["pytest"]
        )

        assert '"pytest"' not in result


class TestRemovePaths:
    def test_removes_directory(self, tmp_path):
        (tmp_path / "tests").mkdir()
        (tmp_path / "tests" / "test_a.py").write_text("x")

        removed = remove_paths(tmp_path, ["tests"])

        assert removed == ["tests"]
        assert not (tmp_path / "tests").exists()

    def test_removes_file(self, tmp_path):
        (tmp_path / "README.md").write_text("x")

        assert remove_paths(tmp_path, ["README.md"]) == ["README.md"]
        assert not (tmp_path / "README.md").exists()

    def test_absent_path_is_ignored(self, tmp_path):
        assert remove_paths(tmp_path, ["nope.md"]) == []


class TestStripPyprojectFeature:
    def test_strips_pytest_only(self, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text(SAMPLE)

        strip_pyproject_feature(path, pytest=False, ruff=True)
        text = path.read_text()

        assert "tool.pytest" not in text
        assert "tool.ruff" in text
        assert "pytest>=" not in text
        assert "ruff>=" in text

    def test_strips_ruff_only(self, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text(SAMPLE)

        strip_pyproject_feature(path, pytest=True, ruff=False)
        text = path.read_text()

        assert "tool.pytest" in text
        assert "tool.ruff" not in text
        assert "ruff>=" not in text

    def test_strips_both(self, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text(SAMPLE)

        strip_pyproject_feature(path, pytest=False, ruff=False)
        text = path.read_text()

        assert "tool.pytest" not in text
        assert "tool.ruff" not in text
        assert "[project]" in text

    def test_keeps_everything_when_both_enabled(self, tmp_path):
        path = tmp_path / "pyproject.toml"
        path.write_text(SAMPLE)

        strip_pyproject_feature(path, pytest=True, ruff=True)

        assert path.read_text().strip() == SAMPLE.strip()

    def test_missing_file_is_noop(self, tmp_path):
        strip_pyproject_feature(
            tmp_path / "nope.toml", pytest=False, ruff=False
        )
        assert not (tmp_path / "nope.toml").exists()


class TestRemoveTomlKey:
    def test_removes_readme_key(self):
        text = '[project]\nname = "demo"\nreadme = "README.md"\n'
        result = remove_toml_key(text, "readme")
        assert "readme" not in result
        assert 'name = "demo"' in result

    def test_removes_key_without_trailing_newline(self):
        text = '[project]\nreadme = "README.md"'
        assert "readme" not in remove_toml_key(text, "readme")

    def test_missing_key_is_noop(self):
        assert remove_toml_key(SAMPLE, "readme") == SAMPLE


class TestCollapseEmptyArrays:
    def test_collapses_multiline_empty_array(self):
        text = "dev = [\n]\n"
        assert collapse_empty_arrays(text) == "dev = []\n"

    def test_collapses_whitespace_only_array(self):
        text = "dev = [   ]\n"
        assert collapse_empty_arrays(text) == "dev = []\n"

    def test_leaves_populated_array_alone(self):
        text = 'dev = [\n    "ruff>=1.0",\n]\n'
        assert collapse_empty_arrays(text) == text


class TestTrailingNewlineHandling:
    """Templates are not guaranteed to end with a newline."""

    def test_removes_section_without_trailing_newline(self):
        text = "[tool.ruff]\nline-length = 88\n\n[tool.ruff.lint]\nselect = [\"E\"]"
        result = remove_toml_section(text, "tool.ruff.lint")

        assert "select" not in result
        assert "[tool.ruff]" in result

    def test_removes_final_key_line_without_trailing_newline(self):
        text = '[project]\nname = "demo"\nreadme = "README.md"'
        result = remove_toml_key(text, "readme")

        assert "readme" not in result
        assert 'name = "demo"' in result

    def test_removes_last_list_entry_without_trailing_newline(self):
        text = (
            "[project.optional-dependencies]\n"
            "dev = [\n"
            '    "pytest>=8.0.0",\n'
            '    "ruff>=0.6.0"'
        )
        result = remove_toml_list_entries(
            text, "project.optional-dependencies", ["ruff"]
        )

        assert "ruff" not in result
        assert "pytest" in result


class TestResultIsValidToml:
    @pytest.mark.parametrize(
        ("pytest_on", "ruff_on"),
        [(True, True), (True, False), (False, True), (False, False)],
    )
    def test_output_parses(self, tmp_path, pytest_on, ruff_on):
        tomllib = pytest.importorskip("tomllib")

        path = tmp_path / "pyproject.toml"
        path.write_text(SAMPLE)

        strip_pyproject_feature(path, pytest=pytest_on, ruff=ruff_on)

        data = tomllib.loads(path.read_text())

        assert data["project"]["name"] == "demo"
        assert "[build-system]" in path.read_text()

    def test_stripping_everything_still_parses(self, tmp_path):
        tomllib = pytest.importorskip("tomllib")

        path = tmp_path / "pyproject.toml"
        path.write_text(SAMPLE)

        strip_pyproject_feature(
            path, pytest=False, ruff=False, readme=False
        )
        text = path.read_text()

        assert "tool.pytest" not in text
        assert "tool.ruff" not in text
        assert "readme" not in text
        assert tomllib.loads(text)["project"]["name"] == "demo"

    def test_every_real_template_survives_stripping(self, tmp_path):
        """Each shipped Python template must stay valid with features off."""
        tomllib = pytest.importorskip("tomllib")

        from pinit.generator import generate_project
        from pinit.models import ProjectConfig
        from pinit.templates import available_types

        for project_type in available_types("python"):
            root = tmp_path / project_type
            root.mkdir()

            generate_project(
                ProjectConfig(
                    name="demo",
                    language="Python",
                    project_type=project_type,
                    git=False,
                    virtualenv=False,
                    pytest=False,
                    ruff=False,
                    readme=False,
                ),
                root,
            )

            data = tomllib.loads(
                (root / "pyproject.toml").read_text()
            )

            assert data["project"]["name"] == "demo"
            assert "readme" not in data["project"]
            assert "tool" not in data or "ruff" not in data["tool"]