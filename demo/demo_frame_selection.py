from nanotui import *


def main():
    app = App("Frame Selection Demo", True, "relative")

    app.create_grid(2, 2)

    frame = Frame(y_symbol="|", x_symbol="-", x=10, y=4, color=DEFAULT)

    label = Label("Select an Option", x=2, y=1, parent=frame, color=DEFAULT)
    selection = Selection(2, 4, parent=frame)

    rechteck = RectArea(width=20, height=3, x=80, y=1, color=DEFAULT, bg_color=BG_RED)

    selection2 = Selection(2, 2, parent=rechteck)

    knopf = Button(80, 10, "Button")

    rahmen = Frame()

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

    selection2.add_option(Option("One", 1, color=WHITE))
    selection2.add_option(Option("Two", 2, color=DEFAULT))
    selection2.add_option(Option("Three", 3, color=DEFAULT))

    app.add_element(frame)
    app.add_element(rechteck)
    app.add_element(knopf)
    app.add_to_grid({
        frame: (1, 1),
        rechteck: (1, 2),
        knopf: (2, 2),
        rahmen: (2, 1)
    })
    app.config_column(1, 2)
    app.draw_all()
    app.run()


if __name__ == "__main__":
    main()
