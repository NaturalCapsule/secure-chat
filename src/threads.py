import time
import sys
import datetime

messages = []
count_users = []
server_uptime = []
users_connected = []


def recv_exact(sock, size):
    data = b""

    while len(data) < size:
        chunk = sock.recv(size - len(data))

        if not chunk:
            return None

        data += chunk

    return data


def UpTime(up_time_, client_list, client_map):
    start = time.perf_counter()

    while True:
        elapsed = time.perf_counter() - start

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        up_time = f"SERVERUPTIME|{hours:02}:{minutes:02}:{seconds:02}"

        up_time_.append(up_time)

        if client_list and client_map:
            share_messages(up_time, "server socket", client_map, client_list, True)

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

        elif data_decrypted.startswith("USER_DISCONNECTED|"):
            messages.append(data_decrypted[18:])

        elif data_decrypted.startswith("USER_JOINED|"):
            messages.append(data_decrypted[12:])

        elif data_decrypted.startswith("SERVERUPTIME|"):
            server_uptime.append(data_decrypted[13:])

        elif data_decrypted.startswith("USERS_CONNECTED|"):
            data_decrypted = data_decrypted[16:]
            users_connected.append(data_decrypted.split(","))

        app.invalidate()


def share_messages(message, sender, client_map, client_list, sending_to_all=False):
    try:
        for client in client_list:
            if not sending_to_all and sender == client:
                continue

            encryption = client_map[client]["encryption"]

            encrypted_message = encryption.encrypt(message)
            message_length = len(encrypted_message)
            header = message_length.to_bytes(4, byteorder="big")

            client.sendall(header + encrypted_message)

    except BrokenPipeError:
        sys.exit()


def handle_client(
    client_socket, client_list, encryption, up_time_, messages, client_map, up_time
):
    share_messages(up_time_[-1], client_socket, client_map, client_list, True)
    client_list.append(client_socket)
    clients_connected = "USER_COUNT|" + str(len(client_list))

    header = recv_exact(client_socket, 4)
    if header is not None:
        message_length = int.from_bytes(header, byteorder="big")

        data = recv_exact(client_socket, message_length)

        decrypted_data = encryption.decrypt(data)

        if decrypted_data.startswith("LOGIN|"):
            client_map[client_socket] = {
                "username": decrypted_data[6:],
                "encryption": encryption,
            }

            share_messages(
                clients_connected, client_socket, client_map, client_list, True
            )
            message_flag = "USERS_CONNECTED|"

            userss = ""
            for user in client_map.values():
                userss += f"● {user['username']},"

            userss = message_flag + userss

            share_messages(
                userss,
                client_socket,
                client_map,
                client_list,
                True,
            )

            while True:
                share_messages(
                    up_time[-1],
                    client_socket,
                    client_map,
                    client_list,
                    True,
                )

                header = recv_exact(client_socket, 4)
                if header is None:
                    break

                message_length = int.from_bytes(header, byteorder="big")
                data = recv_exact(client_socket, message_length)

                if not data:
                    sys.exit()
                    break

                decrypted_data = encryption.decrypt(data)

                if decrypted_data.startswith("CHAT|"):
                    decrypted_data = decrypted_data[5:]
                    username = client_map[client_socket]["username"]
                    message_flag = "CHAT|"

                    message_time = datetime.datetime.now()
                    message_time = message_time.strftime("%I:%M %p")

                    message = (
                        f"{message_flag}[{message_time}] {username} > {decrypted_data}"
                    )

                    print(message)

                    messages.append(message)
                    share_messages(
                        message,
                        client_socket,
                        client_map,
                        client_list,
                    )

                elif decrypted_data.startswith(("USER_DISCONNECTED|", "USER_JOINED")):
                    share_messages(
                        decrypted_data,
                        client_socket,
                        client_map,
                        client_list,
                    )

                    print(decrypted_data)
                    messages.append(decrypted_data)

                else:
                    messages.append(
                        "Something went wrong with message flag...\ndid you change the source code?"
                    )

            client_list.remove(client_socket)
            client_map.pop(client_socket)

            message_flag = "USERS_CONNECTED|"
            userss = ""
            for user in client_map.values():
                userss += f"● {user['username']},"

            userss = message_flag + userss
            share_messages(
                userss,
                client_socket,
                client_map,
                client_list,
                True,
            )

            clients_connected = "USER_COUNT|" + str(len(client_list))
            share_messages(
                clients_connected,
                client_socket,
                client_map,
                client_list,
                True,
            )

            client_socket.close()
