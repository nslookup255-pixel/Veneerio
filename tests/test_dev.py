import os
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, call, patch

from vnr.dev import (
    ApplicationProcess,
    DevelopmentServer,
    FileWatcher,
    discover_project,
)


class ProjectDiscoveryTest(unittest.TestCase):
    def test_discovers_project_and_resolves_entry_point(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            entry_point = project / "main.py"
            entry_point.write_text("pass\n")

            self.assertEqual(
                discover_project(project),
                (project.resolve(), entry_point.resolve()),
            )

    def test_rejects_missing_or_invalid_project_and_entry_point(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            with self.assertRaisesRegex(ValueError, "main.py not found"):
                discover_project(project)

            entry_point = project / "main.py"
            entry_point.mkdir()
            with self.assertRaisesRegex(ValueError, "main.py not found"):
                discover_project(project)

            non_directory = project / "not-a-directory"
            non_directory.write_text("content")
            with self.assertRaisesRegex(
                ValueError,
                "project path is not a directory",
            ):
                discover_project(non_directory)

        with self.assertRaisesRegex(ValueError, "project directory does not exist"):
            discover_project(Path(directory) / "missing")


class FileWatcherTest(unittest.TestCase):
    def test_filters_extensions_and_excluded_directories(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "src").mkdir()
            (project / ".git").mkdir()
            (project / "build").mkdir()
            (project / ".venv").mkdir()
            (project / "src" / "main.py").write_text("pass\n")
            (project / ".git" / "ignored.py").write_text("pass\n")
            (project / "build" / "ignored.html").write_text("<p>build</p>")
            (project / ".venv" / "ignored.js").write_text("ignored")
            watcher = FileWatcher(project)

            (project / "notes.txt").write_text("ignored")
            (project / ".git" / "ignored.py").write_text("changed\n")
            (project / "build" / "ignored.html").write_text("<p>changed</p>")
            (project / ".venv" / "ignored.js").write_text("changed")
            self.assertFalse(watcher.has_changed())

            (project / "src" / "view.css").write_text("body {}")
            self.assertTrue(watcher.has_changed())

    def test_detects_file_creation_modification_and_deletion(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            watcher = FileWatcher(project)
            source = project / "main.py"

            source.write_text("x = 1\n")
            self.assertTrue(watcher.has_changed())
            self.assertFalse(watcher.has_changed())

            source.write_text("x = 2\n")
            self.assertTrue(watcher.has_changed())
            source.unlink()
            self.assertTrue(watcher.has_changed())


class ApplicationProcessTest(unittest.TestCase):
    def setUp(self):
        self.project_root = Path("project").resolve()
        self.entry_point = self.project_root / "main.py"

    def test_uses_current_interpreter_entry_point_and_project_working_directory(self):
        process = Mock()
        popen = Mock(return_value=process)
        manager = ApplicationProcess(
            self.project_root,
            self.entry_point,
            popen_factory=popen,
        )

        with patch("vnr.dev.sys.executable", "python-test"):
            manager.start()

        popen.assert_called_once_with(
            ["python-test", str(self.entry_point)],
            cwd=str(self.project_root),
            shell=False,
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            ),
        )

    def test_stops_gracefully_before_replacement_and_escalates_when_needed(self):
        process = Mock()
        process.poll.return_value = None
        process.wait.return_value = 0
        manager = ApplicationProcess(
            self.project_root,
            self.entry_point,
            popen_factory=Mock(return_value=process),
        )

        manager.start()
        manager.stop()

        if os.name == "nt":
            process.send_signal.assert_called_once_with(signal.CTRL_BREAK_EVENT)
            process.terminate.assert_not_called()
        else:
            process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=2.0)
        self.assertIsNone(manager._process)

        process = Mock()
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("main.py", 2.0), 0]
        manager = ApplicationProcess(
            self.project_root,
            self.entry_point,
            popen_factory=Mock(return_value=process),
        )
        manager.start()
        manager.stop()

        if os.name == "nt":
            process.send_signal.assert_called_once_with(signal.CTRL_BREAK_EVENT)
            process.terminate.assert_not_called()
        else:
            process.terminate.assert_called_once_with()
        process.kill.assert_called_once_with()
        self.assertEqual(process.wait.call_count, 2)
        self.assertEqual(
            process.wait.call_args_list,
            [
                call(timeout=2.0),
                call(timeout=2.0),
            ],
        )
        self.assertIsNone(manager._process)

    def test_real_child_process_runs_from_project_directory(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            marker = project / "started.txt"
            entry_point = project / "main.py"
            entry_point.write_text(
                "from pathlib import Path\n"
                "Path('started.txt').write_text('started')\n"
            )
            manager = ApplicationProcess(project, entry_point)

            manager.start()
            process = manager._process
            self.assertIsNotNone(process)
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(marker.read_text(), "started")
            manager.poll()

    @unittest.skipUnless(os.name == "nt", "Windows process-group behavior")
    def test_windows_child_handles_graceful_shutdown_signal(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            ready = project / "ready.txt"
            stopped = project / "stopped.txt"
            entry_point = project / "main.py"
            entry_point.write_text(
                "import signal\n"
                "import time\n"
                "from pathlib import Path\n"
                "\n"
                "def stop(signum, frame):\n"
                "    Path('stopped.txt').write_text('stopped')\n"
                "    raise SystemExit(0)\n"
                "\n"
                "signal.signal(signal.SIGBREAK, stop)\n"
                "Path('ready.txt').write_text('ready')\n"
                "while True:\n"
                "    time.sleep(0.05)\n"
            )
            manager = ApplicationProcess(project, entry_point)

            manager.start()
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(ready.exists(), "child did not become ready")

                manager.stop()

                self.assertEqual(stopped.read_text(), "stopped")
            finally:
                manager.stop()


class _FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = 0

    def sleep(self, duration):
        self.now += duration
        self.sleeps += 1
        if self.sleeps >= 14:
            raise KeyboardInterrupt


class _ScriptedWatcher:
    def __init__(self, changes):
        self.changes = iter(changes)

    def has_changed(self):
        return next(self.changes, False)


class _FakeApplication:
    def __init__(self, events, exit_codes=()):
        self.events = events
        self.running = False
        self.exit_codes = iter(exit_codes)

    def start(self):
        self.events.append("start")
        self.running = True

    def stop(self):
        if self.running:
            self.events.append("stop")
            self.running = False

    def poll(self):
        if not self.running:
            return None

        return_code = next(self.exit_codes, None)
        if return_code is not None:
            self.running = False
        return return_code


class DevelopmentServerTest(unittest.TestCase):
    def run_server(self, watcher, application, *, start_error=None):
        clock = _FakeClock()
        errors = []
        events = application.events
        if start_error is not None:
            original_start = application.start
            attempts = 0

            def start():
                nonlocal attempts
                attempts += 1
                events.append("start-attempt")
                if attempts == 1:
                    raise start_error
                original_start()

            application.start = start

        server = DevelopmentServer(
            Path("project"),
            Path("project/main.py"),
            watcher=watcher,
            application=application,
            sleep=clock.sleep,
            clock=lambda: clock.now,
            output=lambda message: events.append(message),
            error_output=errors.append,
        )
        server.run()
        return events, errors

    def test_debounces_burst_and_stops_before_restarting(self):
        events = []
        application = _FakeApplication(events)
        changes = [False, True, True, False, False, False, False, False]

        events, errors = self.run_server(
            _ScriptedWatcher(changes),
            application,
        )

        self.assertEqual(events.count("start"), 2)
        self.assertEqual(events.count("stop"), 2)
        self.assertEqual(errors, [])
        lifecycle = [event for event in events if event in {"start", "stop"}]
        self.assertEqual(lifecycle, ["start", "stop", "start", "stop"])

    def test_startup_failure_and_nonzero_exit_recover_after_file_change(self):
        events = []
        application = _FakeApplication(events, exit_codes=[7])
        changes = [
            True,
            False,
            False,
            False,
            False,
            False,
            True,
        ]

        events, errors = self.run_server(
            _ScriptedWatcher(changes),
            application,
            start_error=OSError("simulated startup failure"),
        )

        self.assertTrue(any("could not start application" in error for error in errors))
        self.assertTrue(any("exited with status 7" in error for error in errors))
        self.assertEqual(events.count("start"), 2)
        self.assertIn("stop", events)


if __name__ == "__main__":
    unittest.main()
