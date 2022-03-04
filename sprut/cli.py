# import logging

from argparse import ArgumentParser, FileType

from .exception import PassphraseIsInCorrect, RecieverError
from .tcp import Sender, Reciever


# logging.basicConfig(level=logging.DEBUG)


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


def run():
    args = parser.parse_args()

    if args.command == "send":
        try:
            sender = Sender()
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
            sender.exchange_rsa_pub_keys(addr=sender.reciever_addr)
            sender.send_files(files=args.files)
            
            print("Data succussful transferred")
        except RecieverError:
            print("Reciever not accepted data...")

        sender.close()
    elif args.command == "recieve":
        passphrase = args.code

        print("Connection...")
        try:
            reciever = Reciever(passphrase_for_room=passphrase)
        except PassphraseIsInCorrect:
            print("Wrong code/passphrase.")
        else:
            accept = input("Accept files?(Y/n): ").lower()

            if accept == "y":
                reciever.sendto(b"data accepted", addr=reciever.sender_addr, encrypt=False)
                reciever.exchange_rsa_pub_keys(addr=reciever.sender_addr)
                reciever.recieve_files()

                print("Data succussful transferred")
                reciever.close()
            else:
                reciever.sendto(b"data not accepted", addr=reciever.sender_addr)
                reciever.close()
    else:
        print("Wrong Command")
