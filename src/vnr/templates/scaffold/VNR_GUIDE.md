# Veneerio API Guide

This guide describes the application APIs provided by the installed Veneerio
package. Keep GUI code on the documented paths below; do not assume that
arbitrary HTML, CSS, JavaScript, or component properties are supported.

## Create and run an application

Define a root `Component` whose `render()` method returns a UI element, mount it
on an `App`, and run the app:

```python
from vnr import App, Component
from vnr.ui import Button, Column, Text


def greet():
    print("Hello from Python!")


class MainView(Component):
    def render(self):
        return Column(
            Text("Hello!"),
            Button("Say hello", on_click=greet),
        )


app = App(title="My application", width=800, height=600)
app.mount(MainView())

if __name__ == "__main__":
    app.run()
```

`App.mount()` takes a `Component`, not an element tree or a `content=` argument.
`App.run()` requires a root component and mounts it if needed. Unmounting the
component is not the same as closing its desktop window.

Run this generated project from its root with `vnr dev`. The command runs
`main.py`, watches Python, HTML, CSS, and JavaScript files, and restarts the
application after changes. Press Ctrl+C to stop it.

## Compose the built-in UI

Import components from `vnr.ui`: `Text`, `Button`, `Row`, `Column`, and
`Container`. Nest these in declaration order. Children must be UI elements or
components; wrap plain values in `Text`.

Supported layout properties are `width`, `height`, `padding`, `margin`, `gap`,
and `alignment`. Numeric dimensions use pixels; `alignment` maps to CSS
`align-items`. `visible=False` hides an element, and `enabled=False` disables a
button. Other arbitrary properties are not rendered.

## Connect existing Python logic

Pass an ordinary Python function or bound method as `Button`'s `on_click`
argument. A browser click calls a zero-argument handler without arguments; a
handler accepting one argument receives a dictionary with `type` and
`element_id`. You may also set or clear the callback later with
`button.on_click(handler)` or `button.on_click(None)`.

## State, dialogs, and web assets

`State` (imported from `vnr`) stores Python values on a `Component`. It does
not automatically rerender a mounted component or update the visible UI. Do
not use it as a reactive UI mechanism.

The top-level `alert(title, message)`, `confirm(title, message)`, and
`prompt(title, message)` functions use the active window. `confirm` returns a
boolean; `prompt` returns text or `None` if cancelled. Call them after the
application window is shown, such as from a button callback.

Veneerio renders built-in components to HTML and supplies its base CSS and
event runtime. There is no documented project-level API here for loading
custom HTML, CSS, JavaScript, or other assets. Do not rely on internal
rendering or bridge modules as a substitute.
