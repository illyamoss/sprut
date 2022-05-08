import logging
import socket

from io import TextIOWrapper

from dataclasses import dataclass

from .exception import PassphraseIsInCorrect, RecieverError

from .crypt import EndToEndEncryption, MAX_RSA_ENCRYPTION_SIZE
from .utils import generate_passphrase, split_string_by_bytes


DEFAULT_SPRUT_SERVER_ADDRESS = ("127.0.0.1", 8000)
DEFAULT_PASSPHRASE_WORDS_COUNT = 3


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

    def sendto(
        self, data: bytes, addr: tuple[str, int] = None, encrypt: bool = False
    ) -> None:
        if addr is None:
            addr = self.address

        logging.info(data)
        
        if encrypt:
            data = self.e2ee.encrypt(data)
        self._sock.sendto(data, addr)

    def recvfrom(self, bufsize: int = None, decrypt: bool = False) -> bytes:
        if bufsize is None:
            bufsize = self.e2ee.get_rsa_key_size()

        data, addr = self._sock.recvfrom(bufsize)
        if not data:
            return data
        
        if decrypt:
            data = self.e2ee.decrypt(data)
        return data, addr

    def exchange_rsa_pub_keys(self, addr: tuple[str, int] = None) -> None:
        # Send server public key to peer
        self.sendto(self.e2ee.public_key, addr)
        # Recieve public key from peer
        self.e2ee.public_key = self.recvfrom(1024)[0]

    def close(self):
        self._sock.close()


class Sender(Peer):
    def __init__(self) -> None:
        super().__init__(address=DEFAULT_SPRUT_SERVER_ADDRESS)
        
        self._passphrase_for_room: str = None

        self._create_room()

    def accept_reciever(self) -> None:
        data, addr = self.recvfrom()

        if data.decode() != "data accepted":
            raise RecieverError("Data not accepted")

        print(f"Connection: {addr}\n")

        self.reciever_addr = addr

    def send_files(self, files: list[TextIOWrapper]) -> None:
        """Send files from sender to reciever"""

        for file_ in files:
            self.sendto(file_.name.encode(), addr=self.reciever_addr, encrypt=True)  # Send filename to client
            for line in file_.readlines():
                if len(line.encode()) > MAX_RSA_ENCRYPTION_SIZE:
                    for splited_bytes in split_string_by_bytes(
                        line, bytes_count=MAX_RSA_ENCRYPTION_SIZE
                    ):
                        logging.info(len(splited_bytes))
                        self.sendto(splited_bytes, addr=self.reciever_addr, encrypt=True)
                else:
                    self.sendto(line.encode(), addr=self.reciever_addr, encrypt=True)
            self.sendto(b"\x00", addr=self.reciever_addr, encrypt=True)  # Mark end of a file
        self.sendto(b"\x000", addr=self.reciever_addr, encrypt=True)  # Mark end of a files

    def get_passphrase_for_room(self) -> str:
        return self._passphrase_for_room

    def _create_room(self) -> None:
        self.sendto(b"create room", DEFAULT_SPRUT_SERVER_ADDRESS)
        self._passphrase_for_room = self.recvfrom()[0].decode()


class Reciever(Peer):
    def __init__(self, passphrase_for_room: str) -> None:
        super().__init__(address=DEFAULT_SPRUT_SERVER_ADDRESS)

        self._get_sender_addr(passphrase_for_room)

    def _get_sender_addr(self, passphrase_for_room: str) -> None:
        self.sendto(passphrase_for_room.encode(), self.address)
        if (addr := self.recvfrom()[0].decode()) != "Passphrase is incorrect":
            ip, port = addr.split(":")[0], int(addr.split(":")[1])
            self.sender_addr = (ip, port)
        else:
            raise PassphraseIsInCorrect("Passphrase is incorrect")

    def recieve_files(self) -> None:
        while True:
            file_ = self.recvfrom(decrypt=True)[0]
            if file_ == b"\x000":
                break

            with open(file_.decode(), "wb") as f:
                data = self.recvfrom(decrypt=True)[0]
                while data != b"\x00":
                    f.write(data)
                    data = self.recvfrom(decrypt=True)[0]
            print(f"File: {file_.decode()} delivered")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    server = Server()
    server.accept_connections()
