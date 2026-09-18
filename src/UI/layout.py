from prompt_toolkit.layout.containers import HSplit, VSplit
from prompt_toolkit.layout import FloatContainer

from UI.widgets import *


def ui_layout(messages, count_users, server_uptime, show_users, users_connected):
    message_area.text = lambda: "\n".join(messages)

    try:
        usercount_widget.text = lambda: "Users " + count_users[-1]
        server_uptime_widget.text = lambda: "Server UpTime: " + str(server_uptime[-1])
        user_list_widget.text = lambda: "\n".join(users_connected[-1])
    except Exception:
        pass

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
