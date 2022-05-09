import logging
import socket

from io import TextIOWrapper

from dataclasses import dataclass

from .exception import RecieverError, P2PError

from .crypt import EndToEndEncryption, MAX_RSA_ENCRYPTION_SIZE
from .utils import generate_passphrase, split_string_by_bytes


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
                    self._sock.sendto(
                        f"{room.sender.ip}:{room.sender.port}".encode(), addr
                    )

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


class PeerToPeer:
    def __init__(self) -> None:
        self._sock = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_DGRAM
        )

        self.sessions: dict[tuple, EndToEndEncryption] = dict()

    def create_session(self, addr: tuple[str, int]) -> None:
        e2ee = EndToEndEncryption.generate_keys(rsa_key_size=2048)

        other_peer_pub_key = self._exchange_rsa_pub_keys(
            public_key=e2ee.public_key, addr=addr
        )
        e2ee.public_key = other_peer_pub_key

        self.sessions[addr] = e2ee


    def close_all_sessions(self) -> None:
        for session in self.sessions:
            del session

    def sendto(self, data: bytes, addr: tuple[str, int]) -> None:
        if addr not in self.sessions:
            raise P2PError(f"Session with peer: {addr} is not created")

        logging.info(data)
        
        data = self.sessions[addr].encrypt(data)
        self._sock.sendto(data, addr)

    def recvfrom(self, bufsize: int = 2048) -> bytes:
        data, addr = self._sock.recvfrom(bufsize)

        if addr not in self.sessions:
            raise P2PError(f"Session with peer: {addr} is not created")

        session = self.sessions[addr]

        if not data:
            return
        
        data = session.decrypt(data)
        return data, addr

    def unsafe_sendto(self, data: bytes, addr: tuple[str, int]) -> None:
        """ Send data without E2EE """
        self._sock.sendto(data, addr)

    def unsafe_recvfrom(self, bufsize: int = 2048) -> bytes:
        """ Receive data without E2EE """
        data, addr = self._sock.recvfrom(bufsize)
        return data, addr

    def _exchange_rsa_pub_keys(
        self, *, public_key: bytes, addr: tuple[str, int] = None
    ) -> bytes:
        self.unsafe_sendto(data=public_key, addr=addr)
        peer_public_key = self.unsafe_recvfrom(1024)[0]

        return peer_public_key

    def close(self):
        self.close_all_sessions()
        self._sock.close()


class Sender:
    def __init__(self, sprut_server_address: tuple[str, int]) -> None:
        self.p2p = PeerToPeer()
        
        self.sprut_server_address = sprut_server_address

        self._passphrase_for_room: str = None

        self._create_room()

    def accept_reciever(self) -> None:
        data, addr = self.p2p.unsafe_recvfrom()

        if data.decode() != "data accepted":
            raise RecieverError("Data not accepted")

        print(f"Connection: {addr}\n")

        self.reciever_addr = addr

        self.p2p.create_session(self.reciever_addr)

    def send_files(self, files: list[TextIOWrapper]) -> None:
        """Send files from sender to reciever"""

        for file_ in files:
            self.p2p.sendto(file_.name.encode(), addr=self.reciever_addr)

            for line in file_.readlines():
                if len(line.encode()) > MAX_RSA_ENCRYPTION_SIZE:
                    for splited_bytes in split_string_by_bytes(
                        line, bytes_count=MAX_RSA_ENCRYPTION_SIZE
                    ):
                        logging.info(len(splited_bytes))
                        self.p2p.sendto(splited_bytes, addr=self.reciever_addr)
                else:
                    self.p2p.sendto(line.encode(), addr=self.reciever_addr)
            self.p2p.sendto(b"\x00", addr=self.reciever_addr)  # Mark end of a file
        self.p2p.sendto(b"\x000", addr=self.reciever_addr)  # Mark end of a files

        self.p2p.close()

    def get_passphrase_for_room(self) -> str:
        return self._passphrase_for_room

    def _create_room(self) -> None:
        self.p2p.unsafe_sendto(b"create room", addr=self.sprut_server_address)
        self._passphrase_for_room = self.p2p.unsafe_recvfrom()[0].decode()


class Receiver:
    def __init__(
        self, passphrase_for_room: str, sprut_server_address: tuple[str, int]
    )-> None:
        self.p2p = PeerToPeer()
        self.passphrase_for_room = passphrase_for_room
        self.sprut_server_address = sprut_server_address

    def accept_files(self) -> None:
        self._get_sender_addr(self.passphrase_for_room)

        self.p2p.unsafe_sendto(b"data accepted", addr=self.sender_addr)

        self.p2p.create_session(self.sender_addr)

    def not_accept_files(self) -> None:
        self.p2p.unsafe_sendto(b"data not accepted", addr=self.sender_addr)

    def _get_sender_addr(self, passphrase_for_room: str) -> None:
        self.p2p.unsafe_sendto(
            passphrase_for_room.encode(), addr=self.sprut_server_address
        )

        if (addr := self.p2p.unsafe_recvfrom()[0].decode()) != "Passphrase is incorrect":
            self.sender_addr = addr.split(":")[0], int(addr.split(":")[1])
        else:
            raise ValueError("Passphrase is incorrect")

    def recieve_files(self) -> None:
        while True:
            file_ = self.p2p.recvfrom()[0]
            if file_ == b"\x000":
                break

            with open(file_.decode(), "wb") as f:
                data = self.p2p.recvfrom()[0]
                while data != b"\x00":
                    f.write(data)
                    data = self.p2p.recvfrom()[0]
            print(f"File: {file_.decode()} delivered")

        self.p2p.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    server = Server()
    server.accept_connections()
