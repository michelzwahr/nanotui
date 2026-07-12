from nanotui import *

def main():
    app = App("Demo", True, "relative")

    top_frame = RectArea(color=DEFAULT)
    select_frame = RectArea(color=DEFAULT)
    log_frame = RectArea(color=DEFAULT)
    bottom_frame = RectArea(color=DEFAULT)

    info = LogBox(1, 1, parent=log_frame)

    def title_pos(title):
        title.x = title.parent.width // 2 - title.width
        title.y = title.parent.height // 2 - 1 

    title = Label("Demo", parent=top_frame, color=BLUE, style=BOLD)
    title.on_update(title_pos)


    def selection(selected_value):
        if selected_value == 4:
            info.add_and_log("ERROR!", bg_color=RED)
        else:
            info.add_and_log(f"Option {selected_value} selected!")

    select_label = Label("Please select an option:", x=1, y=1, color=DEFAULT, parent=select_frame, style=BLINK)
    left_select = Selection(1, 3, parent=select_frame, on_select=selection)
    left_select.add_options(
        Option("Option 1", 1),
        Option("Option 2", 2),
        Option("Option 3", 3),
        Option("ERROR", 4, bg_color=BG_RED)
    )


    def button_action():
        info.add_and_log("Button does ACTION")
    def button_select():
        info.add_and_log("Button does SELECT")

    action_button = Button(30, 3, "Action", parent=select_frame, color=DEFAULT, bg_color=BG_BRIGHT_BLUE, on_select=button_action)
    select_button = Button(40, 3, "Select", parent=select_frame, color=DEFAULT, bg_color=BG_BLUE, on_select=button_select)

    another_button = Button(1, 1, "Knopf")

    browser = FileExplorer(1, 1, parent=bottom_frame)

    app.create_grid(3, 3)
    app.add_to_grid([
        (top_frame, (1, 1)),
        (top_frame, (1, 3)),
        (select_frame, (2, 1)),
        (log_frame, (2, 2)),
        (log_frame, (3, 3)),
        (bottom_frame, (3, 1))
    ])   
    app.config_column(1, 5)
    app.config_column(2, 3)
    app.config_row(3, 3)
    app.config_row(2, 2)
    
    app.run(controls=True)


if __name__ == "__main__":
    main()
