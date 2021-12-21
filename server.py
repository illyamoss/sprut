import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8000))
sock.listen(1)

print("Server started")
conn, addrs = sock.accept()
print(addrs)

try:
    while True:
        data = conn.recv(1024)
        print(data)
        
        if data == "data accepted":
            with open("file.txt", "r") as file:
                conn.send(file.read().encode())
except KeyboardInterrupt:
    sock.close()
