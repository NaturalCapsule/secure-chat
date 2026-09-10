import socket
import time
import sys

messages = []
count_users = []


def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data


def get_messages(client_socket, encryption, app):
    while True:
        # data = client_socket.recv(1024)
        header = recv_exact(client_socket, 4)

        if header is None:
            for i in range(3, 0, -1):
                messages.append(f"{i}")
                app.invalidate()
                time.sleep(1)

            app.exit()
            break

        message_length = int.from_bytes(header, byteorder="big")

        data = recv_exact(client_socket, message_length)

        if not data:
            for i in range(3, 0, -1):
                messages.append(f"{i}")
                app.invalidate()
                time.sleep(1)

            app.exit()
            break

        data_decrypted = encryption.decrypt(data)
        if data_decrypted.startswith("USER_COUNT|"):
            count_users.append(data_decrypted[11:])

        elif data_decrypted.startswith("CHAT|"):
            messages.append(data_decrypted[5:])

        app.invalidate()


def share_messages(message, sender, client_list, encryption, sending_all=False):
    try:
        encrypted_message = encryption.encrypt(message)
        message_length = len(encrypted_message)
        header = message_length.to_bytes(4, byteorder="big")

        for client in client_list:
            if sending_all:
                client.sendall(header + encrypted_message)

            if sender != client and not sending_all:
                client.sendall(header + encrypted_message)

    except BrokenPipeError:
        sys.exit()


def handle_client(client_socket, client_list, encryption):
    client_list.append(client_socket)
    clients_connected = "USER_COUNT|" + str(len(client_list))
    share_messages(clients_connected, client_socket, client_list, encryption, True)

    while True:
        header = recv_exact(client_socket, 4)
        if header is None:
            break

        message_length = int.from_bytes(header, byteorder="big")

        data = recv_exact(client_socket, message_length)

        if not data:
            sys.exit()
            break

        decrypted_data = encryption.decrypt(data)

        share_messages(decrypted_data, client_socket, client_list, encryption)

        messages.append(decrypted_data)
        print(messages[-1])

    client_list.remove(client_socket)
    # client_socket.shutdown(socket.SHUT_WR)

    clients_connected = "USER_COUNT|" + str(len(client_list))
    share_messages(clients_connected, client_socket, client_list, encryption, True)

    client_socket.close()
