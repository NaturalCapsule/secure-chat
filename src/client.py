import socket
import sys
import threading
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from encryption import Encryption
from threads import get_messages, messages
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
quit_message = f"{username} has Disconnected from the server"

joined_message = f"{username} has joined the convo"
encrypted_join_message = encryption.encrypt(joined_message)

client_socket.sendall(encrypted_join_message)


run_app(client_socket, encryption, username, shutdown_socket, quit_message)
