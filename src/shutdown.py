import socket
import sys


def shutdown_socket(socket_, encryption, quit_message, client_list=None):
    quit_encrypted = encryption.encrypt(quit_message)

    try:
        if client_list:
            print(client_list)
            for client in client_list:
                client.sendall(quit_encrypted)
                client.shutdown(socket.SHUT_RDWR)
                client.close()

            socket_.close()
        else:
            socket_.sendall(quit_encrypted)

            socket_.shutdown(socket.SHUT_WR)
            socket_.close()
            sys.exit()
    except (OSError, RuntimeWarning, RuntimeError, ConnectionResetError):
        pass
