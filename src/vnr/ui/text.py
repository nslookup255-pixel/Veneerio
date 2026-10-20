from ..core.element import Element


class Text(Element):
	"""A leaf element that stores a Python value for display."""

	def __init__(self, value, **props):
		super().__init__(**props)
		self.value = value
