import socket
import time

messages = []
count_users = []


def get_messages(client_socket, encryption, app):
    while True:
        data = client_socket.recv(4096)

        if not data:
            for i in range(3, 0, -1):
                messages.append(f"{i}")
                app.invalidate()
                time.sleep(1)

            app.exit()
            break

        data_decrypted = encryption.decrypt(data)

        if data_decrypted[:11] == "USER_COUNT|":
            data_decrypted = list(data_decrypted)
            data_decrypted[:11] = ""
            data_decrypted = "".join(data_decrypted)
            count_users.append(data_decrypted)

        elif data_decrypted[:5] == "CHAT|":
            data_decrypted = list(data_decrypted)
            data_decrypted[:5] = ""
            data_decrypted = "".join(data_decrypted)

            messages.append(data_decrypted)

        app.invalidate()


def share_messages(message, sender, client_list, encryption, sending_all=False):
    for client in client_list:
        encrypted_message = encryption.encrypt(message)
        if sending_all:
            client.sendall(encrypted_message)

        if sender != client and not sending_all:
            client.sendall(encrypted_message)


def handle_client(client_socket, client_list, encryption):
    client_list.append(client_socket)
    clients_connected = "USER_COUNT|" + str(len(client_list))
    share_messages(clients_connected, client_socket, client_list, encryption, True)

    while True:
        data = client_socket.recv(4096)
        if not data:
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
