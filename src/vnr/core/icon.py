from __future__ import annotations

import os
from pathlib import Path

# SUPPORTED_ICON_FORMATS = (".ico", ".png", ".jpg", ".jpeg")
# ↑ Currently, only .ico files are supported for native application icons. Other formats may be supported in the future, but for now, we will restrict to .ico files to ensure compatibility across platforms.
SUPPORTED_ICON_FORMATS = (".ico")


def resolve_icon_path(icon: str | os.PathLike[str]) -> Path:
	if not isinstance(icon, (str, os.PathLike)):
		raise TypeError("icon must be a path-like string")

	path = Path(icon).expanduser()
	if not path.is_absolute():
		path = Path.cwd() / path
	path = path.resolve()

	if not path.exists():
		raise FileNotFoundError(f"Icon file does not exist: {path}")
	if not path.is_file():
		raise ValueError(f"Icon path is not a file: {path}")

	suffix = path.suffix.lower()
	if suffix not in SUPPORTED_ICON_FORMATS:
		display_suffix = path.suffix or "<none>"
		raise ValueError(
			f"Unsupported icon format '{display_suffix}'. "
			f"Supported formats: {SUPPORTED_ICON_FORMATS}"
		)

	header = path.read_bytes()[:32]
	valid = {
		".ico": len(header) >= 6 and header[:4] == b"\x00\x00\x01\x00" and header[4:6] != b"\x00\x00",
		".png": header.startswith(b"\x89PNG\r\n\x1a\n"),
		".jpg": header.startswith(b"\xff\xd8\xff"),
		".jpeg": header.startswith(b"\xff\xd8\xff"),
	}[suffix]
	if not valid:
		raise ValueError(f"Invalid {suffix} icon file: {path}")

	return path