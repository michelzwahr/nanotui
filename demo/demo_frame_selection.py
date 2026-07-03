from nanotui import *


def main():
    app = App("Frame Selection Demo")

    frame = Frame(y_symbol="|", x_symbol="-", x=10, y=4, color=DEFAULT)

    label = Label("Select an Option", x=2, y=1, parent=frame, color=DEFAULT)
    selection = Selection(2, 4, parent=frame)

    rechteck = RectArea(width=20, height=3, x=80, y=1, color=DEFAULT, bg_color=BG_RED)

    knopf = Button(80, 10, "Button")

    def on_select(value=None):
        if value:
            label.set_text(f"Selected: {value}")
        else:
            label.set_text("Knopf gedrückt")
        clear_screen()
        app.draw_all()

    selection.on_select = on_select
    knopf.on_select = on_select
    selection.add_option(Option("One", 1, color=DEFAULT))
    selection.add_option(Option("Two", 2, color=DEFAULT))
    selection.add_option(Option("Three", 3, color=DEFAULT))

    app.add_element(frame)
    app.add_element(rechteck)
    app.add_element(knopf)
    app.draw_all()
    app.run()


if __name__ == "__main__":
    main()
