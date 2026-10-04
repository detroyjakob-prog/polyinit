from dataclasses import dataclass


@dataclass
class ProjectConfig:
    name: str
    language: str
    project_type: str
    git: bool
    virtualenv: bool
    pytest: bool
    ruff: bool
    readme: bool
