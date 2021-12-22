import sys
import logging
import socket

logging.basicConfig(level=logging.DEBUG)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(("127.0.0.1", 8000))
sock.listen(1)

logging.info("Server started")

files = sys.argv[1:]
while True:
    conn, addrs = sock.accept()
    logging.info(f"Connection: {addrs}")
    data = conn.recv(1024)
    logging.info(f"Data from client: {data}")
    
    if data.decode() == "data accepted":
        for file in files:
            logging.info("Sending files...")
            conn.send(file.encode())

            with open(file, "r") as file:
                for line in file.readlines():
                    conn.send(line.encode())
            conn.send(b"\x00")

        conn.close()
        logging.info("Data succussful transferred")
        break
    else:
        conn.close()
        break
sock.close()
