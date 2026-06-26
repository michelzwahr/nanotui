from nanotui import App, Frame, Label, Selection, Option, clear_screen


def main():
    app = App("Frame Selection Demo")

    frame = Frame(symbol="#", x=10, y=4)

    label = Label("Select an Option", x=2, y=1, parent=frame)
    selection = Selection(2, 4, parent=frame)

    def on_select(value):
        label.set_text(f"Selected: {value}")
        clear_screen()
        app.draw_all()

    selection.on_select = on_select
    selection.add_option(Option("One", 1))
    selection.add_option(Option("Two", 2))
    selection.add_option(Option("Three", 3))

    app.add_element(frame)
    app.draw_all()
    app.run()


if __name__ == "__main__":
    main()
