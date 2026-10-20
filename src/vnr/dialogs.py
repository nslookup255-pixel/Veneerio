"""Simple browser-backed dialogs for the active Kayat window."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .window import Window


_active_window: Window | None = None


def _set_active_window(window: Window) -> None:
	global _active_window
	_active_window = window


def _clear_active_window(window: Window) -> None:
	global _active_window
	if _active_window is window:
		_active_window = None


def _require_active_window() -> Window:
	if _active_window is None:
		raise RuntimeError("Dialog requires an active Window")
	return _active_window


def alert(title: str, message: str) -> None:
	"""Show an alert in the active Kayat window."""
	return _require_active_window().alert(title, message)


def confirm(title: str, message: str) -> bool:
	"""Show a confirmation dialog and return whether it was accepted."""
	return _require_active_window().confirm(title, message)


def prompt(title: str, message: str) -> str | None:
	"""Show an input dialog and return its value, or ``None`` on cancel."""
	return _require_active_window().prompt(title, message)