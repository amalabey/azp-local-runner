import socket
import sys
import time

DEFAULT_LISTENER_PORT = 4242
DEFAULT_IP = "0.0.0.0"


class DebugConsole():
    def __init__(self, ip=DEFAULT_IP, port=DEFAULT_LISTENER_PORT):
        self.ip = ip
        self.port = port

    def listen(self, input=sys.stdin, output=sys.stdout):
        sys.stdin = input
        sys.stdout = output
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        sock.listen(1)
        print("Waiting for break point hit... ")
        conn, addr = sock.accept()
        print('Connected to agent: ', addr)
        # Upgrade connection using pty
        # upgrade_cmd = "python3 -c \'import pty; pty.spawn(\"/bin/sh\")\'\n\n"
        # conn.send(upgrade_cmd.encode('utf-8'))
        while True:
            # Receive data from the target and get user input
            data = conn.recv(1024)
            if not data:
                print("Connection closed")
                sock.close()
                break

            ans = data.decode()
            sys.stdout.write(ans)
            command = input()

            # Send command
            command += "\n"
            conn.send(command.encode())
            time.sleep(0.2)

            # Remove the output of the "input()" function
            sys.stdout.write("\033[A" + ans.split("\n")[-1])
