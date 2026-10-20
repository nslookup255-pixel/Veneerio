def to_display_text(value):
	"""Convert a Python value to text for display in the rendered UI.

	None is displayed as an empty string. Other values use their Python string
	representation; errors from an invalid __str__ implementation are preserved.
	"""
	return "" if value is None else str(value)