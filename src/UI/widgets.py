from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import Float, ConditionalContainer
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.filters import Condition
from prompt_toolkit.widgets import Frame

input_buffer = Buffer()

connection_indicator = Window(FormattedTextControl("● Connected"))
secure_chat_label = Window(FormattedTextControl("Secure-Chat"))

usercount_widget = FormattedTextControl("")
usercount_window = Window(usercount_widget, wrap_lines=True)

server_uptime_widget = FormattedTextControl("")
server_uptime_window = Window(content=server_uptime_widget)

message_area = FormattedTextControl()
message_window = Window(content=message_area, wrap_lines=True)
message_scroll = ScrollablePane(message_window, show_scrollbar=True)

seperator_1 = Window(height=1, char="─", style="class:line")
seperator_2 = Window(height=1, char="─", style="class:line")
seperator_3 = Window(height=1, char="─", style="class:line")


chat_indicator = Window(FormattedTextControl(text="> "), width=2)

buffer_control = Window(
    content=BufferControl(buffer=input_buffer, focusable=True), height=1
)

user_list_widget = FormattedTextControl()

user_list = Window(
    content=user_list_widget,
    width=30,
    height=10,
)


def users_float_(show_users, floater_ui):

    users_float = Float(
        content=ConditionalContainer(
            content=Frame(body=floater_ui, title="USERS ONLINE"),
            filter=Condition(lambda: show_users[0]),
        ),
    )
    return users_float
