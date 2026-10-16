import socket
import threading

from encryption import *
from threads import *
from shutdown import shutdown_socket
from database import DataBase

PORT = 6787

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", PORT))
server.listen()

print("Server is listening...")


private_key = generate_private_rsa_key()
public_key_bytes = serialize_public_key(private_key)

client_list = []
messages = []

database = DataBase("database.pb")

client_map = {}

up_time_ = []
uptime_thread = threading.Thread(
    target=UpTime, args=(up_time_, client_list, client_map)
)
uptime_thread.start()

server_console_thread = threading.Thread(
    target=server_console, daemon=False, args=(client_map, database.update_user)
).start()


while True:
    try:
        conn, addr = server.accept()

        key_length = len(public_key_bytes)
        header = key_length.to_bytes(4, byteorder="big")

        conn.sendall(header + public_key_bytes)

        header = recv_exact(conn, 4)
        key_length = int.from_bytes(header, byteorder="big")

        encrypted_aes_key = recv_exact(conn, key_length)

        aes_key = private_key.decrypt(
            encrypted_aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        encryption = Encryption(aes_key)

        thread = threading.Thread(
            target=handle_client,
            args=(
                conn,
                client_list,
                encryption,
                up_time_,
                messages,
                client_map,
                up_time_,
                database,
            ),
            daemon=True,
        )

        thread.start()

    except (KeyboardInterrupt, OSError):
        database.close_connection()
        shutdown_socket(
            server,
            encryption,
            "SOCKET_CLOSING|Server has disconnected.\nDisconnecting all users in",
            client_map,
        )
        sys.exit()
