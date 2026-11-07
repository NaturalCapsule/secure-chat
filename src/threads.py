import time
import datetime
import logging
import random
import platform
import os
import sys

from argon2 import PasswordHasher
from commands import *


if platform.system() == "Linux":
    folder_path = f"/home/{os.getlogin()}/.config/secure_chat/"
else:
    folder_path = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Secure_Chat"


if not os.path.exists(folder_path):
    os.makedirs(folder_path)

file_path = os.path.join(folder_path + "logs.log")

logger = logging

logger.basicConfig(
    filename=file_path,
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger.getLogger("asyncio").setLevel(logging.WARNING)

messages = []
count_users = []
server_uptime = []
users_connected = []
current_timemonotinoc = None
user_color = []

commands = ("/kick", "/mute", "/promote", "/demote", "/unmute")

password_hasher = PasswordHasher()


def server_console(client_map, update_user, backup):
    while True:
        server_console_input = input("Server Console: ")

        if server_console_input.strip():
            command = server_console_input.split(" ")
            username = None
            if command[0].strip() != "/users":
                try:
                    username = command[1].strip()
                except IndexError:
                    print("Provide a name next to the command\n'/command user'")

            if server_console_input.startswith("/promote"):
                promote(
                    "server",
                    client_map,
                    "server",
                    username,
                    update_user,
                    True,
                    logger=logger,
                )

            elif server_console_input.startswith("/users"):
                for client in client_map:
                    user = client_map[client]["username"]
                    print("-" * len(user))
                    print(user)
                    print(client_map[client]["role"])

            elif server_console_input.startswith("/demote"):
                promote(
                    "server",
                    client_map,
                    "server",
                    username,
                    update_user,
                    False,
                    logger=logger,
                )

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
                            logger,
                        )
                        break
                else:
                    print("No username found online.")

            elif server_console_input.startswith("/mute"):
                try:
                    duration = int(command[2].strip())
                    print("USERNAME: ", username)
                    mute(
                        "server",
                        client_map,
                        "server",
                        username,
                        duration,
                        current_timemonotinoc,
                        share_messages,
                        backup,
                        logger,
                    )
                except IndexError:
                    print("Make sure there is a duration (e.g. '/mute user 60')")

            elif server_console_input.startswith("/unmute"):
                unmute(
                    "server",
                    client_map,
                    "server",
                    username,
                    current_timemonotinoc,
                    share_messages,
                    backup,
                    logger,
                )


def recv_exact(sock, size):
    data = b""
    try:
        while len(data) < size:
            chunk = sock.recv(size - len(data))

            if not chunk:
                return None

            data += chunk

        return data

    except OSError as e:
        print(e.errno, e)


def UpTime(up_time_, client_map):
    global current_timemonotinoc
    start = time.perf_counter()

    while True:
        current_time = time.monotonic()

        elapsed = time.perf_counter() - start

        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)

        up_time = f"{hours:03}:{minutes:02}:{seconds:02}"

        up_time_.append(up_time)

        if client_map:
            share_messages(
                "SERVERUPTIME|", "", up_time, "server socket", client_map, True, True
            )
            current_timemonotinoc = current_time

        time.sleep(1)


