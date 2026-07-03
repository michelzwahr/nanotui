import sys, os
import time
from .screen import clear_screen, hide_cursor, show_cursor
from .elements import SelectBox, Option, HorizontalDivider, Label
import tty, termios, select

def get_key():
    rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
    if not rlist:
        return None

    raw_input = sys.stdin.read(1)
    
    if raw_input == '\x1b':
        rlist_seq, _, _ = select.select([sys.stdin], [], [], 0.001)
        if rlist_seq:
            raw_input += sys.stdin.read(2)
        else:
            return 'ESC'
    mapping = {
        '\x1b[A': 'UP',
        '\x1b[B': 'DOWN',
        '\x1b[C': 'RIGHT',
        '\x1b[D': 'LEFT',
        '\n': 'ENTER',
        '\r': 'ENTER'
    }
    return mapping.get(raw_input, raw_input)

class App:
    def __init__(self, name, use_grid=False, grid_layout="absolute"):
        self.elements = []
        self.focused_element = 0
        self.running = True
        self.layer = 0
        self.name = name
        self.use_grid = use_grid
        self.grid_layout = grid_layout

        self.quit_box = SelectBox("Quit?", on_select=self.quit)
        self.option_quit = Option("Quit", 1)
        self.option_cancel = Option("Cancel", 0)
        self.quit_box.add_child(self.option_quit)
        self.quit_box.add_child(self.option_cancel)
        self.quit_box._calculate_dimensions()

        self.controls_line = HorizontalDivider(os.get_terminal_size().columns - 2)
        #self.add_element(self.controls_line)

        self.controls = Label("[ESC] go layer up / quit\t[q] quit\t[,] go left\t[.] go right\t[ENTER] select", x=2, y=os.get_terminal_size().columns - 1)
        #self.add_element(self.controls)


    def add_element(self, element: object):
        self.elements.append(element)

    def remove_element(self, element: object):
        self.elements.remove(element)

    def _walk_tree(self, elements=None):
        if elements is None:
            elements = self.elements

        for element in elements:
            yield element
            children = getattr(element, "children", None)
            if children:
                yield from self._walk_tree(children)

    def _selectable_elements(self):
        return [element for element in self._walk_tree() if hasattr(element, "select")]

    def _dynamic_elements(self):
        return [element for element in self._walk_tree() if hasattr(element, "update")]

    def _current_selectable(self):
        selectable_elements = self._selectable_elements()
        if not selectable_elements:
            return None, selectable_elements
        if self.focused_element >= len(selectable_elements):
            self.focused_element = 0
        return selectable_elements[self.focused_element], selectable_elements

    def change_focus(self, direction: int):
        current, selectable_elements = self._current_selectable()
        if not selectable_elements:
            return
        if current is not None:
            current.on_blur()
        self.focused_element = (self.focused_element + direction) % len(selectable_elements)
        selectable_elements[self.focused_element].on_focus()

    def change_layer(self, direction):
        self.layer += direction

    def open_quit_dialog(self):
        if self.quit_box not in self.elements:
            clear_screen()
            self.add_element(self.quit_box)
            self.quit_box.highlighted_option = self.quit_box.options.index(self.option_cancel)
        selectable_elements = self._selectable_elements()
        if selectable_elements:
            self.focused_element = selectable_elements.index(self.quit_box)
        self.layer = 1
        self.quit_box.select()

    def close_quit_dialog(self):
        if self.quit_box not in self.elements:
            return

        self.quit_box.erase()
        self.remove_element(self.quit_box)
        self.layer = 0
        self.draw_all()
        self.focused_element = 0
        selectable_elements = self._selectable_elements()
        if selectable_elements:
            selectable_elements[self.focused_element].on_focus()

    def quit(self, flag):
        if flag == 1:
            self.running=False
        else:
            self.close_quit_dialog()


    def draw_all(self):
        for element in self.elements:
            element.draw()

    def create_grid(self, rows, columns):
        self.grid = [[None for _ in range(columns)] + [[0, 0, 0]] for _ in range(rows)]
        self.grid.append([[0, 0, 0] for _ in range(columns)])


    def config_row(self, row, weight):
        self.grid[row-1][-1][0] = weight

    def config_column(self, column, weight):
        self.grid[-1][column-1][0] = weight

    def add_to_grid(self, grid_mapping: dict):

        for element, position in grid_mapping.items():
            row, col = position
            self.grid[row-1][col-1] = element
            print(self.grid)
            if element.width > self.grid[-1][col-1][2]:
                self.grid[-1][col-1][2] = element.width
            if element.height > self.grid[row-1][-1][2]:
                self.grid[row-1][-1][2] = element.height

            if element not in self.elements:
                self.add_element(element)

        self.update_grid()

    def update_grid(self):
        if self.grid_layout == "absolute":
            sum_height = 1
            for row in range(len(self.grid)) - 1:
                self.grid[row][-1][1] = sum_height
                sum_height += self.grid[row][-1][2]
            sum_width = 1
            for col in range(len(self.grid[0]) ) - 1:
                self.grid[-1][col][1] = sum_width
                sum_width += self.grid[-1][col][2]

        elif self.grid_layout == "relative":
            t_width = os.get_terminal_size().columns
            t_height = os.get_terminal_size().lines
            rows = len(self.grid) - 1
            columns = len(self.grid[0]) - 1

            for row in range(rows):
                self.grid[row][-1][2] = (t_height // rows) - 1
                self.grid[row][-1][1] = (t_height // rows) * row + 1

            for col in range(columns):
                self.grid[-1][col][2] = (t_width // columns) - 1
                self.grid[-1][col][1] = (t_width // columns) * col + 1

            for element in self.elements:
                pos_col, pos_row = self._find_element_in_grid(element)
                element.width = self.grid[-1][pos_col][2]
                element.height = self.grid[pos_row][-1][2]
                element.x = self.grid[-1][pos_col][1]
                element.y = self.grid[pos_row][-1][1]
            
    def _find_element_in_grid(self, element):
        for r_idx, row_lst in enumerate(self.grid):
            for c_idx, item in enumerate(row_lst):
                if item is element:
                    return r_idx, c_idx  # REIHE zuerst, dann SPALTE (Standard-Konvention)
        return None


    def run(self, clearscreen=True):

        is_unix = False
        try:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            is_unix = True
        except ImportError:
            pass

        try: 
            hide_cursor()
            if clearscreen:
                clear_screen()
            selectable_elements = self._selectable_elements()
            if selectable_elements and self.layer == 0:
                selectable_elements[self.focused_element].on_focus()

            old_size = []

            while self.running:

                for el in self._dynamic_elements():
                    el.update()

                current_terminal_size = [os.get_terminal_size().columns, os.get_terminal_size().lines]
                self.controls_line.y = current_terminal_size[1] - 2
                self.controls.y = current_terminal_size[1] - 1

                if current_terminal_size != old_size:
                    clear_screen()
                    self.draw_all()
                old_size = [os.get_terminal_size().columns, os.get_terminal_size().lines]

                
                key = get_key()

                match(key):
                    case "ESC":
                        if self.quit_box in self.elements:
                            self.quit(0)
                        elif self.layer == 1:
                            current, selectable_elements = self._current_selectable()
                            if current is not None:
                                current.on_blur()
                            self.layer = 0
                            if selectable_elements:
                                selectable_elements[self.focused_element].on_focus()
                        else:
                            self.open_quit_dialog()
                    case "q":
                        self.open_quit_dialog()
                    case ".":
                        if self.layer == 0:
                            self.change_focus(1)
                        else:
                            selectable_elements = self._selectable_elements()
                            if selectable_elements:
                                selectable_elements[self.focused_element].input(key)
                    case ",":
                        if self.layer == 0:
                            self.change_focus(-1)
                        else:
                            selectable_elements = self._selectable_elements()
                            if selectable_elements:
                                selectable_elements[self.focused_element].input(key)
                    case "ENTER":
                        selectable_elements = self._selectable_elements()
                        if selectable_elements:
                            if self.layer == 0:
                                selectable_elements[self.focused_element].select()
                                if hasattr(selectable_elements[self.focused_element], "enter"):
                                    self.change_layer(1)
                            elif self.layer == 1 and hasattr(selectable_elements[self.focused_element], "enter"):
                                selectable_elements[self.focused_element].enter()
                    case "r":
                        clear_screen()
                        self.draw_all()
                    case _:
                        pass
                    
                time.sleep(0.05)
        finally:
            show_cursor()
            if is_unix:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            clear_screen()
