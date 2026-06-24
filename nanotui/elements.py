# nanotui/elements.py
from .colors import *
from .screen import *
import time
import os

class Element:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 0
        self.height = 1
        self.is_focused = False

    def erase(self):
        if self.width > 0:
            for i in range(self.height):
                draw_at((self.y + i), self.x, " " * self.width)
            #self.length = 0
            #self.height = 0

    def draw(self):
        pass

    def on_focus(self):
        pass

    def on_blur(self):
        pass

class LoadingBar(Element):
    def __init__(self, x, y, steps=5, symbol=".", interval=0.4, color=WHITE, bg_color="", style="", label=None):
        super().__init__(x, y)
        self.steps = steps
        self.symbol = symbol
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.interval = interval
        self.label = label
        self.width = steps

    def load(self):
        for i in range(1, self.steps + 1):
            bar_string = ctext(text=self.symbol, color=self.color, bg_color=self.bg_color, style=self.style) * i
            draw_at(self.y, self.x, bar_string)
            
            if self.label:
                percentage = int(i * (100 / self.steps))
                self.label.set_percentage(percentage)
                
            time.sleep(self.interval)

    def draw(self):
        self.load()


class Label(Element):
    def __init__(self, text, element=None, x=None, y=None, color=WHITE, bg_color="", style=""):
        self.text = text
        if x is not None and y is not None:
            self.x = x
            self.y = y
        elif element is not None:
            self.x = element.x
            self.y = element.y - 1
            element.label = self
        else:
            self.x = 1
            self.y = 1
        self.width = len(text)
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.output = self.text
        super().__init__(self.x, self.y)

    def draw(self):
        draw_at(self.y, self.x, ctext(self.output, self.color, self.bg_color, self.style))
        

    def set_percentage(self, percentage):
        output = f"{self.text} {percentage}%"
        #draw_at(self.y, self.x, ctext(output, self.color, self.bg_color, self.style))
        self.draw()
        self.width = len(output)

class Spinner(Element):
    def __init__(self, x, y, text="Loading", color=WHITE, interval=0.1, length=5):
        super().__init__(x, y)
        self.text = text
        self.color = color
        self.phases = ["|", "/", "-", "\\"]
        self.current_phase = 0
        self.width = 1
        self.interval = interval
        self.length = length

    def next(self):
        symbol = self.phases[self.current_phase % 4]
        output = f"{ctext(symbol, self.color)} {self.text}"
        draw_at(self.y, self.x, output)
        self.current_phase += 1

    def spin(self):
        for i in range(int(self.length/self.interval)):
            self.next()
            time.sleep(self.interval)
    
    def draw(self):
        self.spin()

class LogBox(Element):
    def __init__(self, x, y, height):
        super().__init__(x, y)
        self.height = height
        self.text = []
    
    def add_entry(self, entry):
        self.text.append(entry)
        if len(self.text) > self.height:
            self.text.pop(0)
        if len(entry) > self.width:
            self.width = len(entry)

    def log(self):
        for i, element in enumerate(self.text):
            draw_at(self.y + i, self.x, element)
    
    def add_and_log(self, entry):
        self.add_entry(entry)
        self.log()

    def draw(self):
        self.log()

class TestSection(Element):
    def __init__(self, x, y, text, color=WHITE, bg_color=""):
        super().__init__(x, y)
        self.is_selected = False
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.width = len(self.text)

    def draw(self):
        draw_at(self.y, self.x, ctext(text=self.text, color=self.color, bg_color=self.bg_color))
    
    def on_focus(self):
        draw_at(self.y, self.x, ctext(text=self.text, color=self.color, bg_color=self.bg_color, style=REVERSE))
        self.width = len(self.text)

    def on_blur(self):
        draw_at(self.y, self.x, ctext(text=self.text, color=self.color, bg_color=self.bg_color, style=RESET))
        self.width = len(self.text)
    
    def select(self):
        self.erase()
        
class Selection(Element):
    def __init__(self, x, y, on_select=None):
        super().__init__(x, y)
        self.options = []
        self.selected = False
        self.highlighted_option = 0
        self.on_select = on_select

    def add_option(self, option):
        self.options.append(option)
        if len(option.text) > self.width:
            self.width = len(option.text)
        self.height = len(self.options)
        self.draw()

    def remove_option(self, option):
        self.options.remove(option)
        self.height = len(self.options)
        self.draw()
    
    def draw(self):
        if self.options:
            for i, op in enumerate(self.options):
                op.y = self.y + i
                op.x = self.x
                op.on_blur()
    
    def on_focus(self):
        if self.options:
            for i, op in enumerate(self.options):
                op.on_focus()

    def on_blur(self):
        self.draw()
        self.selected = False
    
    def select(self):
        self.selected = True
        self.draw()
        self.options[self.highlighted_option].on_focus()

    def change_highlight(self, direction):
        if not self.options: return
        self.options[self.highlighted_option].on_blur()
        self.highlighted_option = (self.highlighted_option + direction) % len(self.options)
        self.options[self.highlighted_option].on_focus()
    
    def input(self, key):
        match(key):
            case ",":
                self.change_highlight(-1)
            case ".":
                self.change_highlight(1)

    def get_value(self):
        return self.options[self.highlighted_option].value
    
    def enter(self):
        if self.on_select:
            self.on_select(self.get_value())

    