def get_messages(client_socket, encryption, app, scroll_down_instant, meesage_scroll):
    while True:
        header = recv_exact(client_socket, 4)

        if header is None:
            for i in range(3, 0, -1):
                try:
                    messages.append(f"{user_color[0]}{i}")
                except IndexError:
                    messages.append(f"#ffffff{i}")
                app.invalidate()
                time.sleep(1)

            app.exit()
            return

        message_length = int.from_bytes(header, byteorder="big")

        data = recv_exact(client_socket, message_length)

        if not data:
            for i in range(3, 0, -1):
                try:
                    messages.append(f"{user_color[0]}{i}\n")
                except IndexError:
                    messages.append(f"#ffffff{i}\n")

                app.invalidate()
                time.sleep(1)

            app.exit()
            return

        data_decrypted = encryption.decrypt(data)
        if data_decrypted.startswith("USER_COUNT|"):
            count_users.append(data_decrypted[11:])

        elif data_decrypted.startswith("USER_MUTED|"):
            data_decrypted = data_decrypted[len("USER_MUTED|") :]
            messages.append(data_decrypted)

        elif data_decrypted.startswith("USER_COLOR|"):
            data_decrypted = data_decrypted[len("USER_COLOR|") :]
            user_color.append(data_decrypted)

        elif data_decrypted.startswith("CHAT|"):
            data_decrypted = data_decrypted[5:]
            color = data_decrypted[:7]
            data_decrypted = data_decrypted[7:]
            timestamp_string, message = data_decrypted.split("]", 1)
            timestamp_string = timestamp_string[1:]
            timestamp = datetime.datetime.fromisoformat(timestamp_string)
            local_time = timestamp.astimezone()
            formatted_time = local_time.strftime("%I:%M %p")
            formatted_time = f"[{formatted_time}]"

            messages.append(f"{color}{formatted_time}{message}")
            scroll_down_instant(meesage_scroll, messages)

        elif data_decrypted.startswith("SOCKET_CLOSING|"):
            data_decrypted = data_decrypted[len("SOCKET_CLOSING|") :]
            messages.append(data_decrypted)

        elif data_decrypted.startswith("USER_DISCONNECTED|"):
            messages.append(data_decrypted[18:])

        elif data_decrypted.startswith("USER_JOINED|"):
            messages.append(data_decrypted[12:])

        elif data_decrypted.startswith("ALERTING_USER|"):
            messages.append(data_decrypted[len("ALERTING_USER|") :])

        elif data_decrypted.startswith("SERVERUPTIME|"):
            server_uptime.append(data_decrypted[13:])

        elif data_decrypted.startswith("USERS_CONNECTED|"):
            data_decrypted = data_decrypted[16:]
            users_connected.append(data_decrypted.split("|USERS_LIST"))

        app.invalidate()


def send_message_to_client(
    message_tag, message_color, message, client_socket, encryption
):
    encrypted_message = encryption.encrypt(message_tag + message_color + message)

    message_length = len(encrypted_message)
    header = message_length.to_bytes(4, byteorder="big")

    client_socket.sendall(header + encrypted_message)


