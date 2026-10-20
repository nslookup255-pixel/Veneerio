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
		self.assertNotIn("VENEERIO", output.getvalue())

	def test_new_help_describes_project_creation(self):
		output = StringIO()
		with redirect_stdout(output), self.assertRaises(SystemExit) as exit_info:
			main(["new", "-h"])

		self.assertEqual(exit_info.exception.code, 0)
		self.assertIn("usage: vnr new", output.getvalue())
		self.assertIn("project directory to create", output.getvalue())

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
				{"main.py", "README.md", "pyproject.toml", ".gitignore", "AGENTS.md", "CLAUDE.md"},
			)
			self.assertIn("my-kayat-app", (project_path / "README.md").read_text())
			self.assertIn("my-kayat-app", (project_path / "main.py").read_text())
			compile(
				(project_path / "main.py").read_text(),
				str(project_path / "main.py"),
				"exec",
			)
			project_metadata = tomllib.loads(
				(project_path / "pyproject.toml").read_text()
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
			write_file = "vnr.cli._write_project_file"
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
			replace_file = "vnr.cli.os.replace"

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
		self.assertEqual(output.getvalue().strip(), f"vnr {version('vnr')}")
		self.assertNotIn("VENEERIO", output.getvalue())

	def test_version_reports_missing_package_metadata(self):
		error_output = StringIO()
		with (
			patch("vnr.cli.version", side_effect=PackageNotFoundError("vnr")),
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
						f"vnr {version('vnr')}",
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
