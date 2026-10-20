DEFAULT_CSS = """\
*, *::before, *::after {
	box-sizing: border-box;
}

html, body {
	margin: 0;
	min-height: 100%;
}

body {
	font-family: sans-serif;
}

.kayat-column,
.kayat-row {
	display: flex;
}

.kayat-column {
	flex-direction: column;
	align-items: flex-start;
}

.kayat-row {
	flex-direction: row;
}
"""


def document_with_css(body, css=DEFAULT_CSS, script=""):
	"""Wrap rendered Kayat HTML in a document containing the base stylesheet."""
	script_markup = f"<script>{script}</script>" if script else ""
	return (
		"<!doctype html><html><head><meta charset=\"utf-8\">"
		f"<style>{css}</style>{script_markup}</head><body>{body}</body></html>"
	)
