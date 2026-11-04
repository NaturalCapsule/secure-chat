from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout import FloatContainer

from UI.widgets import *
import time


def ui_layout(messages, count_users, server_uptime, show_users, users_connected):

    def get_formatted_message(messages_list):
        formatted_message = []

        for message in messages_list:
            color = message[:7]
            message = message[7:] + "\n"

            formatted_message.append((color, message))

        return FormattedText(formatted_message)

    message_area.text = lambda: get_formatted_message(messages)

    time.sleep(0.3)
    usercount_widget.text = lambda: (
        "Users " + count_users[-1] if count_users else "Users 0"
    )

    server_uptime_widget.text = lambda: (
        "Server UpTime: " + str(server_uptime[-1])
        if server_uptime
        else "Server UpTime: N/A"
    )

    # user_list_widget.text = lambda: (
    #     "\n".join(users_connected[-1]) if users_connected else ""
    # )
    user_list_widget.text = lambda: get_formatted_message(users_connected[-1])

    floater_ui = HSplit([user_list])

    users_float = users_float_(show_users, floater_ui)

    ui = HSplit(
        [
            VSplit(
                [secure_chat_label, connection_indicator],
                height=1,
            ),
            seperator_1,
            VSplit(
                [
                    server_uptime_window,
                    usercount_window,
                ],
                height=2,
            ),
            seperator_3,
            message_scroll,
            seperator_2,
            VSplit([chat_indicator, buffer_control]),
        ]
    )

    root_container = FloatContainer(content=ui, floats=[users_float])

    return root_container
