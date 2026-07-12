# nanotui/elements.py
from .colors import *
from .screen import *
from .helpers import get_file_icon
import time
import os


class Element:
    def __init__(self, x=0, y=0, parent=None, width=None, height=None, bg_color=""):
        self.x = x if x is not None else 0
        self.y = y if y is not None else 0
        self.parent = None
        self.children = []
        self._explicit_width = width is not None
        self._explicit_height = height is not None
        self.fill_grid = False
        self.offset_x = 0
        self.offset_y = 0
        self.bg_color = bg_color
        self._update_callback = None
        if width is not None:
            self.width = width
        else:
            self.width = getattr(self, "width", 0)
        if height is not None:
            self.height = height
        else:
            self.height = getattr(self, "height", 1)
        self.is_focused = False

        if parent is not None:
            parent.add_child(self)
            if hasattr(parent, "bg_color") and hasattr(self, "bg_color"):
                if self.bg_color == "":
                    self.bg_color = parent.bg_color
        


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
            if hasattr(child, "layout"):
                child.layout()
            child.draw()

    def draw(self):
        self.draw_children()

    def on_focus(self):
        self.is_focused = True

    def on_blur(self):
        self.is_focused = False

    def set_width(self, width):
        self.width = width
        self._explicit_width = True
        self.request_layout()

    def set_height(self, height):
        self.height = height
        self._explicit_height = True
        self.request_layout()

    def set_size(self, width=None, height=None):
        if width is not None:
            self.set_width(width)
        if height is not None:
            self.set_height(height)

    def available_width(self):
        if self.parent is None:
            return self.width
        return max(0, self.parent.width - self.x - 1)

    def available_height(self):
        if self.parent is None:
            return self.height
        return max(0, self.parent.height - self.y - 1)

    def request_layout(self):
        if self.parent is not None and hasattr(self.parent, "_calculate_dimensions"):
            self.parent._calculate_dimensions()
            self.parent.request_layout()
    
    def on_update(self, callback):
        self._update_callback = callback
        return self
    
    def update(self):
        if self._update_callback:
            self._update_callback(self)

class LoadingBar(Element):
    def __init__(self, x, y, steps=5, symbol=".", interval=0.4, color=WHITE, bg_color="", style="", label=None, parent=None, width=None, height=None):
        super().__init__(x, y, parent=parent, width=width, height=height, bg_color=bg_color)
        self.steps = steps
        self.symbol = symbol
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.interval = interval
        self.label = label
        self.offset_x = x
        self.offset_y = y
        if width is None:
            self.width = steps
        if height is None:
            self.height = 1

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
    def __init__(self, text, element=None, x=None, y=None, color=WHITE, bg_color="", style="", parent=None, width=None, height=None):
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
        if width is None:
            self.width = len(text)
        else:
            self.width = width
        if height is None:
            self.height = 1
        else:
            self.height = height
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.output = self.text
        super().__init__(self.x, self.y, parent=parent, width=width, height=height, bg_color=bg_color)
        self.offset_x = x
        self.offset_y = y

    def draw(self):
        text = self.output
        draw_at(self.global_y(), self.global_x(), ctext(text, self.color, self.bg_color, self.style))
        

    def set_percentage(self, percentage):
        output = f"{self.text} {percentage}%"
        self.output = output
        if not self._explicit_width:
            self.width = len(output)
        self.request_layout()
        self.draw()

    def set_text(self, text):
        self.text = text
        self.output = text
        if not self._explicit_width:
            self.width = len(text)
        self.request_layout()
        self.draw()

class Spinner(Element):
    def __init__(self, x, y, text="Loading", color=WHITE, bg_color="", interval=0.1, length=5, parent=None, width=None, height=None):
        super().__init__(x, y, parent=parent, width=width, height=height, bg_color=bg_color)
        self.text = text
        self.color = color
        self.phases = ["|", "/", "-", "\\"]
        self.current_phase = 0
        if width is None:
            self.width = 1
        self.interval = interval
        self.length = length
        self.offset_y = y
        self.offset_x = x

    def next(self):
        symbol = self.phases[self.current_phase % 4]
        output = f"{ctext(symbol, self.color, self.bg_color)} {self.text}"
        draw_at(self.global_y(), self.global_x(), output)
        self.current_phase += 1

    def spin(self):
        for i in range(int(self.length/self.interval)):
            self.next()
            time.sleep(self.interval)
    
    def draw(self):
        self.spin()

