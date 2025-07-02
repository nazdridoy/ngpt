import sys
import os
import ctypes
import shutil

def supports_ansi_colors():
    """Check if the current terminal supports ANSI colors."""
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            if os.environ.get('TERM_PROGRAM') or os.environ.get('WT_SESSION'):
                return True
            winver = sys.getwindowsversion()
            if winver.major >= 10:
                return True
            return False
        except Exception:
            return False
    return True

COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[36m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "gray": "\033[90m",
    "bg_blue": "\033[44m",
    "bg_cyan": "\033[46m"
}

HAS_COLOR = supports_ansi_colors()

if sys.platform == "win32" and HAS_COLOR:
    COLORS["magenta"] = "\033[95m"
    COLORS["cyan"] = "\033[96m"

if not HAS_COLOR:
    for key in COLORS:
        COLORS[key] = "" 