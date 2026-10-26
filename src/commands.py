from shutdown import shutdown_socket

roles = {"user": 0, "staff": 1, "admin": 2, "server": 3}


def compare_roles(commander_role: str, user_role: str):
    if roles.get(commander_role) > roles.get(user_role):
        return True
    else:
        return False


def get_user_role(username, client_map):
    for client, values in client_map.items():
        if username == values["username"]:
            return client_map[client]["role"]
    return False


def get_user_client(username, client_map):
    for client, values in client_map.items():
        if username == values["username"]:
            return client
    return False


def kick_user(commander_role, username, client_map, share_message, encryption):
    user_role = get_user_role(username, client_map)
    user_client = get_user_client(username, client_map)

    if user_role and compare_roles(commander_role, user_role) and user_client:
        shutdown_socket(
            user_client,
            encryption,
            "SOCKET_CLOSING|You have been kicked.",
            client_map,
            username,
        )

        share_message(
            f"SOCKET_CLOSING|{username} has been kicked", user_client, client_map
        )


def check_passed_time(username, client_map, current_time, backup):
    user_client = get_user_client(username, client_map)

    if client_map[user_client]["muted_until"] < current_time:
        client_map[user_client]["muted_until"] = False
        return True
    else:
        return False


def mute(
    commander_role,
    client_map,
    commander_username,
    user_username,
    duration,
    current_time,
    share_messages,
    backup,
):
    muted_time = current_time + duration

    user_client = get_user_client(user_username, client_map)
    user_role = get_user_role(user_username, client_map)

    if user_role and compare_roles(commander_role, user_role):
        if user_client:
            client_map[user_client]["muted_until"] = muted_time
            backup[user_username] = muted_time
            share_messages(
                f"USER_MUTED|{user_username} has been muted by {commander_username} for {duration} seconds.",
                None,
                client_map,
                True,
            )
        else:
            print("Error. could'nt find user client")

    else:
        print("Error. user role not found or comparing roles failed.")


def unmute(
    commander_role,
    client_map,
    commander_username,
    user_username,
    current_time,
    share_messages,
    backup,
):
    user_role = get_user_role(user_username, client_map)

    if user_role and compare_roles(commander_role, user_role):
        user_client = get_user_client(user_username, client_map)
        if user_client:
            client_map[user_client]["muted_until"] = False
            backup[user_username] = False
            share_messages(
                f"USER_MUTED|{user_username} has been unmuted by {commander_username}.",
                None,
                client_map,
                True,
            )
        else:
            print("Error. could'nt find users client")
    else:
        print("Error. user role not found or comparing roles failed.")


def promote(
    commander_role,
    client_map,
    commander_username,
    user_username,
    update_database,
    promote=True,
):
    user_role = get_user_role(user_username, client_map)

    if user_role and compare_roles(commander_role, user_role):
        user_role_index = roles.get(user_role)

        list_roles = list(roles.items())

        if promote:
            msg = "Promoted"
            if user_role_index == 2:
                print(
                    f"{user_username} is already an admin.\nIf you are trying to make it the 'server' you can't, since the server is the only one with the 'server' role.\nThis action was done by {commander_username}"
                )
                return

            changed_role_name = list_roles[user_role_index + 1][0]
            # changed_role_index = list_roles[user_role_index + 1][1]

        else:
            msg = "Demoted"
            if user_role_index == 0:
                print(f"{user_username} is already at user role level.")
                return
            changed_role_name = list_roles[user_role_index - 1][0]

        message = f"{msg} {user_username} to {changed_role_name} with the help of {commander_username}"

        for client, values in client_map.items():
            if user_username == values["username"]:
                client_map[client]["role"] = changed_role_name
                update_database(changed_role_name, user_username)
                print(message)
                break
    else:
        print(
            f"An error occured.\nEither no user role found or comparing roles failed\nAction done by {commander_username}"
        )
