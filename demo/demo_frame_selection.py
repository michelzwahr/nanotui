from nanotui import *


def main():
    app = App("Frame Selection Demo", True, "relative")


    app.create_grid(2, 2)

    logbox = LogBox(1, 1)
    box_frame = RectArea(element=logbox, color=GREEN)


    top_left = RectArea(color=RED)

    def on_select(value):
        logbox.add_and_log(f"Neuer Eintrag: {value}")

    selection = Selection(1, 1, on_select=on_select)
    frame = Frame(x_symbol="~", y_symbol="|", element=selection)

    selection.add_options(
        Option("Option 1", 1),
        Option("Option 2", 2),
        Option("Option 3", 3),
        Option("Option 4", 4),
        Option("Option 5", 5),
        Option("Option 6", 6)
    )

    app.create_grid(2, 2)
    app.config_column(2, 3)
    app.config_row(2, 3)
    app.add_to_grid(
        {
            top_left: (1, 1),
            frame: (1, 2),
            box_frame: (2, 2)
        }
    )
    
    app.run(controls=True)


if __name__ == "__main__":
    main()
