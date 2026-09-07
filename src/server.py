import socket
import threading

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import Encryption
from get_ip import get_server_public_ip
from threads import *
from shutdown import shutdown_socket


PORT = 6787

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", PORT))
server.listen()

print("Server is listening...")

# key = AESGCM.generate_key(256)
key = bytes.fromhex("00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
encryption = Encryption(key)


get_server_public_ip()
client_list = []

while True:
    try:
        conn, addr = server.accept()

        # Fix this
        addr = ":".join(map(str, addr))

        encrypted_server_addr = encryption.encrypt(addr)
        conn.sendall(encrypted_server_addr)

        thread = threading.Thread(
            target=handle_client,
            args=(conn, addr, client_list, encryption),
            daemon=True,
        )

        thread.start()
    except KeyboardInterrupt:
        shutdown_socket(
            server,
            encryption,
            "Server has disconnected.\nDisconnecting all users in",
            client_list,
        )
