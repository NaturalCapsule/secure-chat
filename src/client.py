import socket
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import Encryption, serialize_public_key, serialization
from shutdown import shutdown_socket
from threads import recv_exact


from UI.main import *

PORT = 6787
IP = "192.168.1.100"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

header = recv_exact(client_socket, 4)

if header is None:
    print("Something went wrong when getting the server public RSA key")
    sys.exit()

key_length = int.from_bytes(header, byteorder="big")
public_key_bytes = recv_exact(client_socket, key_length)

server_public_key = serialization.load_pem_public_key(public_key_bytes)

key = AESGCM.generate_key(bit_length=256)
encryption = Encryption(key)

encrypted_aes_key = server_public_key.encrypt(
    key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)

key_length = len(encrypted_aes_key)
header = key_length.to_bytes(4, byteorder="big")

client_socket.sendall(header + encrypted_aes_key)

username = input("enter your name: ")

encrypted_join_message = encryption.encrypt(f"LOGIN|{username}")

message_length = len(encrypted_join_message)
header = message_length.to_bytes(4, byteorder="big")
client_socket.sendall(header + encrypted_join_message)


quit_message = f"USER_DISCONNECTED|{username} has Disconnected from the server"

joined_message = f"USER_JOINED|{username} has joined the convo"
encrypted_join_message = encryption.encrypt(joined_message)

message_length = len(encrypted_join_message)
header = message_length.to_bytes(4, byteorder="big")
client_socket.sendall(header + encrypted_join_message)


run_app(client_socket, encryption, username, shutdown_socket, quit_message)
