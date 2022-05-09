from argparse import ArgumentParser, FileType

from .exception import RecieverError
from .net import Sender, Receiver


DEFAULT_SPRUT_SERVER_ADDRESS = ("127.0.0.1", 8000)


parser = ArgumentParser(
    prog="Sprut",
    description="Securely and simply transfer \
    files from one computer to another 📦",
)

subparser = parser.add_subparsers(dest="command")
send = subparser.add_parser("send")
recieve = subparser.add_parser("recieve")

send.add_argument(
    "files",
    type=FileType("r"),
    nargs="+",
    help="send files, for example: sprut send file1.txt file2.txt.",
)
recieve.add_argument(
    "code",
    type=str,
    help="Code for connection to server, example: " + "sprut recieve <code>.",
)


def run() -> None:
    args = parser.parse_args()

    if args.command == "send":
        try:
            sender = Sender(sprut_server_address=DEFAULT_SPRUT_SERVER_ADDRESS)
        except ConnectionRefusedError:
            print("Problem with sprut server. Sorry=(")
            exit()
        print("Sprut started")

        passphrase = sender.get_passphrase_for_room()

        print("Sending files: ")
        for file_ in args.files:
            print(file_.name)

        print(
            f"Code is: {passphrase}\n\n"
            "On the other computer run:\n"
            f"sprut recieve {passphrase}\n"
        )

        try:
            sender.accept_reciever()
            sender.send_files(files=args.files)
            
            print("Data succussful transferred")
        except RecieverError:
            print("Reciever not accepted data...")

    elif args.command == "recieve":
        passphrase = args.code

        print("Connection...")
        try:
            receiver = Receiver(
                passphrase_for_room=passphrase, 
                sprut_server_address=DEFAULT_SPRUT_SERVER_ADDRESS
            )
        except ValueError:
            print("Wrong code/passphrase.")
        else:
            accept = input("Accept files?(Y/n): ").lower()

            if accept == "y":
                receiver.accept_files()
                receiver.recieve_files()

                print("Data succussful transferred")
            else:
                receiver.not_accept_files()
                print("Data not accepted")
    else:
        print("Wrong Command")
