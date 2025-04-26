import sys
import os
import shutil
import argparse
import re
import textwrap
import ctypes

# ANSI color codes for terminal output
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

# Check if ANSI colors are supported
def supports_ansi_colors():
    """Check if the current terminal supports ANSI colors."""
    
    # If not a TTY, probably redirected, so no color
    if not sys.stdout.isatty():
        return False
        
    # Windows specific checks
    if sys.platform == "win32":
        try:
            # Windows 10+ supports ANSI colors in cmd/PowerShell
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

# Custom help formatter with color support
class ColoredHelpFormatter(argparse.HelpFormatter):
    """Help formatter that properly handles ANSI color codes without breaking alignment."""
    
    def __init__(self, prog):
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