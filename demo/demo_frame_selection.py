from nanotui import *

# idea: log every row of app.grid in logbox

def main():
    app = App("Frame Selection Demo", True, "relative")


    app.create_grid(2, 2)

    logbox = LogBox(30, 15)
    box_frame = RectArea(color=GREEN)

    boxsecelct = SelectBox("Auswahl")
    boxsecelct.add_options(
        Option("Option 1", 1),
        Option("Option 2", 2)
    )

    divider = HorizontalDivider(0, 2)
    button = Button(5, 5, "Hallo")


    logbox.add_and_log(f"element box_frame: width: {box_frame.width}, height: {box_frame.height}")

    selection = Selection(1, 1)
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

            frame: (1, 2),
            box_frame: (2, 2),
            divider: (2, 1),
            button: (2, 1)
        }
    )
    app.add_element(logbox)
    
    app.run(controls=True)


if __name__ == "__main__":
    main()
