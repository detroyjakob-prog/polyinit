# polyinit

An interactive project generator for the terminal. One command, six languages,
sensible defaults.

```bash
pip install polyinit
polyinit create
```

## Why

Language-native scaffolders are excellent at their own language and useless at
the other five. `cargo new` cannot make you a Go service, and `npm create`
cannot make you a Rust library. polyinit gives you a single interactive flow
that spans every language you are likely to touch, with the same questions and
the same layout each time.

## Usage

### `polyinit create`

Walks you through name, language, project type and features, shows a summary to
confirm, then generates the project.

```bash
polyinit create                # ask for everything
polyinit create my-project     # skip the name prompt
```

The project type list is derived from the templates that actually ship, so
every combination you can pick is one that will generate.

### `polyinit run`

Runs the project in the current directory. It detects the language from the
files present and picks the real entry point, rather than guessing.

```bash
polyinit run              # detect language, ask for runner
polyinit run python uv    # explicit language and runner
```

```console
$ polyinit run
Running: python -m my_app.main
Hello world from my-app!
```

For a library, which has no entry point, it says so and points you at the tests
instead of failing with a stack trace.

### `polyinit templates`

Lists every language and project type that ships with the installed version.

### `polyinit doctor`

Checks your toolchain and verifies the installation. Useful when a template
needs something you have not installed.

### `polyinit version`

Prints the installed version.

## Templates

| Language    | Project types                  |
| ----------- | ------------------------------ |
| Python      | CLI, Library, Web API          |
| JavaScript  | CLI, Library, Web API          |
| TypeScript  | CLI, Library, Web API          |
| Rust        | CLI, Library, Web API          |
| Go          | CLI, Library, Web API          |
| Markdown    | Document                       |

Python projects can optionally include a virtual environment, pytest and ruff.
Selecting a feature that was skipped removes the matching config from
`pyproject.toml` too, so you never get a `[tool.pytest.ini_options]` section
pointing at a `tests/` directory that is not there.

## Adding a template

Templates live in `src/polyinit/templates/<language>/<project-type>/` and are
plain project directories. Drop one in and it appears in the prompts on the
next run, with no code change.

Files and directory names can use two placeholders:

| Placeholder         | Example input   | Result           |
| ------------------- | --------------- | ---------------- |
| `{{project_name}}`  | `my-app`        | `my-app`         |
| `{{package_name}}`  | `my-app`        | `my_app`         |

`{{package_name}}` is also substituted in directory names, so
`src/{{package_name}}/` becomes `src/my_app/`.

Templates ship with every feature enabled and are valid projects on their own.
Opting out of a feature removes it after rendering, which keeps templates
usable by hand without running polyinit.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pytest        # unit tests
ruff check .
```

To build every shipped template and confirm the set is coherent:

```bash
python -m tests.check_templates
```

This writes each template to `generated/` so you can build or run it with the
real toolchain. CI does this across Python, Node, Rust and Go.

## License

MIT. See [LICENSE](LICENSE).