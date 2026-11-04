import threading

from prompt_toolkit.application import Application
from prompt_toolkit.layout.layout import Layout

from UI.keybinds import kb, key_bindings_
from UI.layout import *
from threads import (
    get_messages,
    messages,
    count_users,
    server_uptime,
    users_connected,
    user_color,
)


show_users = [False]


def run_app(client_socket, encryption, username):

    ui = ui_layout(messages, count_users, server_uptime, show_users, users_connected)
    layout = Layout(ui)

    app = Application(
        layout=layout, key_bindings=kb, full_screen=True, mouse_support=True
    )

    threading.Thread(
        target=get_messages,
        args=(client_socket, encryption, app),
        daemon=False,
    ).start()

    key_bindings_(
        input_buffer,
        messages,
        encryption,
        client_socket,
        username,
        message_scroll,
        show_users,
        user_color,
    )

    app.run()
