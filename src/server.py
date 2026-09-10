import socket
import threading

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import Encryption
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

client_list = []

up_time_ = []
uptime_thread = threading.Thread(
    target=UpTime, args=(up_time_, client_list, encryption)
)
uptime_thread.start()

while True:
    try:
        conn, addr = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, client_list, encryption, up_time_),
            daemon=True,
        )

        thread.start()

    except (KeyboardInterrupt, OSError):
        shutdown_socket(
            server,
            encryption,
            "CHAT|Server has disconnected.\nDisconnecting all users in",
            client_list,
        )
