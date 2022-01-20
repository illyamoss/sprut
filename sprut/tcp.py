import socket

from io import TextIOWrapper

from .utils import generate_passphrase, get_public_ip


class Server:
    """ The server is designed for a single connection, 
    after the connection, if the server 
    passphrase is correct, the data is transferred 
    to the client. """
    def __init__(self, localnet: bool = False) -> None:
        self.localnet = localnet  # if client located in local network
        self.__passphrase = generate_passphrase()  # passphrase for connection client to server

        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__sock.bind(("0.0.0.0", 0))  # The port is 0 to connect to any free port
        self.__sock.listen(1)

        self.client: socket.socket

    def accept_client_connection(self) -> None:
        client, addrs = self.__sock.accept()
        print(f"Connection: {addrs}\n")
        passphrase = client.recv(1028).decode()

        if passphrase != self.__passphrase:
            client.send(b"Wrong passphrase")
        else:
            client.send(b"Correct passphrase")
        self.client = client

    def get_client_code(self) -> str:
        port = self.__sock.getsockname()[1]

        if self.localnet:
            host = self.__sock.getsockname()[0]
        else:
            host = get_public_ip()
        return f"{host}:{port}_{self.__passphrase}"

    def send_files(self, files: list[TextIOWrapper]) -> None:
        """ Send files from server to client """
        if self.client.recv(1024).decode() != "data accepted":
            return
    
        for file_ in files:
            self.client.send(file_.name.encode())  # Send filename to client
            for line in file_.readlines():
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
