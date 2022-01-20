# import sys
from argparse import ArgumentParser, FileType

from .tcp import Server, Client


parser = ArgumentParser(
    prog="Sprut", 
    description="Securely and simply transfer \
    files from one computer to another 📦")

subparser = parser.add_subparsers(dest="command")
send = subparser.add_parser("send")
recieve = subparser.add_parser("recieve")

send.add_argument(
    "--local", 
    "-l", 
    dest="localnet",
    default=False,
    type=bool,
    help="specify if the computer to which you want to transfer \
        files is in the local network (default in global network)")
send.add_argument(
    "files", 
    type=FileType("r"), 
    nargs="+",
    help="send files, for example: sprut send --files file1.txt file2.txt")

recieve.add_argument(
    "code",
    type=str, 
    help="for example: sprut recieve <code for connect to server>")


def run():
    args = parser.parse_args()

    if args.command == "send":
        print("Sprut server started")
        server = Server(localnet=args.localnet)

        client_code = server.get_client_code()

        print("Sending files: ")
        for file_ in args.files:
            print(file_.name)

        print(f"Code is: {client_code}\n\n"
            "On the other computer run:\n"
            f"sprut recieve --code {client_code}\n")

        server.accept_client_connection()
        server.send_files(files=args.files)
        print("Data succussful transferred")

        server.close()
    elif args.command == "recieve":
        host = args.code.split("_")[0].split(":")[0]
        port = int(args.code.split("_")[0].split(":")[1])
        passphrase = args.code.split("_")[1]

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
                client.send_data(b"data accepted")
                client.recieve_files_from_server()

                print("Data succussful transferred")
                client.close()
            else:
                client.close()
        except ConnectionRefusedError:
            print("Wrong code/passphrase.")
    else:
        print("Wrong Command")