def share_messages(
    message_tag,
    message_color,
    message,
    sender,
    client_map,
    sending_to_all=False,
    is_sending_time=False,
):
    try:
        for client, user in client_map.items():
            if not sending_to_all and sender == client:
                continue

            encryption = user["encryption"]

            encrypted_message = encryption.encrypt(
                message_tag + message_color + message
            )

            message_length = len(encrypted_message)
            header = message_length.to_bytes(4, byteorder="big")

            if is_sending_time:
                try:
                    client.sendall(header + encrypted_message)
                except OSError:
                    pass
            else:
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
    backup,
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
                    "#ffffff",
                    "Detected blank username or password\nClosing connection in...",
                    client_socket,
                    encryption,
                )
                time.sleep(1)
                logger.error(
                    f"Detected blank username or blank password from {client_socket}"
                )
                client_socket.close()
                print("username or password was blank\nClosing users connection.\n")
                return

            if decrypted_data.startswith("LOGIN|"):
                try:
                    userid, _, hashed_password, role = database.get_user(username)
                    password_hasher.verify(hashed_password, password)
                    logger.info(f"Passed password verification for user '{username}")
                    print(f"Passed password verification for user '{username}'")

                except Exception as e:
                    print(e)
                    print(
                        f"Password and it's hash did not match for user '{username}'\nClosing users connection."
                    )

                    logger.error(
                        "Password and it's hash did not match for user '{username}'\nClosing users connection."
                    )

                    send_message_to_client(
                        "SOCKET_CLOSING|",
                        "#ffffff",
                        f"Password and it's hash did not match for user '{username}'\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    time.sleep(1)
                    client_socket.close()
                    return

            elif decrypted_data.startswith("REGISTER|"):
                if len(username) > 14:
                    send_message_to_client(
                        "SOCKET_CLOSING|",
                        "#ffffff",
                        "Username should not be more than 14 character.\nClosing connection",
                        client_socket,
                        encryption,
                    )
                    logger.error(
                        f"{client_socket} Entered a username which had more than 14 characters '{username}'"
                    )
                    client_socket.close()
                    return

                password_hash = password_hasher.hash(password)

                if database.find_name(username) is False:
                    database.add_user(username, password_hash)
                    userid, _, _, role = database.get_user(username)

                else:
                    send_message_to_client(
                        "SOCKET_CLOSING|",
                        "#ffffff",
                        "Found same username that is registered before\nMaybe you pressed the wrong option or entered wrong username??.\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    print(
                        f"{client_socket} Found same username that is registered before '{username}'"
                    )

                    logger.error(
                        f"{client_socket} Found same username that is registered before '{username}'"
                    )

                    time.sleep(1)
                    client_socket.close()
                    return
            else:
                send_message_to_client(
                    "SOCKET_CLOSING|",
                    "#ffffff",
                    "Invalid tag detected\nClosing connection in...",
                    client_socket,
                    encryption,
                )
                print(
                    f"{username} tried to join with an invalid tag\nClosed it's connection"
                )

                logger.error(
                    f"{username} tried to join with an invalid tag.\nClient socket: {client_socket}"
                )

                time.sleep(1)
                client_socket.close()
                return

            for user in client_map.values():
                if username == user["username"]:
                    send_message_to_client(
                        "SOCKET_CLOSING|",
                        "#ffffff",
                        "Found same username logged in. No duplicated username allowed\nClosing connection in...",
                        client_socket,
                        encryption,
                    )
                    print(
                        f"{client_socket} tried to login with a username that is already online in this session.\nUsername '{username}'"
                    )

                    logger.error(
                        f"{client_socket} tried to login with a username that is already online in this session.\nUsername '{username}'"
                    )

                    time.sleep(1)
                    client_socket.close()
                    return

            if username in backup:
                client_map[client_socket] = {
                    "userID": userid,
                    "username": username,
                    "encryption": encryption,
                    "role": role,
                    "muted_until": backup[username],
                    "color": f"#{random.randint(0, 0xFFFFFF):06x}",
                }
            else:
                backup[username] = False
                client_map[client_socket] = {
                    "userID": userid,
                    "username": username,
                    "encryption": encryption,
                    "role": role,
                    "muted_until": False,
                    "color": f"#{random.randint(0, 0xFFFFFF):06x}",
                }

            user_color_ = client_map[client_socket]["color"]

            quit_message = f"{username} has Disconnected from the server\n"
            joined_message = f"{username} has joined the convo\n"

            client_list.append(client_socket)
            clients_connected = str(len(client_list))

            share_messages(
                "USER_COUNT|", "", clients_connected, client_socket, client_map, True
            )
            send_message_to_client(
                "USER_COLOR|",
                "",
                client_map[client_socket]["color"],
                client_socket,
                encryption,
            )
            message_tag = "USERS_CONNECTED|"

            userss = ""
            for user in client_map.values():
                userss += (
                    f"{user['color']}● {user['username']} ({user['role']})|USERS_LIST"
                )

            share_messages(
                message_tag,
                "",
                userss,
                client_socket,
                client_map,
                True,
            )

            while True:
                header = recv_exact(client_socket, 4)
                if header is None:
                    break

                message_length = int.from_bytes(header, byteorder="big")
                data = recv_exact(client_socket, message_length)

                if not data:
                    break

                decrypted_data = encryption.decrypt(data)

                if decrypted_data.startswith("CHAT|"):
                    decrypted_data = decrypted_data[5:]
                    username = client_map[client_socket]["username"]
                    message_tag = "CHAT|"

                    message_time = datetime.datetime.now(datetime.UTC).isoformat()

                    message = f"[{message_time}] {username} > {decrypted_data}"

                    if client_map[client_socket]["muted_until"] != False:
                        has_passed = check_passed_time(
                            client_map[client_socket]["username"],
                            client_map,
                            current_timemonotinoc,
                            backup,
                        )

                        if has_passed:
                            print(message)

                            messages.append(message)
                            share_messages(
                                message_tag,
                                client_map[client_socket]["color"],
                                message,
                                client_socket,
                                client_map,
                            )
                    else:
                        print(message)

                        messages.append(message)
                        share_messages(
                            message_tag,
                            client_map[client_socket]["color"],
                            message,
                            client_socket,
                            client_map,
                        )

                elif decrypted_data.startswith("COMMAND|"):
                    decrypted_data = decrypted_data[len("COMMAND|") :]
                    command = decrypted_data.split(" ")
                    try:
                        user_username = command[1].strip()
                    except IndexError:
                        user_username = ""
                        send_message_to_client(
                            "ALERTING_USER|",
                            "#ffffff",
                            "Next time try to add a username instead of leaving it blank.",
                            client_socket,
                            encryption,
                        )

                    if command[0] in commands and database.find_name(user_username):
                        print(f"{username} ENTERED: " + decrypted_data)
                        logger.info(f"{username} Entered: {decrypted_data}")

                        commander_role = client_map[client_socket]["role"]
                        commander_username = client_map[client_socket]["username"]

                        if decrypted_data.startswith("/promote"):
                            promote(
                                commander_role,
                                client_map,
                                commander_username,
                                user_username,
                                database.update_user,
                                logger=logger,
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
                                logger,
                            )

                        elif decrypted_data.startswith("/mute"):
                            try:
                                duration = int(command[2].strip())
                                mute(
                                    commander_role,
                                    client_map,
                                    commander_username,
                                    user_username,
                                    duration,
                                    current_timemonotinoc,
                                    share_messages,
                                    backup,
                                    logger,
                                )
                            except IndexError:
                                send_message_to_client(
                                    "ALERTING_USER|",
                                    "#ffffff",
                                    "Next time try to add a duration instead of leaving it blank",
                                    client_socket,
                                    encryption,
                                )

                        elif decrypted_data.startswith("/unmute"):
                            unmute(
                                commander_role,
                                client_map,
                                commander_username,
                                user_username,
                                current_timemonotinoc,
                                share_messages,
                                backup,
                                logger,
                            )
                    else:
                        print("Command or username not found")
                        logger.warning(f"{username}, Command or username not found!")

                elif decrypted_data.startswith(("USER_DISCONNECTED|", "USER_JOINED|")):
                    if decrypted_data.startswith("USER_JOINED|"):
                        user_joined_count += 1
                        if user_joined_count >= 2:
                            decrypted_data = f"{username} tried to change message tag which led to close it's connection."
                            share_messages(
                                "SOCKET_CLOSING|",
                                "#ffffff",
                                decrypted_data,
                                client_socket,
                                client_map,
                            )
                            shutdown_socket(
                                client_socket,
                                encryption,
                                "SOCKET_CLOSING|",
                                "#ffffff",
                                decrypted_data,
                                client_map,
                                username,
                            )
                            print(
                                f"{username} tried to change tag which led to close it's connection\n"
                            )

                            logger.error(decrypted_data)

                            break
                        else:
                            share_messages(
                                decrypted_data,
                                user_color_,
                                joined_message,
                                client_socket,
                                client_map,
                            )

                            print(decrypted_data + joined_message)
                            logger.info(joined_message)
                            messages.append(decrypted_data + joined_message)

                    if (
                        decrypted_data.startswith("USER_DISCONNECTED|")
                        and user_joined_count >= 1
                    ):
                        user_disconnected_count += 1
                        if user_disconnected_count >= 2:
                            decrypted_data = f"{username} tired to change message tag which led to close it's connection."
                            share_messages(
                                "SOCKET_CLOSING|",
                                "#ffffff",
                                decrypted_data,
                                client_socket,
                                client_map,
                            )

                            shutdown_socket(
                                client_socket,
                                encryption,
                                "USER_DISCONNECTED|",
                                user_color_,
                                quit_message,
                                client_map,
                                username,
                            )
                            print(
                                f"{username} tried to change tag which led to close it's connection\n"
                            )

                            logger.error(decrypted_data)

                            break

                        else:
                            share_messages(
                                "USER_DISCONNECTED|",
                                user_color_,
                                quit_message,
                                client_socket,
                                client_map,
                            )

                            print(decrypted_data + quit_message)
                            logger.info(quit_message)
                            messages.append(decrypted_data + quit_message)
                            client_socket.close()
                            break

                    elif user_joined_count < 1:
                        error_message = f"{username} tired to change message tag which led to close it's connection.\n"
                        share_messages(
                            "SOCKET_CLOSING|",
                            "#ffffff",
                            error_message,
                            client_socket,
                            client_map,
                        )
                        shutdown_socket(
                            client_socket,
                            encryption,
                            "USER_DISCONNECTED|",
                            user_color_,
                            quit_message,
                            client_map,
                            username,
                        )
                        print(error_message)
                        logger.error(error_message)
                        break

            client_list.remove(client_socket)
            client_map.pop(client_socket)
            message_tag = "USERS_CONNECTED|"

            userss = ""
            for user in client_map.values():
                userss += (
                    f"{user['color']}● {user['username']} ({user['role']})|USERS_LIST"
                )

            share_messages(
                message_tag,
                "",
                userss,
                client_socket,
                client_map,
                True,
            )

            clients_connected = str(len(client_list))
            share_messages(
                "USER_COUNT|",
                "",
                clients_connected,
                client_socket,
                client_map,
                True,
            )

            client_socket.close()
            return
