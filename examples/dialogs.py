from vnr import App,Component,alert, confirm, prompt
from vnr.ui import Button,Column, Button


class DialogsExample(Component):
    def handle_alert(self):
        alert("Alert", "This is an alert dialog.")

    def handle_confirm(self):
        result = confirm("Confirm", "Do you want to proceed?")
        if result:
            print("User confirmed.")
        else:
            print("User canceled.")

    def handle_prompt(self):
        result = prompt("Prompt", "Please enter your name:")
        if result is not None:
            print(f"User entered: {result}")
        else:
            print("User canceled the prompt.")

    def render(self):
        return Column(
            Button("Show Alert", on_click=self.handle_alert),
            Button("Show Confirm", on_click=self.handle_confirm),
            Button("Show Prompt", on_click=self.handle_prompt),
        )

if __name__ == "__main__":
    app = App(title="Dialogs Example")
    app.mount(DialogsExample())
    app.run()