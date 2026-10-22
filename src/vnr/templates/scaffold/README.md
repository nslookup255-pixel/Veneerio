# {{project_name}}

A desktop application built with Veneerio, a Python-first GUI framework using HTML and CSS.
This starter requires Python 3.10 or newer.

## Install and run

Veneerio is currently developed from its public GitHub repository; the PyPI release is planned for v0.3.0.
Installing the Git-based dependency requires Git to be available on `PATH`.

```bash
python -m venv .venv
```

Activate the environment, then install the project and its Veneerio dependency:

```bash
# macOS/Linux
source .venv/bin/activate
python -m pip install -e .
python main.py
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1`, then run the two Python commands above.
After installation, use `vnr dev` instead of `python main.py` to automatically
restart the application when Python, HTML, CSS, or JavaScript files change.
Press Ctrl+C to stop the development server.

## Project structure

```text
{{project_name}}/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── main.py
├── pyproject.toml
└── .gitignore
```

`main.py` is the application entry point. It creates a Veneerio `App`, mounts the
root component, and runs the desktop window. The example button calls the
ordinary Python function `greet`; replace it with a function from your existing
program or pass your own function to a `Button`'s `on_click` callback.

For example, import your existing business logic in `main.py` and provide that
function as the button callback. This lets your Python logic remain independent
of the GUI.

## Links

- [Veneerio source repository](https://github.com/nslookup255-pixel/Veneerio)

Official documentation is currently being developed.

This starter does not include a test suite or lint/type-check configuration.
