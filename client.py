import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("127.0.0.1", 8000))

accept = input("Accept files?(Y/n): ").lower()

if accept == "y":
    sock.sendall("data accepted".encode())
elif accept == "n":
    exit()
else:
    print("Wrong answer")
    exit()

while True:
    data, addrs = sock.recvfrom(1024)

    with open("file1.txt", "wb") as file:
        print(data, data.decode())
        file.write(data)
        sock.close()
