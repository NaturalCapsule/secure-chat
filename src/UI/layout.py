from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl

from UI.widgets import *


def ui_layout(messages):
    ui = HSplit(
        [
            VSplit(
                [secure_chat_label, connection_indicator],
                height=1,
            ),
            seperator_1,
            VSplit(
                [
                    Window(FormattedTextControl("Hello User!")),
                    Window(FormattedTextControl("This is a test!")),
                ],
                height=2,
            ),
            seperator_3,
            Window(FormattedTextControl(lambda: "\n".join(messages)), wrap_lines=True),
            seperator_2,
            VSplit([chat_indicator, buffer_control]),
        ]
    )

    return ui
