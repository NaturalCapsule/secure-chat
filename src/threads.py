import socket


def get_messages(client_socket, encryption):
    while True:
        data = client_socket.recv(4096)

        data_decrypted = encryption.decrypt(data)

        if data:
            # print(data.decode())
            print(data_decrypted)


def share_messages(message, sender, client_list, encryption):
    for client in client_list:
        if sender != client:
            encrypted_message = encryption.encrypt(message)

            client.sendall(encrypted_message)


def handle_client(client_socket, addr, client_list, encryption):
    client_list.append(client_socket)

    while True:
        data = client_socket.recv(4096)
        decrypted_data = encryption.decrypt(data)

        if not data:
            break

        share_messages(decrypted_data, client_socket, client_list, encryption)
        print(decrypted_data)

    client_list.remove(client_socket)
    client_socket.shutdown(socket.SHUT_WR)
    client_socket.close()
