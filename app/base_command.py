from abc import ABC, abstractmethod
from app.terminal_ui import TerminalUi


class Command(ABC):
    def __init__(self, app: TerminalUi) -> None:
        super().__init__()
        self.app = app

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def handle_command(command: str):
        pass

    def write_output(self, msg):
        self.app.post_message(TerminalUi.Output(msg))
