import types
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


class FakeWindow:
	def __init__(self):
		self.scripts = []
		self.destroyed = False

	def evaluate_js(self, script):
		self.scripts.append(script)
		return {"script": script}

	def destroy(self):
		self.destroyed = True


class FakeWebViewModule:
	def __init__(self):
		self.window = FakeWindow()
		self.created_with = None

	def create_window(self, *args, **kwargs):
		self.created_with = (args, kwargs)
		return self.window

	def start(self, **kwargs):
		self.started_with = kwargs
		return None


from vnr.webview.pywebview import PyWebView
from vnr.bridge import Bridge
from vnr.window import PythonAPI


class PyWebViewTest(unittest.TestCase):
	def setUp(self):
		self.fake_webview = FakeWebViewModule()
		for name in ("create_window", "start"):
			patcher = patch(
				f"vnr.webview.pywebview.webview.{name}",
				side_effect=getattr(self.fake_webview, name),
			)
			patcher.start()
			self.addCleanup(patcher.stop)

	def test_show_passes_icon_to_pywebview_start(self):
		with TemporaryDirectory() as directory:
			icon = Path(directory) / "icon.ico"
			icon.write_bytes(b"\x00\x00\x01\x00\x01\x00")
			view = PyWebView("Test", 800, 600, icon=icon)
			view.load_html("<h1>Test</h1>")

			view.show()

			self.assertEqual(self.fake_webview.started_with, {"icon": str(icon.resolve())})

	def test_invalid_icon_paths_fail_clearly(self):
		with self.assertRaisesRegex(FileNotFoundError, "Icon file does not exist"):
			PyWebView("Test", 800, 600, icon="missing.ico")

		with TemporaryDirectory() as directory:
			icon = Path(directory) / "icon.txt"
			icon.write_text("not an icon")
			with self.assertRaisesRegex(ValueError, "Unsupported icon format"):
				PyWebView("Test", 800, 600, icon=icon)

	def test_path_objects_are_supported_for_icons(self):
		with TemporaryDirectory() as directory:
			icon = Path(directory) / "icon.ico"
			icon.write_bytes(b"\x00\x00\x01\x00\x01\x00")

			view = PyWebView("Test", 800, 600, icon=icon)

			self.assertEqual(view.icon, icon.resolve())

	def test_window_connects_both_communication_directions(self):
		from vnr.window import Window

		window = Window("Test")
		window.bridge.register("hello", lambda name: f"Hello, {name}!")

		self.assertIs(window.webview.js_api, window.api)
		self.assertEqual(window.api.hello("World"), "Hello, World!")
		self.assertIs(window.js._webview, window.webview)

	def test_window_load_forwards_html_to_webview(self):
		from vnr.window import Window

		window = Window("Test")
		window.webview = types.SimpleNamespace(html=None)
		window.webview.load_html = lambda html: setattr(window.webview, "html", html)

		window.load('<span class="kayat-text">Hello</span>')

		self.assertIn('<span class="kayat-text">Hello</span>', window.webview.html)
		self.assertIn('.kayat-column {', window.webview.html)
		self.assertIn('flex-direction: column;', window.webview.html)
		self.assertIn('align-items: flex-start;', window.webview.html)
		self.assertIn('flex-direction: row;', window.webview.html)

	def test_window_load_applies_base_css_without_replacing_layout_styles(self):
		from vnr.rendering import HTMLRenderer
		from vnr.ui import Column, Text
		from vnr.window import Window

		window = Window("Test")
		window.webview = types.SimpleNamespace(html=None)
		window.webview.load_html = lambda html: setattr(window.webview, "html", html)

		window.load(HTMLRenderer().render(Column(Text("Hello"), gap=12, alignment="center")))

		self.assertIn('.kayat-column {', window.webview.html)
		self.assertIn('flex-direction: column;', window.webview.html)
		self.assertIn('align-items: flex-start;', window.webview.html)
		self.assertIn('gap: 12px; align-items: center', window.webview.html)

	def test_window_load_injects_event_runtime(self):
		from vnr.window import Window

		window = Window("Test")
		window.webview = types.SimpleNamespace(html=None)
		window.webview.load_html = lambda html: setattr(window.webview, "html", html)

		window.load('<button data-kayat-id="element-1" data-kayat-event="click">Click</button>')

		self.assertIn("pywebviewready", window.webview.html)
		self.assertIn("dispatch_event", window.webview.html)

	def test_window_load_preserves_all_hello_example_children(self):
		from vnr.rendering import HTMLRenderer
		from vnr.ui import Button, Column, Text
		from vnr.window import Window

		window = Window("Test")
		window.webview = types.SimpleNamespace(html=None)
		window.webview.load_html = lambda html: setattr(window.webview, "html", html)
		tree = Column(
			Text("Welcome to Kayat!"),
			Text("This is a simple example of a Kayat app."),
			Button("Click me!"),
		)

		window.load(HTMLRenderer().render(tree))

		self.assertLess(
			window.webview.html.index("Welcome to Kayat!"),
			window.webview.html.index("This is a simple example of a Kayat app."),
		)
		self.assertLess(
			window.webview.html.index("This is a simple example of a Kayat app."),
			window.webview.html.index("Click"),
		)

	def test_registered_bridge_function_is_exposed_directly_on_js_api(self):
		bridge = Bridge()

		def hello(name):
			return f"Hello, {name}!"

		bridge.register("hello", hello)
		api = PythonAPI(bridge)

		self.assertEqual(api.hello("World"), "Hello, World!")
		self.assertIn("hello", dir(api))

	def test_show_passes_python_api_to_pywebview(self):
		api = object()
		view = PyWebView("Test", 800, 600, api)
		view.load_html("<h1>Test</h1>")

		view.show()

		args, kwargs = self.fake_webview.created_with
		self.assertEqual(args, ("Test",))
		self.assertEqual(kwargs["html"], "<h1>Test</h1>")
		self.assertEqual(kwargs["width"], 800)
		self.assertEqual(kwargs["height"], 600)
		self.assertIs(kwargs["js_api"], api)

	def test_show_does_not_start_a_second_gui_loop(self):
		view = PyWebView("Test", 800, 600)
		view.load_html("<h1>Test</h1>")

		view.show()
		view.show()

		self.assertEqual(self.fake_webview.created_with[1]["html"], "<h1>Test</h1>")

	def test_evaluate_js_and_close_delegate_to_window(self):
		view = PyWebView("Test", 800, 600)
		view.window = self.fake_webview.window

		self.assertEqual(view.evaluate_js("1 + 1"), {"script": "1 + 1"})
		view.close()

		self.assertTrue(self.fake_webview.window.destroyed)

	def test_window_operations_require_showing_the_webview(self):
		view = PyWebView("Test", 800, 600)

		with self.assertRaisesRegex(RuntimeError, "WebView is not shown"):
			view.evaluate_js("1 + 1")
		with self.assertRaisesRegex(RuntimeError, "WebView is not shown"):
			view.close()


if __name__ == "__main__":
	unittest.main()
