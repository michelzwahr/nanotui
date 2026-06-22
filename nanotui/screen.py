# nanotui/screen.py
import sys


def clear_screen():
    """Clears the entire terminal screen and moves the cursor to the top-left corner."""
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def move_cursor(row, column):
    """Moves the cursor to an exact coordinate (1-based index)."""
    sys.stdout.write(f"\033[{row};{column}H")
    sys.stdout.flush()

def draw_at(row, column, text):
    """Draws a string at a specific terminal coordinate."""
    move_cursor(row, column)
    sys.stdout.write(text)
    sys.stdout.flush()

