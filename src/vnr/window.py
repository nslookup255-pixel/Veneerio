from .bridge import Bridge, JS
from .dialogs import _clear_active_window, _set_active_window
from .rendering import document_with_css
from .webview.pywebview import PyWebView


class PythonAPI:
    def __init__(self, bridge):
        self._bridge = bridge

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)

        try:
            return self._bridge._functions[name]
        except KeyError as error:
            raise AttributeError(name) from error

    def __dir__(self):
        return sorted(set(super().__dir__()) | set(self._bridge._functions))

    def call(self, name, *args, **kwargs):
        return self._bridge.call(name, *args, **kwargs)

    def dispatch_event(self, element_id, event_name, *args, **kwargs):
        return self._bridge.dispatch_event(element_id, event_name, *args, **kwargs)


class Window:
    def __init__(self, title="Kayat App", width=800, height=600, icon=None):
        self.title = title
        self.width = width
        self.height = height
        self.icon = icon

        self.bridge = Bridge()
        self.api = PythonAPI(self.bridge)

        self.webview = PyWebView(
            title,
            width,
            height,
            self.api,
            icon,
        )
        self.js = JS(self.webview)

    def load_html(self, html):
        self.webview.load_html(html)

    def load(self, html):
        """Load rendered HTML into the window's WebView."""
        self.load_html(document_with_css(html, script=self.bridge.javascript_runtime()))

    def show(self):
        _set_active_window(self)
        try:
            self.webview.show()
        except Exception:
            _clear_active_window(self)
            raise

    def close(self):
        self.webview.close()
        _clear_active_window(self)

    def alert(self, title, message):
        self._validate_dialog_text(title, "title")
        self._validate_dialog_text(message, "message")
        self.js.call("window.alert", f"{title}\n\n{message}")
        return None

    def confirm(self, title, message):
        self._validate_dialog_text(title, "title")
        self._validate_dialog_text(message, "message")
        result = self.js.call("window.confirm", f"{title}\n\n{message}")
        if not isinstance(result, bool):
            raise RuntimeError("WebView returned an invalid confirmation result")
        return result

    def prompt(self, title, message):
        self._validate_dialog_text(title, "title")
        self._validate_dialog_text(message, "message")
        result = self.js.call("window.prompt", f"{title}\n\n{message}")
        if result is not None and not isinstance(result, str):
            raise RuntimeError("WebView returned an invalid prompt result")
        return result

    @staticmethod
    def _validate_dialog_text(value, name):
        if not isinstance(value, str):
            raise TypeError(f"Dialog {name} must be a string")
