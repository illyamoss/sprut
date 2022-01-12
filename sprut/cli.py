import sys

from .tcp import Server, Client


def run():
    sys_args = sys.argv[1:]

    match sys_args[0].strip():
        case "send":
            server = Server()
            client_code = server.get_client_code()

            files = sys_args[1:]  # Select input files name, except command "send"
            print("Sending: ")
            for filename in files:
                print(filename)

            print(f"Code is: {client_code}\n\n"
                "On the other computer run:\n"
                f"sprut recieve {client_code}\n")

            server.accept_client_connection()
            server.send_files_to_client(files=files)
            print("Data succussful transferred")

            server.close()

        case "recieve":
            code = sys_args[1]
            host = code.split("-")[0].split(":")[0]
            port = int(code.split("-")[0].split(":")[1])
            passphrase = code.split("-")[1]

            client = Client(host=host, port=port, passphrase=passphrase)
            print("Connected to the server")

            if client.recieve_data().decode() != "Correct passphrase":
                print("Wrong passphrase")
                client.close()
                exit()

            accept = input("Accept files?(Y/n): ").lower()

            if accept == "y":
                client.send_data("data accepted".encode())
            else:
                client.close()
                exit()

            client.recieve_files_from_server()

            print("Data succussful transferred")
            client.close()
        case _:
            print("Wrong Command")
