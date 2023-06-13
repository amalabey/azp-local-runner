from abc import ABC, abstractmethod


class Receiver(object):
    def on_log_output(output: str):
        pass

    def on_command_output(output: str):
        pass

    def on_worker_request(callback):
        pass


class Command(ABC):

    @abstractmethod
    def execute(self) -> None:
        pass

    @abstractmethod
    def submit_command(command: str):
        pass