class LogBox(Element):
    def __init__(self, x, y, height=None, parent=None, width=None):
        super().__init__(x, y, parent=parent, width=width, height=height)
        self.text = []
        self.fill_grid = True
    
    def add_entry(self, entry, color=DEFAULT, bg_color=""):
        self.text.append((entry, color, bg_color))
        max_entries = self.height
        if not self._explicit_height:
            max_entries = self.available_height()
        if max_entries > 0 and len(self.text) > max_entries:
            self.text.pop(0)
        if len(entry) > self.width:
            self.width = len(entry)

    def log(self):
        if self.parent and hasattr(self.parent, "bg_color"):
            bg = self.parent.bg_color
        visible_height = self.height
        if not self._explicit_height:
            visible_height = self.available_height()
        elif self.parent is not None:
            visible_height = min(visible_height, self.available_height())

        for i, (element, color, bg_color) in enumerate(self.text[:visible_height]):
            if bg_color != "":
                bg = bg_color
            draw_at(self.global_y() + i, self.global_x(), ctext(element, color, bg))
    
    def add_and_log(self, entry, color=DEFAULT, bg_color=""):
        self.add_entry(entry, color, bg_color)
        self.log()

    def draw(self):
        self.log()

class Button(Element):
    def __init__(self, x, y, text, on_select=None, color=WHITE, bg_color="", parent=None):
        super().__init__(x, y, parent=parent, bg_color=bg_color)
        self.is_selected = False
        self.text = text
        self.color = color
        self.width = len(self.text)
        self.height = 1
        self.on_select = on_select
        self.offset_x = x
        self.offset_y = y

    def draw(self):
        text = self.text
        draw_at(self.global_y(), self.global_x(), ctext(text=text, color=self.color, bg_color=self.bg_color))
    
    def on_focus(self):
        super().on_focus()
        draw_at(self.global_y(), self.global_x(), ctext(text=self.text, color=self.color, bg_color=self.bg_color, style=REVERSE))

    def on_blur(self):
        super().on_blur()
        draw_at(self.global_y(), self.global_x(), ctext(text=self.text, color=self.color, bg_color=self.bg_color, style=RESET))
    
    def select(self):
        if self.on_select:
            self.on_select()
     
class Selection(Element):
    def __init__(self, x, y, on_select=None, parent=None, width=None, height=None):
        super().__init__(x, y, parent=parent, width=width, height=height)
        self.options = self.children
        self.selected = False
        self.highlighted_option = 0
        self.on_select = on_select
        self.fill_width = True
        self.offset_y = y
        self.offset_x = x

    def layout(self):
        if self.parent is None or not self.fill_width or self._explicit_width:
            return
        available_width = self.parent.width - self.x - 1
        if available_width > self.width:
            self.width = available_width

    def add_option(self, option):
        self.add_child(option)
        if not self._explicit_width and len(option.text) > self.width:
            self.width = len(option.text)
        if not self._explicit_height:
            self.height = len(self.options)
        if option.bg_color == "":
            option.bg_color = self.bg_color
        self.request_layout()
        self.draw()

    def remove_option(self, option):
        self.remove_child(option)
        if not self._explicit_height:
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
            visible_height = len(self.options)
            if self.parent is not None and not self._explicit_height:
                visible_height = min(visible_height, self.available_height())

            for i, op in enumerate(self.options[:visible_height]):
                op.y = i
                op.x = 0
                if not op._explicit_width:
                    op.width = self.width
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
            case "UP" | "LEFT":
                self.change_highlight(-1)
            case "DOWN" | "RIGHT":
                self.change_highlight(1)

    def get_value(self):
        return self.options[self.highlighted_option].value
    
    def enter(self):
        if self.on_select:
            self.on_select(self.get_value())
  
class Option(Element):
    def __init__(self, text, value, color=WHITE, bg_color="", parent=None, width=None, height=None):
        super().__init__(0, 0, parent=parent, width=width, height=height)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.value = value
        if width is None:
            self.width = len(text)
        if height is None:
            self.height = 1
    
    def on_blur(self):
        self.is_focused = False
        draw_at(self.global_y(), self.global_x(), ctext(self.text, self.color, self.bg_color, RESET))

    def on_focus(self):
        self.is_focused = True
        draw_at(self.global_y(), self.global_x(), ctext(self.text, self.color, self.bg_color, REVERSE))

    def draw(self):
        draw_at(self.global_y(), self.global_x(), ctext(self.text, self.color, self.bg_color))

