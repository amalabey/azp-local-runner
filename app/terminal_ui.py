from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Header, Label, TextLog
from textual.widgets import Input
from rich.syntax import Syntax
from textual.message import Message

CMD_INPUT_ID = "cmd-input-text"
CMD_OUTPUT_ID = "cmd-output-text"
LOG_OUTPUT_ID = "log-output-text"
LOG_OUTPUT_CONTAINER = "log_output_container"


class TerminalUi(App):
    CSS_PATH = "app.css"

    class ConsoleMessage(Message):
        def __init__(self, output: str) -> None:
            self.output = output
            super().__init__()

    class LogMessage(Message):
        def __init__(self, output: str) -> None:
            self.output = output
            super().__init__()

    def on_console_message(self, message: ConsoleMessage) -> None:
        self.append_cmd_output(message.output)

    def on_log_message(self, message: LogMessage) -> None:
        self.append_log_output(message.output)

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
                yield TextLog(id=CMD_OUTPUT_ID, highlight=True, markup=False)
                with Container(id="cmd-input-container"):
                    with Horizontal(id="cmd-bar"):
                        yield Label(">", id="cmd-label-text")
                        cmd_input = Input(placeholder="", id=CMD_INPUT_ID)
                        cmd_input.action_submit = self.on_action_submit
                        yield cmd_input
            with Container(id=LOG_OUTPUT_CONTAINER):
                with Header():
                    yield Label("Output")
                yield TextLog(id=LOG_OUTPUT_ID, highlight=True, markup=False)

    async def on_mount(self) -> None:
        cmd_input = self.query_one(f"#{CMD_INPUT_ID}")
        cmd_input.focus()

    async def on_ready(self) -> None:
        self.run_worker(self.on_ui_ready, exclusive=True, group="cmd")

    async def on_action_submit(self):
        self.run_worker(self.on_cmd, exclusive=True)

    def on_cmd(self):
        pass

    def append_cmd_output(self, text: str):
        cmd_output = self.query_one(f"#{CMD_OUTPUT_ID}")
        cmd_output.write(text)

    def write_cmd_output(self, text: str):
        cmd_output = self.query_one(f"#{CMD_OUTPUT_ID}")
        cmd_output.clear()
        cmd_output.write(text)

    def append_log_output(self, text: str):
        log_output = self.query_one(f"#{LOG_OUTPUT_ID}")
        log_output.write(text)

    def write_log_output(self, text: str):
        cmd_output = self.query_one(f"#{LOG_OUTPUT_ID}")
        cmd_output.clear()
        cmd_output.write(text)

    def pop_cmd_text(self):
        cmd_input = self.query_one(f"#{CMD_INPUT_ID}")
        cmd_text = cmd_input.value
        cmd_input.value = ""
        return cmd_text

    def on_ui_ready(self):
        pass

    def render_file(self, file_path, file_type):
        with open(file_path, "rt") as code_file:
            syntax = Syntax(code_file.read(), file_type, line_numbers=True)
            self.write_log_output(syntax)


if __name__ == "__main__":
    app = TerminalUi()
    app.run()
