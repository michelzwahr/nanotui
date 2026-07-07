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
    def __init__(self, name, use_grid=False, grid_layout="relative"):
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
        self.controls = Label("[ESC] go layer up / quit\t[q] quit\t[,] go left\t[.] go right\t[ENTER] select", x=2, y=os.get_terminal_size().columns - 1)
        self.show_controls = False
        self.test = None


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
        self.grid = [[[] for _ in range(columns)] + [[1, 0, 0]] for _ in range(rows)]
        self.grid.append([[1, 0, 0] for _ in range(columns)])


    def config_row(self, row, weight):
        self.grid[row-1][-1][0] = weight

    def config_column(self, column, weight):
        self.grid[-1][column-1][0] = weight

    def add_to_grid(self, grid_mapping: list):
        # group all positions by element with a dict
        element_positions = {}
        for element, position in grid_mapping:
            if element not in element_positions:
                element_positions[element] = []
            element_positions[element].append(position)

        # go through every element in the element group
        for element, positions in element_positions.items():
            # collect all rows and columns
            rows = [pos[0] for pos in positions]
            cols = [pos[1] for pos in positions]
            
            # calculate the min and max area
            min_row, max_row = min(rows), max(rows)
            min_col, max_col = min(cols), max(cols)
            
            # take all cells in this area
            for row in range(min_row, max_row + 1):
                for col in range(min_col, max_col + 1):
                    
                    if element.fill_grid is True:
                        # cell is empty or is already been used by this element
                        if not self.grid[row-1][col-1] or self.grid[row-1][col-1] == element:
                            self.grid[row-1][col-1] = element
                        else:
                            # cell is used by an other element
                            clear_screen()
                            raise ValueError(f"Grid ({row-1}, {col-1}) is already been used")
                    else:
                        # multiple elements in one cell
                        if element not in self.grid[row-1][col-1]:
                            self.grid[row-1][col-1].append(element)
                
            if element not in self.elements:
                self.add_element(element)

        self.update_grid()

    def update_grid(self):
        if self.grid_layout == "relative":
            t_width = os.get_terminal_size().columns
            t_height = os.get_terminal_size().lines - 2 if self.show_controls else os.get_terminal_size().lines
            rows = len(self.grid) - 1
            columns = len(self.grid[0]) - 1

            def build_spans(weights, total_size):
                total_weight = sum(max(weight, 1) for weight in weights)
                spans = []
                start = 1
                remaining = total_size

                for index, weight in enumerate(weights):
                    normalized_weight = max(weight, 1)
                    if index == len(weights) - 1:
                        span = remaining
                    else:
                        span = max(1, (total_size * normalized_weight) // total_weight)
                        remaining -= span
                    spans.append((start, span))
                    start += span

                return spans

            row_spans = build_spans([self.grid[row][-1][0] for row in range(rows)], t_height)
            col_spans = build_spans([self.grid[-1][col][0] for col in range(columns)], t_width)

            for row, (start, span) in enumerate(row_spans):
                self.grid[row][-1][1] = start
                self.grid[row][-1][2] = span - 1

            for col, (start, span) in enumerate(col_spans):
                self.grid[-1][col][1] = start
                self.grid[-1][col][2] = span - 1

            for i, element in enumerate(self.elements):
                try:
                    pos_lst = self._find_element_in_grid(element)
                    if not pos_lst:
                        continue
                    
                    # Definiere direkt die erste Zeile und Spalte für später
                    first_row, first_col = pos_lst[0]

                    if element.fill_grid is True:
                        width = 0
                        height = 0
                        used_cols = []
                        used_rows = []
                        
                        # KORREKTUR 1: Zuerst pos_row, dann pos_col entpacken!
                        for pos_row, pos_col in pos_lst:
                            if pos_col not in used_cols:
                                width += self.grid[-1][pos_col][2]
                                used_cols.append(pos_col)
                            if pos_row not in used_rows:
                                height += self.grid[pos_row][-1][2]
                                used_rows.append(pos_row)
                                
                        if hasattr(element, "set_size"):
                            element.set_size(width=width, height=height)
                        
                        # KORREKTUR 2: x nutzt die Spalte (col), y nutzt die Zeile (row)
                        element.x = self.grid[-1][first_col][1]
                        element.y = self.grid[first_row][-1][1]
                        self.test = element
                    else:
                        # KORREKTUR 3: Auch hier für den Offset-Fall korrigieren
                        element.x = self.grid[-1][first_col][1] + element.offset_x
                        element.y = self.grid[first_row][-1][1] + element.offset_y

                except TypeError as e:
                    continue
            
    def _find_element_in_grid(self, element):
        position = []
        for r_idx, row_lst in enumerate(self.grid):
            for c_idx, item in enumerate(row_lst):
                if not isinstance(item, list):
                    # Geändert: '==' statt 'is' und zusätzliche Klammern bei append
                    if item == element:
                        position.append((r_idx, c_idx))
                else:
                    for el in item:
                        # Geändert: '==' statt 'is' und zusätzliche Klammern bei append
                        if el == element:
                            position.append((r_idx, c_idx))
        return position


    def run(self, clearscreen=True, controls=False):

        

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

            if controls:
                self.show_controls = True
                self.add_element(self.controls_line)
                self.add_element(self.controls)

            while self.running:

                

                for el in self._dynamic_elements():
                    el.update()

                current_terminal_size = [os.get_terminal_size().columns, os.get_terminal_size().lines]
                self.controls_line.y = current_terminal_size[1] - 2
                self.controls.y = current_terminal_size[1] - 1



                if current_terminal_size != old_size:
                    if self.use_grid:
                        self.update_grid()
                    clear_screen()
                    self.draw_all()
                    #raise Exception(self.test.x, self.test.y, self.test.width, self.test.height)
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
                    case "g":
                        raise Exception(self.test.x, self.test.y, self.test.width, self.test.height)
                    case _:
                        pass
                    
                time.sleep(0.05)
        finally:
            show_cursor()
            if is_unix:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            clear_screen()
