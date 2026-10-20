class Element:
	"""A renderable UI node with child elements or components."""

	def __init__(self, *children, **props):
		self.children = []
		self.props = props
		self.extend(children)

	def _validate_child(self, child):
		# Import here to avoid a module-level Element <-> Component cycle.
		from .component import Component

		if not isinstance(child, (Element, Component)):
			raise TypeError("Element children must be Element or Component instances")

	def append(self, child):
		"""Add an Element or Component child and return it."""
		self._validate_child(child)
		self.children.append(child)
		return child

	def extend(self, children):
		"""Add each child from *children* after validating it."""
		for child in children:
			self.append(child)

	def walk(self):
		"""Yield leaf descendants in their declaration order.

		Nested Elements are traversed; Component children are yielded as leaves
		because rendering a component is part of its lifecycle, not traversal.
		"""
		if not self.children:
			yield self
			return

		for child in self.children:
			yield from child.walk() if isinstance(child, Element) else (child,)

	def trigger(self, event_name: str, *args, **kwargs) -> object | None:
		callback = self.props.get(f"on_{event_name}")
		if callback is None:
			return None
		if not callable(callback):
			raise TypeError(f"Event callback for {event_name!r} must be callable")
		return callback(*args, **kwargs)
