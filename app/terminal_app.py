from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Static
from textual.widgets import Input


class TerminalApp(App):
    CSS_PATH = "app.css"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with Container(id="left-pane"):
                with VerticalScroll(id="cmd-output-container"):
                    for num in range(100):
                        yield Static(".......cmd output.....")
                with Container(id="cmd-input-container"):
                    yield Input(placeholder=">", id="cmd-input-text")
            with VerticalScroll(id="right-pane"):
                for number in range(100):
                    yield Static(f"Vertical layout, child {number}")


if __name__ == "__main__":
    app = TerminalApp()
    app.run()
