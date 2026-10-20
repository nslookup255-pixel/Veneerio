import argparse
import os
import re
import sys
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files
from pathlib import Path
from tempfile import TemporaryDirectory


_PROJECT_NAME_PATTERN = re.compile(
    r"[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?"
)
_TEMPLATE_FILES = (
    "main.py",
    "README.md",
    "pyproject.toml",
    ".gitignore",
    "AGENTS.md",
    "CLAUDE.md",
)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vnr",
        description="A Python-first desktop GUI framework powered by HTML and CSS.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="show the installed Veneerio version and exit",
    )
    subparsers = parser.add_subparsers(dest="command")
    new_parser = subparsers.add_parser("new", help="create a new Veneerio project")
    new_parser.add_argument(
        "path",
        type=Path,
        help="project directory to create",
    )
    return parser


def _render_template(filename: str, project_name: str) -> str:
    template = (
        files("vnr")
        .joinpath("templates", "scaffold", filename)
        .read_text(encoding="utf-8")
    )
    return template.replace("{{project_name}}", project_name)


def _write_project_file(directory: Path, filename: str, content: str) -> None:
    (directory / filename).write_text(content, encoding="utf-8")


def create_project(path: Path) -> Path:
    project_name = path.name
    if not project_name or not _PROJECT_NAME_PATTERN.fullmatch(project_name):
        raise ValueError(
            "project directory name must start with a letter or number and "
            "contain only letters, numbers, '.', '_' or '-'"
        )

    destination = Path(os.path.abspath(path.expanduser()))
    if os.path.lexists(destination):
        raise FileExistsError(f"target already exists: {destination}")
    if not destination.parent.is_dir():
        raise FileNotFoundError(
            f"parent directory does not exist: {destination.parent}"
        )

    with TemporaryDirectory(prefix=".vnr-", dir=destination.parent) as temporary:
        staging_directory = Path(temporary)
        for filename in _TEMPLATE_FILES:
            _write_project_file(
                staging_directory,
                filename,
                _render_template(filename, project_name),
            )

        destination.mkdir()
        created_files: list[Path] = []
        try:
            for filename in _TEMPLATE_FILES:
                staged_file = staging_directory / filename
                project_file = destination / filename
                os.replace(staged_file, project_file)
                created_files.append(project_file)
        except Exception:
            for project_file in created_files:
                project_file.unlink()
            destination.rmdir()
            raise

    return destination


def print_header() -> None:
    print("VENEERIO")
    print("Python GUI Framework")


def main(argv: Sequence[str] | None = None) -> None:
    parser = create_parser()
    arguments = sys.argv[1:] if argv is None else argv
    options = parser.parse_args(arguments)
    if options.version:
        try:
            installed_version = version("vnr")
        except PackageNotFoundError:
            parser.error("could not determine the installed Veneerio version")
        print(f"{parser.prog} {installed_version}")
        parser.exit()
    if not arguments:
        print_header()
        return
    if options.command == "new":
        try:
            project_path = create_project(options.path)
        except ValueError as error:
            parser.error(str(error))
        except OSError as error:
            parser.error(f"could not create project: {error}")

        print(f"Created Veneerio project at {project_path}")
        print("Next steps:")
        print(f"  cd {options.path}")
        print("  python -m venv .venv")
        print("  python -m pip install -e .")
        print("  python main.py")
