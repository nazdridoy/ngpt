import argparse
import sys
import os
from .client import NGPTClient
from .config import load_config, get_config_path, load_configs, add_config_entry, remove_config_entry
from .cli_config import (
    set_cli_config_option, 
    get_cli_config_option, 
    unset_cli_config_option, 
    apply_cli_config,
    list_cli_config_options,
    CLI_CONFIG_OPTIONS
)
from . import __version__

# Try to import markdown rendering libraries
try:
    import rich
    from rich.markdown import Markdown
    from rich.console import Console
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Try to import the glow command if available
def has_glow_installed():
    """Check if glow is installed in the system."""
    import shutil
    return shutil.which("glow") is not None

HAS_GLOW = has_glow_installed()

# ANSI color codes for terminal output
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[36m",
    "green": "\033[32m", 
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "gray": "\033[90m",
    "bg_blue": "\033[44m",
    "bg_cyan": "\033[46m"
}

# Check if ANSI colors are supported
def supports_ansi_colors():
    """Check if the current terminal supports ANSI colors."""
    import os
    import sys
    
    # If not a TTY, probably redirected, so no color
    if not sys.stdout.isatty():
        return False
        
    # Windows specific checks
    if sys.platform == "win32":
        try:
            # Windows 10+ supports ANSI colors in cmd/PowerShell
            import ctypes
            kernel32 = ctypes.windll.kernel32
            
            # Try to enable ANSI color support
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            
            # Check if TERM_PROGRAM is set (WSL/ConEmu/etc.)
            if os.environ.get('TERM_PROGRAM') or os.environ.get('WT_SESSION'):
                return True
                
            # Check Windows version - 10+ supports ANSI natively
            winver = sys.getwindowsversion()
            if winver.major >= 10:
                return True
                
            return False
        except Exception:
            return False
    
    # Most UNIX systems support ANSI colors
    return True

# Initialize color support
HAS_COLOR = supports_ansi_colors()

# If we're on Windows, use brighter colors that work better in PowerShell
if sys.platform == "win32" and HAS_COLOR:
    COLORS["magenta"] = "\033[95m"  # Bright magenta for metavars
    COLORS["cyan"] = "\033[96m"     # Bright cyan for options

# If no color support, use empty color codes
if not HAS_COLOR:
    for key in COLORS:
        COLORS[key] = ""

def has_markdown_renderer(renderer='auto'):
    """Check if the specified markdown renderer is available.
    
    Args:
        renderer (str): Which renderer to check: 'auto', 'rich', or 'glow'
    
    Returns:
        bool: True if the renderer is available, False otherwise
    """
    if renderer == 'auto':
        return HAS_RICH or HAS_GLOW
    elif renderer == 'rich':
        return HAS_RICH
    elif renderer == 'glow':
        return HAS_GLOW
    else:
        return False

