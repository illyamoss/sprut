import logging
import socket

from io import TextIOWrapper

from dataclasses import dataclass
from enum import Enum

from .exception import PassphraseIsInCorrect, RecieverError

from .crypt import EndToEndEncryption
from .utils import generate_passphrase, split_string_by_bytes


logging.basicConfig(level=logging.DEBUG)


DEFAULT_SPRUT_SERVER_ADDRESS = ("127.0.0.1", 8000)
DEFAULT_PASSPHRASE_WORDS_COUNT = 3


class TypesOfClient(Enum):
    SENDER = "sender"
    RECIEVER = "reciever"


@dataclass
class SenderSchema:
    ip: str
    port: int


@dataclass
class Room:
    id_: int
    passphrase: str
    sender: SenderSchema


class Server:
    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 8000
    ) -> None:
        self._sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))

        logging.info("Sprut server started")

        self._rooms: list[Room] = []
    
    def accept_connections(self) -> None:
        while True:
            data, addr = self._sock.recvfrom(1024)
            logging.info(f"Connection {addr}")

            if data.decode() == "create room":
                passphrase = self._create_room(sender=addr)
                self._sock.sendto(passphrase.encode(), addr)
            else:
                passphrase = data.decode()

                room = self._search_room_by_passphrase(passphrase)
                
                if room is None:
                    self._sock.sendto(b"Passphrase is incorrect", addr)
                else:
                    self._sock.sendto(f"{room.sender.ip}:{room.sender.port}".encode(), addr)

    def _create_room(self, sender: tuple) -> str:
        passphrase = generate_passphrase(DEFAULT_PASSPHRASE_WORDS_COUNT)

        sender = SenderSchema(ip=sender[0], port=sender[1])
        room = Room(
            id_=len(self._rooms)+1, passphrase=passphrase, sender=sender
        )
        self._rooms.append(room)

        return passphrase

    def _search_room_by_passphrase(self, passphrase: str) -> Room | None:
        for room in self._rooms:
            if room.passphrase == passphrase:
                return room
        return None

    def close(self) -> None:
        self._sock.close()


class Peer:
    def __init__(self, *, address: tuple) -> None:
        self.address = address
        self._sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )

        self.e2ee = EndToEndEncryption.generate_keys(rsa_key_size=2048)
        self.max_rsa_chipher_size = self.e2ee.get_max_rsa_chipher_size()

    def sendto(self, data: bytes, addr: tuple[str, int] = None) -> None:
        if addr is None:
            addr = self.address
        # hash_ = self.e2ee.encrypt(data)
        # self._sock.sendto(hash_, addr)
        self._sock.sendto(data, addr)

    def recv(self, bufsize: int = None) -> bytes:
        if bufsize is None:
            bufsize = self.max_rsa_chipher_size

        data = self._sock.recvfrom(bufsize)[0]
        if not data:
            return data
        # return self.e2ee.decrypt(data)
        return data

    def exchange_rsa_pub_keys(self, addr: tuple[str, int] = None) -> None:
        # Send server public key to peer
        self._sock.sendto(self.e2ee.public_key, addr)
        # Recieve public key from peer
        self.e2ee.public_key = self._sock.recvfrom(1024)[0]

    def close(self):
        self._sock.close()


class Sender(Peer):
    def __init__(self) -> None:
        super().__init__(address=DEFAULT_SPRUT_SERVER_ADDRESS)
        
        self._passphrase_for_room: str = None

        self._create_room()

    def accept_reciever(self) -> None:
        data, addr = self._sock.recvfrom(1024)

        if data.decode() != "data accepted":
            raise RecieverError("Data not accepted")

        print(f"Connection: {addr}\n")

        self.reciever_addr = addr

    def send_files(self, files: list[TextIOWrapper]) -> None:
        """Send files from reciever to server"""

        for file_ in files:
            self.sendto(file_.name.encode(), addr=self.reciever_addr)  # Send filename to client
            for line in file_.readlines():
                if len(line.encode()) > self.max_rsa_chipher_size:
                    for splited_line in split_string_by_bytes(
                        line, bytes_count=self.max_rsa_chipher_size
                    ):
                        self.sendto(splited_line.encode(), addr=self.reciever_addr)
                else:
                    self.sendto(line.encode(), addr=self.reciever_addr)
            self.sendto(b"\x00", addr=self.reciever_addr)  # Mark end of a file
        self.sendto(b"\x000", addr=self.reciever_addr)  # Mark end of a files

    def get_passphrase_for_room(self) -> str:
        return self._passphrase_for_room

    def _create_room(self) -> None:
        self._sock.sendto(b"create room", DEFAULT_SPRUT_SERVER_ADDRESS)
        self._passphrase_for_room = self._sock.recvfrom(1024)[0].decode()


class Reciever(Peer):
    def __init__(self, passphrase_for_room: str) -> None:
        super().__init__(address=DEFAULT_SPRUT_SERVER_ADDRESS)

        self._get_sender_addr(passphrase_for_room)

    def _get_sender_addr(self, passphrase_for_room: str) -> None:
        self._sock.sendto(passphrase_for_room.encode(), self.address)
        if (addr := self._sock.recvfrom(1024)[0].decode()) != "Passphrase is incorrect":
            ip, port = addr.split(":")[0], int(addr.split(":")[1])
            self.sender_addr = (ip, port)
        else:
            raise PassphraseIsInCorrect("Passphrase is incorrect")

    def recieve_files(self) -> None:
        while True:
            file_ = self.recv()
            if file_ == b"\x000":
                break

            with open(file_.decode(), "wb") as f:
                data = self.recv()
                while data != b"\x00":
                    f.write(data)
                    data = self.recv()
            print(f"File: {file_.decode()} delivered")


if __name__ == "__main__":
    server = Server()
    server.accept_connections()
