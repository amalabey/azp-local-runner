from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Header, Static, Label
from textual.widgets import Input
from rich.syntax import Syntax
from textual.message import Message

CMD_INPUT_ID = "cmd-input-text"
CMD_OUTPUT_ID = "cmd-output-text"
LOG_OUTPUT_ID = "log-output-text"


class TerminalUi(App):
    CSS_PATH = "app.css"

    class Output(Message):
        def __init__(self, output: str) -> None:
            self.output = output
            super().__init__()

    def __init__(self):
        super().__init__()
        self.cmd_output_text = ""
        self.log_output_text = ""

    def compose(self) -> ComposeResult:
        with Header(id="app-header"):
            yield Label("Azp Local Runner", id="app-header-text")
        with Container(id="app-grid"):
            with Container(id="left-pane"):
                with Header():
                    yield Label("Console")
                with VerticalScroll(id="cmd-output-container"):
                    yield Static("", id=CMD_OUTPUT_ID)
                with Container(id="cmd-input-container"):
                    with Horizontal(id="cmd-bar"):
                        yield Label(">", id="cmd-label-text")
                        cmd_input = Input(placeholder="", id=CMD_INPUT_ID)
                        cmd_input.action_submit = self.on_action_submit
                        yield cmd_input
            with VerticalScroll(id="right-pane"):
                with Header():
                    yield Label("Output")
                yield Static("", id=LOG_OUTPUT_ID)

    async def on_mount(self) -> None:
        cmd_input = self.query_one(f"#{CMD_INPUT_ID}")
        cmd_input.focus()

    async def on_ready(self) -> None:
        self.run_worker(self.on_ui_ready, exclusive=True)

    def on_action_submit(self):
        self.on_cmd()
        cmd_input = self.query_one(f"#{CMD_INPUT_ID}")
        cmd_input.value = ""

    def on_cmd(self):
        pass

    def on_terminal_ui_output(self, message: Output) -> None:
        self.append_cmd_output(message.output)

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

    def on_ui_ready(self):
        pass

    def render_file(self, file_path, file_type):
        with open(file_path, "rt") as code_file:
            syntax = Syntax(code_file.read(), file_type, line_numbers=True)
            log_output = self.query_one(f"#{LOG_OUTPUT_ID}")
            log_output.update(syntax)


if __name__ == "__main__":
    app = TerminalUi()
    app.run()
