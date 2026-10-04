# Contributing

Thanks for taking the time. This is a small project and contributions are
welcome.

## Getting set up

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Python 3.11 or newer is required.

## Before opening a pull request

```bash
ruff check .
pytest
python -m tests.check_templates
```

The last command regenerates every template into `generated/`. If your change
touches a template, build the affected project with its real toolchain so you
know it compiles and its tests pass. CI does this automatically.

## Adding a template

Create a directory at `src/polyinit/templates/<language>/<project-type>/`. No
code change is needed; the prompt and `polyinit run` pick it up from the
filesystem.

A few things to keep in mind:

- Use `{{project_name}}` and `{{package_name}}` rather than hardcoding a name.
- Include a README and at least one real test, so the template is a working
  project on its own.
- Templates ship with every feature enabled. Opting out is handled after
  rendering, so a template should not contain feature conditionals.

## Style

- Follow the surrounding code rather than a personal preference.
- Keep the dependency list small. The current runtime deps are typer, rich and
  questionary, and that restraint is deliberate.
- Public functions get type hints and a docstring explaining why they exist
  when the reason is not obvious.

## Reporting bugs

Open an issue with your polyinit version (`polyinit version`), your platform, and the
command you ran. If a generated project misbehaves, include the language and
project type, since the templates differ substantially.