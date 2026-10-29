import socket
import sys
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import Encryption, serialize_public_key, serialization
from threads import recv_exact


from UI.main import *

IP = None
try:
    IP = sys.argv[1].strip()
    print(IP)
except IndexError:
    print("Enter an IP address to connect to the server")
    print("<client> <IP> <PORT>")
    sys.exit(0)
try:
    PORT = sys.argv[2].strip()
    PORT = int(PORT)
except (ValueError, IndexError):
    PORT = 6767
    print(
        f"Make sure port number is integer data type for next time.\nUsing default port {PORT}"
    )


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((IP, PORT))
except ConnectionRefusedError:
    print("Maybe the server is not online or you entered a wrong port?")
    sys.exit()

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

print("Press '1' for login or '2' for sign up")

choice = input("")

if choice == "2":
    message_flag = "REGISTER|"
elif choice == "1":
    message_flag = "LOGIN|"
else:
    print("Invalid choice")
    client_socket.close()
    sys.exit()


username = input("Enter name: ")
password = input("Enter password: ")

encrypted_join_message = encryption.encrypt(f"{message_flag}{username}\n{password}")

message_length = len(encrypted_join_message)
header = message_length.to_bytes(4, byteorder="big")
client_socket.sendall(header + encrypted_join_message)


joined_tag = "USER_JOINED|"
encrypted_join_message = encryption.encrypt(joined_tag)

message_length = len(encrypted_join_message)
header = message_length.to_bytes(4, byteorder="big")
client_socket.sendall(header + encrypted_join_message)


run_app(client_socket, encryption, username)
