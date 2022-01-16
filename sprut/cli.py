# import sys
from argparse import ArgumentParser, FileType

from .tcp import Server, Client


parser = ArgumentParser(
    prog="Sprut", 
    description="Securely and simply transfer \
    files from one computer to another 📦")

parser.add_argument(
    "--command", 
    "-c", 
    type=str, 
    default="recieve", 
    choices=("send", "recieve"))

parser.add_argument(
    "--files", 
    "-f", 
    type=FileType("r"), 
    nargs="+",
    help="send files, for example: sprut --send file1.txt file2.txt")

parser.add_argument(
    "--code",
    type=str, 
    help="for example: sprut --recive <code for connect to server>")


def run():
    command = parser.parse_args().command
    files = parser.parse_args().files
    code = parser.parse_args().code

    if command == "send":
        print("Sprut server started")
        server = Server()
        client_code = server.get_client_code()

        print("Sending files: ")
        for file_ in files:
            print(file_.name)

        print(f"Code is: {client_code}\n\n"
            "On the other computer run:\n"
            f"sprut --command recieve --code {client_code}\n")

        server.accept_client_connection()
        server.send_files_to_client(files=files)
        print("Data succussful transferred")

        server.close()
    elif command == "recieve":
        host = code.split("-")[0].split(":")[0]
        port = int(code.split("-")[0].split(":")[1])
        passphrase = code.split("-")[1]

        print("Connection...")
        try:
            client = Client(host=host, port=port, passphrase=passphrase)

            if client.recieve_data().decode() != "Correct passphrase":
                print("Wrong code/passphrase.")
                client.close()
                return
            
            print("Connected to the server")

            accept = input("Accept files?(Y/n): ").lower()

            if accept == "y":
                client.send_data("data accepted".encode())
                client.recieve_files_from_server()

                print("Data succussful transferred")
                client.close()
            else:
                client.close()
        except ConnectionRefusedError:
            print("Wrong code/passphrase.")
    else:
        print("Wrong Command")
