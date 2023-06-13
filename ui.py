from textual.app import App, ComposeResult
from textual.widgets import Input


class InputApp(App):
    def compose(self) -> ComposeResult:
        self.cmd = Input(placeholder=">")
        self.cmd.action_submit = self.action_submit
        self.output = Input(placeholder="....")
        yield self.cmd
        yield self.output

    def action_submit(self):
        self.output.value = f"Hello {self.cmd.value}"

if __name__ == "__main__":
    app = InputApp()
    app.run()
