import datetime
from prompt_toolkit.key_binding import KeyBindings

kb = KeyBindings()


def key_bindings_(
    input_buffer,
    messages,
    encryption,
    client_socket,
    shutdown_socket,
    username,
    quit_message,
    message_scroll,
):
    @kb.add("enter")
    def send(event):

        if input_buffer.text == "<quit>":
            print("Disconnecting...")
            shutdown_socket(client_socket, encryption, quit_message)

        message_time = datetime.datetime.now()
        message_time = message_time.strftime("%H:%M:%S")

        messages.append(f"{message_time}\n{username} (You) > {input_buffer.text}\n")

        encrypted_data = encryption.encrypt(
            f"{message_time}\n{username} > {input_buffer.text}\n"
        )
        client_socket.sendall(encrypted_data)

        input_buffer.text = ""
        input_buffer.reset()

    @kb.add("c-q")
    def _(event):
        event.app.exit()
        shutdown_socket(client_socket, encryption, quit_message)

    @kb.add("up")
    def scroll_up(event):
        if message_scroll.vertical_scroll > 0:
            message_scroll.vertical_scroll -= 1
            event.app.invalidate()

    @kb.add("down")
    def scroll_down(event):
        if message_scroll.vertical_scroll < (len(messages) * 3) - 3:
            message_scroll.vertical_scroll += 1
            event.app.invalidate()
