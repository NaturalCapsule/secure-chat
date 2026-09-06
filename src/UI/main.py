from prompt_toolkit.application import Application
from prompt_toolkit.layout.layout import Layout

from UI.layout import *
from threads import messages, get_messages
from UI.keybinds import key_bindings_, kb

import threading

ui = ui_layout(messages)

layout = Layout(ui)

app = Application(layout=layout, key_bindings=kb, full_screen=True, mouse_support=True)


def run_app(client_socket, encryption, username, shutdown_socket, quit_message):

    threading.Thread(
        target=get_messages,
        args=(client_socket, encryption, app.invalidate),
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
