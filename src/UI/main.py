from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, Window, VSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.key_binding import KeyBindings


kb = KeyBindings()

messages = []


@kb.add("c-q")
def _(event):
    event.app.exit()


@kb.add("enter")
def send(event):
    messages.append(input_buffer.text)

    input_buffer.text = ""
    input_buffer.reset()


input_buffer = Buffer()


ui = HSplit(
    [
        VSplit(
            [
                Window(FormattedTextControl("Secure-Chat")),
                Window(FormattedTextControl("● Connected")),
            ],
            height=1,
        ),
        Window(height=1, char="─", style="class:line"),
        VSplit(
            [
                Window(FormattedTextControl("Hello User!")),
                Window(FormattedTextControl("This is a test!")),
            ],
            height=2,
        ),
        Window(height=1, char="─", style="class:line"),
        Window(FormattedTextControl(lambda: "\n".join(messages)), wrap_lines=True),
        Window(height=1, char="─", style="class:line"),
        VSplit(
            [
                Window(FormattedTextControl(text="> "), width=2),
                Window(
                    content=BufferControl(buffer=input_buffer, focusable=True), height=1
                ),
            ]
        ),
    ]
)


layout = Layout(ui)


app = Application(layout=layout, key_bindings=kb, full_screen=True)
app.run()
