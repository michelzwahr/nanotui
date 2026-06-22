# nanotui/colors.py

# --- BASE STYLES ---
RESET = "\033[0m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"       # Not supported by all terminals
UNDERLINE = "\033[4m"
BLINK = "\033[5m"        # Retro blink effect
REVERSE = "\033[7m"      # Swaps foreground and background colors
STRIKETHROUGH = "\033[9m"

# --- STANDARD COLORS (Normal) ---
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BLACK = "\033[30m"

# --- BRIGHT COLORS ---
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# --- BACKGROUND COLORS (Normal) ---
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"

# --- BACKGROUND COLORS (Bright) ---
BG_BRIGHT_RED = "\033[101m"
BG_BRIGHT_GREEN = "\033[102m"
BG_BRIGHT_YELLOW = "\033[103m"
BG_BRIGHT_BLUE = "\033[104m"
BG_BRIGHT_MAGENTA = "\033[105m"
BG_BRIGHT_CYAN = "\033[106m"
BG_BRIGHT_WHITE = "\033[107m"


def ctext(text, color, bg_color="", style=""):
    """
    Returns a formatted string with terminal styles, foreground, and background colors.
    """
    return f"{style}{bg_color}{color}{text}{RESET}"