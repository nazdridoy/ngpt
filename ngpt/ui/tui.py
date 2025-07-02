import sys
import time
import shutil
import platform
from ngpt.ui.colors import COLORS

# Optional imports for enhanced UI
try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.layout.containers import HSplit, Window
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.application import Application
    from prompt_toolkit.widgets import TextArea
    from prompt_toolkit.layout.margins import ScrollbarMargin
    from prompt_toolkit.filters import to_filter
    from prompt_toolkit.history import InMemoryHistory
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

def create_multiline_editor(initial_text=None):
    """Create a multi-line editor with prompt_toolkit.
    
    Args:
        initial_text: Optional initial text to prepopulate the editor with
    
    Returns:
        tuple: (app, has_prompt_toolkit) - the editor application and a boolean
               indicating if prompt_toolkit is available
    """
    if not HAS_PROMPT_TOOLKIT:
        return None, False
        
    try:
        # Create key bindings
        kb = KeyBindings()
        
        # Explicitly bind Ctrl+D to exit
        @kb.add('c-d')
        def _(event):
            event.app.exit(result=event.app.current_buffer.text)
            
        # Explicitly bind Ctrl+C to exit
        @kb.add('c-c')
        def _(event):
            event.app.exit(result=None)
            print("\nInput cancelled by user. Exiting gracefully.")
            sys.exit(130)
        
        # Get terminal dimensions
        term_width, term_height = shutil.get_terminal_size()
        
        # Create a styled TextArea
        text_area = TextArea(
            style="class:input-area",
            multiline=True,
            wrap_lines=True,
            width=term_width - 10,
            height=min(15, term_height - 10),
            prompt=HTML("<ansicyan><b>> </b></ansicyan>"),
            scrollbar=True,
            focus_on_click=True,
            lexer=None,
            text=initial_text or "", # Set initial text if provided
        )
        text_area.window.right_margins = [ScrollbarMargin(display_arrows=True)]
        
        # Create a title bar
        title_bar = FormattedTextControl(
            HTML("<ansicyan><b> nGPT Multi-line Editor </b></ansicyan>")
        )
        
        # Create a status bar with key bindings info
        status_bar = FormattedTextControl(
            HTML("<ansiblue><b>Ctrl+D</b></ansiblue>: Submit | <ansiblue><b>Ctrl+C</b></ansiblue>: Cancel | <ansiblue><b>↑↓←→</b></ansiblue>: Navigate")
        )
        
        # Create the layout
        layout = Layout(
            HSplit([
                Window(title_bar, height=1),
                Window(height=1, char="─", style="class:separator"),
                text_area,
                Window(height=1, char="─", style="class:separator"),
                Window(status_bar, height=1),
            ])
        )
        
        # Create a style
        style = Style.from_dict({
            "separator": "ansicyan",
            "input-area": "fg:ansiwhite",
            "cursor": "bg:ansiwhite fg:ansiblack",
        })
        
        # Create and return the application
        app = Application(
            layout=layout,
            full_screen=False,
            key_bindings=kb,
            style=style,
            mouse_support=True,
        )
        
        return app, True
        
    except Exception as e:
        print(f"Error creating editor: {e}")
        return None, False

def get_multiline_input(initial_text=None):
    """Get multi-line input from the user using either prompt_toolkit or standard input.
    
    Args:
        initial_text: Optional initial text to prepopulate the editor with
    
    Returns:
        str: The user's input text, or None if cancelled
    """
    editor_app, has_editor = create_multiline_editor(initial_text)
    
    if has_editor and editor_app:
        try:
            prompt = editor_app.run()
            if not prompt or not prompt.strip():
                print("Empty prompt. Exiting.")
                return None
            return prompt
        except KeyboardInterrupt:
            print("\nInput cancelled by user. Exiting gracefully.")
            return None
    else:
        # Fallback to standard input with a better implementation
        print("Enter your multi-line prompt (press Ctrl+D to submit):")
        if not HAS_PROMPT_TOOLKIT:
            print("Note: Install 'prompt_toolkit' package for an enhanced input experience")
        
        # Show initial text if provided
        if initial_text:
            print(initial_text)
            lines = initial_text.splitlines()
        else:
            lines = []
        
        # Use a more robust approach for multiline input without prompt_toolkit
        try:
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:  # Ctrl+D was pressed
                    break
            
            prompt = "\n".join(lines)
            if not prompt.strip():
                print("Empty prompt. Exiting.")
                return None
            return prompt
            
        except KeyboardInterrupt:
            print("\nInput cancelled by user. Exiting gracefully.")
            return None

