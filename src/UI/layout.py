from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl

from UI.widgets import *


def ui_layout(messages, count_users):
    message_area.text = lambda: "\n".join(messages)

    usercount_widget.text = lambda: "Users " + count_users[-1]
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
                    Window(FormattedTextControl("This is a test!")),
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
