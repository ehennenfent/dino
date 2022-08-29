import socket

HOST = "127.0.0.1"
PORT = 12345


class SocketSender:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.sock.sendto(message, (HOST, PORT))
