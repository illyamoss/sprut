import logging
import socket


logging.basicConfig(level=logging.DEBUG)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 8000))

accept = input("Accept files?(Y/n): ").lower()

if accept == "y":
    sock.send("data accepted".encode())
elif accept == "n":
    sock.close()
    exit()
else:
    sock.close()
    print("Wrong answer")
    exit()

while True:
    file = sock.recv(1024).decode()
    if not file:
        break

    with open(file, "wb") as file:
        data = sock.recv(1024)
        while data != b"\x00":
            file.write(data)
            data = sock.recv(1024)

sock.close()
logging.info("Data successful transferred")
