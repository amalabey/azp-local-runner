from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Static
from textual.widgets import Input
from rich.syntax import Syntax

CMD_INPUT_ID = "cmd-input-text"
CMD_OUTPUT_ID = "cmd-output-text"
LOG_OUTPUT_ID = "log-output-text"


class TerminalUi(App):
    CSS_PATH = "app.css"

    def __init__(self):
        super().__init__()
        self.cmd_output_text = ""
        self.log_output_text = ""

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with Container(id="left-pane"):
                with VerticalScroll(id="cmd-output-container"):
                    yield Static("......output......", id=CMD_OUTPUT_ID)
                with Container(id="cmd-input-container"):
                    with Horizontal(id="cmd-bar"):
                        yield Static(">", id="cmd-label-text")
                        cmd_input = Input(placeholder="", id=CMD_INPUT_ID)
                        cmd_input.action_submit = self.on_action_submit
                        yield cmd_input
            with VerticalScroll(id="right-pane"):
                yield Static(".......logs output.....", id=LOG_OUTPUT_ID)

    def on_mount(self) -> None:
        cmd_input = self.query_one(f"#{CMD_INPUT_ID}")
        cmd_input.focus()
        self.on_load()

    def on_action_submit(self):
        self.on_cmd()

    def on_cmd(self):
        pass

    def append_cmd_output(self, text: str):
        cmd_output = self.query_one(f"#{CMD_OUTPUT_ID}")
        self.cmd_output_text += text
        cmd_output.update(self.cmd_output_text)

    def write_cmd_output(self, text: str):
        cmd_output = self.query_one(f"#{CMD_OUTPUT_ID}")
        self.cmd_output_text = text
        cmd_output.update(self.cmd_output_text)

    def get_cmd_text(self):
        cmd_input = self.query_one(f"#{CMD_INPUT_ID}")
        return cmd_input.value

    def on_load(self):
        pass

    def render_file(self, file_path, file_type):
        with open(file_path, "rt") as code_file:
            syntax = Syntax(code_file.read(), file_type, line_numbers=True)
            log_output = self.query_one(f"#{LOG_OUTPUT_ID}")
            log_output.update(syntax)


if __name__ == "__main__":
    app = TerminalUi()
    app.run()
