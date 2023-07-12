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

    def append_console_output(self, msg):
        self.app.append_cmd_output(msg)

    def write_console_output(self, msg):
        self.app.write_cmd_output(msg)

    def append_log_output(self, msg):
        self.app.append_log_output(msg)

    def write_log_output(self, msg):
        self.app.write_log_output(msg)
