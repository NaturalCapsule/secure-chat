import socket
import sys


def shutdown_socket(socket_, encryption, quit_message, client_map=None, username=None):
    try:
        if client_map and not username:
            for client, values in client_map.items():
                encryption_ = values["encryption"]
                quit_encrypted = encryption_.encrypt(quit_message)
                message_length = len(quit_encrypted)
                header = message_length.to_bytes(4, byteorder="big")
                client.sendall(header + quit_encrypted)

                client.shutdown(socket.SHUT_RDWR)
                client.close()

            socket_.close()
            sys.exit()
            return
        else:
            if username and client_map:
                for client, values in client_map.items():
                    if username == values["username"]:
                        encryption = client_map[client]["encryption"]
                        break

            quit_encrypted = encryption.encrypt(quit_message)
            message_length = len(quit_encrypted)
            header = message_length.to_bytes(4, byteorder="big")

            socket_.sendall(header + quit_encrypted)

            socket_.shutdown(socket.SHUT_WR)
            socket_.close()
    except (OSError, RuntimeWarning, RuntimeError, ConnectionResetError):
        pass
