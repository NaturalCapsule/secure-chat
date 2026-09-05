import socket
import sys


def shutdown_socket(client_socket, encryption, quit_message):
    quit_encrypted = encryption.encrypt(quit_message)

    # client_socket.sendall(quit_message)
    client_socket.sendall(quit_encrypted)

    client_socket.shutdown(socket.SHUT_WR)
    client_socket.close()
    sys.exit()
