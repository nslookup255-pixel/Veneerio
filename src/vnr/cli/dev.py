import hashlib
import os
import signal
import stat as stat_module
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path


_WATCHED_EXTENSIONS = {".py", ".html", ".css", ".js"}
_EXCLUDED_DIRECTORIES = {
    ".eggs",
    ".conda",
    ".env",
    ".git",
    ".mypy_cache",
    ".nox",
    ".pixi",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    ".virtualenv",
    "__pycache__",
    "__pypackages__",
    "build",
    "dist",
    "env",
    "env.bak",
    "htmlcov",
    "myvenv",
    "node_modules",
    "site-packages",
    "target",
    "venv",
    "venv.bak",
    "venvs",
    "virtualenv",
}


def discover_project(project_root: Path | str) -> tuple[Path, Path]:
    root = Path(project_root).expanduser()
    try:
        root = root.resolve(strict=True)
    except FileNotFoundError as error:
        raise ValueError(f"project directory does not exist: {root}") from error
    except (OSError, RuntimeError) as error:
        raise ValueError(
            f"could not resolve project directory {root}: {error}"
        ) from error

    if not root.is_dir():
        raise ValueError(f"project path is not a directory: {root}")

    entry_point = root / "main.py"
    if not entry_point.is_file():
        raise ValueError(f"main.py not found in project directory: {root}")

    return root, entry_point.resolve()


def _raise_walk_error(error: OSError) -> None:
    raise error


class FileWatcher:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self._previous_snapshot = self._snapshot()

    def _snapshot(self) -> dict[Path, tuple[int, int, int, bytes]]:
        snapshot: dict[Path, tuple[int, int, int, bytes]] = {}
        for current, directory_names, file_names in os.walk(
            self.project_root,
            topdown=True,
            followlinks=False,
            onerror=_raise_walk_error,
        ):
            current_path = Path(current)
            directory_names[:] = [
                name
                for name in directory_names
                if name.lower() not in _EXCLUDED_DIRECTORIES
                and not (current_path / name).is_symlink()
            ]
            for file_name in file_names:
                path = current_path / file_name
                if path.suffix.lower() not in _WATCHED_EXTENSIONS:
                    continue
                if path.is_symlink():
                    try:
                        resolved_path = path.resolve(strict=True)
                    except FileNotFoundError:
                        continue
                    if not resolved_path.is_relative_to(self.project_root):
                        continue
                try:
                    file_stat = path.stat()
                except FileNotFoundError:
                    continue
                if not stat_module.S_ISREG(file_stat.st_mode):
                    continue
                digest = hashlib.blake2b(digest_size=16)
                try:
                    with path.open("rb") as source:
                        for chunk in iter(lambda: source.read(65536), b""):
                            digest.update(chunk)
                except FileNotFoundError:
                    continue
                snapshot[path.relative_to(self.project_root)] = (
                    file_stat.st_mtime_ns,
                    file_stat.st_ctime_ns,
                    file_stat.st_size,
                    digest.digest(),
                )
        return snapshot

    def has_changed(self) -> bool:
        snapshot = self._snapshot()
        changed = snapshot != self._previous_snapshot
        self._previous_snapshot = snapshot
        return changed


class ApplicationProcess:
    def __init__(
        self,
        project_root: Path,
        entry_point: Path,
        *,
        popen_factory: Callable[..., subprocess.Popen] = subprocess.Popen,
        termination_timeout: float = 2.0,
    ):
        self.project_root = project_root
        self.entry_point = entry_point
        self._popen_factory = popen_factory
        self._termination_timeout = termination_timeout
        self._process: subprocess.Popen | None = None

    def start(self) -> None:
        if self._process is not None:
            if self._process.poll() is None:
                raise RuntimeError("application process is already running")
            self._process = None

        creation_flags = (
            subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        )
        self._process = self._popen_factory(
            [sys.executable, str(self.entry_point)],
            cwd=str(self.project_root),
            shell=False,
            creationflags=creation_flags,
        )

    def poll(self) -> int | None:
        if self._process is None:
            return None

        return_code = self._process.poll()
        if return_code is not None:
            self._process = None
        return return_code

    def stop(self) -> None:
        process = self._process
        if process is None:
            return

        if process.poll() is None:
            if os.name == "nt":
                try:
                    process.send_signal(signal.CTRL_BREAK_EVENT)
                except (OSError, ValueError):
                    if process.poll() is None:
                        process.terminate()
            else:
                try:
                    process.terminate()
                except OSError:
                    if process.poll() is None:
                        raise

        try:
            process.wait(timeout=self._termination_timeout)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except OSError:
                if process.poll() is None:
                    raise
            process.wait(timeout=self._termination_timeout)
        self._process = None


def _write_error(message: str) -> None:
    print(message, file=sys.stderr)


class DevelopmentServer:
    def __init__(
        self,
        project_root: Path,
        entry_point: Path,
        *,
        watcher: FileWatcher | None = None,
        application: ApplicationProcess | None = None,
        poll_interval: float = 0.1,
        debounce_interval: float = 0.5,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
        output: Callable[[str], None] = print,
        error_output: Callable[[str], None] = _write_error,
    ):
        self.watcher = watcher or FileWatcher(project_root)
        self.application = application or ApplicationProcess(project_root, entry_point)
        self.poll_interval = poll_interval
        self.debounce_interval = debounce_interval
        self._sleep = sleep
        self._clock = clock
        self._output = output
        self._error_output = error_output

    def _start_application(self) -> None:
        try:
            self.application.start()
        except OSError as error:
            self._error_output(f"vnr dev: could not start application: {error}")

    def run(self) -> None:
        self._start_application()
        last_change: float | None = None
        reported_watch_error: str | None = None
        try:
            while True:
                try:
                    changed = self.watcher.has_changed()
                    reported_watch_error = None
                except OSError as error:
                    message = str(error)
                    if message != reported_watch_error:
                        self._error_output(
                            f"vnr dev: could not scan project files: {message}"
                        )
                        reported_watch_error = message
                    changed = False

                now = self._clock()
                if changed:
                    last_change = now
                if (
                    last_change is not None
                    and now - last_change >= self.debounce_interval
                ):
                    self.application.stop()
                    self._start_application()
                    last_change = None

                return_code = self.application.poll()
                if return_code not in (None, 0):
                    self._error_output(
                        "vnr dev: application exited with status "
                        f"{return_code}; waiting for file changes"
                    )
                self._sleep(self.poll_interval)
        except KeyboardInterrupt:
            self._output("\nStopping Veneerio development server.")
        finally:
            self.application.stop()


def run_dev(project_root: Path | str) -> None:
    root, entry_point = discover_project(project_root)
    DevelopmentServer(root, entry_point).run()
