import html

from ..core.component import Component
from ..core.element import Element
from ..core.values import to_display_text
from ..ui.button import Button
from ..ui.column import Column
from ..ui.container import Container
from ..ui.row import Row
from ..ui.text import Text


class HTMLRenderer:
	"""Render Kayat elements and components as deterministic HTML."""

	_TAGS = {
		Button: ("button", "kayat-button"),
		Column: ("div", "kayat-column"),
		Container: ("div", "kayat-container"),
		Row: ("div", "kayat-row"),
		Text: ("span", "kayat-text"),
	}
	_STYLE_PROPS = (
		("width", "width"),
		("height", "height"),
		("padding", "padding"),
		("margin", "margin"),
		("gap", "gap"),
		("alignment", "align-items"),
	)
	_DIMENSION_PROPS = {"width", "height", "padding", "margin", "gap"}

	def __init__(self, bridge=None):
		self.bridge = bridge
		self._element_counter = 0

	def set_bridge(self, bridge):
		self.bridge = bridge

	def render(self, node):
		"""Return HTML for an Element or Component tree."""
		self._element_counter = 0
		if self.bridge is not None:
			self.bridge.begin_render()
		return self._render_node(node)

	def _render_node(self, node):
		if isinstance(node, Component):
			node = node.mount()
			return self._render_node(node)
		if not isinstance(node, Element):
			raise TypeError("HTMLRenderer.render() requires an Element or Component")

		if type(node) not in self._TAGS:
			raise TypeError(f"HTMLRenderer does not support element type {type(node).__name__}")

		tag, class_name = self._TAGS[type(node)]
		attributes = [f'class="{class_name}"']
		if isinstance(node, Button) and node.props.get("on_click") is not None:
			element_id = self._next_element_id()
			attributes.extend([
				f'data-kayat-id="{element_id}"',
				'data-kayat-event="click"',
			])
			if self.bridge is not None:
				self.bridge.register_event(
					element_id, "click", node._dispatch_browser_click
				)
		style = self._style(node.props)
		if style:
			attributes.append(f'style="{html.escape(style, quote=True)}"')
		if isinstance(node, Button) and node.props.get("enabled", True) is False:
			attributes.append("disabled")

		content = self._content(node)
		return f"<{tag} {' '.join(attributes)}>{content}</{tag}>"

	def _next_element_id(self):
		self._element_counter += 1
		return f"element-{self._element_counter}"

	def _content(self, node):
		if isinstance(node, Text):
			return html.escape(to_display_text(node.value), quote=True)
		if isinstance(node, Button):
			return html.escape(to_display_text(node.label), quote=True)
		return "".join(self._render_node(child) for child in node.children)

	def _style(self, props):
		declarations = []
		if props.get("visible", True) is False:
			declarations.append("display: none")
		for prop_name, css_name in self._STYLE_PROPS:
			if prop_name not in props or props[prop_name] is None:
				continue
			value = props[prop_name]
			if prop_name in self._DIMENSION_PROPS and isinstance(value, (int, float)):
				value = f"{value}px" if value != 0 else "0"
			declarations.append(f"{css_name}: {value}")
		return "; ".join(declarations)
