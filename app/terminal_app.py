from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Static
from textual.widgets import Input

CMD_INPUT_ID = "cmd-input-text"
CMD_OUTPUT_ID = "cmd-output-text"


class TerminalApp(App):
    CSS_PATH = "app.css"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with Container(id="left-pane"):
                with VerticalScroll(id="cmd-output-container"):
                    yield Static(".......cmd output.....", id=CMD_OUTPUT_ID)
                with Container(id="cmd-input-container"):
                    cmd_input = Input(placeholder=">", id=CMD_INPUT_ID)
                    cmd_input.action_submit = self.action_submit
                    yield cmd_input
            with VerticalScroll(id="right-pane"):
                for number in range(100):
                    yield Static(f"Vertical layout, child {number}")

    def action_submit(self):
        cmd_input = self.query_one(f"#{CMD_INPUT_ID}")
        cmd_output = self.query_one(f"#{CMD_OUTPUT_ID}")
        cmd_output.update(f"cmd .... {cmd_input.value}")


if __name__ == "__main__":
    app = TerminalApp()
    app.run()
