import threading

from prompt_toolkit.application import Application
from prompt_toolkit.layout.layout import Layout

from UI.keybinds import kb, key_bindings_
from UI.layout import *
from threads import get_messages, messages, count_users


def run_app(client_socket, encryption, username, shutdown_socket, quit_message):

    ui = ui_layout(messages, count_users)
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
        shutdown_socket,
        username,
        quit_message,
        message_scroll,
    )

    app.run()
