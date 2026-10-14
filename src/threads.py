import time
import sys
import datetime

from argon2 import PasswordHasher
from commands import *

messages = []
count_users = []
server_uptime = []
users_connected = []

commands = ("/kick", "/mute", "/promote", "/demote")

password_hasher = PasswordHasher()


def server_console(client_map, update_user):
    while True:
        server_console_input = input("Server Console: ")

        if server_console_input.strip():
            command = server_console_input.split(" ", 1)
            username = None
            if command[0] != "/users":
                try:
                    username = command[1].strip()
                except IndexError:
                    print("Provide a name next to the command\n'/command user'")

            if server_console_input.startswith("/promote"):
                promote("server", client_map, "server", username, update_user, True)

            elif server_console_input.startswith("/users"):
                for client in client_map:
                    print("-" * len(client_map[client]["username"]))
                    print(client_map[client]["username"])
                    print(client_map[client]["role"])

            elif server_console_input.startswith("/demote"):
                promote("server", client_map, "server", username, update_user, False)

            elif server_console_input.startswith("/kick"):
                for client, values in client_map.items():
                    if username == values["username"]:
                        encryption = client_map[client]["encryption"]
                        kick_user(
                            "server",
                            username,
                            client_map,
                            share_messages,
                            encryption,
                        )
                        break
                else:
                    print("No username found online.")


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

        elif data_decrypted.startswith("SOCKET_CLOSING|"):
            data_decrypted = data_decrypted[len("SOCKET_CLOSING|") :]
            messages.append(data_decrypted)

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

            try:
                client.sendall(header + encrypted_message)
            except OSError:
                continue

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

    user_joined_count, user_disconnected_count = 0, 0

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
                    "SOCKET_CLOSING|",
                    "Detected blank username or password\nClosing connection in...",
                    client_socket,
                    encryption,
                )
                time.sleep(1)
                client_socket.close()
                print("username or password was blank\nClosing users connection.\n")
                return

            if decrypted_data.startswith("LOGIN|"):
                try:
                    userid, _, password_, role = database.get_user(username)
                    password_hasher.verify(password_, password)
                    print(f"Passed password verification for user '{username}'")

                except Exception as e:
                    print(e)
                    print(
                        f"Password and it's hash did not match for user '{username}'\nClosing users connection."
                    )
                    send_message_to_client(
                        "SOCKET_CLOSING|",
                        f"Password and it's hash did not match for user '{username}'\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    time.sleep(1)
                    client_socket.close()
                    return

            elif decrypted_data.startswith("REGISTER|"):
                password_hash = password_hasher.hash(password)

                if database.find_name(username) is False:
                    database.add_user(username, password_hash)
                    userid, _, password_, role = database.get_user(username)

                else:
                    send_message_to_client(
                        "SOCKET_CLOSING|",
                        "Found same username that is registered before\nMaybe you pressed the wrong option or entered wrong username??.\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    print(
                        f"{client_socket} Found same username that is registered before '{username}'"
                    )
                    time.sleep(1)
                    client_socket.close()
                    return
            else:
                send_message_to_client(
                    "SOCKET_CLOSING|",
                    "Invalid tag detected\nClosing connection in...",
                    client_socket,
                    encryption,
                )
                print(
                    f"{client_socket} tried to join with an invalid tag\nClosed it's connection"
                )
                time.sleep(1)
                client_socket.close()
                return

            for user in client_map.values():
                if username == user["username"]:
                    send_message_to_client(
                        "SOCKET_CLOSING|",
                        "Found same username logged in. No duplicated username allowed\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    print(
                        f"{client_socket} tried to login with a username that is already online in this session.\nUsername '{username}'"
                    )
                    time.sleep(1)
                    client_socket.close()
                    return

            client_map[client_socket] = {
                "userID": userid,
                "username": username,
                "encryption": encryption,
                "role": role,
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

                elif decrypted_data.startswith("COMMAND|"):
                    decrypted_data = decrypted_data[len("COMMAND|") :]
                    command = decrypted_data.split(" ")
                    user_username = command[1].strip()

                    if command[0] in commands and database.find_name(user_username):
                        print(f"{username} ENTERED: " + decrypted_data)

                        commander_role = client_map[client_socket]["role"]
                        commander_username = client_map[client_socket]["username"]

                        if decrypted_data.startswith("/promote"):
                            promote(
                                commander_role,
                                client_map,
                                commander_username,
                                user_username,
                                database.update_user,
                            )

                        elif decrypted_data.startswith("/demote"):
                            promote(
                                commander_role,
                                client_map,
                                commander_username,
                                user_username,
                                database.update_user,
                                promote=False,
                            )

                        elif decrypted_data.startswith("/kick"):
                            kick_user(
                                commander_role,
                                user_username,
                                client_map,
                                share_messages,
                                encryption,
                            )
                    else:
                        print("Command or username not found")

                elif decrypted_data.startswith(("USER_DISCONNECTED|", "USER_JOINED|")):
                    if decrypted_data.startswith("USER_DISCONNECTED|"):
                        user_disconnected_count += 1
                        if user_disconnected_count >= 2:
                            share_messages(
                                decrypted_data,
                                client_socket,
                                client_map,
                            )

                            send_message_to_client(
                                "SOCKET_CLOSING|",
                                "USER_DISCONNECTED| Tag has been used more than once, meaning the tag has changed\nClosing connection in...",
                                client_socket,
                                encryption,
                            )
                            print(
                                f"{client_socket} tried to change tag which led to close it's connection\nUsername {username}"
                            )
                            time.sleep(1)
                            client_socket.close()
                            client_map.pop(client_socket)
                            return

                    if decrypted_data.startswith("USER_JOINED|"):
                        user_joined_count += 1
                        if user_joined_count >= 2:
                            share_messages(
                                decrypted_data,
                                client_socket,
                                client_map,
                            )

                            send_message_to_client(
                                "SOCKET_CLOSING|",
                                "USER_JOINED| Tag has been used more than once, meaning the tag has changed\nClosing connection in...",
                                client_socket,
                                encryption,
                            )
                            print(
                                f"{client_socket} tried to change tag which led to close it's connection\nUsername {username}"
                            )
                            time.sleep(1)
                            client_socket.close()
                            client_map.pop(client_socket)
                            return

                    share_messages(
                        decrypted_data,
                        client_socket,
                        client_map,
                    )

                    print(decrypted_data)
                    messages.append(decrypted_data)

            client_list.remove(client_socket)
            try:
                client_map.pop(client_socket)
            except KeyError:
                pass
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
