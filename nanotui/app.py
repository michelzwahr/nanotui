import sys
import time
from .screen import clear_screen, hide_cursor, show_cursor
from .elements import SelectBox, Option
import tty, termios, select

def get_key():
    rlist, _, _ = select.select([sys.stdin], [], [], 0.0)
    if not rlist:
        return None  # Keine Taste gedrückt
        
    # 2. Den GESAMTEN Puffer auslesen, der JETZT bereitsteht
    # Eine Pfeiltaste schickt ihre 3 Zeichen zeitgleich, sie sind also alle hier drin.
    raw_input = sys.stdin.read(1)
    
    # Wenn es mit Escape anfängt, schauen wir, was noch im Stream liegt
    if raw_input == '\x1b':
        # Schau nach, ob sofort weitere Zeichen da sind
        rlist_seq, _, _ = select.select([sys.stdin], [], [], 0.001)
        if rlist_seq:
            # Es sind Zeichen da! Wir lesen die restlichen (meistens 2, z.B. '[A')
            raw_input += sys.stdin.read(2)
        else:
            # Es war wirklich nur die isolierte ESC-Taste
            return 'ESC'
    
    # 3. Auswertung der gelesenen Zeichenkette
    mapping = {
        '\x1b[A': 'UP',
        '\x1b[B': 'DOWN',
        '\x1b[C': 'RIGHT',
        '\x1b[D': 'LEFT',
        '\n': 'ENTER',
        '\r': 'ENTER'
    }
    
    # Wenn es im Mapping ist, gib den lesbaren String zurück, ansonsten das Zeichen selbst
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

    def add_element(self, element: object):
        self.elements.append(element)

        if hasattr(element, "update"):
            self.dynamic_elemets.append(element)

        if hasattr(element, "select"):
            self.selectable_elements.append(element)

    def change_focus(self, direction: int):
        if not self.selectable_elements: return 
        self.selectable_elements[self.focused_element].on_blur()
        self.focused_element = (self.focused_element + direction) % len(self.selectable_elements)
        self.selectable_elements[self.focused_element].on_focus()

    def change_layer(self, direction):
        self.layer += direction

    def quit(self):
        pass

    def draw_all(self):
        for element in self.elements:
            element.draw()

    def run(self):

        is_unix = False
        try:
            import tty, termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setraw(fd)  # Schaltet das gesamte Terminal ab JETZT stumm
            is_unix = True
        except ImportError:
            pass

        try: 
            hide_cursor()
            while self.running:

                for el in self.dynamic_elemets:
                    el.update()

                if self.selectable_elements and self.layer == 0:
                    self.selectable_elements[self.focused_element].on_focus()
                
                key = get_key()

                match(key):
                    case "ESC":
                        if self.layer == 0:
                            self.running = False
                        else:
                            self.change_layer(-1)
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
                        # Das fängt alle anderen Tasten (und None) ab, damit nichts passiert
                        pass
                    



                time.sleep(0.05)
        finally:
            # Reißleine: Egal was passiert (selbst bei einem Absturz),
            # wir stellen das Terminal für den User wieder sauber her!
            show_cursor()
            if is_unix:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            clear_screen()
