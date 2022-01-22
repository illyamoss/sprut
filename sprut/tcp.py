import socket

from io import TextIOWrapper

from .crypt import EndToEndEncryption
from .utils import generate_passphrase, get_public_ip, split_string_by_bytes


class Server:
    """ The server is designed for a single connection. 
    After, if client connected to a server, make a secure connection. 
    Client send passphrase to the server, if the server passphrase is correct, 
    transfer the data to the client.
    """
    def __init__(
        self, 
        *, 
        rsa_key_size: int, 
        passphrase_words_count: int = 3, 
        localnet: bool = False
    ) -> None:
        self.localnet = localnet
        # The server passphrase
        self.__passphrase = generate_passphrase(passphrase_words_count)

        self.__sock = socket.socket(
            family=socket.AF_INET, 
            type=socket.SOCK_STREAM)
        self.__sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # The port is 0 to connect to any free port
        self.__sock.bind(("0.0.0.0", 0))  
        self.__sock.listen(1)

        self.e2ee = EndToEndEncryption(rsa_key_size=rsa_key_size)
        self.max_rsa_chipher_size = self.e2ee.get_max_rsa_chipher_size()

        self.__client: socket.socket

    def send(self, data: bytes) -> None:
        hash_ = self.e2ee.encrypt(data)
        self.__client.send(hash_)

    def recv(self, bufsize: int = 0) -> bytes:
        if bufsize == 0:
            bufsize = self.max_rsa_chipher_size

        data = self.__client.recv(bufsize)
        if not data:
            return data
        return self.e2ee.decrypt(data)

    def accept_client_connection(self) -> None:
        self.__client, addrs = self.__sock.accept()
        print(f"Connection: {addrs}\n")

        self.exchange_rsa_pub_keys()
        passphrase = self.recv().decode()

        if passphrase == self.__passphrase:
            self.send(b"Correct passphrase")
        else:
            self.send(b"Wrong passphrase")

    def get_client_code(self) -> str:
        port = self.__sock.getsockname()[1]

        if self.localnet:
            host = self.__sock.getsockname()[0]
        else:
            host = get_public_ip()
        return f"{host}:{port}_{self.__passphrase}"

    def exchange_rsa_pub_keys(self) -> None:
        # Send server public key to client
        self.__client.send(self.e2ee.public_key)
        # Recieve public key from client
        self.e2ee.public_key = self.__client.recv(1024)

    def close(self) -> None:
        self.__sock.close()


class Client:
    def __init__(
        self, *, host: str, port: int, rsa_key_size: int, passphrase: str
    ) -> None:
        self.__sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.__sock.connect((host, port))
        self.e2ee = EndToEndEncryption(rsa_key_size=rsa_key_size)
        self.max_rsa_chipher_size = self.e2ee.get_max_rsa_chipher_size()

        self.exchange_rsa_pub_keys()

        self.send(passphrase.encode())

    def send(self, data: bytes) -> None:
        hash_ = self.e2ee.encrypt(data)
        self.__sock.send(hash_)

    def recv(self, bufsize: int = 0) -> bytes:
        if bufsize == 0:
            bufsize = self.max_rsa_chipher_size

        data = self.__sock.recv(bufsize)
        if not data:
            return data
        return self.e2ee.decrypt(data)

    def exchange_rsa_pub_keys(self) -> None:
        # Send server public key to server
        self.__sock.send(self.e2ee.public_key)
        # Recieve public key from server
        self.e2ee.public_key = self.__sock.recv(1024)

    def close(self):
        self.__sock.close()


class FileSender:
    def __init__(self, sock: Server) -> None:
        self.sock = sock
    
    def send_files(self, files: list[TextIOWrapper]) -> None:
        """ Send files from server to client """

        for file_ in files:
            self.sock.send(file_.name.encode())  # Send filename to client
            for line in file_.readlines():
                if len(line.encode()) > self.sock.max_rsa_chipher_size:
                    for splited_line in split_string_by_bytes(
                        line, bytes_count=self.sock.max_rsa_chipher_size
                    ):
                        self.sock.send(splited_line.encode())
                else:
                    self.sock.send(line.encode())
            self.sock.send(b"\x00")  # Mark end of a file

    def send_folders(self, folders: list) -> None:
        ...


class FileReciever:
    def __init__(self, sock: Client) -> None:
        self.sock = sock

    def recieve_files(self) -> None:
        while True:
            filename = self.sock.recv().decode()
            if not filename:
                break

            with open(filename, "wb") as file_:
                data = self.sock.recv()
                while data != b"\x00":
                    file_.write(data)
                    data = self.sock.recv()
            print(f"File: {filename} delivered")
    
    def recieve_folders(self) -> None:
        ...
