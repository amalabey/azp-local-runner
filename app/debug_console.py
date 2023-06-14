import socket
import sys
import time

DEFAULT_LISTENER_PORT = 4242
DEFAULT_IP = "0.0.0.0"


class DebugConsole():
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_LISTENER_PORT, repel=True):
        self.ip = ip
        self.port = port
        self.repel = repel

    def listen(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.ip, self.port))
        self.sock.listen(1)
        print("Waiting for break point hit... ")
        self.conn, addr = self.sock.accept()
        print('Connected to agent: ', addr)
        # Upgrade connection using pty
        # upgrade_cmd = "python3 -c \'import pty; pty.spawn(\"/bin/sh\")\'\n\n"
        # conn.send(upgrade_cmd.encode('utf-8'))
        if self.repel:
            while True:
                # Receive data from the target and get user input
                data = self.conn.recv(1024)
                if not data:
                    print("Connection closed")
                    self.sock.close()
                    break

                ans = data.decode()
                self.on_response(ans)
                command = input()

                # Send command
                command += "\n"
                self.conn.send(command.encode())
                time.sleep(0.2)

                # Remove the output of the "input()" function
                sys.stdout.write("\033[A" + ans.split("\n")[-1])

    def on_response(self, response: str):
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
            self.on_response(ans)
