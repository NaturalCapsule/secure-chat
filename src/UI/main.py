from prompt_toolkit.application import Application
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

from UI.layout import *
from threads import messages, get_messages

import threading

kb = KeyBindings()


@kb.add("c-q")
def _(event):
    event.app.exit()


ui = ui_layout(messages)

layout = Layout(ui)

app = Application(layout=layout, key_bindings=kb, full_screen=True)


def run_app(client_socket, encryption, username, shutdown_socket, quit_message):

    threading.Thread(
        target=get_messages,
        args=(client_socket, encryption, app.invalidate),
        daemon=False,
    ).start()

    @kb.add("enter")
    def send(event):

        if input_buffer.text == "quit":
            print("Disconnecting...")
            shutdown_socket(client_socket, encryption, quit_message)

        messages.append(f"{username} (You) > {input_buffer.text}")

        encrypted_data = encryption.encrypt(f"{username} > {input_buffer.text}")
        client_socket.sendall(encrypted_data)

        input_buffer.text = ""
        input_buffer.reset()

    app.run()
