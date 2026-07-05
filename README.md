# nanotui

A lightweight, dependency-free Python library for building terminal user interfaces (TUIs) with ANSI escape codes. No `curses`, no third-party packages — just plain Python.

## Features

- **Zero dependencies** — pure Python standard library
- **Widget-based** — labels, buttons, menus, progress bars, spinners, log boxes, frames, dividers, and more
- **Parent/child element tree** with automatic layout recalculation
- **Grid layout system** with weighted rows and columns for responsive-ish terminal layouts
- **Keyboard-driven navigation** with focus management and a two-layer interaction model for drilling into composite widgets
- **Built-in quit confirmation dialog**
- **Simple color/style helpers** built on raw ANSI codes

## Requirements

- Python 3.10 or higher (the event loop uses `match`/`case` syntax)

## Installation

### Option 1: Clone and install locally

```bash
git clone https://github.com/michelzwahr/nanotui.git
cd nanotui
pip install .
```

### Option 2: Install directly from GitHub

```bash
pip install git+https://github.com/michelzwahr/nanotui.git
```

## Quick Start

```python
from nanotui import App, Button

def main():
    app = App("My First App")

    def say_hello():
        pass  # runs when the button is activated

    button = Button(x=5, y=5, text="Press Enter", on_select=say_hello)
    app.add_element(button)

    app.run()

if __name__ == "__main__":
    main()
```

Run it, press `Enter` to trigger the button, and `q` or `Esc` to quit.

## Table of Contents

