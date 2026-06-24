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
        self.selectable_elements = []
        self.dynamic_elemets = []
        self.focused_element = 0
        self.running = True
        self.layer = 0
        self.name = name
        self.quit_box = SelectBox("Quit?", on_select=self.quit)
        self.option_quit = Option("Quit", 1)
        self.option_cancel = Option("Cancel", 0)
        self.quit_box.add_option(self.option_quit)
        self.quit_box.add_option(self.option_cancel)

    def add_element(self, element: object):
        self.elements.append(element)

        if hasattr(element, "update"):
            self.dynamic_elemets.append(element)

        if hasattr(element, "select"):
            self.selectable_elements.append(element)

    def remove_element(self, element: object):
        self.elements.remove(element)

        if hasattr(element, "update"):
            self.dynamic_elemets.remove(element)

        if hasattr(element, "select"):
            self.selectable_elements.remove(element)

    def change_focus(self, direction: int):
        if not self.selectable_elements: return 
        self.selectable_elements[self.focused_element].on_blur()
        self.focused_element = (self.focused_element + direction) % len(self.selectable_elements)
        self.selectable_elements[self.focused_element].on_focus()

    def change_layer(self, direction):
        self.layer += direction

    def quit(self, value):
        if value == 1:
            self.running=False
        else:
            if self.quit_box in self.elements:
                self.change_layer(-1)
                self.remove_element(self.quit_box)
                self.draw_all()
                self.focused_element = 0
                self.selectable_elements[self.focused_element].on_focus()


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
            if self.selectable_elements and self.layer == 0:
                self.selectable_elements[self.focused_element].on_focus()

            old_size = []

            while self.running:

                for el in self.dynamic_elemets:
                    el.update()

                
                current_terminal_size = [os.get_terminal_size().columns, os.get_terminal_size().lines]
                if current_terminal_size != old_size:
                    self.draw_all()
                old_size = [os.get_terminal_size().columns, os.get_terminal_size().lines]
                
                key = get_key()

                match(key):
                    case "ESC":
                        if self.layer == 0:
                            clear_screen()
                            self.add_element(self.quit_box)
                            self.quit_box.highlighted_option = self.quit_box.options.index(self.option_cancel)
                            self.focused_element = self.selectable_elements.index(self.quit_box)
                            self.layer = 1
                            self.quit_box.select()
                        else:
                            self.quit(0)
                    case ".":
                        if self.layer == 0:
                            self.change_focus(1)
                        else:
                            self.selectable_elements[self.focused_element].input(key)
                    case ",":
                        if self.layer == 0:
                            self.change_focus(-1)
                        else:
                            self.selectable_elements[self.focused_element].input(key)
                    case "ENTER":
                        if self.selectable_elements:
                            if self.layer == 0:
                                self.selectable_elements[self.focused_element].select()
                                self.change_layer(1)
                            elif self.layer == 1 and hasattr(self.selectable_elements[self.focused_element], "enter"):
                                self.selectable_elements[self.focused_element].enter()
                    case _:
                        pass
                    
                time.sleep(0.05)
        finally:
            show_cursor()
            if is_unix:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            clear_screen()
