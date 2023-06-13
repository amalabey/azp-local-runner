from textual.app import App, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.widgets import Header, Static


class TerminalApp(App):
    CSS_PATH = "app.css"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-grid"):
            with Container(id="left-pane"):
                yield Static("grid layout!", id="bottom-right-final")
                yield Static(">>", id="cmd-input")
            with VerticalScroll(id="right-pane"):
                for number in range(15):
                    yield Static(f"Vertical layout, child {number}")


if __name__ == "__main__":
    app = TerminalApp()
    app.run()
