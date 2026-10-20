from collections.abc import Callable

from .element import Element
from .events import Events
from .state import State


class Component:
	"""Reusable UI and logic unit that renders an element/component tree."""

	def __init__(self):
		self._state = State()
		self._events = Events()
		self._mounted = False
		self._rendered = None

	@property
	def mounted(self):
		return self._mounted

	@property
	def element(self):
		return self._rendered

	@property
	def state(self):
		return self._state

	def render(self):
		raise NotImplementedError

	def mount(self):
		if self._mounted:
			return self._rendered
		rendered = self.render()
		if not isinstance(rendered, (Element, Component)):
			raise TypeError("Component.render() must return an Element or Component")
		self._rendered = rendered
		self._mounted = True
		self._mount_children(self._rendered)
		self.on_mount()
		return self._rendered

	def unmount(self):
		if not self._mounted:
			return
		self.on_unmount()
		self._unmount_children(self._rendered)
		self._rendered = None
		self._mounted = False

	def on_mount(self):
		pass

	def on_unmount(self):
		pass

	def on(self, event_name: str, listener: Callable[..., object]) -> None:
		self._events.on(event_name, listener)

	def off(self, event_name: str, listener: Callable[..., object]) -> None:
		self._events.off(event_name, listener)

	def emit(self, event_name: str, *args, **kwargs) -> None:
		self._events.emit(event_name, *args, **kwargs)

	def _mount_children(self, node):
		if isinstance(node, Component):
			node.mount()
		elif isinstance(node, Element):
			for child in node.children:
				self._mount_children(child)

	def _unmount_children(self, node):
		if isinstance(node, Component):
			node.unmount()
		elif isinstance(node, Element):
			for child in node.children:
				self._unmount_children(child)
