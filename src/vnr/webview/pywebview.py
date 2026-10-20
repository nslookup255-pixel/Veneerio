import platform
from typing import Protocol

import webview

from ..core.icon import resolve_icon_path
from .base import WebView


class _NativeWindow(Protocol):
    def evaluate_js(self, script): ...

    def destroy(self): ...


class PyWebView(WebView):
    def __init__(self, title, width, height, js_api=None, icon=None):
        self.title = title
        self.width = width
        self.height = height
        self.js_api = js_api
        self.icon = resolve_icon_path(icon) if icon is not None else None
        if self.icon is not None:
            current_platform = platform.system()
            if current_platform not in {"Windows", "Darwin", "Linux", "OpenBSD"}:
                raise RuntimeError(
                    f"Native application icons are unsupported on {current_platform or 'this platform'}"
                )
            if current_platform == "Windows" and self.icon.suffix.lower() != ".ico":
                raise ValueError("Windows native application icons require an .ico file")
        self.html = ""
        self.window: _NativeWindow | None = None
        self._started = False

    def load_html(self, html):
        self.html = html

    def evaluate_js(self, script):
        return self._require_window().evaluate_js(script)

    def _require_window(self) -> _NativeWindow:
        window = self.window
        if window is None:
            raise RuntimeError("WebView is not shown")
        return window

    def show(self):
        if self._started:
            return

        self.window = webview.create_window(
            self.title,
            html=self.html,
            width=self.width,
            height=self.height,
            js_api=self.js_api,
        )

        if self.icon is None:
            webview.start()
        else:
            webview.start(icon=str(self.icon))
        self._started = True

    def close(self):
        self._require_window().destroy()