import socket

messages = []


def get_messages(client_socket, encryption, invalidate):
    while True:
        data = client_socket.recv(4096)

        if not data:
            break

        data_decrypted = encryption.decrypt(data)

        messages.append(data_decrypted)
        invalidate()


def share_messages(message, sender, client_list, encryption):
    for client in client_list:
        if sender != client:
            encrypted_message = encryption.encrypt(message)

            client.sendall(encrypted_message)


def handle_client(client_socket, addr, client_list, encryption):
    client_list.append(client_socket)

    while True:
        data = client_socket.recv(4096)
        if not data:
            break

        decrypted_data = encryption.decrypt(data)

        share_messages(decrypted_data, client_socket, client_list, encryption)
        # print(decrypted_data)
        messages.append(decrypted_data)
        print(messages[-1])

    client_list.remove(client_socket)
    client_socket.shutdown(socket.SHUT_WR)
    client_socket.close()
