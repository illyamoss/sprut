from argparse import ArgumentParser, FileType

from .tcp import Server, Client, FileSender, FileReciever


parser = ArgumentParser(
    prog="Sprut", 
    description="Securely and simply transfer \
    files from one computer to another 📦")

subparser = parser.add_subparsers(dest="command")
send = subparser.add_parser("send")
recieve = subparser.add_parser("recieve")

send.add_argument(
    "files", 
    type=FileType("r"), 
    nargs="+",
    help="send files, for example: sprut send file1.txt file2.txt.")
send.add_argument(
    "--localnet", 
    "-l",
    help="specify if the computer to which you want to transfer \
        files is in the local network (default in global network).")
send.add_argument(
    "--rsakeysize",
    "-k",
    type=int,
    default=2048,
    help="Set a size of the RSA encryption key (default: 2048).")

recieve.add_argument(
    "code",
    type=str, 
    help="Code for connection to server, example: " + \
    "sprut recieve <code>.")


def run():
    args = parser.parse_args()

    if args.command == "send":
        if args.localnet is None:
            localnet = True
        else:
            localnet = False

        server = Server(rsa_key_size=2048, localnet=localnet)
        print("Sprut server started")

        client_code = server.get_client_code()

        print("Sending files: ")
        for file_ in args.files:
            print(file_.name)

        print(f"Code is: {client_code}\n\n"
            "On the other computer run:\n"
            f"sprut recieve {client_code}\n")

        server.accept_client_connection()

        if server.recv(1024).decode() == "data accepted":
            FileSender(sock=server).send_files(files=args.files)
            print("Data succussful transferred")
        else:
            print("Client not accepted data...")

        server.close()
    elif args.command == "recieve":
        host = args.code.split("_")[0].split(":")[0]
        port = int(args.code.split("_")[0].split(":")[1])
        passphrase = args.code.split("_")[1]

        print("Connection...")
        try:
            client = Client(host=host, port=port, rsa_key_size=2048, passphrase=passphrase)
        except ConnectionRefusedError:
            print("Wrong code/passphrase.")
        else:
            if client.recv(1024).decode() != "Correct passphrase":
                print("Wrong code/passphrase.")
                client.close()
                return
            print("Connected to the server")

            accept = input("Accept files?(Y/n): ").lower()

            if accept == "y":
                client.send(b"data accepted")
                FileReciever(sock=client).recieve_files()

                print("Data succussful transferred")
                client.close()
            else:
                client.send(b"data not accepted")
                client.close()
    else:
        print("Wrong Command")
