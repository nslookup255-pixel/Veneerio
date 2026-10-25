import json
import os
import subprocess
import sys
import sysconfig
import unittest
from contextlib import redirect_stderr, redirect_stdout
from importlib.metadata import PackageNotFoundError, version
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

try:
	import tomllib
except ModuleNotFoundError:
	from setuptools._vendor import tomli as tomllib

from vnr.cli import create_project, main


class CLITest(unittest.TestCase):
	def test_existing_top_level_package_exports_are_available(self):
		import vnr

		for name in vnr.__all__:
			with self.subTest(name=name):
				self.assertIsNotNone(getattr(vnr, name))

	def test_help_shows_usage_description_and_supported_options(self):
		output = StringIO()
		with redirect_stdout(output), self.assertRaises(SystemExit) as exit_info:
			main(["--help"])

		self.assertEqual(exit_info.exception.code, 0)
		self.assertIn("usage: vnr", output.getvalue())
		self.assertIn("Python-first desktop GUI framework", output.getvalue())
		self.assertIn("--help", output.getvalue())
		self.assertIn("--version", output.getvalue())
		self.assertIn("dump", output.getvalue())
		self.assertNotIn("VENEERIO", output.getvalue())

	def test_new_help_describes_project_creation(self):
		output = StringIO()
		with redirect_stdout(output), self.assertRaises(SystemExit) as exit_info:
			main(["new", "-h"])

		self.assertEqual(exit_info.exception.code, 0)
		self.assertIn("usage: vnr new", output.getvalue())
		self.assertIn("project directory to create", output.getvalue())

	def test_dev_help_describes_development_server(self):
		output = StringIO()
		with redirect_stdout(output), self.assertRaises(SystemExit) as exit_info:
			main(["dev", "-h"])

		self.assertEqual(exit_info.exception.code, 0)
		self.assertIn("usage: vnr dev", output.getvalue())
		self.assertIn("restart it when project files change", output.getvalue())

	def test_dev_runs_the_current_working_directory(self):
		with patch("vnr.cli.entrypoint.Path.cwd", return_value=Path("project")) as cwd:
			with patch("vnr.cli.entrypoint.run_dev") as run_dev:
				main(["dev"])

		cwd.assert_called_once_with()
		run_dev.assert_called_once_with(Path("project"))

	def test_dev_reports_invalid_project_without_traceback(self):
		error_output = StringIO()
		with (
			patch("vnr.cli.entrypoint.run_dev", side_effect=ValueError("main.py is missing")),
			redirect_stderr(error_output),
			self.assertRaises(SystemExit) as exit_info,
		):
			main(["dev"])

		self.assertEqual(exit_info.exception.code, 2)
		self.assertIn("main.py is missing", error_output.getvalue())
		self.assertNotIn("Traceback", error_output.getvalue())

	def test_dump_prints_application_state_as_json_without_running_main_block(self):
		with TemporaryDirectory() as directory:
			project = Path(directory)
			(project / "main.py").write_text(
				"from vnr import App, Component, State\n"
				"from vnr.ui import Text\n"
				"class Root(Component):\n"
				"    count = State(3)\n"
				"    def render(self):\n"
				"        return Text(str(self.count))\n"
				"app = App(title='Inspect me')\n"
				"app.mount(Root())\n"
				"if __name__ == '__main__':\n"
				"    raise RuntimeError('window must not start')\n",
				encoding="utf-8",
			)
			output = StringIO()
			with patch("vnr.cli.entrypoint.Path.cwd", return_value=project):
				with redirect_stdout(output):
					main(["dump"])

		dump = json.loads(output.getvalue())
		self.assertEqual(dump["application"]["title"], "Inspect me")
		self.assertEqual(dump["root"]["state"], {"count": 3})

	def test_dump_writes_json_to_output_file(self):
		with TemporaryDirectory() as directory:
			project = Path(directory)
			(project / "main.py").write_text(
				"from vnr import App, Component\n"
				"from vnr.ui import Text\n"
				"class Root(Component):\n"
				"    def render(self):\n"
				"        return Text('ready')\n"
				"app = App()\n"
				"app.mount(Root())\n",
				encoding="utf-8",
			)
			output_path = project / "state.json"
			with patch("vnr.cli.entrypoint.Path.cwd", return_value=project):
				main(["dump", "--output", str(output_path)])

			dump = json.loads(output_path.read_text(encoding="utf-8"))
			self.assertEqual(dump["schema_version"], 1)

	def test_dump_reports_output_file_errors(self):
		with TemporaryDirectory() as directory:
			project = Path(directory)
			(project / "main.py").write_text(
				"from vnr import App, Component\n"
				"from vnr.ui import Text\n"
				"class Root(Component):\n"
				"    def render(self):\n"
				"        return Text('ready')\n"
				"app = App()\n"
				"app.mount(Root())\n",
				encoding="utf-8",
			)
			error_output = StringIO()
			with (
				patch("vnr.cli.entrypoint.Path.cwd", return_value=project),
				redirect_stderr(error_output),
				self.assertRaises(SystemExit) as exit_info,
			):
				main(["dump", "--output", str(project / "missing" / "state.json")])

		self.assertEqual(exit_info.exception.code, 2)
		self.assertIn("could not write state dump", error_output.getvalue())
		self.assertNotIn("Traceback", error_output.getvalue())

	def test_dump_reports_application_errors_without_traceback(self):
		with TemporaryDirectory() as directory:
			project = Path(directory)
			(project / "main.py").write_text("value = 1\n", encoding="utf-8")
			error_output = StringIO()
			with (
				patch("vnr.cli.entrypoint.Path.cwd", return_value=project),
				redirect_stderr(error_output),
				self.assertRaises(SystemExit) as exit_info,
			):
				main(["dump"])

		self.assertEqual(exit_info.exception.code, 2)
		self.assertIn("no App instance found", error_output.getvalue())
		self.assertNotIn("Traceback", error_output.getvalue())

	def test_new_without_path_reports_usage_error(self):
		error_output = StringIO()
		with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_info:
			main(["new"])

		self.assertEqual(exit_info.exception.code, 2)
		self.assertIn("the following arguments are required: path", error_output.getvalue())

	def test_new_creates_project_files_and_uses_project_name(self):
		with TemporaryDirectory() as directory:
			output = StringIO()
			project_path = Path(directory) / "my-kayat-app"
			with redirect_stdout(output):
				main(["new", str(project_path)])

			self.assertEqual(
				{path.name for path in project_path.iterdir()},
				{
					"main.py",
					"README.md",
					"VNR_GUIDE.md",
					"pyproject.toml",
					".gitignore",
					"AGENTS.md",
					"CLAUDE.md",
				},
			)
			self.assertIn(
				"my-kayat-app",
				(project_path / "README.md").read_text(encoding="utf-8"),
			)
			self.assertIn(
				"my-kayat-app",
				(project_path / "main.py").read_text(encoding="utf-8"),
			)
			guide = (project_path / "VNR_GUIDE.md").read_text(encoding="utf-8")
			self.assertIn("automatically rerender", guide)
			self.assertIn(
				"Read `VNR_GUIDE.md`",
				(project_path / "AGENTS.md").read_text(encoding="utf-8"),
			)
			compile(
				(project_path / "main.py").read_text(encoding="utf-8"),
				str(project_path / "main.py"),
				"exec",
			)
			project_metadata = tomllib.loads(
				(project_path / "pyproject.toml").read_text(encoding="utf-8")
			)
			self.assertEqual(project_metadata["project"]["name"], "my-kayat-app")
			self.assertEqual(project_metadata["project"]["requires-python"], ">=3.10")
			self.assertEqual(
				project_metadata["project"]["dependencies"],
				["vnr @ git+https://github.com/nslookup255-pixel/Veneerio.git"],
			)
			self.assertIn(str(project_path), output.getvalue())
			self.assertIn("python main.py", output.getvalue())

	def test_new_does_not_modify_existing_directory_or_file(self):
		with TemporaryDirectory() as directory:
			existing_directory = Path(directory) / "existing"
			existing_directory.mkdir()
			existing_file = existing_directory / "keep.txt"
			existing_file.write_text("keep this data")

			for target in (existing_directory, existing_file):
				with self.subTest(target=target):
					error_output = StringIO()
					with (
						redirect_stderr(error_output),
						self.assertRaises(SystemExit) as exit_info,
					):
						main(["new", str(target)])
					self.assertEqual(exit_info.exception.code, 2)
					self.assertIn("target already exists", error_output.getvalue())

			self.assertEqual(existing_file.read_text(), "keep this data")
			self.assertEqual(list(existing_directory.iterdir()), [existing_file])

	def test_new_rejects_invalid_project_name_and_missing_parent(self):
		with TemporaryDirectory() as directory:
			error_output = StringIO()
			with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_info:
				main(["new", str(Path(directory) / "bad$name")])
			self.assertEqual(exit_info.exception.code, 2)
			self.assertIn("project directory name", error_output.getvalue())

			error_output = StringIO()
			with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_info:
				main(["new", str(Path(directory) / "missing" / "app")])
			self.assertEqual(exit_info.exception.code, 2)
			self.assertIn("parent directory does not exist", error_output.getvalue())

	def test_project_creation_failure_cleans_staging_and_partial_destination(self):
		with TemporaryDirectory() as directory:
			project_path = Path(directory) / "failed-app"
			write_file = "vnr.cli.new._write_project_file"
			error_output = StringIO()
			with patch(write_file, side_effect=OSError("simulated write failure")):
				with (
					redirect_stderr(error_output),
					self.assertRaises(SystemExit) as exit_info,
				):
					main(["new", str(project_path)])

			self.assertEqual(exit_info.exception.code, 2)
			self.assertIn("simulated write failure", error_output.getvalue())
			self.assertFalse(project_path.exists())
			self.assertEqual(list(Path(directory).iterdir()), [])

	def test_project_publish_failure_removes_created_files_and_directory(self):
		with TemporaryDirectory() as directory:
			project_path = Path(directory) / "failed-app"
			replace_file = "vnr.cli.new.os.replace"

			real_replace = os.replace
			call_count = 0

			def fail_after_first_publish(source, destination):
				nonlocal call_count
				call_count += 1
				if call_count == 2:
					raise OSError("simulated publish failure")
				real_replace(source, destination)

			with patch(replace_file, side_effect=fail_after_first_publish):
				with self.assertRaisesRegex(OSError, "simulated publish failure"):
					create_project(project_path)

			self.assertFalse(project_path.exists())
			self.assertEqual(list(Path(directory).iterdir()), [])

	def test_version_matches_installed_package_metadata(self):
		output = StringIO()
		with redirect_stdout(output), self.assertRaises(SystemExit) as exit_info:
			main(["--version"])

		self.assertEqual(exit_info.exception.code, 0)
		self.assertEqual(output.getvalue().strip(), f"vnr {version('Veneerio')}")
		self.assertNotIn("VENEERIO", output.getvalue())

	def test_version_reports_missing_package_metadata(self):
		error_output = StringIO()
		with (
			patch("vnr.cli.entrypoint.version", side_effect=PackageNotFoundError("Veneerio")),
			redirect_stderr(error_output),
			self.assertRaises(SystemExit) as exit_info,
		):
			main(["--version"])

		self.assertEqual(exit_info.exception.code, 2)
		self.assertIn("could not determine the installed Veneerio version", error_output.getvalue())

	def test_no_arguments_prints_brand_header(self):
		output = StringIO()
		with redirect_stdout(output):
			main([])

		self.assertEqual(output.getvalue(), "VENEERIO\nPython GUI Framework\n")

	def test_options_do_not_import_gui_modules(self):
		for option in ("--help", "--version"):
			with self.subTest(option=option):
				code = (
					"import sys\n"
					"from vnr.cli import main\n"
					"try:\n"
					f"    main([{option!r}])\n"
					"except SystemExit as error:\n"
					"    if error.code != 0:\n"
					"        raise\n"
					"assert not any(name == 'webview' or "
					"name.startswith('vnr.webview') or name == 'vnr.window' "
					"for name in sys.modules)\n"
				)
				result = subprocess.run(
					[sys.executable, "-c", code],
					capture_output=True,
					text=True,
					check=False,
				)

				self.assertEqual(result.returncode, 0, result.stderr)

	def test_installed_console_script_handles_help_and_version(self):
		script_name = "vnr.exe" if os.name == "nt" else "vnr"
		script = Path(sysconfig.get_path("scripts")) / script_name
		self.assertTrue(script.is_file(), f"Console script not found: {script}")

		for option in ("--help", "--version"):
			with self.subTest(option=option):
				result = subprocess.run(
					[str(script), option],
					capture_output=True,
					text=True,
					check=False,
				)
				self.assertEqual(result.returncode, 0, result.stderr)
				if option == "--help":
					self.assertIn("usage: vnr", result.stdout)
					self.assertNotIn("VENEERIO", result.stdout)
				else:
					self.assertEqual(
						result.stdout.strip(),
						f"vnr {version('Veneerio')}",
					)
					self.assertNotIn("Python GUI Framework", result.stdout)

	def test_installed_console_script_supports_new_help(self):
		script_name = "vnr.exe" if os.name == "nt" else "vnr"
		script = Path(sysconfig.get_path("scripts")) / script_name
		for help_option in ("-h", "--help"):
			with self.subTest(help_option=help_option):
				result = subprocess.run(
					[str(script), "new", help_option],
					capture_output=True,
					text=True,
					check=False,
				)

				self.assertEqual(result.returncode, 0, result.stderr)
				self.assertIn("usage: vnr new", result.stdout)

	def test_installed_console_script_shows_header_without_arguments(self):
		script_name = "vnr.exe" if os.name == "nt" else "vnr"
		script = Path(sysconfig.get_path("scripts")) / script_name
		result = subprocess.run(
			[str(script)],
			capture_output=True,
			text=True,
			check=False,
		)

		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertEqual(result.stdout, "VENEERIO\nPython GUI Framework\n")


if __name__ == "__main__":
	unittest.main()
