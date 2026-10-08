import time
import sys
import datetime

from argon2 import PasswordHasher

messages = []
count_users = []
server_uptime = []
users_connected = []

password_hasher = PasswordHasher()


def recv_exact(sock, size):
    data = b""
    try:
        while len(data) < size:
            chunk = sock.recv(size - len(data))

            if not chunk:
                return None

            data += chunk

        return data

    except OSError:
        pass


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
            share_messages(up_time, "server socket", client_map, True)

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
            data_decrypted = data_decrypted[5:]
            timestamp_string, message = data_decrypted.split("]", 1)
            timestamp_string = timestamp_string[1:]
            timestamp = datetime.datetime.fromisoformat(timestamp_string)
            local_time = timestamp.astimezone()
            formatted_time = local_time.strftime("%I:%M %p")
            formatted_time = f"[{formatted_time}]"

            messages.append(f"{formatted_time}{message}")

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


def send_message_to_client(message_flag, message, client_socket, encryption):
    encrypted_message = encryption.encrypt(message_flag + message)

    message_length = len(encrypted_message)
    header = message_length.to_bytes(4, byteorder="big")

    client_socket.sendall(header + encrypted_message)


def share_messages(message, sender, client_map, sending_to_all=False):
    try:
        for client, user in client_map.items():
            if not sending_to_all and sender == client:
                continue

            encryption = user["encryption"]

            encrypted_message = encryption.encrypt(message)

            message_length = len(encrypted_message)
            header = message_length.to_bytes(4, byteorder="big")

            client.sendall(header + encrypted_message)

    except BrokenPipeError:
        pass


def handle_client(
    client_socket,
    client_list,
    encryption,
    up_time_,
    messages,
    client_map,
    up_time,
    database,
):
    username = ""

    header = recv_exact(client_socket, 4)
    if header is not None:
        message_length = int.from_bytes(header, byteorder="big")

        data = recv_exact(client_socket, message_length)

        decrypted_data = encryption.decrypt(data)

        if decrypted_data.startswith(("LOGIN|", "REGISTER|")):
            if decrypted_data.startswith("LOGIN|"):
                credentials = decrypted_data[6:]
            elif decrypted_data.startswith("REGISTER|"):
                credentials = decrypted_data[9:]
            else:
                client_socket.close()
                return

            credentials = credentials.split("\n", 1)
            username = credentials[0]
            password = credentials[1]

            if not username.strip() or not password.strip():
                send_message_to_client(
                    "CHAT|",
                    "Detected blank username or password\nClosing connection in...",
                    client_socket,
                    encryption,
                )
                client_socket.close()
                print("username or password was blank\nClosing users connection.\n")
                return

            if decrypted_data.startswith("LOGIN|"):
                try:
                    _, _, password_ = database.get_user(username)
                    password_hasher.verify(password_, password)
                    print(f"Passed password verification for user '{username}'")
                except Exception:
                    print(
                        f"Password and it's hash did not match for user '{username}'\nClosing users connection."
                    )
                    send_message_to_client(
                        "CHAT|",
                        f"Password and it's hash did not match for user '{username}'\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    client_socket.close()
                    return

            for user in client_map.values():
                if username == user["username"]:
                    send_message_to_client(
                        "CHAT|",
                        "Found same username logged in. No duplicated username allowed\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    print(
                        f"{client_socket} tried to login with a username that is already online in this session.\n Username '{username}'"
                    )
                    client_socket.close()
                    return

            if decrypted_data.startswith("REGISTER|"):
                password_hash = password_hasher.hash(password)

                if database.find_name(username) is False:
                    print(f"Successfully added '{username}' to the database!!")
                    database.add_user(username, password_hash)
                else:
                    send_message_to_client(
                        "CHAT|",
                        "Found same username that is resgistered before\nMaybe you pressed the wrong option or entered wrong username??.\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    print(
                        f"{client_socket} Found same username that is resgistered before '{username}'"
                    )
                    client_socket.close()
                    return

            client_map[client_socket] = {
                "username": username,
                "encryption": encryption,
            }

            client_list.append(client_socket)
            clients_connected = "USER_COUNT|" + str(len(client_list))

            share_messages(clients_connected, client_socket, client_map, True)
            message_flag = "USERS_CONNECTED|"

            userss = ""
            for user in client_map.values():
                userss += f"● {user['username']},"

            userss = message_flag + userss

            share_messages(
                userss,
                client_socket,
                client_map,
                True,
            )

            while True:
                share_messages(
                    up_time[-1],
                    client_socket,
                    client_map,
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

                    message_time = datetime.datetime.now(datetime.UTC).isoformat()

                    message = (
                        f"{message_flag}[{message_time}] {username} > {decrypted_data}"
                    )

                    print(message)

                    messages.append(message)
                    share_messages(
                        message,
                        client_socket,
                        client_map,
                    )

                elif decrypted_data.startswith(("USER_DISCONNECTED|", "USER_JOINED")):
                    share_messages(
                        decrypted_data,
                        client_socket,
                        client_map,
                    )

                    print(decrypted_data)
                    messages.append(decrypted_data)

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
                True,
            )

            clients_connected = "USER_COUNT|" + str(len(client_list))
            share_messages(
                clients_connected,
                client_socket,
                client_map,
                True,
            )

            client_socket.close()
            return
