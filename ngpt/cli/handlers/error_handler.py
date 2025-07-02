import sys
import traceback
from ngpt.ui.colors import COLORS

def handle_validation_error(error):
    """
    Handle validation errors when parsing arguments.
    
    Args:
        error: The validation error
    """
    print(f"{COLORS['bold']}{COLORS['yellow']}error: {COLORS['reset']}{str(error)}\n")
    sys.exit(2)

def handle_keyboard_interrupt():
    """Handle keyboard interrupt (Ctrl+C)."""
    print("\nOperation cancelled by user. Exiting gracefully.")
    # Make sure we exit with a non-zero status code to indicate the operation was cancelled
    sys.exit(130)  # 130 is the standard exit code for SIGINT (Ctrl+C)

def handle_exception(e, debug=False):
    """
    Handle general exceptions.
    
    Args:
        e: The exception
        debug: Whether to print traceback (default: False)
    """
    if debug:
        traceback.print_exc()
    print(f"{COLORS['red']}Error: {e}{COLORS['reset']}")
    sys.exit(1)  # Exit with error code 