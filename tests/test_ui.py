"""Tests for the interactive prompt flow.

The prompts are mocked at the questionary boundary so the wiring between
questions, choices and the resulting config is covered without a terminal.
"""

from __future__ import annotations

import pytest
import questionary

from polyinit import ui
from polyinit.templates import available_languages, available_types


class FakeQuestion:
    def __init__(self, answer):
        self.answer = answer

    def ask(self):
        return self.answer


class FakePrompt:
    def __init__(self, answers: dict):
        self.answers = answers
        self.calls: list[dict] = []

    def _record(self, message, choices):
        self.calls.append({"message": message, "choices": choices})
        return FakeQuestion(self.answers.get(message))

    def select(self, message, choices=None, **kwargs):
        return self._record(message, choices)

    def checkbox(self, message, choices=None, **kwargs):
        return self._record(message, choices)

    def text(self, message, **kwargs):
        return self._record(message, None)

    def confirm(self, message, **kwargs):
        return self._record(message, None)


@pytest.fixture
def fake_prompt(monkeypatch):
    def install(answers):
        prompt = FakePrompt(answers)
        for attribute in ("select", "checkbox", "text", "confirm"):
            monkeypatch.setattr(
                questionary, attribute, getattr(prompt, attribute)
            )
        return prompt

    return install


def test_asks_for_a_name_when_omitted(fake_prompt):
    prompt = fake_prompt(
        {
            "Project name:": "typed-name",
            "What language?": "Python",
            "What type of project?": "CLI",
            "Features:": [],
        }
    )

    config = ui.ask_config()

    assert config is not None
    assert config.name == "typed-name"
    assert prompt.calls[0]["message"] == "Project name:"


def test_skips_name_prompt_when_given(fake_prompt):
    prompt = fake_prompt(
        {
            "What language?": "Python",
            "What type of project?": "CLI",
            "Features:": [],
            "Create this project?": True,
        }
    )

    ui.ask_config("given-name")

    assert "Project name:" not in [c["message"] for c in prompt.calls]


class TestChoiceSets:
    def test_language_choices_match_templates(self, fake_prompt):
        prompt = fake_prompt(
            {
                "What language?": "Python",
                "What type of project?": "CLI",
                "Features:": [],
            }
        )

        ui.ask_config("demo")

        languages = prompt.calls[0]["choices"]
        assert len(languages) == len(available_languages())

    def test_language_labels_are_properly_cased(self, fake_prompt):
        prompt = fake_prompt(
            {
                "What language?": "Python",
                "What type of project?": "CLI",
                "Features:": [],
            }
        )

        ui.ask_config("demo")

        languages = prompt.calls[0]["choices"]

        assert "JavaScript" in languages
        assert "TypeScript" in languages
        assert "Javascript" not in languages
        assert "Typescript" not in languages

    def test_type_choices_match_the_selected_language(self, fake_prompt):
        prompt = fake_prompt(
            {
                "What language?": "Markdown",
                "What type of project?": "Document",
                "Features:": [],
            }
        )

        ui.ask_config("demo")

        types = prompt.calls[1]["choices"]
        assert types == ["Document"]

    def test_every_offered_combination_has_a_template(self, fake_prompt):
        """A choice the prompt makes must be generatable."""
        for language in available_languages():
            label = ui.LANGUAGE_LABELS.get(
                language, language.capitalize()
            )
            fake_prompt(
                {
                    "What language?": label,
                    "What type of project?": ui.TYPE_LABELS[
                        available_types(language)[0]
                    ],
                    "Features:": [],
                }
            )

            config = ui.ask_config("demo")

            assert config is not None
            assert config.language.lower() == language

    def test_feature_choices_are_language_aware(self, fake_prompt):
        prompt = fake_prompt(
            {
                "What language?": "Rust",
                "What type of project?": "CLI",
                "Features:": ["Git"],
            }
        )

        ui.ask_config("demo")

        features = prompt.calls[2]["choices"]
        titles = [c.title for c in features]

        assert "Pytest" not in titles
        assert "Ruff" not in titles
        assert "Virtual environment" not in titles
        assert "Git" in titles

    def test_python_gets_the_full_feature_list(self, fake_prompt):
        prompt = fake_prompt(
            {
                "What language?": "Python",
                "What type of project?": "CLI",
                "Features:": [],
            }
        )

        ui.ask_config("demo")

        titles = [c.title for c in prompt.calls[2]["choices"]]
        assert titles == [
            "Git",
            "README",
            "Virtual environment",
            "Pytest",
            "Ruff",
        ]

    def test_defaults_are_preselected(self, fake_prompt):
        prompt = fake_prompt(
            {
                "What language?": "Python",
                "What type of project?": "CLI",
                "Features:": [],
            }
        )

        ui.ask_config("demo")

        checked = {c.title for c in prompt.calls[2]["choices"] if c.checked}
        assert checked == {"Git", "README", "Virtual environment"}


class TestConfigMapping:
    def test_maps_selected_features(self, fake_prompt):
        fake_prompt(
            {
                "What language?": "Python",
                "What type of project?": "CLI",
                "Features:": ["Git", "Pytest"],
            }
        )

        config = ui.ask_config("demo")

        assert config.git is True
        assert config.pytest is True
        assert config.ruff is False
        assert config.readme is False
        assert config.virtualenv is False

    def test_maps_no_features(self, fake_prompt):
        fake_prompt(
            {
                "What language?": "Rust",
                "What type of project?": "CLI",
                "Features:": [],
            }
        )

        config = ui.ask_config("demo")

        assert config.git is False
        assert config.readme is False
        assert config.virtualenv is False

    def test_strips_whitespace_from_name(self, fake_prompt):
        fake_prompt(
            {
                "What language?": "Go",
                "What type of project?": "CLI",
                "Features:": [],
            }
        )

        config = ui.ask_config("  spaced  ")

        assert config.name == "spaced"


class TestCancellation:
    @pytest.mark.parametrize(
        "cancelling_prompt",
        ["Project name:", "What language?", "What type of project?", "Features:"],
    )
    def test_returns_none_when_cancelled(self, fake_prompt, cancelling_prompt):
        answers = {
            "Project name:": "demo",
            "What language?": "Python",
            "What type of project?": "CLI",
            "Features:": [],
        }
        answers[cancelling_prompt] = None

        fake_prompt(answers)

        assert ui.ask_config() is None


class TestConfirmSummary:
    def test_summary_lists_only_relevant_features(self, fake_prompt, capsys):
        fake_prompt(
            {
                "What language?": "Rust",
                "What type of project?": "CLI",
                "Features:": ["Git"],
                "Create this project?": True,
            }
        )

        config = ui.ask_config("demo")
        assert config is not None

        assert ui.confirm_config(config) is True

        out = capsys.readouterr().out
        assert "Pytest" not in out
        assert "Ruff" not in out
        assert "Git" in out

    def test_declining_returns_false(self, fake_prompt):
        fake_prompt(
            {
                "What language?": "Go",
                "What type of project?": "CLI",
                "Features:": [],
                "Create this project?": False,
            }
        )

        config = ui.ask_config("demo")
        assert config is not None

        assert ui.confirm_config(config) is False