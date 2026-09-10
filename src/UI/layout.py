from prompt_toolkit.layout.containers import HSplit, VSplit

from UI.widgets import *


def ui_layout(messages, count_users, server_uptime):
    message_area.text = lambda: "\n".join(messages)

    usercount_widget.text = lambda: "Users " + count_users[-1]
    server_uptime_widget.text = lambda: "Server UpTime: " + str(server_uptime[-1])

    ui = HSplit(
        [
            VSplit(
                [secure_chat_label, connection_indicator],
                height=1,
            ),
            seperator_1,
            VSplit(
                [
                    usercount_window,
                    server_uptime_window,
                ],
                height=2,
            ),
            seperator_3,
            message_scroll,
            seperator_2,
            VSplit([chat_indicator, buffer_control]),
        ]
    )

    return ui
