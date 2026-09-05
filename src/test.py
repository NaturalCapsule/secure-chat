from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

# 1. Create an input buffer to hold user text
input_buffer = Buffer()

# 2. Design the layout
# We use an empty window that takes up remaining space (acting as a spacer)
# and push the input window to the absolute bottom.
root_container = HSplit(
    [
        Window(
            content=FormattedTextControl(
                "Application Content Area\nPress Enter to submit."
            )
        ),
        Window(),  # This empty window stretches to fill available space, pushing the next item down
        HSplit(
            [
                Window(height=1, char="-", style="class:line"),  # Optional divider line
                Window(
                    height=1,
                    content=BufferControl(buffer=input_buffer, focusable=True),
                ),
            ]
        ),
    ]
)

layout = Layout(root_container)

# 3. Handle submissions (e.g., when the user presses Enter)
kb = KeyBindings()


@kb.add("enter")
def _(event):
    text = input_buffer.text
    # Process your text input here
    print(f"User entered: {text}")

    # Reset the buffer or exit the application
    input_buffer.reset()
    event.app.exit(result=text)


@kb.add("c-c")  # Ctrl+C to exit
def _(event):
    event.app.exit()


# 4. Build and run the full-screen application
app = Application(
    layout=layout,
    key_bindings=kb,
    full_screen=True,  # This forces the app to fill the entire terminal screen
)

if __name__ == "__main__":
    app.run()
