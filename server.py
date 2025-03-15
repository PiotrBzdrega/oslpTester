import socket

class server:
    def __init__(self, host="0.0.0.0", port=12123):
        self.host = host
        self.port = port
        # self.handler = handler
        self.client_socket = 0

    def add_handler(self, handler):
        self.handler = handler

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            print(f"Server listening on {self.host}:{self.port}...")

            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Connection from {client_address}")
                self.handler(client_socket)
                print("Close the connection2") 