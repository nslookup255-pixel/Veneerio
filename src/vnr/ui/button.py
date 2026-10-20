import inspect
from collections.abc import Callable

from ..core.element import Element


class Button(Element):
	"""A clickable leaf element."""

	def __init__(self, label, on_click: Callable[..., object] | None = None, **props):
		super().__init__(on_click=on_click, **props)
		self.label = label

	def on_click(self, handler: Callable[..., object] | None) -> None:
		"""Set or clear the Python callback invoked when this button is clicked."""
		self.props["on_click"] = handler

	def _dispatch_browser_click(
		self, event: dict[str, str] | None = None
	) -> object | None:
		handler = self.props.get("on_click")
		if handler is None:
			return None
		try:
			signature = inspect.signature(handler)
		except (TypeError, ValueError):
			return self.trigger("click", event)

		try:
			signature.bind(event)
		except TypeError:
			try:
				signature.bind()
			except TypeError:
				return self.trigger("click", event)
			return self.trigger("click")
		return self.trigger("click", event)

	def click(self, *args, **kwargs) -> object | None:
		return self.trigger("click", *args, **kwargs)
