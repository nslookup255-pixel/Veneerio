import unittest

from vnr import Component
from vnr.ui import Button, Column, Container, Row, Text


class Child(Component):
	def render(self):
		return Text("child")


class UITest(unittest.TestCase):
	def test_text_stores_its_value(self):
		text = Text("Hello", visible=True)
		self.assertEqual(text.value, "Hello")
		self.assertTrue(text.props["visible"])

	def test_button_triggers_click_callback(self):
		calls = []
		button = Button("Save", on_click=lambda value: calls.append(value))
		self.assertIsNone(button.click("done"))
		self.assertEqual(calls, ["done"])

	def test_plain_function_can_be_event_handler(self):
		calls = []
		button = Button("Save")

		def handler():
			calls.append("clicked")

		button.on_click(handler)
		button.click()

		self.assertEqual(calls, ["clicked"])

	def test_zero_argument_handler(self):
		calls = []
		button = Button("Save")
		button.on_click(lambda: calls.append("clicked"))

		button.click()

		self.assertEqual(calls, ["clicked"])

	def test_event_argument_handler(self):
		event = object()
		received = []
		button = Button("Save")
		button.on_click(received.append)

		button.click(event)

		self.assertIs(received[0], event)

	def test_lambda_can_be_event_handler(self):
		calls = []
		button = Button("Save")
		button.on_click(lambda: calls.append("clicked"))

		button.click()

		self.assertEqual(calls, ["clicked"])

	def test_callable_object_can_be_event_handler(self):
		calls = []

		class Handler:
			def __call__(self):
				calls.append("clicked")

		button = Button("Save")
		button.on_click(Handler())
		button.click()

		self.assertEqual(calls, ["clicked"])

	def test_bound_method_can_be_event_handler(self):
		calls = []

		class Logic:
			def handle_click(self):
				calls.append("clicked")

		button = Button("Save")
		button.on_click(Logic().handle_click)
		button.click()

		self.assertEqual(calls, ["clicked"])

	def test_pure_python_logic_runs_from_event_handler(self):
		results = []

		def calculate_score(value):
			return value * 10

		def handler():
			results.append(calculate_score(5))

		button = Button("Score")
		button.on_click(handler)
		button.click()

		self.assertEqual(results, [50])

	def test_on_click_can_clear_handler(self):
		button = Button("Save", on_click=lambda: self.fail("handler called"))

		button.on_click(None)

		self.assertIsNone(button.click())

	def test_non_callable_handler_is_rejected_when_clicked(self):
		button = Button("Save")
		button.on_click("not callable")

		with self.assertRaisesRegex(TypeError, "must be callable"):
			button.click()

	def test_row_and_column_keep_children_in_order(self):
		first, second = Text("first"), Text("second")
		self.assertEqual(Row(first, second).children, [first, second])
		self.assertEqual(Column(first, second).children, [first, second])

	def test_container_accepts_layout_properties_and_nested_elements(self):
		tree = Container(
			Column(Row(Text("A"), Button("B"))),
			padding=20,
			margin=4,
			width=200,
		)
		self.assertEqual(tree.props, {"padding": 20, "margin": 4, "width": 200})
		self.assertEqual(
			[node.value if isinstance(node, Text) else node.label for node in tree.walk()],
			["A", "B"],
		)

	def test_elements_can_contain_components(self):
		child = Child()
		tree = Column(child)
		self.assertEqual(list(tree.walk()), [child])

	def test_invalid_children_are_rejected(self):
		with self.assertRaisesRegex(TypeError, "Element or Component"):
			Column("not a UI node")


if __name__ == "__main__":
	unittest.main()