def show_available_renderers():
    """Show which markdown renderers are available and their status."""
    print(f"\n{COLORS['cyan']}{COLORS['bold']}Available Markdown Renderers:{COLORS['reset']}")
    
    if HAS_GLOW:
        print(f"  {COLORS['green']}✓ Glow{COLORS['reset']} - Terminal-based Markdown renderer")
    else:
        print(f"  {COLORS['yellow']}✗ Glow{COLORS['reset']} - Not installed (https://github.com/charmbracelet/glow)")
        
    if HAS_RICH:
        print(f"  {COLORS['green']}✓ Rich{COLORS['reset']} - Python library for terminal formatting (Recommended)")
    else:
        print(f"  {COLORS['yellow']}✗ Rich{COLORS['reset']} - Not installed (pip install \"ngpt[full]\" or pip install rich)")
        
    if not HAS_GLOW and not HAS_RICH:
        print(f"\n{COLORS['yellow']}To enable prettified markdown output, install one of the above renderers.{COLORS['reset']}")
        print(f"{COLORS['yellow']}For Rich: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
    else:
        renderers = []
        if HAS_RICH:
            renderers.append("rich")
        if HAS_GLOW:
            renderers.append("glow")
        print(f"\n{COLORS['green']}Usage examples:{COLORS['reset']}")
        print(f"  ngpt --prettify \"Your prompt here\"                {COLORS['gray']}# Beautify markdown responses{COLORS['reset']}")
        print(f"  ngpt -c --prettify \"Write a sort function\"        {COLORS['gray']}# Syntax highlight generated code{COLORS['reset']}")
        if renderers:
            renderer = renderers[0]
            print(f"  ngpt --prettify --renderer={renderer} \"Your prompt\"  {COLORS['gray']}# Specify renderer{COLORS['reset']}")
    
    print("")

def warn_if_no_markdown_renderer(renderer='auto'):
    """Warn the user if the specified markdown renderer is not available.
    
    Args:
        renderer (str): Which renderer to check: 'auto', 'rich', or 'glow'
    
    Returns:
        bool: True if the renderer is available, False otherwise
    """
    if has_markdown_renderer(renderer):
        return True
    
    if renderer == 'auto':
        print(f"{COLORS['yellow']}Warning: No markdown rendering library available.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\"{COLORS['reset']}")
        print(f"{COLORS['yellow']}Or install 'glow' from https://github.com/charmbracelet/glow{COLORS['reset']}")
    elif renderer == 'rich':
        print(f"{COLORS['yellow']}Warning: Rich is not available.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
    elif renderer == 'glow':
        print(f"{COLORS['yellow']}Warning: Glow is not available.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install from https://github.com/charmbracelet/glow{COLORS['reset']}")
    else:
        print(f"{COLORS['yellow']}Error: Invalid renderer '{renderer}'. Use 'auto', 'rich', or 'glow'.{COLORS['reset']}")
    
    return False

def prettify_markdown(text, renderer='auto'):
    """Render markdown text with beautiful formatting using either Rich or Glow.
    
    The function handles both general markdown and code blocks with syntax highlighting.
    For code generation mode, it automatically wraps the code in markdown code blocks.
    
    Args:
        text (str): Markdown text to render
        renderer (str): Which renderer to use: 'auto', 'rich', or 'glow'
        
    Returns:
        bool: True if rendering was successful, False otherwise
    """
    # For 'auto', prefer rich if available, otherwise use glow
    if renderer == 'auto':
        if HAS_RICH:
            return prettify_markdown(text, 'rich')
        elif HAS_GLOW:
            return prettify_markdown(text, 'glow')
        else:
            return False
    
    # Use glow for rendering
    elif renderer == 'glow':
        if not HAS_GLOW:
            print(f"{COLORS['yellow']}Warning: Glow is not available. Install from https://github.com/charmbracelet/glow{COLORS['reset']}")
            # Fall back to rich if available
            if HAS_RICH:
                print(f"{COLORS['yellow']}Falling back to Rich renderer.{COLORS['reset']}")
                return prettify_markdown(text, 'rich')
            return False
            
        # Use glow
        import tempfile
        import subprocess
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp:
            temp_filename = temp.name
            temp.write(text)
            
        try:
            # Execute glow on the temporary file
            subprocess.run(["glow", temp_filename], check=True)
            os.unlink(temp_filename)
            return True
        except Exception as e:
            print(f"{COLORS['yellow']}Error using glow: {str(e)}{COLORS['reset']}")
            os.unlink(temp_filename)
            
            # Fall back to rich if available
            if HAS_RICH:
                print(f"{COLORS['yellow']}Falling back to Rich renderer.{COLORS['reset']}")
                return prettify_markdown(text, 'rich')
            return False
    
    # Use rich for rendering
    elif renderer == 'rich':
        if not HAS_RICH:
            print(f"{COLORS['yellow']}Warning: Rich is not available.{COLORS['reset']}")
            print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
            # Fall back to glow if available
            if HAS_GLOW:
                print(f"{COLORS['yellow']}Falling back to Glow renderer.{COLORS['reset']}")
                return prettify_markdown(text, 'glow')
            return False
            
        # Use rich
        try:
            console = Console()
            md = Markdown(text)
            console.print(md)
            return True
        except Exception as e:
            print(f"{COLORS['yellow']}Error using rich for markdown: {str(e)}{COLORS['reset']}")
            return False
    
    # Invalid renderer specified
    else:
        print(f"{COLORS['yellow']}Error: Invalid renderer '{renderer}'. Use 'auto', 'rich', or 'glow'.{COLORS['reset']}")
        return False

# Custom help formatter with color support
class ColoredHelpFormatter(argparse.HelpFormatter):
    """Help formatter that properly handles ANSI color codes without breaking alignment."""
    
    def __init__(self, prog):
        # Import modules needed for terminal size detection
        import re
        import textwrap
        import shutil
        
        # Get terminal size for dynamic width adjustment
        try:
            self.term_width = shutil.get_terminal_size().columns
        except:
            self.term_width = 80  # Default if we can't detect terminal width
        
        # Calculate dynamic layout values based on terminal width
        self.formatter_width = self.term_width - 2  # Leave some margin
        
        # For very wide terminals, limit the width to maintain readability
        if self.formatter_width > 120:
            self.formatter_width = 120
            
        # Calculate help position based on terminal width (roughly 1/3 of width)
        self.help_position = min(max(20, int(self.term_width * 0.33)), 36)
        
        # Initialize the parent class with dynamic values
        super().__init__(prog, max_help_position=self.help_position, width=self.formatter_width)
        
        # Calculate wrap width based on remaining space after help position
        self.wrap_width = self.formatter_width - self.help_position - 5
        
        # Set up the text wrapper for help text
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        self.wrapper = textwrap.TextWrapper(width=self.wrap_width)
        
    def _strip_ansi(self, s):
        """Strip ANSI escape sequences for width calculations"""
        return self.ansi_escape.sub('', s)
        
    def _colorize(self, text, color, bold=False):
        """Helper to consistently apply color with optional bold"""
        if bold:
            return f"{COLORS['bold']}{COLORS[color]}{text}{COLORS['reset']}"
        return f"{COLORS[color]}{text}{COLORS['reset']}"
        
    def _format_action_invocation(self, action):
        if not action.option_strings:
            # For positional arguments
            metavar = self._format_args(action, action.dest.upper())
            return self._colorize(metavar, 'cyan', bold=True)
        else:
            # For optional arguments with different color for metavar
            if action.nargs != argparse.SUPPRESS:
                default = self._get_default_metavar_for_optional(action)
                args_string = self._format_args(action, default)
                
                # Color option name and metavar differently
                option_part = ', '.join(action.option_strings)
                colored_option = self._colorize(option_part, 'cyan', bold=True)
                
                if args_string:
                    # Make metavars more visible with brackets and color
                    # If HAS_COLOR is False, brackets will help in PowerShell
                    if not HAS_COLOR:
                        # Add brackets to make metavars stand out even without color
                        formatted_args = f"<{args_string}>"
                    else:
                        # Use color for metavar
                        formatted_args = self._colorize(args_string, 'magenta')
                    
                    return f"{colored_option} {formatted_args}"
                else:
                    return colored_option
            else:
                return self._colorize(', '.join(action.option_strings), 'cyan', bold=True)
        
    def _format_usage(self, usage, actions, groups, prefix):
        usage_text = super()._format_usage(usage, actions, groups, prefix)
        
        # Replace "usage:" with colored version
        colored_usage = self._colorize("usage:", 'green', bold=True)
        usage_text = usage_text.replace("usage:", colored_usage)
        
        # We won't color metavars in usage text as it breaks the formatting
        # Just return with the colored usage prefix
        return usage_text
    
    def _join_parts(self, part_strings):
        """Override to fix any potential formatting issues with section joins"""
        return '\n'.join([part for part in part_strings if part])
        
    def start_section(self, heading):
        # Remove the colon as we'll add it with color
        if heading.endswith(':'):
            heading = heading[:-1]
        heading_text = f"{self._colorize(heading, 'yellow', bold=True)}:"
        super().start_section(heading_text)
            
    def _get_help_string(self, action):
        # Add color to help strings
        help_text = action.help
        if help_text:
            return help_text.replace('(default:', f"{COLORS['gray']}(default:") + COLORS['reset']
        return help_text
        
    def _wrap_help_text(self, text, initial_indent="", subsequent_indent="  "):
        """Wrap long help text to prevent overflow"""
        if not text:
            return text
            
        # Strip ANSI codes for width calculation
        clean_text = self._strip_ansi(text)
        
        # If the text is already short enough, return it as is
        if len(clean_text) <= self.wrap_width:
            return text
            
        # Handle any existing ANSI codes
        has_ansi = text != clean_text
        wrap_text = clean_text
        
        # Wrap the text
        lines = self.wrapper.wrap(wrap_text)
        
        # Add indentation to all but the first line
        wrapped = lines[0]
        for line in lines[1:]:
            wrapped += f"\n{subsequent_indent}{line}"
            
        # Re-add the ANSI codes if they were present
        if has_ansi and text.endswith(COLORS['reset']):
            wrapped += COLORS['reset']
            
        return wrapped
        
    def _format_action(self, action):
        # For subparsers, just return the regular formatting
        if isinstance(action, argparse._SubParsersAction):
            return super()._format_action(action)
            
        # Get the action header with colored parts (both option names and metavars)
        # The coloring is now done in _format_action_invocation
        action_header = self._format_action_invocation(action)
        
        # Format help text
        help_text = self._expand_help(action)
        
        # Get the raw lengths without ANSI codes for formatting
        raw_header_len = len(self._strip_ansi(action_header))
        
        # Calculate the indent for the help text
        help_position = min(self._action_max_length + 2, self._max_help_position)
        help_indent = ' ' * help_position
        
        # If the action header is too long, put help on the next line
        if raw_header_len > help_position:
            # An action header that's too long gets a line break
            # Wrap the help text with proper indentation
            wrapped_help = self._wrap_help_text(help_text, subsequent_indent=help_indent)
            line = f"{action_header}\n{help_indent}{wrapped_help}"
        else:
            # Standard formatting with proper spacing
            padding = ' ' * (help_position - raw_header_len)
            # Wrap the help text with proper indentation
            wrapped_help = self._wrap_help_text(help_text, subsequent_indent=help_indent)
            line = f"{action_header}{padding}{wrapped_help}"
            
        # Handle subactions
        if action.help is argparse.SUPPRESS:
            return line
            
        if not action.help:
            return line
            
        return line

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
    import shutil
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

def show_config_help():
    """Display help information about configuration."""
    print(f"\n{COLORS['green']}{COLORS['bold']}Configuration Help:{COLORS['reset']}")
    print(f"  1. {COLORS['cyan']}Create a config file at one of these locations:{COLORS['reset']}")
    if sys.platform == "win32":
        print(f"     - {COLORS['yellow']}%APPDATA%\\ngpt\\ngpt.conf{COLORS['reset']}")
    elif sys.platform == "darwin":
        print(f"     - {COLORS['yellow']}~/Library/Application Support/ngpt/ngpt.conf{COLORS['reset']}")
    else:
        print(f"     - {COLORS['yellow']}~/.config/ngpt/ngpt.conf{COLORS['reset']}")
    
    print(f"  2. {COLORS['cyan']}Format your config file as JSON:{COLORS['reset']}")
    print(f"""{COLORS['yellow']}     [
       {{
         "api_key": "your-api-key-here",
         "base_url": "https://api.openai.com/v1/",
         "provider": "OpenAI",
         "model": "gpt-3.5-turbo"
       }},
       {{
         "api_key": "your-second-api-key",
         "base_url": "http://localhost:1337/v1/",
         "provider": "Another Provider",
         "model": "different-model"
       }}
     ]{COLORS['reset']}""")
    
    print(f"  3. {COLORS['cyan']}Or set environment variables:{COLORS['reset']}")
    print(f"     - {COLORS['yellow']}OPENAI_API_KEY{COLORS['reset']}")
    print(f"     - {COLORS['yellow']}OPENAI_BASE_URL{COLORS['reset']}")
    print(f"     - {COLORS['yellow']}OPENAI_MODEL{COLORS['reset']}")
    
    print(f"  4. {COLORS['cyan']}Or provide command line arguments:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --api-key your-key --base-url https://api.example.com --model your-model \"Your prompt\"{COLORS['reset']}")
    
    print(f"  5. {COLORS['cyan']}Use --config-index to specify which configuration to use or edit:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config-index 1 \"Your prompt\"{COLORS['reset']}")
    
    print(f"  6. {COLORS['cyan']}Use --provider to specify which configuration to use by provider name:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --provider Gemini \"Your prompt\"{COLORS['reset']}")
    
    print(f"  7. {COLORS['cyan']}Use --config without arguments to add a new configuration:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config{COLORS['reset']}")
    print(f"     Or specify an index or provider to edit an existing configuration:")
    print(f"     {COLORS['yellow']}ngpt --config --config-index 1{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config --provider Gemini{COLORS['reset']}")

    print(f"  8. {COLORS['cyan']}Remove a configuration by index or provider:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config --remove --config-index 1{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config --remove --provider Gemini{COLORS['reset']}")

    print(f"  9. {COLORS['cyan']}List available models for the current configuration:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --list-models{COLORS['reset']}")

def check_config(config):
    """Check config for common issues and provide guidance."""
    if not config.get("api_key"):
        print(f"{COLORS['yellow']}{COLORS['bold']}Error: API key is not set.{COLORS['reset']}")
        show_config_help()
        return False
        
    # Check for common URL mistakes
    base_url = config.get("base_url", "")
    if base_url and not (base_url.startswith("http://") or base_url.startswith("https://")):
        print(f"{COLORS['yellow']}Warning: Base URL '{base_url}' doesn't start with http:// or https://{COLORS['reset']}")
    
    return True

def interactive_chat_session(client, web_search=False, no_stream=False, temperature=0.7, top_p=1.0, max_tokens=None, log_file=None, preprompt=None, prettify=False, renderer='auto', stream_prettify=False):
    """Start an interactive chat session with the AI.
    
    Args:
        client: The NGPTClient instance
        web_search: Whether to enable web search capability
        no_stream: Whether to disable streaming
        temperature: Controls randomness in the response
        top_p: Controls diversity via nucleus sampling
        max_tokens: Maximum number of tokens to generate in each response
        log_file: Optional filepath to log conversation to
        preprompt: Custom system prompt to control AI behavior
        prettify: Whether to enable markdown rendering
        renderer: Which markdown renderer to use
        stream_prettify: Whether to enable streaming with prettify
    """
    # Get terminal width for better formatting
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80  # Default fallback
    
    # Improved visual header with better layout
    header = f"{COLORS['cyan']}{COLORS['bold']}🤖 nGPT Interactive Chat Session 🤖{COLORS['reset']}"
    print(f"\n{header}")
    
    # Create a separator line - use a consistent separator length for all lines
    separator_length = min(40, term_width - 10)
    separator = f"{COLORS['gray']}{'─' * separator_length}{COLORS['reset']}"
    print(separator)
    
    # Group commands into categories with better formatting
    print(f"\n{COLORS['cyan']}Navigation:{COLORS['reset']}")
    print(f"  {COLORS['yellow']}↑/↓{COLORS['reset']} : Browse input history")
    
    print(f"\n{COLORS['cyan']}Session Commands:{COLORS['reset']}")
    print(f"  {COLORS['yellow']}history{COLORS['reset']} : Show conversation history")
    print(f"  {COLORS['yellow']}clear{COLORS['reset']}   : Reset conversation")
    print(f"  {COLORS['yellow']}exit{COLORS['reset']}    : End session")
    
    print(f"\n{separator}\n")
    
    # Initialize log file if provided
    log_handle = None
    if log_file:
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_handle = open(log_file, 'a', encoding='utf-8')
            log_handle.write(f"\n--- nGPT Session Log: {sys.argv} ---\n")
            log_handle.write(f"Started at: {timestamp}\n\n")
            print(f"{COLORS['green']}Logging conversation to: {log_file}{COLORS['reset']}")
        except Exception as e:
            print(f"{COLORS['yellow']}Warning: Could not open log file: {str(e)}{COLORS['reset']}")
            log_handle = None
    
    # Custom separator - use the same length for consistency
    def print_separator():
        print(f"\n{separator}\n")
    
    # Initialize conversation history
    system_prompt = preprompt if preprompt else "You are a helpful assistant."
    
    # Add markdown formatting instruction to system prompt if prettify is enabled
    if prettify:
        if system_prompt:
            system_prompt += " You can use markdown formatting in your responses where appropriate."
        else:
            system_prompt = "You are a helpful assistant. You can use markdown formatting in your responses where appropriate."
    
    conversation = []
    system_message = {"role": "system", "content": system_prompt}
    conversation.append(system_message)
    
    # Log system prompt if logging is enabled
    if log_handle and preprompt:
        log_handle.write(f"System: {system_prompt}\n\n")
        log_handle.flush()
    
    # Initialize prompt_toolkit history
    prompt_history = InMemoryHistory() if HAS_PROMPT_TOOLKIT else None
    
    # Decorative chat headers with rounded corners
    def user_header():
        return f"{COLORS['cyan']}{COLORS['bold']}╭─ 👤 You {COLORS['reset']}"
    
    def ngpt_header():
        return f"{COLORS['green']}{COLORS['bold']}╭─ 🤖 nGPT {COLORS['reset']}"
    
    # Function to display conversation history
    def display_history():
        if len(conversation) <= 1:  # Only system message
            print(f"\n{COLORS['yellow']}No conversation history yet.{COLORS['reset']}")
            return
            
        print(f"\n{COLORS['cyan']}{COLORS['bold']}Conversation History:{COLORS['reset']}")
        print(separator)
        
        # Skip system message
        message_count = 0
        for i, msg in enumerate(conversation):
            if msg["role"] == "system":
                continue
                
            if msg["role"] == "user":
                message_count += 1
                print(f"\n{user_header()}")
                print(f"{COLORS['cyan']}│ [{message_count}] {COLORS['reset']}{msg['content']}")
            elif msg["role"] == "assistant":
                print(f"\n{ngpt_header()}")
                print(f"{COLORS['green']}│ {COLORS['reset']}{msg['content']}")
        
        print(f"\n{separator}")  # Consistent separator at the end
    
    # Function to clear conversation history
    def clear_history():
        nonlocal conversation
        conversation = [{"role": "system", "content": system_prompt}]
        print(f"\n{COLORS['yellow']}Conversation history cleared.{COLORS['reset']}")
        print(separator)  # Add separator for consistency
    
    try:
        while True:
            # Get user input
            if HAS_PROMPT_TOOLKIT:
                # Custom styling for prompt_toolkit
                style = Style.from_dict({
                    'prompt': 'ansicyan bold',
                    'input': 'ansiwhite',
                })
                
                # Create key bindings for Ctrl+C handling
                kb = KeyBindings()
                @kb.add('c-c')
                def _(event):
                    event.app.exit(result=None)
                    raise KeyboardInterrupt()
                
                # Get user input with styled prompt - using proper HTML formatting
                user_input = pt_prompt(
                    HTML("<ansicyan><b>╭─ 👤 You:</b></ansicyan> "),
                    style=style,
                    key_bindings=kb,
                    history=prompt_history
                )
            else:
                user_input = input(f"{user_header()}: {COLORS['reset']}")
            
            # Check for exit commands
            if user_input.lower() in ('exit', 'quit', 'bye'):
                print(f"\n{COLORS['green']}Ending chat session. Goodbye!{COLORS['reset']}")
                break
            
            # Check for special commands
            if user_input.lower() == 'history':
                display_history()
                continue
            
            if user_input.lower() == 'clear':
                clear_history()
                continue
            
            # Skip empty messages but don't raise an error
            if not user_input.strip():
                print(f"{COLORS['yellow']}Empty message skipped. Type 'exit' to quit.{COLORS['reset']}")
                continue
            
            # Add user message to conversation
            user_message = {"role": "user", "content": user_input}
            conversation.append(user_message)
            
            # Log user message if logging is enabled
            if log_handle:
                log_handle.write(f"User: {user_input}\n")
                log_handle.flush()
            
            # Print assistant indicator with formatting
            if not no_stream and not stream_prettify:
                print(f"\n{ngpt_header()}: {COLORS['reset']}", end="", flush=True)
            elif not stream_prettify:
                print(f"\n{ngpt_header()}: {COLORS['reset']}", flush=True)
            
            # If prettify is enabled with regular streaming
            if prettify and not no_stream and not stream_prettify:
                print(f"\n{COLORS['yellow']}Note: Streaming disabled to enable markdown rendering.{COLORS['reset']}")
                print(f"\n{ngpt_header()}: {COLORS['reset']}", flush=True)
                should_stream = False
            else:
                # Regular behavior with stream-prettify taking precedence
                should_stream = not no_stream
            
            # Setup for stream-prettify
            stream_callback = None
            live_display = None
            
            if stream_prettify and should_stream:
                # Get the correct header for interactive mode
                header = ngpt_header()
                live_display, stream_callback = prettify_streaming_markdown(renderer, is_interactive=True, header_text=header)
                if not live_display:
                    # Fallback to normal prettify if live display setup failed
                    prettify = True
                    stream_prettify = False
                    should_stream = False
                    print(f"{COLORS['yellow']}Falling back to regular prettify mode.{COLORS['reset']}")
            
            # Start live display if using stream-prettify
            if stream_prettify and live_display:
                live_display.start()
            
            # Get AI response with conversation history
            response = client.chat(
                prompt=user_input,
                messages=conversation,
                stream=should_stream,
                web_search=web_search,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                markdown_format=prettify or stream_prettify,
                stream_callback=stream_callback
            )
            
            # Stop live display if using stream-prettify
            if stream_prettify and live_display:
                live_display.stop()
            
            # Add AI response to conversation history
            if response:
                assistant_message = {"role": "assistant", "content": response}
                conversation.append(assistant_message)
                
                # Print response if not streamed (either due to no_stream or prettify)
                if no_stream or prettify:
                    if prettify:
                        prettify_markdown(response, renderer)
                    else:
                        print(response)
                
                # Log assistant response if logging is enabled
                if log_handle:
                    log_handle.write(f"Assistant: {response}\n\n")
                    log_handle.flush()
            
            # Print separator between exchanges
            print_separator()
            
    except KeyboardInterrupt:
        print(f"\n\n{COLORS['green']}Chat session ended by user. Goodbye!{COLORS['reset']}")
    except Exception as e:
        print(f"\n{COLORS['yellow']}Error during chat session: {str(e)}{COLORS['reset']}")
        # Print traceback for debugging if it's a serious error
        import traceback
        traceback.print_exc()
    finally:
        # Close log file if it was opened
        if log_handle:
            log_handle.write(f"\n--- End of Session ---\n")
            log_handle.close()

def prettify_streaming_markdown(renderer='rich', is_interactive=False, header_text=None):
    """Set up streaming markdown rendering.
    
    This function creates a live display context for rendering markdown
    that can be updated in real-time as streaming content arrives.
    
    Args:
        renderer (str): Which renderer to use (currently only 'rich' is supported for streaming)
        is_interactive (bool): Whether this is being used in interactive mode
        header_text (str): Header text to include at the top (for interactive mode)
        
    Returns:
        tuple: (live_display, update_function) if successful, (None, None) otherwise
    """
    # Only warn if explicitly specifying a renderer other than 'rich' or 'auto'
    if renderer != 'rich' and renderer != 'auto':
        print(f"{COLORS['yellow']}Warning: Streaming prettify only supports 'rich' renderer currently.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Falling back to Rich renderer.{COLORS['reset']}")
    
    # Always use rich for streaming prettify
    renderer = 'rich'
    
    if not HAS_RICH:
        print(f"{COLORS['yellow']}Warning: Rich is not available for streaming prettify.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
        return None, None
        
    try:
        from rich.live import Live
        from rich.markdown import Markdown
        from rich.console import Console
        from rich.text import Text
        from rich.panel import Panel
        import rich.box
        
        console = Console()
        
        # Create an empty markdown object to start with
        if is_interactive and header_text:
            # For interactive mode, include header in a panel
            # Clean up the header text to avoid duplication - use just "🤖 nGPT" instead of "╭─ 🤖 nGPT"
            clean_header = "🤖 nGPT"
            panel_title = Text(clean_header, style="cyan bold")
            
            # Create a nicer, more compact panel
            padding = (1, 1)  # Less horizontal padding (left, right)
            md_obj = Panel(
                Markdown(""),
                title=panel_title,
                title_align="left",
                border_style="cyan",
                padding=padding,
                width=console.width - 4,  # Make panel slightly narrower than console
                box=rich.box.ROUNDED
            )
        else:
            md_obj = Markdown("")
        
        # Initialize the Live display with an empty markdown
        live = Live(md_obj, console=console, refresh_per_second=10)
        
        # Define an update function that will be called with new content
        def update_content(content):
            nonlocal md_obj
            if is_interactive and header_text:
                # Update the panel content
                md_obj.renderable = Markdown(content)
                live.update(md_obj)
            else:
                md_obj = Markdown(content)
                live.update(md_obj)
            
        return live, update_content
    except Exception as e:
        print(f"{COLORS['yellow']}Error setting up Rich streaming display: {str(e)}{COLORS['reset']}")
        return None, None

def show_cli_config_help():
    """Display help information about CLI configuration."""
    print(f"\n{COLORS['green']}{COLORS['bold']}CLI Configuration Help:{COLORS['reset']}")
    print(f"  {COLORS['cyan']}Command syntax:{COLORS['reset']}")
    print(f"    {COLORS['yellow']}ngpt --cli-config set OPTION VALUE{COLORS['reset']}    - Set a default value for OPTION")
    print(f"    {COLORS['yellow']}ngpt --cli-config get OPTION{COLORS['reset']}          - Get the current value of OPTION")
    print(f"    {COLORS['yellow']}ngpt --cli-config get{COLORS['reset']}                 - Show all CLI configuration settings")
    print(f"    {COLORS['yellow']}ngpt --cli-config unset OPTION{COLORS['reset']}        - Remove OPTION from configuration")
    print(f"    {COLORS['yellow']}ngpt --cli-config list{COLORS['reset']}                - List all available options")
    
    print(f"\n  {COLORS['cyan']}Available options:{COLORS['reset']}")
    
    # Group options by context
    context_groups = {
        "all": [],
        "code": [],
        "interactive": [],
        "text": [],
        "shell": []
    }
    
    for option, meta in CLI_CONFIG_OPTIONS.items():
        for context in meta["context"]:
            if context in context_groups:
                if context == "all":
                    context_groups[context].append(option)
                    break
                else:
                    context_groups[context].append(option)
    
    # Print general options (available in all contexts)
    print(f"    {COLORS['yellow']}General options (all modes):{COLORS['reset']}")
    for option in sorted(context_groups["all"]):
        meta = CLI_CONFIG_OPTIONS[option]
        default = f"(default: {meta['default']})" if meta['default'] is not None else ""
        exclusive = f" [exclusive with: {', '.join(meta['exclusive'])}]" if "exclusive" in meta else ""
        print(f"      {COLORS['green']}{option}{COLORS['reset']} - {meta['type']} {default}{exclusive}")
    
    # Print mode-specific options
    for mode, options in [
        ("code", "Code generation mode"),
        ("interactive", "Interactive mode"),
        ("text", "Text mode"),
        ("shell", "Shell mode")
    ]:
        if context_groups[mode]:
            print(f"\n    {COLORS['yellow']}Options for {options}:{COLORS['reset']}")
            for option in sorted(context_groups[mode]):
                # Skip if already listed in general options
                if option in context_groups["all"]:
                    continue
                meta = CLI_CONFIG_OPTIONS[option]
                default = f"(default: {meta['default']})" if meta['default'] is not None else ""
                exclusive = f" [exclusive with: {', '.join(meta['exclusive'])}]" if "exclusive" in meta else ""
                print(f"      {COLORS['green']}{option}{COLORS['reset']} - {meta['type']} {default}{exclusive}")
    
    print(f"\n  {COLORS['cyan']}Example usage:{COLORS['reset']}")
    print(f"    {COLORS['yellow']}ngpt --cli-config set language java{COLORS['reset']}        - Set default language to java for code generation")
    print(f"    {COLORS['yellow']}ngpt --cli-config set temperature 0.9{COLORS['reset']}      - Set default temperature to 0.9")
    print(f"    {COLORS['yellow']}ngpt --cli-config set no-stream true{COLORS['reset']}       - Disable streaming by default")
    print(f"    {COLORS['yellow']}ngpt --cli-config unset language{COLORS['reset']}           - Remove language setting")
    
    print(f"\n  {COLORS['cyan']}Notes:{COLORS['reset']}")
    print(f"    - CLI configuration is stored in {COLORS['yellow']}~/.config/ngpt/ngpt-cli.conf{COLORS['reset']} (or equivalent for your OS)")
    print(f"    - Settings are applied based on context (e.g., language only applies to code generation mode)")
    print(f"    - Command-line arguments always override CLI configuration")
    print(f"    - Some options are mutually exclusive and will not be applied together")

def handle_cli_config(action, option=None, value=None):
    """Handle CLI configuration commands."""
    if action == "list":
        # List all available options
        print(f"{COLORS['green']}{COLORS['bold']}Available CLI configuration options:{COLORS['reset']}")
        for option in list_cli_config_options():
            meta = CLI_CONFIG_OPTIONS[option]
            default = f"(default: {meta['default']})" if meta['default'] is not None else ""
            contexts = ', '.join(meta['context'])
            if "all" in meta['context']:
                contexts = "all modes"
            print(f"  {COLORS['cyan']}{option}{COLORS['reset']} - {meta['type']} {default} - Available in: {contexts}")
        return
    
    if action == "get":
        if option is None:
            # Get all options
            success, config = get_cli_config_option()
            if success and config:
                print(f"{COLORS['green']}{COLORS['bold']}Current CLI configuration:{COLORS['reset']}")
                for opt, val in config.items():
                    if opt in CLI_CONFIG_OPTIONS:
                        print(f"  {COLORS['cyan']}{opt}{COLORS['reset']} = {val}")
                    else:
                        print(f"  {COLORS['yellow']}{opt}{COLORS['reset']} = {val} (unknown option)")
            else:
                print(f"{COLORS['yellow']}No CLI configuration set. Use 'ngpt --cli-config set OPTION VALUE' to set options.{COLORS['reset']}")
        else:
            # Get specific option
            success, result = get_cli_config_option(option)
            if success:
                if result is None:
                    print(f"{COLORS['cyan']}{option}{COLORS['reset']} is not set (default: {CLI_CONFIG_OPTIONS.get(option, {}).get('default', 'N/A')})")
                else:
                    print(f"{COLORS['cyan']}{option}{COLORS['reset']} = {result}")
            else:
                print(f"{COLORS['yellow']}{result}{COLORS['reset']}")
        return
    
    if action == "set":
        if option is None or value is None:
            print(f"{COLORS['yellow']}Error: Both OPTION and VALUE are required for 'set' command.{COLORS['reset']}")
            print(f"Usage: ngpt --cli-config set OPTION VALUE")
            return
            
        success, message = set_cli_config_option(option, value)
        if success:
            print(f"{COLORS['green']}{message}{COLORS['reset']}")
        else:
            print(f"{COLORS['yellow']}{message}{COLORS['reset']}")
        return
    
    if action == "unset":
        if option is None:
            print(f"{COLORS['yellow']}Error: OPTION is required for 'unset' command.{COLORS['reset']}")
            print(f"Usage: ngpt --cli-config unset OPTION")
            return
            
        success, message = unset_cli_config_option(option)
        if success:
            print(f"{COLORS['green']}{message}{COLORS['reset']}")
        else:
            print(f"{COLORS['yellow']}{message}{COLORS['reset']}")
        return
    
    # If we get here, the action is not recognized
    print(f"{COLORS['yellow']}Error: Unknown action '{action}'. Use 'set', 'get', 'unset', or 'list'.{COLORS['reset']}")
    show_cli_config_help()

def main():
    # Colorize description - use a shorter description to avoid line wrapping issues
    description = f"{COLORS['cyan']}{COLORS['bold']}nGPT{COLORS['reset']} - Interact with AI language models via OpenAI-compatible APIs"
    
    # Minimalist, clean epilog design
    epilog = f"\n{COLORS['yellow']}nGPT {COLORS['bold']}v{__version__}{COLORS['reset']}  •  {COLORS['green']}Docs: {COLORS['bold']}https://nazdridoy.github.io/ngpt/usage/cli_usage.html{COLORS['reset']}"
    
    parser = argparse.ArgumentParser(description=description, formatter_class=ColoredHelpFormatter, epilog=epilog)
    
    # Add custom error method with color
    original_error = parser.error
    def error_with_color(message):
        parser.print_usage(sys.stderr)
        parser.exit(2, f"{COLORS['bold']}{COLORS['yellow']}error: {COLORS['reset']}{message}\n")
    parser.error = error_with_color
    
    # Custom version action with color
    class ColoredVersionAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print(f"{COLORS['green']}{COLORS['bold']}nGPT{COLORS['reset']} version {COLORS['yellow']}{__version__}{COLORS['reset']}")
            parser.exit()
    
    # Version flag
    parser.add_argument('-v', '--version', action=ColoredVersionAction, nargs=0, help='Show version information and exit')
    
    # Config options
    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument('--config', nargs='?', const=True, help='Path to a custom config file or, if no value provided, enter interactive configuration mode to create a new config')
    config_group.add_argument('--config-index', type=int, default=0, help='Index of the configuration to use or edit (default: 0)')
    config_group.add_argument('--provider', help='Provider name to identify the configuration to use')
    config_group.add_argument('--remove', action='store_true', help='Remove the configuration at the specified index (requires --config and --config-index)')
    config_group.add_argument('--show-config', action='store_true', help='Show the current configuration(s) and exit')
    config_group.add_argument('--all', action='store_true', help='Show details for all configurations (requires --show-config)')
    config_group.add_argument('--list-models', action='store_true', help='List all available models for the current configuration and exit')
    config_group.add_argument('--list-renderers', action='store_true', help='Show available markdown renderers for use with --prettify')
    
    # Global options
    global_group = parser.add_argument_group('Global Options')
    global_group.add_argument('--api-key', help='API key for the service')
    global_group.add_argument('--base-url', help='Base URL for the API')
    global_group.add_argument('--model', help='Model to use')
    global_group.add_argument('--web-search', action='store_true', 
                      help='Enable web search capability (Note: Your API endpoint must support this feature)')
    global_group.add_argument('-n', '--no-stream', action='store_true',
                      help='Return the whole response without streaming')
    global_group.add_argument('--temperature', type=float, default=0.7,
                      help='Set temperature (controls randomness, default: 0.7)')
    global_group.add_argument('--top_p', type=float, default=1.0,
                      help='Set top_p (controls diversity, default: 1.0)')
    global_group.add_argument('--max_tokens', type=int, 
                      help='Set max response length in tokens')
    global_group.add_argument('--log', metavar='FILE',
                      help='Set filepath to log conversation to (For interactive modes)')
    global_group.add_argument('--preprompt', 
                      help='Set custom system prompt to control AI behavior')
    global_group.add_argument('--prettify', action='store_const', const='auto',
                      help='Render markdown responses and code with syntax highlighting and formatting')
    global_group.add_argument('--stream-prettify', action='store_true',
                      help='Enable streaming with markdown rendering (automatically uses Rich renderer)')
    global_group.add_argument('--renderer', choices=['auto', 'rich', 'glow'], default='auto',
                      help='Select which markdown renderer to use with --prettify (auto, rich, or glow)')
    
    # Mode flags (mutually exclusive)
    mode_group = parser.add_argument_group('Modes (mutually exclusive)')
    mode_exclusive_group = mode_group.add_mutually_exclusive_group()
    mode_exclusive_group.add_argument('-i', '--interactive', action='store_true', help='Start an interactive chat session')
    mode_exclusive_group.add_argument('-s', '--shell', action='store_true', help='Generate and execute shell commands')
    mode_exclusive_group.add_argument('-c', '--code', action='store_true', help='Generate code')
    mode_exclusive_group.add_argument('-t', '--text', action='store_true', help='Enter multi-line text input (submit with Ctrl+D)')
    # Note: --show-config is handled separately and implicitly acts as a mode
    
    # Language option for code mode
    parser.add_argument('--language', default="python", help='Programming language to generate code in (for code mode)')
    
    # Prompt argument
    parser.add_argument('prompt', nargs='?', default=None, help='The prompt to send')
    
    # Add CLI configuration command
    config_group.add_argument('--cli-config', nargs='*', metavar='COMMAND',
                      help='Manage CLI configuration (set, get, unset, list)')
    
    args = parser.parse_args()
    
    # Handle CLI configuration command
    if args.cli_config is not None:
        # Show help if no arguments or "help" argument
        if len(args.cli_config) == 0 or (len(args.cli_config) > 0 and args.cli_config[0].lower() == "help"):
            show_cli_config_help()
            return
            
        action = args.cli_config[0].lower()
        option = args.cli_config[1] if len(args.cli_config) > 1 else None
        value = args.cli_config[2] if len(args.cli_config) > 2 else None
        
        if action in ("set", "get", "unset", "list"):
            handle_cli_config(action, option, value)
            return
        else:
            show_cli_config_help()
            return
    
    # Validate --all usage
    if args.all and not args.show_config:
        parser.error("--all can only be used with --show-config")
    
    # Handle --renderers flag to show available markdown renderers
    if args.list_renderers:
        show_available_renderers()
        return
    
    # Load CLI configuration early
    from .cli_config import load_cli_config
    cli_config = load_cli_config()
    
    # Priority order for config selection:
    # 1. Command-line arguments (args.provider, args.config_index)
    # 2. CLI configuration (cli_config["provider"], cli_config["config-index"])
    # 3. Default values (None, 0)
    
    # Get provider/config-index from CLI config if not specified in args
    effective_provider = args.provider
    effective_config_index = args.config_index
    
    # Only apply CLI config for provider/config-index if not explicitly set on command line
    if not effective_provider and 'provider' in cli_config and '--provider' not in sys.argv:
        effective_provider = cli_config['provider']
    
    if effective_config_index == 0 and 'config-index' in cli_config and '--config-index' not in sys.argv:
        effective_config_index = cli_config['config-index']
    
    # Check for mutual exclusivity between provider and config-index
    if effective_config_index != 0 and effective_provider:
        parser.error("--config-index and --provider cannot be used together")

    # Handle interactive configuration mode
    if args.config is True:  # --config was used without a value
        config_path = get_config_path()
        
        # Handle configuration removal if --remove flag is present
        if args.remove:
            # Validate that config_index is explicitly provided
            if '--config-index' not in sys.argv and not effective_provider:
                parser.error("--remove requires explicitly specifying --config-index or --provider")
            
            # Show config details before asking for confirmation
            configs = load_configs(str(config_path))
            
            # Determine the config index to remove
            config_index = effective_config_index
            if effective_provider:
                # Find config index by provider name
                matching_configs = [i for i, cfg in enumerate(configs) if cfg.get('provider', '').lower() == effective_provider.lower()]
                if not matching_configs:
                    print(f"Error: No configuration found for provider '{effective_provider}'")
                    return
                elif len(matching_configs) > 1:
                    print(f"Multiple configurations found for provider '{effective_provider}':")
                    for i, idx in enumerate(matching_configs):
                        print(f"  [{i}] Index {idx}: {configs[idx].get('model', 'Unknown model')}")
                    
                    try:
                        choice = input("Choose a configuration to remove (or press Enter to cancel): ")
                        if choice and choice.isdigit() and 0 <= int(choice) < len(matching_configs):
                            config_index = matching_configs[int(choice)]
                        else:
                            print("Configuration removal cancelled.")
                            return
                    except (ValueError, IndexError, KeyboardInterrupt):
                        print("\nConfiguration removal cancelled.")
                        return
                else:
                    config_index = matching_configs[0]
            
            # Check if index is valid
            if config_index < 0 or config_index >= len(configs):
                print(f"Error: Configuration index {config_index} is out of range. Valid range: 0-{len(configs)-1}")
                return
            
            # Show the configuration that will be removed
            config = configs[config_index]
            print(f"Configuration to remove (index {config_index}):")
            print(f"  Provider: {config.get('provider', 'N/A')}")
            print(f"  Model: {config.get('model', 'N/A')}")
            print(f"  Base URL: {config.get('base_url', 'N/A')}")
            print(f"  API Key: {'[Set]' if config.get('api_key') else '[Not Set]'}")
            
            # Ask for confirmation
            try:
                print("\nAre you sure you want to remove this configuration? [y/N] ", end='')
                response = input().lower()
                if response in ('y', 'yes'):
                    remove_config_entry(config_path, config_index)
                else:
                    print("Configuration removal cancelled.")
            except KeyboardInterrupt:
                print("\nConfiguration removal cancelled by user.")
            
            return
        
        # Regular config addition/editing (existing code)
        # If --config-index was not explicitly specified, create a new entry by passing None
        # This will cause add_config_entry to create a new entry at the end of the list
        # Otherwise, edit the existing config at the specified index
        config_index = None
        
        # Determine if we're editing an existing config or creating a new one
        if effective_provider:
            # Find config by provider name
            configs = load_configs(str(config_path))
            matching_configs = [i for i, cfg in enumerate(configs) if cfg.get('provider', '').lower() == effective_provider.lower()]
            
            if not matching_configs:
                print(f"No configuration found for provider '{effective_provider}'. Creating a new configuration.")
            elif len(matching_configs) > 1:
                print(f"Multiple configurations found for provider '{effective_provider}':")
                for i, idx in enumerate(matching_configs):
                    print(f"  [{i}] Index {idx}: {configs[idx].get('model', 'Unknown model')}")
                
                try:
                    choice = input("Choose a configuration to edit (or press Enter for the first one): ")
                    if choice and choice.isdigit() and 0 <= int(choice) < len(matching_configs):
                        config_index = matching_configs[int(choice)]
                    else:
                        config_index = matching_configs[0]
                except (ValueError, IndexError, KeyboardInterrupt):
                    config_index = matching_configs[0]
            else:
                config_index = matching_configs[0]
                
            print(f"Editing existing configuration at index {config_index}")
        elif effective_config_index != 0 or '--config-index' in sys.argv:
            # Check if the index is valid
            configs = load_configs(str(config_path))
            if effective_config_index >= 0 and effective_config_index < len(configs):
                config_index = effective_config_index
                print(f"Editing existing configuration at index {config_index}")
            else:
                print(f"Configuration index {effective_config_index} is out of range. Creating a new configuration.")
        else:
            # Creating a new config
            configs = load_configs(str(config_path))
            print(f"Creating new configuration at index {len(configs)}")
        
        add_config_entry(config_path, config_index)
        return
    
    # Load configuration using the effective provider/config-index
    active_config = load_config(args.config, effective_config_index, effective_provider)
    
    # Command-line arguments override config settings for active config display
    if args.api_key:
        active_config["api_key"] = args.api_key
    if args.base_url:
        active_config["base_url"] = args.base_url
    if args.model:
        active_config["model"] = args.model
    
    # Show config if requested
    if args.show_config:
        config_path = get_config_path(args.config)
        configs = load_configs(args.config)
        
        print(f"Configuration file: {config_path}")
        print(f"Total configurations: {len(configs)}")
        
        # Determine active configuration and display identifier
        active_identifier = f"index {effective_config_index}"
        if effective_provider:
            active_identifier = f"provider '{effective_provider}'"
        print(f"Active configuration: {active_identifier}")

        if args.all:
            # Show details for all configurations
            print("\nAll configuration details:")
            for i, cfg in enumerate(configs):
                provider = cfg.get('provider', 'N/A')
                active_str = '(Active)' if (
                    (effective_provider and provider.lower() == effective_provider.lower()) or 
                    (not effective_provider and i == effective_config_index)
                ) else ''
                print(f"\n--- Configuration Index {i} / Provider: {COLORS['green']}{provider}{COLORS['reset']} {active_str} ---")
                print(f"  API Key: {'[Set]' if cfg.get('api_key') else '[Not Set]'}")
                print(f"  Base URL: {cfg.get('base_url', 'N/A')}")
                print(f"  Model: {cfg.get('model', 'N/A')}")
        else:
            # Show active config details and summary list
            print("\nActive configuration details:")
            print(f"  Provider: {COLORS['green']}{active_config.get('provider', 'N/A')}{COLORS['reset']}")
            print(f"  API Key: {'[Set]' if active_config.get('api_key') else '[Not Set]'}")
            print(f"  Base URL: {active_config.get('base_url', 'N/A')}")
            print(f"  Model: {active_config.get('model', 'N/A')}")
            
            if len(configs) > 1:
                print("\nAvailable configurations:")
                # Check for duplicate provider names for warning
                provider_counts = {}
                for cfg in configs:
                    provider = cfg.get('provider', 'N/A').lower()
                    provider_counts[provider] = provider_counts.get(provider, 0) + 1
                
                for i, cfg in enumerate(configs):
                    provider = cfg.get('provider', 'N/A')
                    provider_display = provider
                    # Add warning for duplicate providers
                    if provider_counts.get(provider.lower(), 0) > 1:
                        provider_display = f"{provider} {COLORS['yellow']}(duplicate){COLORS['reset']}"
                    
                    active_marker = "*" if (
                        (effective_provider and provider.lower() == effective_provider.lower()) or 
                        (not effective_provider and i == effective_config_index)
                    ) else " "
                    print(f"[{i}]{active_marker} {COLORS['green']}{provider_display}{COLORS['reset']} - {cfg.get('model', 'N/A')} ({'[API Key Set]' if cfg.get('api_key') else '[API Key Not Set]'})")
                
                # Show instruction for using --provider
                print(f"\nTip: Use {COLORS['yellow']}--provider NAME{COLORS['reset']} to select a configuration by provider name.")
        
        return
    
    # For interactive mode, we'll allow continuing without a specific prompt
    if not args.prompt and not (args.shell or args.code or args.text or args.interactive or args.show_config or args.list_models):
        parser.print_help()
        return
        
    # Check configuration (using the potentially overridden active_config)
    if not args.show_config and not args.list_models and not check_config(active_config):
        return
    
    # Check if --prettify is used but no markdown renderer is available
    # This will warn the user immediately if they request prettify but don't have the tools
    has_renderer = True
    if args.prettify:
        has_renderer = warn_if_no_markdown_renderer(args.renderer)
        if not has_renderer:
            # Set a flag to disable prettify since we already warned the user
            print(f"{COLORS['yellow']}Continuing without markdown rendering.{COLORS['reset']}")
            show_available_renderers()
            args.prettify = False
        
    # Check if --prettify is used with --stream-prettify (conflict)
    if args.prettify and args.stream_prettify:
        parser.error("--prettify and --stream-prettify cannot be used together. Choose one option.")

    # Check if --stream-prettify is used but Rich is not available
    if args.stream_prettify and not has_markdown_renderer('rich'):
        parser.error("--stream-prettify requires Rich to be installed. Install with: pip install \"ngpt[full]\" or pip install rich")

    # Initialize client using the potentially overridden active_config
    client = NGPTClient(**active_config)
    
    try:
        # Handle listing models
        if args.list_models:
            print("Retrieving available models...")
            models = client.list_models()
            if models:
                print(f"\nAvailable models for {active_config.get('provider', 'API')}:")
                print("-" * 50)
                for model in models:
                    if "id" in model:
                        owned_by = f" ({model.get('owned_by', 'Unknown')})" if "owned_by" in model else ""
                        current = " [active]" if model["id"] == active_config["model"] else ""
                        print(f"- {model['id']}{owned_by}{current}")
                print("\nUse --model MODEL_NAME to select a specific model")
            else:
                print("No models available or could not retrieve models.")
            return
        
        # Handle modes
        if args.interactive:
            # Apply CLI config for interactive mode
            args = apply_cli_config(args, "interactive")
            
            # Interactive chat mode
            interactive_chat_session(
                client,
                web_search=args.web_search,
                no_stream=args.no_stream, 
                temperature=args.temperature,
                top_p=args.top_p,
                max_tokens=args.max_tokens,
                log_file=args.log,
                preprompt=args.preprompt,
                prettify=args.prettify,
                renderer=args.renderer,
                stream_prettify=args.stream_prettify
            )
        elif args.shell:
            # Apply CLI config for shell mode
            args = apply_cli_config(args, "shell")
            
            if args.prompt is None:
                try:
                    print("Enter shell command description: ", end='')
                    prompt = input()
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            else:
                prompt = args.prompt
                
            command = client.generate_shell_command(prompt, web_search=args.web_search, 
                                                 temperature=args.temperature, top_p=args.top_p,
                                                 max_tokens=args.max_tokens)
            if not command:
                return  # Error already printed by client
                
            print(f"\nGenerated command: {command}")
            
            try:
                print("Do you want to execute this command? [y/N] ", end='')
                response = input().lower()
            except KeyboardInterrupt:
                print("\nCommand execution cancelled by user.")
                return
                
            if response == 'y' or response == 'yes':
                import subprocess
                try:
                    try:
                        print("\nExecuting command... (Press Ctrl+C to cancel)")
                        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                        print(f"\nOutput:\n{result.stdout}")
                    except KeyboardInterrupt:
                        print("\nCommand execution cancelled by user.")
                except subprocess.CalledProcessError as e:
                    print(f"\nError:\n{e.stderr}")
                    
        elif args.code:
            # Apply CLI config for code mode
            args = apply_cli_config(args, "code")
            
            if args.prompt is None:
                try:
                    print("Enter code description: ", end='')
                    prompt = input()
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            else:
                prompt = args.prompt

            # Setup for streaming and prettify logic
            stream_callback = None
            live_display = None
            should_stream = True # Default to streaming
            use_stream_prettify = False
            use_regular_prettify = False

            # Determine final behavior based on flag priority
            if args.stream_prettify:
                # Highest priority: stream-prettify
                if has_markdown_renderer('rich'):
                    should_stream = True
                    use_stream_prettify = True
                    live_display, stream_callback = prettify_streaming_markdown(args.renderer)
                    if not live_display:
                        # Fallback if live display fails
                        use_stream_prettify = False
                        use_regular_prettify = True
                        should_stream = False 
                        print(f"{COLORS['yellow']}Live display setup failed. Falling back to regular prettify mode.{COLORS['reset']}")
                else:
                    # Rich not available for stream-prettify
                    print(f"{COLORS['yellow']}Warning: Rich is not available for --stream-prettify. Install with: pip install \"ngpt[full]\".{COLORS['reset']}")
                    print(f"{COLORS['yellow']}Falling back to default streaming without prettify.{COLORS['reset']}")
                    should_stream = True
                    use_stream_prettify = False
            elif args.no_stream:
                # Second priority: no-stream
                should_stream = False
                use_regular_prettify = False # No prettify if no streaming
            elif args.prettify:
                # Third priority: prettify (requires disabling stream)
                if has_markdown_renderer(args.renderer):
                    should_stream = False
                    use_regular_prettify = True
                    print(f"{COLORS['yellow']}Note: Streaming disabled to enable regular markdown rendering (--prettify).{COLORS['reset']}")
                else:
                    # Renderer not available for prettify
                    print(f"{COLORS['yellow']}Warning: Renderer '{args.renderer}' not available for --prettify.{COLORS['reset']}")
                    show_available_renderers()
                    print(f"{COLORS['yellow']}Falling back to default streaming without prettify.{COLORS['reset']}")
                    should_stream = True 
                    use_regular_prettify = False
            # else: Default is should_stream = True
            
            print("\nGenerating code...")
            
            # Start live display if using stream-prettify
            if use_stream_prettify and live_display:
                live_display.start()
                
            generated_code = client.generate_code(
                prompt=prompt, 
                language=args.language, 
                web_search=args.web_search,
                temperature=args.temperature, 
                top_p=args.top_p,
                max_tokens=args.max_tokens,
                # Request markdown from API if any prettify option is active
                markdown_format=use_regular_prettify or use_stream_prettify,
                stream=should_stream,
                stream_callback=stream_callback
            )
            
            # Stop live display if using stream-prettify
            if use_stream_prettify and live_display:
                live_display.stop()
                
            # Print non-streamed output if needed
            if generated_code and not should_stream:
                if use_regular_prettify:
                    print("\nGenerated code:")
                    prettify_markdown(generated_code, args.renderer)
                else:
                    # Should only happen if --no-stream was used without prettify
                    print(f"\nGenerated code:\n{generated_code}")
        
        elif args.text:
            # Apply CLI config for text mode
            args = apply_cli_config(args, "text")
            
            if args.prompt is not None:
                prompt = args.prompt
            else:
                try:
                    if HAS_PROMPT_TOOLKIT:
                        print("\033[94m\033[1m" + "Multi-line Input Mode" + "\033[0m")
                        print("Press Ctrl+D to submit, Ctrl+C to exit")
                        print("Use arrow keys to navigate, Enter for new line")
                        
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
                        
                        # Create and run the application
                        app = Application(
                            layout=layout,
                            full_screen=False,
                            key_bindings=kb,
                            style=style,
                            mouse_support=True,
                        )
                        
                        prompt = app.run()
                        
                        if not prompt or not prompt.strip():
                            print("Empty prompt. Exiting.")
                            return
                    else:
                        # Fallback to standard input with a better implementation
                        print("Enter your multi-line prompt (press Ctrl+D to submit):")
                        print("Note: Install 'prompt_toolkit' package for an enhanced input experience")
                        
                        # Use a more robust approach for multiline input without prompt_toolkit
                        lines = []
                        while True:
                            try:
                                line = input()
                                lines.append(line)
                            except EOFError:  # Ctrl+D was pressed
                                break
                        
                        prompt = "\n".join(lines)
                        if not prompt.strip():
                            print("Empty prompt. Exiting.")
                            return
                        
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            
            print("\nSubmission successful. Waiting for response...")
            
            # Create messages array with preprompt if available
            messages = None
            if args.preprompt:
                messages = [
                    {"role": "system", "content": args.preprompt},
                    {"role": "user", "content": prompt}
                ]
            
            # Set default streaming behavior based on --no-stream and --prettify arguments
            should_stream = not args.no_stream and not args.prettify
            
            # If stream-prettify is enabled
            stream_callback = None
            live_display = None
            
            if args.stream_prettify:
                should_stream = True  # Enable streaming
                # This is the standard mode, not interactive
                live_display, stream_callback = prettify_streaming_markdown(args.renderer)
                if not live_display:
                    # Fallback to normal prettify if live display setup failed
                    args.prettify = True
                    args.stream_prettify = False
                    should_stream = False
                    print(f"{COLORS['yellow']}Falling back to regular prettify mode.{COLORS['reset']}")
            
            # If regular prettify is enabled with streaming, inform the user
            if args.prettify and not args.no_stream:
                print(f"{COLORS['yellow']}Note: Streaming disabled to enable markdown rendering.{COLORS['reset']}")
            
            # Start live display if using stream-prettify
            if args.stream_prettify and live_display:
                live_display.start()
            
            response = client.chat(prompt, stream=should_stream, web_search=args.web_search,
                               temperature=args.temperature, top_p=args.top_p,
                               max_tokens=args.max_tokens, messages=messages,
                               markdown_format=args.prettify or args.stream_prettify,
                               stream_callback=stream_callback)
            
            # Stop live display if using stream-prettify
            if args.stream_prettify and live_display:
                live_display.stop()
                
            # Handle non-stream response or regular prettify
            if (args.no_stream or args.prettify) and response:
                if args.prettify:
                    prettify_markdown(response, args.renderer)
                else:
                    print(response)
        
        else:
            # Default to chat mode
            # Apply CLI config for default chat mode
            args = apply_cli_config(args, "all")
            
            if args.prompt is None:
                try:
                    print("Enter your prompt: ", end='')
                    prompt = input()
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            else:
                prompt = args.prompt
                
            # Create messages array with preprompt if available
            messages = None
            if args.preprompt:
                messages = [
                    {"role": "system", "content": args.preprompt},
                    {"role": "user", "content": prompt}
                ]
            
            # Set default streaming behavior based on --no-stream and --prettify arguments
            should_stream = not args.no_stream and not args.prettify
            
            # If stream-prettify is enabled
            stream_callback = None
            live_display = None
            
            if args.stream_prettify:
                should_stream = True  # Enable streaming
                # This is the standard mode, not interactive
                live_display, stream_callback = prettify_streaming_markdown(args.renderer)
                if not live_display:
                    # Fallback to normal prettify if live display setup failed
                    args.prettify = True
                    args.stream_prettify = False
                    should_stream = False
                    print(f"{COLORS['yellow']}Falling back to regular prettify mode.{COLORS['reset']}")
            
            # If regular prettify is enabled with streaming, inform the user
            if args.prettify and not args.no_stream:
                print(f"{COLORS['yellow']}Note: Streaming disabled to enable markdown rendering.{COLORS['reset']}")
            
            # Start live display if using stream-prettify
            if args.stream_prettify and live_display:
                live_display.start()
            
            response = client.chat(prompt, stream=should_stream, web_search=args.web_search,
                               temperature=args.temperature, top_p=args.top_p,
                               max_tokens=args.max_tokens, messages=messages,
                               markdown_format=args.prettify or args.stream_prettify,
                               stream_callback=stream_callback)
            
            # Stop live display if using stream-prettify
            if args.stream_prettify and live_display:
                live_display.stop()
                
            # Handle non-stream response or regular prettify
            if (args.no_stream or args.prettify) and response:
                if args.prettify:
                    prettify_markdown(response, args.renderer)
                else:
                    print(response)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting gracefully.")
        # Make sure we exit with a non-zero status code to indicate the operation was cancelled
        sys.exit(130)  # 130 is the standard exit code for SIGINT (Ctrl+C)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with error code

if __name__ == "__main__":
    main() 