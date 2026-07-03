# nanotui/elements.py
from .colors import *
from .screen import *
import time
import os


class Element:
    def __init__(self, x=0, y=0, parent=None):
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.parent = None
        self.children = []
        self.width = getattr(self, "width", 0)
        self.height = getattr(self, "height", 1)
        self.is_focused = False

        if parent is not None:
            parent.add_child(self)

    def add_child(self, child):
        if child.parent is self:
            return child
        if child.parent is not None:
            child.parent.remove_child(child)
        child.parent = self
        self.children.append(child)
        self.request_layout()
        return child

    def remove_child(self, child):
        self.children.remove(child)
        child.parent = None
        self.request_layout()
        return child
    
    def add_children(self, *children):
        for child in children:
            if child.parent is self:
                continue
            if child.parent is not None:
                child.parent.remove_child(child)
            child.parent = self
            self.children.append(child)
        self.request_layout()

    def remove_children(self, *children):
        for child in children:
            self.children.remove(child)
            child.parent = None
        self.request_layout()

    def global_x(self):
        if self.parent is None:
            return self.x
        return self.parent.global_x() + self.x

    def global_y(self):
        if self.parent is None:
            return self.y
        return self.parent.global_y() + self.y

    def erase(self):
        if self.width > 0:
            for i in range(self.height):
                draw_at(self.global_y() + i, self.global_x(), " " * (self.width+1))

    def draw_children(self):
        for child in self.children:
            child.draw()

    def draw(self):
        self.draw_children()

    def on_focus(self):
        self.is_focused = True

    def on_blur(self):
        self.is_focused = False

    def request_layout(self):
        if self.parent is not None and hasattr(self.parent, "_calculate_dimensions"):
            self.parent._calculate_dimensions()
            self.parent.request_layout()

class LoadingBar(Element):
    def __init__(self, x, y, steps=5, symbol=".", interval=0.4, color=WHITE, bg_color="", style="", label=None, parent=None):
        super().__init__(x, y, parent=parent)
        self.steps = steps
        self.symbol = symbol
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.interval = interval
        self.label = label
        self.width = steps

        if self.label is not None and self.label.parent is None:
            self.add_child(self.label)
            self.label.x = 0
            self.label.y = -1
        elif self.label is not None:
            self.label.x = 0
            self.label.y = -1

    def load(self):
        for i in range(1, self.steps + 1):
            bar_string = ctext(text=self.symbol, color=self.color, bg_color=self.bg_color, style=self.style) * i
            draw_at(self.global_y(), self.global_x(), bar_string)
            
            if self.label:
                percentage = int(i * (100 / self.steps))
                self.label.set_percentage(percentage)
                
            time.sleep(self.interval)

    def draw(self):
        self.load()


class Label(Element):
    def __init__(self, text, element=None, x=None, y=None, color=WHITE, bg_color="", style="", parent=None):
        self.text = text
        if element is not None and parent is None:
            parent = element
        if x is not None and y is not None:
            self.x = x
            self.y = y
        elif element is not None:
            self.x = 0
            self.y = -1
            element.label = self
        else:
            self.x = 1
            self.y = 1
        self.width = len(text)
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.output = self.text
        super().__init__(self.x, self.y, parent=parent)

    def draw(self):
        draw_at(self.global_y(), self.global_x(), ctext(self.output, self.color, self.bg_color, self.style))
        

    def set_percentage(self, percentage):
        output = f"{self.text} {percentage}%"
        self.output = output
        self.width = len(output)
        self.request_layout()
        self.draw()

    def set_text(self, text):
        self.text = text
        self.output = text
        self.width = len(text)
        self.request_layout()
        self.draw()

class Spinner(Element):
    def __init__(self, x, y, text="Loading", color=WHITE, interval=0.1, length=5, parent=None):
        super().__init__(x, y, parent=parent)
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
        draw_at(self.global_y(), self.global_x(), output)
        self.current_phase += 1

    def spin(self):
        for i in range(int(self.length/self.interval)):
            self.next()
            time.sleep(self.interval)
    
    def draw(self):
        self.spin()

class LogBox(Element):
    def __init__(self, x, y, height, parent=None):
        super().__init__(x, y, parent=parent)
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
            draw_at(self.global_y() + i, self.global_x(), element)
    
    def add_and_log(self, entry):
        self.add_entry(entry)
        self.log()

    def draw(self):
        self.log()

