from vnr import App, Component
from vnr.ui import Button, Column, Text


def greet():
    print("Hello from {{project_name}}!")


class MainView(Component):
    def render(self):
        return Column(
            Text("Welcome to {{project_name}}!"),
            Button("Say hello", on_click=greet),
        )


app = App(title="{{project_name}}")
app.mount(MainView())

if __name__ == "__main__":
    app.run()