class Option(Element):
    def __init__(self, text, value, color=WHITE, bg_color=""):
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.value = value
        self.x = None
        self.y = None
        self.height = 1
        self.width = len(text)
    
    def on_blur(self):
        draw_at(self.y, self.x, ctext(self.text, self.color, self.bg_color, RESET))

    def on_focus(self):
        draw_at(self.y, self.x, ctext(self.text, self.color, self.bg_color, REVERSE))

    def draw(self):
        draw_at(self.y, self.x, ctext(self.text, self.color, self.bg_color))


class SelectBox(Element):
    def __init__(self, text, x=None, y=None, frame_symbol="#", color=WHITE, bg_color="", style="", on_select=None):
        super().__init__(x, y)
        self.options = []
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.frame = frame_symbol
        self.highlighted_option = 0
        self.selected = False
        self.on_select = on_select

        self.height = 7

        if not self.x:
            self.set_x = False
        else: self.set_x = True

        if not self.y:
            self.set_y = False
        else: self.set_y = True
            
        self._calculate_dimensions()
    
    def clear(self):
        for i in range(self.height+1):
                draw_at((self.y + i), self.x, " " * (self.width+1))
    
    def draw(self):
        self.clear()
        self._calculate_dimensions()
        draw_at(self.y, self.x, self.frame * (self.width))
        for i in range(self.height):
            draw_at(self.y + i, self.x, self.frame)
            draw_at(self.y + i, self.x + self.width, self.frame)
        draw_at(self.y + self.height - 1, self.x, self.frame * (self.width))

        draw_at(self.y + 2, self.x + ((self.width - len(self.text)+1) // 2), self.text)
        all_options = 1
        for l, op in enumerate(self.options):
            op.y = self.y + 4

            if l == 0:
                op.x = self.x + 2
                all_options += len(op.text) + 1
            else:
                op.x = self.x + 1 + all_options
                all_options += len(op.text) + 1
                
            op.on_blur()
    
    def add_option(self, option):
        self.options.append(option)
        self._calculate_dimensions()
        self.draw()

    def _calculate_dimensions(self):
        count = 2
        for option in self.options:
            count += len(option.text) + 1
        if count >= len(self.text) + 4:
            self.width = count
        else:
            self.width = len(self.text) + 4

        if not self.set_x:
            self.x = (os.get_terminal_size().columns - self.width) // 2
        if not self.set_y:
            self.y = (os.get_terminal_size().lines - 7) // 2

        #self.length = self.width + 1
        
    
    def change_highlight(self, direction):
        if not self.options: return
        self.options[self.highlighted_option].on_blur()
        self.highlighted_option = (self.highlighted_option + direction) % len(self.options)
        self.options[self.highlighted_option].on_focus()

    def input(self, key):
        match(key):
            case ",":
                self.change_highlight(-1)
            case ".":
                self.change_highlight(1)
    
    def on_focus(self):
        if self.options:
            for i, op in enumerate(self.options):
                op.on_focus()

    def on_blur(self):
        self.draw()
        self.selected = False
    
    def select(self):
        self.selected = True
        self.draw()
        self.options[self.highlighted_option].on_focus()

    def enter(self):
        if self.on_select:
            self.on_select(self.options[self.highlighted_option].value)

class Frame(Element):
    def __init__(self, symbol="#", element=None, x=None, y=None, height=None, width=None, color=WHITE, bg_color=""):
        super().__init__(x, y)
        self.symbol = symbol
        self.element = element
        if x and y:
            self.x = x
            self.y = y
        elif element:
            self.x = element.x -1
            self.y = element.y - 1
            
            element.frame = self
        else:
            self.x = 1
            self.y = 1

        if width and height:
            self.height = height
            self.width = width
        elif element:
            self.width = element.width + 1 if hasattr(element, "width") else (element.length + 1 if hasattr(element, "length") else 0)
            self.height = element.height + 1
        else:
            self.width = 5
            self.height = 5
        self.color = color
        self.bg_color = bg_color

        self.draw()

    def draw(self):
        draw_at(self.y, self.x, ctext(self.symbol * self.width, self.color, self.bg_color))
        draw_at(self.y + self.height, self.x, ctext(self.symbol * self.width, self.color, self.bg_color))
        for i in range(self.height + 1):
            draw_at(self.y + i, self.x, ctext(self.symbol, self.color, self.bg_color))
            draw_at(self.y + i, self.x + self.width, ctext(self.symbol, self.color, self.bg_color))

class HorizontalDivider(Element):
    def __init__(self, y, symbol="-", color=WHITE, bg_color="", style=""):
        super().__init__(1, y)
        self.symbol = symbol
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.width = os.get_terminal_size().columns

    def draw(self):
        for i in range(os.get_terminal_size().columns):
            draw_at(self.y, i, ctext(self.symbol, self.color, self.bg_color, self.style))
        self.width = os.get_terminal_size().columns

