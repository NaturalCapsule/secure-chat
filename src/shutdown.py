import socket
import sys


def shutdown_socket(socket_, encryption, quit_message):
    quit_encrypted = encryption.encrypt(quit_message)

    socket_.sendall(quit_encrypted)

    socket_.shutdown(socket.SHUT_WR)
    socket_.close()
    sys.exit()
