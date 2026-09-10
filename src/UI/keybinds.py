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
        if input_buffer.text != "" and input_buffer.text.strip():
            if input_buffer.text == "<quit>":
                shutdown_socket(client_socket, encryption, quit_message)

            message_time = datetime.datetime.now()
            message_time = message_time.strftime("%I:%M %p")

            messages.append(
                f"[{message_time}] {username} (You) > {input_buffer.text}\n"
            )

            encrypted_data = encryption.encrypt(
                f"CHAT|[{message_time}] {username} > {input_buffer.text}\n"
            )

            message_length = len(encrypted_data)
            header = message_length.to_bytes(4, byteorder="big")

            client_socket.sendall(header + encrypted_data)

            input_buffer.text = ""
            input_buffer.reset()

            if message_scroll.vertical_scroll + 2 == (len(messages) * 2) - 16:
                message_scroll.vertical_scroll += 2

    @kb.add("c-q")
    def _(event):
        event.app.exit()
        shutdown_socket(client_socket, encryption, quit_message)

    @kb.add("up")
    def scroll_up(event):
        if message_scroll.vertical_scroll > 0:
            message_scroll.vertical_scroll -= 2
            event.app.invalidate()

    @kb.add("down")
    def scroll_down(event):
        if message_scroll.vertical_scroll < (len(messages) * 2) - 16:
            message_scroll.vertical_scroll += 2
            event.app.invalidate()