class TestSection(Element):
    def __init__(self, x, y, text, color=WHITE, bg_color="", parent=None):
        super().__init__(x, y, parent=parent)
        self.is_selected = False
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.width = len(self.text)

    def draw(self):
        draw_at(self.global_y(), self.global_x(), ctext(text=self.text, color=self.color, bg_color=self.bg_color))
    
    def on_focus(self):
        super().on_focus()
        draw_at(self.global_y(), self.global_x(), ctext(text=self.text, color=self.color, bg_color=self.bg_color, style=REVERSE))
        self.width = len(self.text)

    def on_blur(self):
        super().on_blur()
        draw_at(self.global_y(), self.global_x(), ctext(text=self.text, color=self.color, bg_color=self.bg_color, style=RESET))
        self.width = len(self.text)
    
    def select(self):
        self.erase()
        
class Selection(Element):
    def __init__(self, x, y, on_select=None, parent=None):
        super().__init__(x, y, parent=parent)
        self.options = self.children
        self.selected = False
        self.highlighted_option = 0
        self.on_select = on_select

    def add_option(self, option):
        self.add_child(option)
        if len(option.text) > self.width:
            self.width = len(option.text)
        self.height = len(self.options)
        self.request_layout()
        self.draw()

    def remove_option(self, option):
        self.remove_child(option)
        self.height = len(self.options)
        self.request_layout()
        self.draw()

    def add_options(self, *options):
        for option in options:
            self.add_option(option)

    def remove_options(self, *options):
        for option in options:
            self.remove_option(option)
    
    def draw(self):
        if self.options:
            for i, op in enumerate(self.options):
                op.y = i
                op.x = 0
                op.on_blur()

    def on_focus(self):
        super().on_focus()
        if self.options:
            for i, op in enumerate(self.options):
                op.on_focus()

    def on_blur(self):
        super().on_blur()
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
    def __init__(self, text, value, color=WHITE, bg_color="", parent=None):
        super().__init__(0, 0, parent=parent)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.value = value
        self.height = 1
        self.width = len(text)
    
    def on_blur(self):
        self.is_focused = False
        draw_at(self.global_y(), self.global_x(), ctext(self.text, self.color, self.bg_color, RESET))

    def on_focus(self):
        self.is_focused = True
        draw_at(self.global_y(), self.global_x(), ctext(self.text, self.color, self.bg_color, REVERSE))

    def draw(self):
        draw_at(self.global_y(), self.global_x(), ctext(self.text, self.color, self.bg_color))


