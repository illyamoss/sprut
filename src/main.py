import os
import sys
import logging
import socket


logging.basicConfig(level=logging.DEBUG)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sys_args = sys.argv[1:]


def send_file_to_client(
    client_socket: socket.socket, path_to_file: str
) -> None:
    """ Send file from server to client """
    client_socket.send(os.path.basename(path_to_file).encode())
    with open(path_to_file, "r") as file:
        for line in file.readlines():
            client_socket.send(line.encode())
    client_socket.send(b"\x00")  # End of the file


def recieve_files_from_server(
    server_socket: socket.socket, 
    filename: str
) -> None:
    with open(filename, "wb") as file:
        data = server_socket.recv(1024)
        while data != b"\x00":
            file.write(data)
            data = server_socket.recv(1024)


if sys_args[0] == "send":
    files = sys_args[1:]

    sock.bind(("127.0.0.1", 8000))
    sock.listen(1)

    logging.info("Server started")

    while True:
        client, addrs = sock.accept()
        logging.info(f"Connection: {addrs}")
        data = client.recv(1024)
        logging.info(f"Data from client: {data}")
        
        if data.decode() == "data accepted":
            for path_to_file in files:
                logging.info("Sending files...")
                send_file_to_client(
                    client_socket=client, 
                    path_to_file=path_to_file
                )

            client.close()
            logging.info("Data succussful transferred")
            break
        else:
            client.close()
            break
elif sys_args[0] == "recieve":
    sock.connect(("127.0.0.1", 8000))

    logging.info("Client connected")

    accept = input("Accept files?(Y/n): ").lower()

    match accept:
        case "y":
            sock.send("data accepted".encode())
        case _:
            sock.close()
            exit()

    while True:
        filename = sock.recv(1024).decode()
        if not filename:
            break
        recieve_files_from_server(server_socket=sock, filename=filename)

    logging.info("Data succussful transferred")


sock.close()
