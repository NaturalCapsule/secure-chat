import socket
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import Encryption
from shutdown import shutdown_socket

from UI.main import *

PORT = 6787
IP = "192.168.1.100"

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))


# key = AESGCM.generate_key(bit_length=256)
key = bytes.fromhex("00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff")
encryption = Encryption(key)


username = input("enter your name: ")

quit_message = f"CHAT|{username} has Disconnected from the server"

joined_message = f"CHAT|{username} has joined the convo"
encrypted_join_message = encryption.encrypt(joined_message)

message_length = len(encrypted_join_message)
header = message_length.to_bytes(4, byteorder="big")
client_socket.sendall(header + encrypted_join_message)


run_app(client_socket, encryption, username, shutdown_socket, quit_message)