class SelectBox(Element):
    def __init__(self, text, x=None, y=None, frame_symbol="#", color=WHITE, bg_color="", style="", on_select=None, parent=None):
        super().__init__(x if x is not None else 0, y if y is not None else 0, parent=parent)
        self.options = self.children
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.frame = frame_symbol
        self.highlighted_option = 0
        self.selected = False
        self.on_select = on_select

        self.height = 7

        if x is None:
            self.set_x = False
        else: self.set_x = True

        if y is None:
            self.set_y = False
        else: self.set_y = True
            
        self._calculate_dimensions()
    
    def clear(self):
        for i in range(self.height+1):
                draw_at(self.global_y() + i, self.global_x(), " " * (self.width+1))
    
    def draw(self):
        self.clear()
        self._calculate_dimensions()
        draw_at(self.global_y(), self.global_x(), self.frame * (self.width))
        for i in range(self.height):
            draw_at(self.global_y() + i, self.global_x(), self.frame)
            draw_at(self.global_y() + i, self.global_x() + self.width, self.frame)
        draw_at(self.global_y() + self.height - 1, self.global_x(), self.frame * (self.width))

        draw_at(self.global_y() + 2, self.global_x() + ((self.width - len(self.text)+1) // 2), self.text)
        all_options = 1
        for l, op in enumerate(self.options):
            op.y = 4

            if l == 0:
                op.x = 2
                all_options += len(op.text) + 1
            else:
                op.x = 1 + all_options
                all_options += len(op.text) + 1
                
            op.on_blur()
    
    def add_option(self, option):
        self.add_child(option)
        self._calculate_dimensions()
        self.draw()

    def remove_option(self, option):
        self.remove_child(option)
        self._calculate_dimensions()
        self.draw()

    def add_options(self, *options):
        for option in options:
            self.add_option(option)

    def remove_options(self, *options):
        for option in options:
            self.remove_option(option)

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
        super().on_focus()
        if self.options:
            for i, op in enumerate(self.options):
                op.on_focus()

    def on_blur(self):
        super().on_blur()
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
    def __init__(self, x_symbol="#", y_symbol="#", element=None, x=None, y=None, height=None, width=None, color=WHITE, bg_color="", style="", parent=None):
        super().__init__(x if x is not None else 0, y if y is not None else 0, parent=parent)
        self.x_symbol = x_symbol
        self.y_symbol = y_symbol
        self.element = element
        self._explicit_width = width is not None
        self._explicit_height = height is not None
        if x is not None and y is not None:
            self.x = x
            self.y = y
        elif element:
            self.x = element.x - 1
            self.y = element.y - 1
            element.x = 1
            element.y = 1
            self.add_child(element)
        else:
            self.x = 1
            self.y = 1

        self.color = color
        self.bg_color = bg_color
        self.style = style

        self._calculate_dimensions(width=width, height=height)
        #self.draw()

    def _child_width(self, child):
        return getattr(child, "width", getattr(child, "length", 0))

    def _child_height(self, child):
        return getattr(child, "height", 1)

    def _calculate_dimensions(self, width=None, height=None):
        if self.children and not self._explicit_width:
            max_width = 0
            for child in self.children:
                child_extent = child.x + self._child_width(child)
                if child_extent > max_width:
                    max_width = child_extent
            self.width = max_width + 1
        elif width is not None:
            self.width = width
        elif not self.children and not self._explicit_width:
            self.width = 5

        if self.children and not self._explicit_height:
            max_height = 0
            for child in self.children:
                child_extent = child.y + self._child_height(child)
                if child_extent > max_height:
                    max_height = child_extent
            self.height = max_height + 1
        elif height is not None:
            self.height = height
        elif not self.children and not self._explicit_height:
            self.height = 5

    def add_child(self, child):
        result = super().add_child(child)
        self._calculate_dimensions()
        return result

    def remove_child(self, child):
        result = super().remove_child(child)
        self._calculate_dimensions()
        return result

    def draw(self):
        self._calculate_dimensions()
        draw_at(self.global_y(), self.global_x(), ctext(self.x_symbol * self.width, self.color, self.bg_color, self.style))
        draw_at(self.global_y() + self.height, self.global_x(), ctext(self.x_symbol * self.width, self.color, self.bg_color, self.style))
        for i in range(self.height + 1):
            draw_at(self.global_y() + i, self.global_x(), ctext(self.y_symbol, self.color, self.bg_color, self.style))
            draw_at(self.global_y() + i, self.global_x() + self.width, ctext(self.y_symbol, self.color, self.bg_color, self.style))
        self.draw_children()

class HorizontalDivider(Element):
    def __init__(self, y, symbol="─", color=WHITE, bg_color="", style="", parent=None):
        super().__init__(1, y, parent=parent)
        self.symbol = symbol
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.width = os.get_terminal_size().columns

    def draw(self):
        for i in range(os.get_terminal_size().columns):
            draw_at(self.global_y(), i, ctext(self.symbol, self.color, self.bg_color, self.style))
        self.width = os.get_terminal_size().columns

class VerticalDivider(Element):
    def __init__(self, x, symbol="│", color=WHITE, bg_color="", style="", parent=None):
        super().__init__(x, 1, parent=parent)
        self.symbol = symbol
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.height = os.get_terminal_size().lines
        self.width = 1
    
    def draw(self):
        for i in range(os.get_terminal_size().lines):
            draw_at(i, self.global_x(), ctext(self.symbol, self.color, self.bg_color, self.style))
        self.height = os.get_terminal_size().lines

class RectArea(Frame):
    def __init__(self, element=None, x=None, y=None, height=None, width=None, color=WHITE, bg_color="", style="", parent=None):
        super().__init__(element=element, x=x, y=y, height=height, width=width, color=color, bg_color=bg_color, style=style, parent=parent)

    def draw(self):
        self._calculate_dimensions()
        tl, tr, bl, br = "┌", "┐", "└", "┘"
        h = "─"
        v = "│"

        t = tl + h * (self.width-2) + tr
        m = v + " " * (self.width-2) + v
        b = bl + h * (self.width-2) + br

        draw_at(self.y, self.x, ctext(t, self.color, self.bg_color))
        draw_at(self.y + self.height - 1, self.x, ctext(b, self.color, self.bg_color))

        for i in range(self.y + 1, self.y + self.height -1):
            draw_at(i, self.x, ctext(m, self.color, self.bg_color))

        self.draw_children()
