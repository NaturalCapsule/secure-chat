import socket
import time
import sys


def shutdown_socket(socket_, encryption, quit_message, client_list=None):
    quit_encrypted = encryption.encrypt(quit_message)

    try:
        if client_list:
            for client in client_list:
                message_length = len(quit_encrypted)
                header = message_length.to_bytes(4, byteorder="big")
                client.sendall(header + quit_encrypted)

                time.sleep(1)

                client.shutdown(socket.SHUT_RDWR)
                client.close()

            socket_.close()
            sys.exit()
        else:
            message_length = len(quit_encrypted)
            header = message_length.to_bytes(4, byteorder="big")
            socket_.sendall(header + quit_encrypted)

            socket_.shutdown(socket.SHUT_WR)
            socket_.close()
    except (OSError, RuntimeWarning, RuntimeError, ConnectionResetError):
        pass
