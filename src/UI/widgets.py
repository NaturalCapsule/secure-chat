from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.layout.containers import Window

input_buffer = Buffer()

connection_indicator = Window(FormattedTextControl("● Connected"))
secure_chat_label = Window(FormattedTextControl("Secure-Chat"))

seperator_1 = Window(height=1, char="─", style="class:line")
seperator_2 = Window(height=1, char="─", style="class:line")
seperator_3 = Window(height=1, char="─", style="class:line")


chat_indicator = Window(FormattedTextControl(text="> "), width=2)


buffer_control = Window(
    content=BufferControl(buffer=input_buffer, focusable=True), height=1
)