def get_terminal_input():
    """Get input from terminal in a cross-platform way, even when stdin is redirected."""
    if platform.system() == 'Windows':
        # Windows-specific solution
        try:
            import msvcrt
            sys.stdout.flush()
            
            # Wait for a complete line (including Enter key)
            input_chars = []
            while True:
                # Get a character
                char = msvcrt.getch()
                
                # If it's Enter (CR or LF), break the loop
                if char in [b'\r', b'\n']:
                    print()  # Move to the next line after Enter
                    break
                    
                # If it's backspace, handle it
                if char == b'\x08':
                    if input_chars:
                        # Remove the last character
                        input_chars.pop()
                        # Erase the character on screen (backspace + space + backspace)
                        sys.stdout.write('\b \b')
                        sys.stdout.flush()
                    continue
                    
                # For regular characters, add to input and echo
                try:
                    char_decoded = char.decode('utf-8').lower()
                    input_chars.append(char_decoded)
                    print(char_decoded, end='', flush=True)  # Echo the character without newline
                except UnicodeDecodeError:
                    # Skip characters that can't be decoded
                    continue
            
            # Join all characters and return
            return ''.join(input_chars).strip().lower()
        except ImportError:
            # Fallback if msvcrt is not available
            return None
    else:
        # Unix-like systems (Linux, macOS)
        try:
            with open('/dev/tty', 'r') as tty:
                return tty.readline().strip().lower()
        except (IOError, OSError):
            return None

def copy_to_clipboard(content, prompt_message=None, skip_confirmation=False):
    """Copy content to clipboard with user confirmation.
    
    Args:
        content: The text content to copy to clipboard
        prompt_message: Optional custom message for the prompt (default: "Copy to clipboard? (y/n)")
        skip_confirmation: When True, skips the confirmation prompt and copies directly
        
    Returns:
        bool: True if copied to clipboard successfully, False otherwise
    """
    # Only prompt if stdout is connected to a terminal
    if not sys.stdout.isatty():
        return False
        
    try:
        # Skip confirmation if requested
        if skip_confirmation:
            answer = 'y'
        else:
            # Default prompt message
            if prompt_message is None:
                prompt_message = "Copy to clipboard? (y/n)"
                
            # Make the prompt more visible with colors and formatting
            clipboard_prompt = f"{COLORS['cyan']}{COLORS['bold']}{prompt_message}{COLORS['reset']} "
            print(clipboard_prompt, end="")
            sys.stdout.flush()
            
            # Cross-platform terminal input
            answer = get_terminal_input()
        
        if answer == 'y':
            try:
                import pyperclip
                pyperclip.copy(content)
                print(f"{COLORS['green']}Copied to clipboard.{COLORS['reset']}")
                return True
            except ImportError:
                print(f"{COLORS['yellow']}pyperclip not installed. Try: pip install \"ngpt[clipboard]\" {COLORS['reset']}")
                return False
        return False
    except (KeyboardInterrupt, EOFError):
        return False

def spinner(message, duration=5, spinner_chars="⣾⣽⣻⢿⡿⣟⣯⣷", color=None, stop_event=None, clean_exit=False):
    """Display a spinner animation with a message.
    
    Args:
        message: The message to display alongside the spinner
        duration: Duration in seconds to show the spinner (used if stop_event is None)
        spinner_chars: Characters to use for the spinner animation
        color: Optional color from COLORS dict to use for the message
        stop_event: Optional threading.Event to signal when to stop the spinner
                   If provided, duration is ignored and spinner runs until event is set
        clean_exit: When True, cleans up more aggressively to prevent blank lines
    """
    char_duration = 0.2

    # Apply color to message if provided
    colored_message = message
    if color:
        colored_message = f"{color}{message}{COLORS['reset']}"

    # Save cursor position - will be needed for clean exit
    if clean_exit:
        # Start by printing a \r to ensure we begin at the start of the line
        sys.stdout.write("\r")
        sys.stdout.flush()

    if stop_event:
        i = 0
        while not stop_event.is_set():
            char = spinner_chars[i % len(spinner_chars)]
            # Always use sys.stdout.write for consistent behavior
            sys.stdout.write(f"\r{colored_message} {char}")
            sys.stdout.flush()
            i += 1
            time.sleep(char_duration)
    else:
        total_chars = int(duration / char_duration)
        for i in range(total_chars):
            char = spinner_chars[i % len(spinner_chars)]
            sys.stdout.write(f"\r{colored_message} {char}")
            sys.stdout.flush()
            time.sleep(char_duration)

    # Clear the line when done - use terminal width to clear the entire line
    terminal_width = shutil.get_terminal_size().columns
    sys.stdout.write("\r" + " " * terminal_width + "\r")
    sys.stdout.flush() 