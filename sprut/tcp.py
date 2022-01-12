import os
import socket

from .crypto import generate_passphrase


class Server:
    def __init__(self) -> None:
        self.__passphrase = generate_passphrase()

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind((socket.gethostbyname(socket.gethostname()), 0))  # The port is 0 to connect to any free port
        self.__sock.listen(1)

        self.client: socket.socket | None

    def accept_client_connection(self) -> None:
        client, addrs = self.__sock.accept()
        print(f"Connection: {addrs}\n")
        passphrase = client.recv(1028).decode()

        if passphrase != self.__passphrase:
            client.send("Wrong passphrase".encode())
        else:
            client.send("Correct passphrase".encode())
        self.client = client
    
    def get_client_code(self) -> str:
        host, port = self.__sock.getsockname()[0], self.__sock.getsockname()[1]
        return f"{host}:{port}-{self.__passphrase}"

    def send_files_to_client(self, files: list) -> None:
        """ Send files from server to client """
        if self.client.recv(1024).decode() != "data accepted":
            return
    
        for path_to_file in files:
            self.client.send(os.path.basename(path_to_file).encode())  # Send filename to client
            with open(path_to_file, "r") as file:
                for line in file.readlines():
                    self.client.send(line.encode())
            self.client.send(b"\x00")  # Mark end of a file

    def close(self) -> None:
        self.__sock.close()


class Client:
    def __init__(self, host: str, port: int, passphrase: str):
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.connect((host, port))
        self.__sock.send(passphrase.encode())

    def send_data(self, data: bytes) -> None:
        self.__sock.send(data)

    def recieve_data(self, bufsize: int = 1024) -> bytes:
        return self.__sock.recv(bufsize)

    def recieve_files_from_server(self) -> None:
        while True:
            filename = self.recieve_data().decode()
            if not filename:
                break
            with open(filename, "wb") as file:
                data = self.recieve_data()
                while data not in b"\x00":
                    file.write(data.removesuffix(b"\x00"))
                    data = self.recieve_data()
            print(f"File: {filename} delivered")

    def close(self):
        self.__sock.close()