class SelectBox(Element):
    def __init__(self, text, x=None, y=None, frame_symbol="#", color=WHITE, bg_color="", style="", on_select=None, parent=None, width=None, height=None):
        super().__init__(x if x is not None else 0, y if y is not None else 0, parent=parent, width=width, height=height)
        self.options = self.children
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.frame = frame_symbol
        self.highlighted_option = 0
        self.selected = False
        self.on_select = on_select
        self.fill_grid = True

        if height is None:
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
        box_width = max(self.width, 2)
        box_height = max(self.height, 2)
        draw_at(self.global_y(), self.global_x(), self.frame * box_width)
        for i in range(box_height):
            draw_at(self.global_y() + i, self.global_x(), self.frame)
            draw_at(self.global_y() + i, self.global_x() + box_width - 1, self.frame)
        draw_at(self.global_y() + box_height - 1, self.global_x(), self.frame * box_width)

        draw_at(self.global_y() + 2, self.global_x() + ((self.width - len(self.text)+1) // 2), self.text)
        all_options = 1
        visible_options = self.options
        if self.parent is not None:
            available_option_rows = max(0, self.available_height() - 4)
            visible_options = self.options[:available_option_rows]

        for l, op in enumerate(visible_options):
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
        if not self._explicit_width:
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

        
    
    def change_highlight(self, direction):
        if not self.options: return
        self.options[self.highlighted_option].on_blur()
        self.highlighted_option = (self.highlighted_option + direction) % len(self.options)
        self.options[self.highlighted_option].on_focus()

    def input(self, key):
        match(key):
            case "LEFT":
                self.change_highlight(-1)
            case "RIGHT":
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
        self.fill_grid = True
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

    def _child_width(self, child):
        return getattr(child, "width", getattr(child, "length", 0))

    def _child_height(self, child):
        return getattr(child, "height", 1)

    def _calculate_dimensions(self, width=None, height=None):
        if width is not None:
            self.width = width
            self._explicit_width = True
        elif self.children and not self._explicit_width:
            max_width = 0
            for child in self.children:
                child_extent = child.x + self._child_width(child)
                if child_extent > max_width:
                    max_width = child_extent
            self.width = max_width + 1
        elif not self.children and not self._explicit_width:
            self.width = 2

        if height is not None:
            self.height = height
            self._explicit_height = True
        elif self.children and not self._explicit_height:
            max_height = 0
            for child in self.children:
                child_extent = child.y + self._child_height(child)
                if child_extent > max_height:
                    max_height = child_extent
            self.height = max_height + 1
        elif not self.children and not self._explicit_height:
            self.height = 2

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
        box_width = max(self.width, 2)
        box_height = max(self.height, 2)
        draw_at(self.global_y(), self.global_x(), ctext(self.x_symbol * box_width, self.color, self.bg_color, self.style))
        draw_at(self.global_y() + box_height - 1, self.global_x(), ctext(self.x_symbol * box_width, self.color, self.bg_color, self.style))
        for i in range(box_height):
            draw_at(self.global_y() + i, self.global_x(), ctext(self.y_symbol, self.color, self.bg_color, self.style))
            draw_at(self.global_y() + i, self.global_x() + box_width - 1, ctext(self.y_symbol, self.color, self.bg_color, self.style))
        self.draw_children()

class HorizontalDivider(Element):
    def __init__(self, y, x=0, symbol="─", color=WHITE, bg_color="", style="", parent=None, width=None, height=None):
        super().__init__(1, y, parent=parent, width=width, height=height, bg_color=bg_color)
        self.symbol = symbol
        self.color = color
        self.style = style
        self.offset_y = y
        self.offset_x = x

        if width is None:
            self.width = os.get_terminal_size().columns
        if height is None:
            self.height = 1

    def draw(self):
        width = self.width if self._explicit_width else os.get_terminal_size().columns
        for i in range(width):
            draw_at(self.y, self.x + i, ctext(self.symbol, self.color, self.bg_color, self.style))
        self.width = width

class VerticalDivider(Element):
    def __init__(self, x, y=0, symbol="│", color=WHITE, bg_color="", style="", parent=None, width=None, height=None):
        super().__init__(x, 1, parent=parent, width=width, height=height, bg_color=bg_color)
        self.symbol = symbol
        self.color = color
        self.style = style
        self.offset_x = x
        self.offset_y = y
        
        if height is None:
            self.height = os.get_terminal_size().lines
        if width is None:
            self.width = 1
    
    def draw(self):
        height = self.height if self._explicit_height else os.get_terminal_size().lines
        for i in range(height):
            draw_at(self.y+i, self.x, ctext(self.symbol, self.color, self.bg_color, self.style))
        self.height = height

class RectArea(Frame):
    def __init__(self, element=None, x=None, y=None, height=None, width=None, color=WHITE, bg_color="", style="", parent=None):
        super().__init__(element=element, x=x, y=y, height=height, width=width, color=color, bg_color=bg_color, style=style, parent=parent)
        self.fill_grid = True
    def draw(self):
        self._calculate_dimensions()
        tl, tr, bl, br = "┌", "┐", "└", "┘"
        h = "─"
        v = "│"

        box_width = max(self.width, 2)
        box_height = max(self.height, 2)
        t = tl + h * (box_width - 2) + tr
        m = v + " " * (box_width - 2) + v
        b = bl + h * (box_width - 2) + br

        draw_at(self.y, self.x, ctext(t, self.color, self.bg_color))
        draw_at(self.y + box_height - 1, self.x, ctext(b, self.color, self.bg_color))

        for i in range(self.y + 1, self.y + box_height -1):
            draw_at(i, self.x, ctext(m, self.color, self.bg_color))

        self.draw_children()

class ProgressBar(Element):
    def __init__(self, x=0, y=0, end_symbols=["[", "]"], fill_symbol="█", unfilled_symbol="░", unfilled_color=DEFAULT, color=DEFAULT, bg_color="", parent=None, width=None):
        super().__init__(x, y, parent, width, height=1, bg_color=bg_color)
        self.start_symbol = end_symbols[0]
        self.end_symbol = end_symbols[1]
        self.color = color
        self.filled = 0
        self.unfilled = unfilled_symbol
        self.unfilled_color = unfilled_color
        self.progress_lst = []
        self.fillable_width = self.width-2
        self.filled_width = 0
        self.fill_symbol = fill_symbol
        self.offset_y = y
        self.offset_x = x
        
    def draw(self):
        self.fillable_width = self.width-2
        draw_at(self.y, self.x, ctext(self.start_symbol, self.color, self.bg_color)) # draw start
        draw_at(self.y, self.x + self.width - 1, ctext(self.end_symbol, self.color, self.bg_color)) #draw end
        draw_at(self.y, self.x + self.filled + 1, ctext(self.unfilled * (self.fillable_width-self.filled), self.unfilled_color)) # draw unfilled space

        for progress in self.progress_lst:
            width = int(self.fillable_width * progress["percentage"])

            draw_at(self.y, self.x + self.filled_width + 1, ctext(self.fill_symbol * width, progress["color"]))

            self.filled_width += width

        self.filled_width = 0

    def set_progress(self, name: str, percentage: float = None, color: str = None):
        for progress in self.progress_lst:
            if progress["name"] == name:
                if percentage is not None:
                    progress["percentage"] = percentage
                if color is not None:
                    progress["color"] = color
                self.draw()
                return
            

    def add_progress(self, name:str, percentage:float, color:str):
        self.progress_lst.append(
            {
                "name": name,
                "percentage": percentage,
                "color": color
            }
        )
        
        self.draw()

 
class FileExplorer(Element):
    """A scrollable file/folder browser. Unlike Selection/SelectBox, entries
    are kept as plain (name, is_dir) tuples instead of individual child
    Elements, since a directory can easily hold far more entries than it
    makes sense to manage as separate Option objects. Only the FileExplorer
    itself is selectable - it manages its own highlight and scroll state
    internally, the same way LogBox manages its own scrolling text buffer."""

    def __init__(self, x, y, path=".", on_select=None, on_navigate=None,
                 show_hidden=False, color=WHITE, bg_color="", style="",
                 folder_color=CYAN, file_color=WHITE, parent=None,
                 width=None, height=None):
        super().__init__(x, y, parent=parent, width=width, height=height)
        self.fill_grid = True
        self.offset_x = x
        self.offset_y = y

        self.path = os.path.abspath(path)
        self.on_select = on_select      # called with the full file path once a file is chosen
        self.on_navigate = on_navigate  # optional: called with the new dir path on folder change
        self.show_hidden = show_hidden

        self.color = color
        self.bg_color = bg_color
        self.style = style
        self.folder_color = folder_color
        self.file_color = file_color

        if width is None:
            self.width = 40
        if height is None:
            self.height = 15

        self.entries = []       # list of (name, is_dir) tuples
        self.highlighted = 0
        self.scroll_offset = 0
        self.selected = False

        self._refresh_entries()

    def _refresh_entries(self):
        try:
            raw = os.listdir(self.path)
        except OSError:
            raw = []

        if not self.show_hidden:
            raw = [name for name in raw if not name.startswith(".")]

        dirs, files = [], []
        for name in raw:
            full_path = os.path.join(self.path, name)
            (dirs if os.path.isdir(full_path) else files).append(name)

        dirs.sort(key=str.lower)
        files.sort(key=str.lower)

        self.entries = []
        if os.path.dirname(self.path) != self.path:
            self.entries.append(("..", True))
        self.entries += [(name, True) for name in dirs]
        self.entries += [(name, False) for name in files]

        self.highlighted = 0
        self.scroll_offset = 0

    def _list_height(self):
        # row 0 is reserved for the path header, so one less than the box height
        height = self.height if self._explicit_height else self.available_height()
        return max(1, height - 1)

    def draw(self, focus=False):
        self.erase()

        max_path_len = max(self.width, 1)
        if len(self.path) <= max_path_len:
            header = self.path
        else:
            header = "..." + self.path[-max(max_path_len - 3, 0):]
        draw_at(self.global_y(), self.global_x(), ctext(header.ljust(self.width), self.color, self.bg_color, BOLD))

        visible_height = self._list_height()
        visible = self.entries[self.scroll_offset:self.scroll_offset + visible_height]

        for i, (name, is_dir) in enumerate(visible):
            icon, icon_color = get_file_icon(name, is_dir)
            index = self.scroll_offset + i
            label = (name + "/") if (is_dir and name != "..") else name
            row_color = self.folder_color if is_dir else self.file_color
            row_style = REVERSE if (self.selected and index == self.highlighted) or focus else RESET
            draw_at(self.global_y() + 1 + i, self.global_x() + 1,
                    ctext(label[:self.width].ljust(self.width), row_color, self.bg_color, row_style))
            draw_at(self.global_y() + 1 + i, self.global_x(), ctext(icon, self.folder_color if is_dir else icon_color))

    def on_focus(self):
        super().on_focus()
        self.draw(focus=True)

    def on_blur(self):
        super().on_blur()
        self.selected = False
        self.draw()

    def select(self):
        self.selected = True
        self.draw()

    def _move_highlight(self, direction):
        if not self.entries:
            return
        self.highlighted = (self.highlighted + direction) % len(self.entries)

        visible_height = self._list_height()
        if self.highlighted < self.scroll_offset:
            self.scroll_offset = self.highlighted
        elif self.highlighted >= self.scroll_offset + visible_height:
            self.scroll_offset = self.highlighted - visible_height + 1

        self.draw()

    def _navigate_into(self, name):
        new_path = os.path.abspath(os.path.join(self.path, name))
        if os.path.isdir(new_path):
            self.path = new_path
            self._refresh_entries()
            self.draw()
            if self.on_navigate:
                self.on_navigate(self.path)

    def input(self, key):
        match key:
            case "UP":
                self._move_highlight(-1)
            case "DOWN":
                self._move_highlight(1)
            case "RIGHT":
                if self.entries:
                    name, is_dir = self.entries[self.highlighted]
                    if is_dir:
                        self._navigate_into(name)
            case "LEFT":
                self._navigate_into("..")

    def enter(self):
        if not self.entries:
            return
        name, is_dir = self.entries[self.highlighted]
        if is_dir:
            self._navigate_into(name)
        elif self.on_select:
            self.on_select(os.path.join(self.path, name))

    def get_value(self):
        if not self.entries:
            return None
        name, _ = self.entries[self.highlighted]
        return os.path.join(self.path, name)