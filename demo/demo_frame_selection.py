from nanotui import *

# idea: log every row of app.grid in logbox

def main():
    app = App("Frame Selection Demo", True, "relative")

    def on_select(value):
        box.add_and_log(f"Button gedrückt: {value}")

    app.create_grid(3, 3)

    box = LogBox(2, 2)

    auswahl = Selection(1, 1, on_select=on_select)

    auswahl.add_options(
        Option("Auswahl1", 1),
        Option("Auswahl2", 2),
        Option("Auswahl3", 3)
    )

    frame1 = RectArea(element=box)
    frame2 = Frame()
    frame3 = RectArea(element=auswahl)

    app.add_to_grid([
        (frame1, (1, 1)),
        (frame2, (2, 1)),
        (frame3, (3, 1)),
        (frame1, (1, 3)),
        (frame2, (2, 3)),
        (frame3, (3, 3))
    ])
    
    
    app.run(controls=True)


if __name__ == "__main__":
    main()