- [Core Concepts](#core-concepts)
  - [The App Class](#the-app-class)
  - [Navigation & Focus](#navigation--focus)
  - [The Element Base Class](#the-element-base-class)
  - [The Grid Layout System](#the-grid-layout-system)
- [Widget Reference](#widget-reference)
  - [Label](#label)
  - [Button](#button)
  - [Selection & Option](#selection--option)
  - [SelectBox](#selectbox)
  - [Frame](#frame)
  - [RectArea](#rectarea)
  - [HorizontalDivider & VerticalDivider](#horizontaldivider--verticaldivider)
  - [LogBox](#logbox)
  - [ProgressBar](#progressbar)
  - [LoadingBar](#loadingbar)
  - [Spinner](#spinner)
- [Colors & Styling](#colors--styling)
- [Low-Level Screen API](#low-level-screen-api)
- [Examples](#examples)

---

## Core Concepts

### The App Class

`App` owns the render loop, keyboard input, and focus/layer state.

```python
App(name, use_grid=False, grid_layout="absolute")
```

| Parameter     | Description |
|---------------|-------------|
| `name`        | Name of the application (currently used as an identifier; not rendered on screen). |
| `use_grid`    | If `True`, the terminal-resize handler will call `update_grid()` to recompute the grid layout. Only relevant if you're using the grid system. |
| `grid_layout` | `"absolute"` (default) or `"relative"`. See [The Grid Layout System](#the-grid-layout-system). |

**Key methods:**

| Method | Description |
|---|---|
| `add_element(element)` | Registers a top-level element with the app so it gets drawn, focused, and updated. |
| `remove_element(element)` | Removes a previously added top-level element. |
| `run(clearscreen=True, controls=False)` | Starts the blocking event loop. `clearscreen` clears the terminal on start. `controls` displays a help bar at the bottom of the screen listing the default key bindings. |

Calling `run()` puts the terminal into raw mode (via `tty`/`termios`), hides the cursor, and restores everything automatically when the loop exits — even on an unhandled exception, since cleanup happens in a `finally` block.

### Navigation & Focus

Only elements that expose a `select()` method (buttons, menus, etc.) participate in focus/keyboard navigation. The app walks its entire element tree (including nested children) to find them.

There are two **layers**:

- **Layer 0** — you move focus *between* elements.
- **Layer 1** — you interact *inside* the currently focused element (e.g. scrolling through the options of a menu).

Default key bindings:

| Key | Layer 0 (between elements) | Layer 1 (inside an element) |
|---|---|---|
| `,` | Move focus to the previous selectable element | Forwarded to the element's `input()` (e.g. highlight previous option) |
| `.` | Move focus to the next selectable element | Forwarded to the element's `input()` (e.g. highlight next option) |
| `Enter` | Calls the focused element's `select()`. If that element also defines an `enter()` method, the app drops into Layer 1 | Calls the element's `enter()` — typically confirms the current choice and fires its `on_select` callback |
| `Esc` | Opens the quit-confirmation dialog | Backs out to Layer 0 |
| `q` | Opens the quit-confirmation dialog (works from either layer) | |
| `r` | Forces a full screen clear + redraw | |

This is why a plain `Button` reacts to a single `Enter` press (it only has `select()`), while a `SelectBox` or `Selection` needs `Enter` to "enter" it, then `,`/`.` to move the highlight, then `Enter` again to confirm — because those widgets additionally define `enter()`.

### Quit Dialog

Every `App` instance comes with a built-in `SelectBox` ("Quit?" with "Quit"/"Cancel" options), triggered by `q` or `Esc`. Confirming closes the app loop; cancelling returns you to whatever you were doing. You don't need to build this yourself.

### The Element Base Class

Every widget subclasses `Element`, which provides the positioning and tree logic:

```python
Element(x=0, y=0, parent=None, width=None, height=None)
```

- **`x`, `y`** — position *relative to the parent* (or absolute, if there's no parent).
- **`parent`** / **`children`** — elements can be nested. A parent's `draw()` calls `draw_children()`, which recursively draws (and lays out) all children.
- **`global_x()`, `global_y()`** — resolves the element's absolute screen coordinates by walking up the parent chain.
- **`add_child(child)` / `remove_child(child)`** and the plural `add_children(*children)` / `remove_children(*children)` — manage the tree. Adding/removing a child triggers `request_layout()`.
- **`request_layout()`** — asks the parent to recompute its size (`_calculate_dimensions()`, if it has one) and propagates the request upward. This is how containers like `Frame` auto-resize when you add a new child.
- **`set_width(width)`, `set_height(height)`, `set_size(width, height)`** — explicitly lock a dimension (marks it "explicit" so auto-sizing logic won't override it).
- **`available_width()`, `available_height()`** — remaining space inside the parent, useful when writing custom widgets that should adapt to their container.
- **`erase()`** — blanks out the area the element currently occupies.
- **`on_focus()` / `on_blur()`** — called automatically by the app when focus enters/leaves the element; override to change appearance.
- **`fill_grid`** — a flag (default `False`) used by the grid system; see below.

### The Grid Layout System

The grid system lets you place elements into a rows × columns layout instead of hand-computing pixel coordinates.

```python
app.create_grid(rows, columns)
app.config_row(row, weight)       # 1-based row index
app.config_column(column, weight) # 1-based column index
app.add_to_grid({
    element_a: (1, 1),   # (row, column), 1-based
    element_b: (1, 2),
})
```

- `create_grid(rows, columns)` sets up an empty grid.
- `config_row` / `config_column` assign a relative **weight** to a row/column, controlling how much space it gets when `grid_layout="relative"` is used. Rows/columns default to a weight of `1`.
- `add_to_grid(mapping)` places elements into grid cells and automatically calls `add_element()` for you if it hasn't been added yet.

**Two placement styles per cell:**

- Elements with `fill_grid = True` (e.g. `Frame`, `RectArea`, `SelectBox`, `LogBox`) claim the **entire cell** — only one such element is allowed per cell (a second one raises `ValueError`). In `"relative"` mode, its `width`/`height`/`x`/`y` are recalculated to match the cell's computed size.
- Elements with `fill_grid = False` (e.g. `Button`, `Label`, `Divider`, `ProgressBar`) can share a cell with others and keep their own size. Their **original constructor `x`/`y` are remembered as an offset**, and are re-applied relative to the cell's top-left corner. For example, `Button(5, 5, "Hallo")` placed into a cell will always render 5 columns and 5 rows in from that cell's origin.

**Layout modes:**

- `grid_layout="relative"` — on resize (or when `update_grid()` is called), row/column spans are computed proportionally from the configured weights, and every grid element's position/size is recalculated accordingly. This is the mode used for responsive layouts.
- `grid_layout="absolute"` — currently a no-op placement mode reserved for future use; elements keep whatever coordinates they were constructed with. Prefer `"relative"` for now if you want the grid to actually manage sizing.

## Widget Reference

All widgets below are importable directly from `nanotui`:

```python
from nanotui import (
    Label, Button, Selection, Option, SelectBox, Frame, RectArea,
    HorizontalDivider, VerticalDivider, LogBox, ProgressBar,
    LoadingBar, Spinner, App
)
```

### Label

A simple styled text element.

```python
Label(text, element=None, x=None, y=None, color=WHITE, bg_color="", style="", parent=None, width=None, height=None)
```

- If `element` is given (instead of `x`/`y`), the label attaches itself just above that element (`y=-1`) and registers itself as `element.label` — handy for captioning another widget (e.g. a `LoadingBar`).
- `set_text(text)` — updates the displayed text and redraws.
- `set_percentage(percentage)` — renders as `"{text} {percentage}%"`; used internally by `LoadingBar` but callable directly.

```python
label = Label("Progress", x=2, y=1, color=CYAN)
app.add_element(label)
label.set_text("Done!")
```

### Button

A one-shot, immediately-activating control.

```python
Button(x, y, text, on_select=None, color=WHITE, bg_color="", parent=None)
```

- `select()` calls `on_select()` (no arguments) when the button is activated with `Enter`.
- Focus is shown by reversing the foreground/background colors (`on_focus()`/`on_blur()`).

```python
def handle_click():
    log.add_and_log("Button clicked!")

button = Button(x=5, y=5, text="Click me", on_select=handle_click)
app.add_element(button)
```

### Selection & Option

A free-floating, vertically-stacked list of choices — typically wrapped in a `Frame` for a border.

```python
Selection(x, y, on_select=None, parent=None, width=None, height=None)
Option(text, value, color=WHITE, bg_color="", parent=None, width=None, height=None)
```

- `add_option(option)` / `add_options(*options)` — append one or more `Option` children (auto-grows width/height unless explicitly set).
- `remove_option(option)` / `remove_options(*options)`
- `get_value()` — returns the `value` of the currently highlighted option.
- `enter()` — fires `on_select(get_value())`; called automatically by the app when you confirm with `Enter` at Layer 1.
- By default, `Selection` stretches to fill the remaining width of its parent (`fill_width = True`) unless an explicit width was given.

```python
def on_choice(value):
    log.add_and_log(f"Selected: {value}")

selection = Selection(1, 1, on_select=on_choice)
frame = Frame(x_symbol="~", y_symbol="|", element=selection)
selection.add_options(
    Option("Option 1", 1),
    Option("Option 2", 2),
    Option("Option 3", 3),
)
app.add_element(frame)
```

### SelectBox

A bordered, titled, horizontally-laid-out option box — well suited to short Yes/No-style dialogs (it's what powers the built-in quit dialog).

```python
SelectBox(text, x=None, y=None, frame_symbol="#", color=WHITE, bg_color="", style="", on_select=None, parent=None, width=None, height=None)
```

- `text` is shown as a centered title inside the box.
- If `x`/`y` are omitted, the box **auto-centers itself** in the terminal — convenient for modal dialogs.
- Options are arranged left-to-right on a single row and sized automatically to fit.
- Same option-management API as `Selection`: `add_option`, `add_options`, `remove_option`, `remove_options`.
- `enter()` fires `on_select(value)` with the highlighted option's value.

```python
def on_result(flag):
    if flag == 1:
        print("Confirmed")

box = SelectBox("Save changes?", on_select=on_result)
box.add_options(Option("Yes", 1), Option("No", 0))
app.add_element(box)
```

### Frame

A generic border that wraps another element (or a set of children), auto-sizing to fit its content.

```python
Frame(x_symbol="#", y_symbol="#", element=None, x=None, y=None, height=None, width=None, color=WHITE, bg_color="", style="", parent=None)
```

- `x_symbol` draws the top/bottom border; `y_symbol` draws the left/right border — set them independently for e.g. an ASCII box.
- Pass `element=` to wrap an existing widget: the frame repositions itself around that element and adds it as a child (the element's local coordinates become `(1, 1)`, just inside the border).
- Without explicit `width`/`height`, the frame grows to fit its children automatically as they're added or removed.
- `fill_grid = True` — a `Frame` claims its entire grid cell when placed via `add_to_grid`.

```python
frame = Frame(x_symbol="=", y_symbol="|", width=20, height=5)
label = Label("Inside a frame", x=1, y=1, parent=frame)
app.add_element(frame)
```

### RectArea

Like `Frame`, but always drawn with box-drawing characters (`┌─┐│└┘`) instead of custom symbols. Useful as an empty placeholder box or to frame another element with a cleaner look.

```python
RectArea(element=None, x=None, y=None, height=None, width=None, color=WHITE, bg_color="", style="", parent=None)
```

Inherits all of `Frame`'s sizing/wrapping behavior — the constructor still accepts the same shape, just note that `RectArea` ignores any custom border symbols and always renders the standard box-drawing border.

```python
logbox = LogBox(1, 1)
framed_log = RectArea(element=logbox, color=GREEN)
app.add_element(framed_log)
```

### HorizontalDivider & VerticalDivider

Simple decorative lines.

```python
HorizontalDivider(y, x=0, symbol="─", color=WHITE, bg_color="", style="", parent=None, width=None, height=None)
VerticalDivider(x, y=0, symbol="│", color=WHITE, bg_color="", style="", parent=None, width=None, height=None)
```

- Without an explicit `width` (horizontal) or `height` (vertical), the divider stretches to the full current terminal width/height and re-measures itself on every draw.

```python
divider = HorizontalDivider(y=3)
app.add_element(divider)
```

### LogBox

A scrolling text log — good for status/event output.

```python
LogBox(x, y, height=None, parent=None, width=None)
```

- `add_entry(entry)` — appends a line, trimming the oldest entry once the visible height is exceeded. Does **not** redraw by itself.
- `log()` — redraws all currently buffered lines.
- `add_and_log(entry)` — the usual way to use it: appends and immediately redraws.
- `fill_grid = True` — fills its entire grid cell when used with the grid system (typically wrapped in a `Frame`/`RectArea` for a visible border, as shown above).

```python
logbox = LogBox(1, 1, height=10)
app.add_element(logbox)
logbox.add_and_log("Application started")
```

### ProgressBar

A single bar that can track **multiple independent, differently-colored progress segments** stacked side-by-side (e.g. multiple parallel jobs sharing one bar).

```python
ProgressBar(x=0, y=0, end_symbols=["[", "]"], fill_symbol="█", unfilled_symbol="░", unfilled_color=DEFAULT, color=DEFAULT, bg_color=DEFAULT, parent=None, width=None)
```

- `add_progress(name, percentage, color)` — registers a new named segment (`percentage` from `0.0` to `1.0`) and draws it.
- `set_progress(name, percentage=None, color=None)` — updates an existing segment by name (only touches the fields you pass) and redraws.
- Segments are drawn in the order they were added, filling up left-to-right.

```python
import threading, time
from nanotui import App, ProgressBar, GREEN, DEFAULT

app = App("Progress Demo")
bar = ProgressBar(x=4, y=4, width=40, unfilled_symbol="|", fill_symbol="|")
bar.add_progress("job", 0.0, GREEN)
app.add_element(bar)

def advance():
    value = 0.0
    while value < 1.0:
        time.sleep(1)
        value = min(1.0, value + 0.05)
        bar.set_progress("job", value)

threading.Thread(target=advance, daemon=True).start()
app.run()
```

> Since `ProgressBar` has no `update()` method, it won't animate on its own inside `app.run()` — drive it from a background thread (as above) or update it from your own logic between draws.

### LoadingBar

A **blocking**, one-shot fill animation — useful as a splash/loading screen before your main UI starts.

```python
LoadingBar(x, y, steps=5, symbol=".", interval=0.4, color=WHITE, bg_color="", style="", label=None, parent=None, width=None, height=None)
```

- Calling `.load()` (or `.draw()`, which just calls `.load()`) blocks for `steps * interval` seconds while filling in `symbol` one step at a time.
- Pass a `Label` via `label=` to have it automatically update with a live `"{text} {percentage}%"` readout as the bar fills.

```python
from nanotui import LoadingBar, Label

label = Label("Loading")
bar = LoadingBar(x=2, y=2, steps=20, interval=0.05, label=label)
bar.load()  # blocks until finished, then continue with app.run() etc.
```

### Spinner

A **blocking** indeterminate spinner (`| / - \`).

```python
Spinner(x, y, text="Loading", color=WHITE, interval=0.1, length=5, parent=None, width=None, height=None)
```

- `.next()` advances the spinner by a single frame (non-blocking) — call this yourself if you want to drive it from your own loop or thread.
- `.spin()` (also triggered by `.draw()`) blocks for `length` seconds, calling `.next()` every `interval` seconds.

```python
spinner = Spinner(x=2, y=2, text="Connecting...")
spinner.spin()  # blocks for `length` seconds
```

## Colors & Styling

`nanotui.colors` provides raw ANSI escape sequences as constants, plus a helper to combine them.

```python
ctext(text, color, bg_color="", style="")
```

Wraps `text` with the given style/background/foreground codes and a trailing reset code.

**Styles:** `RESET`, `BOLD`, `FAINT`, `ITALIC`, `UNDERLINE`, `BLINK`, `REVERSE`, `STRIKETHROUGH`

**Foreground:** `BLACK`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `WHITE`, `DEFAULT`, and bright variants `BRIGHT_RED`, `BRIGHT_GREEN`, `BRIGHT_YELLOW`, `BRIGHT_BLUE`, `BRIGHT_MAGENTA`, `BRIGHT_CYAN`, `BRIGHT_WHITE`

**Background:** `BG_BLACK`, `BG_RED`, `BG_GREEN`, `BG_YELLOW`, `BG_BLUE`, `BG_MAGENTA`, `BG_CYAN`, `BG_WHITE`, `BG_DEFAULT`, and bright variants `BG_BRIGHT_RED`, `BG_BRIGHT_GREEN`, `BG_BRIGHT_YELLOW`, `BG_BRIGHT_BLUE`, `BG_BRIGHT_MAGENTA`, `BG_BRIGHT_CYAN`, `BG_BRIGHT_WHITE`

```python
from nanotui import ctext, GREEN, BOLD

print(ctext("Success!", GREEN, style=BOLD))
```

## Low-Level Screen API

Most widgets use these internally, but they're available for custom drawing:

| Function | Description |
|---|---|
| `clear_screen()` | Clears the terminal and moves the cursor to the top-left. |
| `move_cursor(row, column)` | Moves the cursor to a 1-based coordinate. |
| `draw_at(row, column, text)` | Moves the cursor and writes `text`. |
| `hide_cursor()` / `show_cursor()` | Toggles cursor visibility. |

## Examples

The `demo/` folder contains runnable examples:

- **`demo_frame_selection.py`** — combines a 2×2 grid, `Frame`, `RectArea`, `SelectBox`, `Selection`/`Option`, dividers, and a `Button` to show off the grid layout system end-to-end.
- **`progress_live_demo.py`** — drives a `ProgressBar` from a background thread while the app loop runs, demonstrating live updates alongside `app.run()`.

Run either with:

```bash
python demo/demo_frame_selection.py
python demo/progress_live_demo.py
```
