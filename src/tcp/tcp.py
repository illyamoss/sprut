import os
import logging
import socket


logging.basicConfig(level=logging.DEBUG)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


def init_server(host: str, port: int) -> socket.socket:
    sock.bind((host, port))
    sock.listen(1)

    logging.info("Server started")
    return sock


def connect_to_server(host: str, port: int) -> socket.socket:
    sock.connect((host, port))

    logging.info("Client successful connected to server")
    return sock


def send_file_to_client(
    client: socket.socket, path_to_file: str
) -> None:
    """ Send file from server to client """
    client.send(os.path.basename(path_to_file).encode())
    with open(path_to_file, "r") as file:
        for line in file.readlines():
            client.send(line.encode())
    client.send(b"\x00")  # Mark end of a file


def recieve_files_from_server(
    server: socket.socket, 
    filename: str
) -> None:
    with open(filename, "wb") as file:
        data = server.recv(1024)
        while data not in b"\x00":
            file.write(data.removesuffix(b"\x00"))
            data = server.recv(1024)


def send_file(
    server: socket.socket, 
    client: socket.socket, 
    data_from_client: bytes, 
    files: list
) -> None:
    if data_from_client.decode() == "data accepted":
        for path_to_file in files:
            logging.info("Sending files...")
            send_file_to_client(
                client_socket=client, 
                path_to_file=path_to_file
            )

        client.close()
        logging.info("Data succussful transferred")
    else:
        client.close()
    server.close()
