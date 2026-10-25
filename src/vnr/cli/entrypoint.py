import argparse
import json
import sys
from collections.abc import Sequence
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .dev import run_dev
from .new import create_project
from .state_dump import StateDumpError, create_state_dump


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
    subparsers.add_parser(
        "dev",
        help="run and restart the current project on changes",
        description="Run main.py and restart it when project files change.",
    )
    dump_parser = subparsers.add_parser(
        "dump",
        help="export application state as JSON",
        description="Inspect the App declared in main.py and export its component and state tree.",
    )
    dump_parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write JSON to this file instead of standard output",
    )
    return parser


def print_header() -> None:
    print("VENEERIO")
    print("Python GUI Framework")


def main(argv: Sequence[str] | None = None) -> None:
    parser = create_parser()
    arguments = sys.argv[1:] if argv is None else argv
    options = parser.parse_args(arguments)
    if options.version:
        try:
            installed_version = version("Veneerio")
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
    elif options.command == "dev":
        try:
            run_dev(Path.cwd())
        except (ValueError, OSError) as error:
            parser.error(str(error))
    elif options.command == "dump":
        try:
            state = create_state_dump(Path.cwd())
            output = json.dumps(state, indent=2, sort_keys=True, allow_nan=False)
        except StateDumpError as error:
            parser.error(str(error))
        except (TypeError, ValueError) as error:
            parser.error(f"could not serialize application state: {error}")

        if options.output is None:
            try:
                sys.stdout.write(f"{output}\n")
            except OSError as error:
                parser.error(f"could not write state dump to standard output: {error}")
        else:
            output_path = options.output.expanduser()
            try:
                output_path.write_text(f"{output}\n", encoding="utf-8")
            except OSError as error:
                parser.error(f"could not write state dump to {output_path}: {error}")
