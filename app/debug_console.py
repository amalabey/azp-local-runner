import socket
import sys
import time

DEFAULT_LISTENER_PORT = 4242
DEFAULT_IP = "0.0.0.0"


class DebugConsole():
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_LISTENER_PORT):
        self.ip = ip
        self.port = port

    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        while True:
            self.conn, addr = self.sock.accept()
            self.on_output(f"Connected to agent: {addr}")

    def on_output(self, response: str):
        sys.stdout.write(response)

    def send_command(self, command: str):
        if self.conn:
            command += "\n"
            self.conn.send(command.encode())
            time.sleep(0.2)

            data = self.conn.recv(1024)
            if not data:
                self.sock.close()
                raise Exception("Connection Closed")

            ans = data.decode()
            self.on_output(ans)
        else:
            self.on_output("--- Not Connected ---")
