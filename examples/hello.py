from vnr import App, Component
from vnr.ui import Column, Text, Button


class Hello(Component):
    def handle_click(self):
        print("Button clicked!")

    def render(self):
        return Column(
            Text("Welcome to Veneerio!"),
            Text("This is a simple example of a Veneerio app."),
            Button("Click me!", on_click=self.handle_click),
        )

if __name__ == "__main__":
    app = App(title="Hello from Veneerio")
    app.mount(Hello())
    app.run()
