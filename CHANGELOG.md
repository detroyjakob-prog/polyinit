# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Renamed from `pinit` to `polyinit`. The name `pinit` is already taken on PyPI
  by an unrelated Linux shortcut tool that installs the same `pinit` console
  script, so publishing under it would have been a direct conflict.

## [0.3.0]

### Added

- Per-language project types. The prompt now offers only the combinations that
  ship as templates, instead of failing after the fact on selections like
  Python / Document.
- Optional features now do something. Selecting Pytest, Ruff or README creates
  the corresponding files and config; deselecting them removes the matching
  config from `pyproject.toml` rather than leaving it dangling.
- `polyinit run` detects the language from the project files and resolves the real
  entry point, so libraries report that they have nothing to run instead of
  failing on a missing module. Node package managers, `uv` and a project
  virtualenv each produce genuinely different commands.
- `polyinit doctor` covers Go, TypeScript, `uv`, `bun`, `yarn` and `pnpm`, and
  compiles modules in memory instead of writing bytecode into the install.
- Test suite covering template discovery, feature support, rendering, the
  config edits and language detection.
- CI that tests on Linux, macOS and Windows, builds the distributions, checks
  the wheel contains the templates, and builds every generated project.
- MIT license, contributing guide and changelog.

### Fixed

- `pytest` no longer fails at collection on a fresh checkout. It was walking
  into the template fixtures, which contain unrendered `{{package_name}}`
  placeholders and are not valid Python.
- Templates no longer ship stray `__pycache__` directories in the wheel.
- Empty `require ()` blocks removed from the Go module templates.
- Removed unused imports and dead code, and the mid-file imports and
  `shell=True` usage in the runner.

[Unreleased]: https://github.com/jacob/polyinit/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/jacob/polyinit/releases/tag/v0.3.0