import sys, os
import time
from .screen import clear_screen, hide_cursor, show_cursor
from .elements import SelectBox, Option
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
    def __init__(self, name):
        self.elements = []
        self.focused_element = 0
        self.running = True
        self.layer = 0
        self.name = name
        self.quit_box = SelectBox("Quit?", on_select=self.quit)
        self.option_quit = Option("Quit", 1)
        self.option_cancel = Option("Cancel", 0)
        self.quit_box.add_child(self.option_quit)
        self.quit_box.add_child(self.option_cancel)
        self.quit_box._calculate_dimensions()

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

    def quit(self, value):
        if value == 1:
            self.running=False
        else:
            self.close_quit_dialog()


    def draw_all(self):
        for element in self.elements:
            element.draw()

    def run(self):

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
            selectable_elements = self._selectable_elements()
            if selectable_elements and self.layer == 0:
                selectable_elements[self.focused_element].on_focus()

            old_size = []

            while self.running:

                for el in self._dynamic_elements():
                    el.update()

                
                current_terminal_size = [os.get_terminal_size().columns, os.get_terminal_size().lines]
                if current_terminal_size != old_size:
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
