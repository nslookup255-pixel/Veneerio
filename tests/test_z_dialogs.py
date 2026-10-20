import unittest

from vnr import alert, confirm, prompt
from vnr.bridge import JS
from vnr.window import Window


class RecordingWebView:
	def __init__(self, results):
		self.results = iter(results)
		self.scripts = []

	def show(self):
		return None

	def close(self):
		return None

	def evaluate_js(self, script):
		self.scripts.append(script)
		return next(self.results, None)


class DialogTest(unittest.TestCase):
	def setUp(self):
		self.window = Window("Test")
		self.webview = RecordingWebView([])
		self.window.webview = self.webview
		self.window.js = JS(self.webview)

	def tearDown(self):
		try:
			self.window.close()
		except RuntimeError:
			pass

	def test_dialogs_require_a_shown_window(self):
		with self.assertRaisesRegex(RuntimeError, "active Window"):
			alert("Title", "Message")

	def test_alert_uses_the_active_window_and_returns_none(self):
		self.window.show()

		self.assertIsNone(alert("Hello", "Welcome"))
		self.assertEqual(
			self.webview.scripts,
			['globalThis["window"]["alert"]("Hello\\n\\nWelcome")'],
		)

	def test_confirm_returns_true_or_false(self):
		self.webview.results = iter([True, False])
		self.window.show()

		self.assertTrue(confirm("Delete", "Are you sure?"))
		self.assertFalse(confirm("Delete", "Are you sure?"))

	def test_prompt_returns_text_or_none_for_cancel(self):
		self.webview.results = iter(["Kayat", None])
		self.window.show()

		self.assertEqual(prompt("Name", "What is your name?"), "Kayat")
		self.assertIsNone(prompt("Name", "What is your name?"))

	def test_dialog_arguments_must_be_strings(self):
		self.window.show()

		with self.assertRaisesRegex(TypeError, "title must be a string"):
			alert(1, "Message")
		with self.assertRaisesRegex(TypeError, "message must be a string"):
			confirm("Title", None)

	def test_invalid_webview_results_are_rejected(self):
		self.webview.results = iter(["yes", 12])
		self.window.show()

		with self.assertRaisesRegex(RuntimeError, "invalid confirmation result"):
			confirm("Title", "Message")
		with self.assertRaisesRegex(RuntimeError, "invalid prompt result"):
			prompt("Title", "Message")

	def test_closing_window_removes_it_from_public_dialog_api(self):
		self.window.show()
		self.window.close()

		with self.assertRaisesRegex(RuntimeError, "active Window"):
			prompt("Title", "Message")


if __name__ == "__main__":
	unittest.main()