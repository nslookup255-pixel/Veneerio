import unittest

from vnr.ui import Button, Column, Component, Element, State, Text


class Counter(Component):
	count = State(0)

	def increment(self):
		self.count += 1

	def render(self):
		return Column(Text(f"Count: {self.count}"), Button("+", on_click=self.increment))


class LifecycleComponent(Component):
	def __init__(self):
		super().__init__()
		self.calls = []

	def render(self):
		return Text("ready")

	def on_mount(self):
		self.calls.append("mount")

	def on_unmount(self):
		self.calls.append("unmount")


class ComponentTest(unittest.TestCase):
	def test_state_and_element_event(self):
		counter = Counter()
		tree = counter.mount()

		self.assertIsInstance(tree, Element)
		self.assertEqual(tree.children[0].value, "Count: 0")
		tree.children[1].click()
		self.assertEqual(counter.count, 1)

	def test_nested_component_lifecycle(self):
		child = LifecycleComponent()

		class Page(Component):
			def render(self):
				return Column(child)

		page = Page()
		page.mount()
		self.assertTrue(child.mounted)
		self.assertEqual(child.calls, ["mount"])
		page.unmount()
		self.assertEqual(child.calls, ["mount", "unmount"])

	def test_component_events_use_existing_events_system(self):
		component = LifecycleComponent()
		called = []
		component.on("ready", called.append)
		component.emit("ready", 1)
		self.assertEqual(called, [1])

	def test_render_must_return_a_ui_node(self):
		class Invalid(Component):
			def render(self):
				return "invalid"

		with self.assertRaises(TypeError):
			Invalid().mount()


if __name__ == "__main__":
	unittest.main()