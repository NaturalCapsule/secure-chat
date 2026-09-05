import socket
import threading

# import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import Encryption
from get_ip import get_server_public_ip
from threads import *


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
    conn, addr = server.accept()
    print(addr)

    thread = threading.Thread(
        target=handle_client, args=(conn, addr, client_list, encryption), daemon=True
    )

    thread.start()
