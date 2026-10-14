import time
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
        shutdown_socket(user_client, encryption, "SOCKET_CLOSING|You have been kicked.")
        print("EXECUTED")

        share_message(
            f"SOCKET_CLOSING|{username} has been kicked", user_client, client_map
        )


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
