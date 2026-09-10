import time
import sys

messages = []
count_users = []
server_uptime = []


def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data


def UpTime(up_time_, client_list, encryption):
    start = time.perf_counter()

    while True:
        elapsed = time.perf_counter() - start

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        up_time = f"SERVERUPTIME|{hours:02}:{minutes:02}:{seconds:02}"

        if up_time_:
            up_time_.pop()

        up_time_.append(up_time)

        if client_list:
            share_messages(up_time_[-1], None, client_list, encryption, True)

        time.sleep(1)


def get_messages(client_socket, encryption, app):
    while True:
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

        elif data_decrypted.startswith("SERVERUPTIME|"):
            server_uptime.append(data_decrypted[13:])
        app.invalidate()


def share_messages(message, sender, client_list, encryption, sending_to_all=False):
    try:
        encrypted_message = encryption.encrypt(message)
        message_length = len(encrypted_message)
        header = message_length.to_bytes(4, byteorder="big")

        for client in client_list:
            if sending_to_all:
                client.sendall(header + encrypted_message)

            if sender != client and not sending_to_all:
                client.sendall(header + encrypted_message)

    except BrokenPipeError:
        sys.exit()


def handle_client(client_socket, client_list, encryption, up_time_):
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
