import argparse
import sys
from .. import __version__
from .formatters import COLORS, ColoredHelpFormatter
from .renderers import has_markdown_renderer, warn_if_no_markdown_renderer

def setup_argument_parser():
    """Set up and return a fully configured argument parser for nGPT CLI."""
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
    parser.add_argument('-v', '--version', action=ColoredVersionAction, nargs=0, 
                        help='Show version information and exit')
    # Language option for code mode
    parser.add_argument('--language', default="python", 
                        help='Programming language to generate code in (for code mode)')
    
    # Prompt argument
    parser.add_argument('prompt', nargs='?', default=None, 
                        help='The prompt to send')

    # Config options
    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument('--config', nargs='?', const=True, 
                              help='Path to a custom config file or, if no value provided, enter interactive configuration mode to create a new config')
    config_group.add_argument('--config-index', type=int, default=0, 
                              help='Index of the configuration to use or edit (default: 0)')
    config_group.add_argument('--provider', 
                              help='Provider name to identify the configuration to use')
    config_group.add_argument('--remove', action='store_true', 
                              help='Remove the configuration at the specified index (requires --config and --config-index or --provider)')
    config_group.add_argument('--show-config', action='store_true', 
                              help='Show the current configuration(s) and exit')
    config_group.add_argument('--all', action='store_true', 
                              help='Show details for all configurations (requires --show-config)')
    config_group.add_argument('--list-models', action='store_true', 
                              help='List all available models for the current configuration and exit')
    config_group.add_argument('--list-renderers', action='store_true', 
                              help='Show available markdown renderers for use with --prettify')
    config_group.add_argument('--cli-config', nargs='*', metavar='COMMAND', 
                              help='Manage CLI configuration (set, get, unset, list, help)')

    # Global options
    global_group = parser.add_argument_group('Global Options')
    global_group.add_argument('--api-key', 
                              help='API key for the service')
    global_group.add_argument('--base-url', 
                              help='Base URL for the API')
    global_group.add_argument('--model', 
                              help='Model to use')
    global_group.add_argument('--web-search', action='store_true', 
                      help='Enable web search capability using DuckDuckGo to enhance prompts with relevant information')
    global_group.add_argument('--temperature', type=float, default=0.7,
                      help='Set temperature (controls randomness, default: 0.7)')
    global_group.add_argument('--top_p', type=float, default=1.0,
                      help='Set top_p (controls diversity, default: 1.0)')
    global_group.add_argument('--max_tokens', type=int, 
                      help='Set max response length in tokens')
    global_group.add_argument('--log', metavar='FILE', nargs='?', const=True,
                      help='Set filepath to log conversation to, or create a temporary log file if no path provided')
    global_group.add_argument('--preprompt', 
                      help='Set custom system prompt to control AI behavior')
    
    # Output display options (mutually exclusive group)
    output_group = parser.add_argument_group('Output Display Options (mutually exclusive)')
    output_exclusive_group = output_group.add_mutually_exclusive_group()
    output_exclusive_group.add_argument('--no-stream', action='store_true',
                      help='Return the whole response without streaming or formatting')
    output_exclusive_group.add_argument('--prettify', action='store_const', const='auto',
                      help='Render complete response with markdown and code formatting (non-streaming)')
    output_exclusive_group.add_argument('--stream-prettify', action='store_true', default=True,
                      help='Stream response with real-time markdown rendering (default)')
    
    global_group.add_argument('--renderer', choices=['auto', 'rich', 'glow'], default='auto',
                      help='Select which markdown renderer to use with --prettify or --stream-prettify (auto, rich, or glow)')
    
    # GitCommit message options
    gitcommsg_group = parser.add_argument_group('Git Commit Message Options')
    gitcommsg_group.add_argument('--rec-chunk', action='store_true',
                      help='Process large diffs in chunks with recursive analysis if needed')
    gitcommsg_group.add_argument('--diff', metavar='FILE', nargs='?', const=True,
                      help='Use diff from specified file instead of staged changes. If used without a path, uses the path from CLI config.')
    gitcommsg_group.add_argument('--chunk-size', type=int, default=200,
                      help='Number of lines per chunk when chunking is enabled (default: 200)')
    gitcommsg_group.add_argument('--analyses-chunk-size', type=int, default=200,
                      help='Number of lines per chunk when recursively chunking analyses (default: 200)')
    gitcommsg_group.add_argument('--max-msg-lines', type=int, default=20,
                      help='Maximum number of lines in commit message before condensing (default: 20)')
    gitcommsg_group.add_argument('--max-recursion-depth', type=int, default=3,
                      help='Maximum recursion depth for commit message condensing (default: 3)')
    
    # Mode flags (mutually exclusive)
    mode_group = parser.add_argument_group('Modes (mutually exclusive)')
    mode_exclusive_group = mode_group.add_mutually_exclusive_group()
    mode_exclusive_group.add_argument('-i', '--interactive', action='store_true', 
                                      help='Start an interactive chat session')
    mode_exclusive_group.add_argument('-s', '--shell', action='store_true', 
                                      help='Generate and execute shell commands')
    mode_exclusive_group.add_argument('-c', '--code', action='store_true', 
                                      help='Generate code')
    mode_exclusive_group.add_argument('-t', '--text', action='store_true', 
                                      help='Enter multi-line text input (submit with Ctrl+D)')
    mode_exclusive_group.add_argument('-p', '--pipe', action='store_true',
                                      help='Read from stdin and use content with prompt. Use {} in prompt as placeholder for stdin content')
    mode_exclusive_group.add_argument('-r', '--rewrite', action='store_true',
                                      help='Rewrite text from stdin to be more natural while preserving tone and meaning')
    mode_exclusive_group.add_argument('-g', '--gitcommsg', action='store_true',
                                      help='Generate AI-powered git commit messages from staged changes or diff file')
    
    return parser

def parse_args():
    """Parse command line arguments using the configured parser."""
    parser = setup_argument_parser()
    return parser.parse_args()

def validate_args(args):
    """Validate parsed arguments for correctness and compatibility."""
    # Validate --all usage
    if args.all and not args.show_config:
        raise ValueError("--all can only be used with --show-config")
    
    # These three options are mutually exclusive rendering modes
    provided_modes = []
    if '--no-stream' in sys.argv:
        provided_modes.append('--no-stream')
    if '--prettify' in sys.argv:
        provided_modes.append('--prettify')
    if '--stream-prettify' in sys.argv:
        provided_modes.append('--stream-prettify')
    
    # If more than one rendering mode explicitly provided, raise error
    if len(provided_modes) > 1:
        raise ValueError(f"The options {', '.join(provided_modes)} cannot be used together. These options are mutually exclusive.")
    
    # Handle the conflict between default stream-prettify and explicitly provided options
    if args.no_stream:
        args.stream_prettify = False
        args.prettify = False
    elif args.prettify:
        args.stream_prettify = False
        args.no_stream = False
    elif args.stream_prettify:
        args.no_stream = False
        args.prettify = False
    
    # Check if --stream-prettify is used but Rich is not available
    if args.stream_prettify and not has_markdown_renderer('rich'):
        raise ValueError("--stream-prettify requires Rich to be installed. Install with: pip install \"ngpt[full]\" or pip install rich")
    
    # If stdin mode is used, check if input is available
    if args.pipe and sys.stdin.isatty():
        raise ValueError("--pipe was specified but no input is piped. Use echo 'content' | ngpt --pipe 'prompt with {}'")
    
    return args

def validate_markdown_renderer(args):
    """Validate that required markdown renderers are available.
    
    Args:
        args: The parsed command line arguments.
    
    Returns:
        tuple: (has_renderer, args)
            - has_renderer: Boolean indicating if a renderer is available
            - args: Potentially modified args with prettify disabled if no renderer is available
    """
    has_renderer = True
    if args.prettify:
        has_renderer = warn_if_no_markdown_renderer(args.renderer)
        if not has_renderer:
            # Set a flag to disable prettify since we already warned the user
            print(f"{COLORS['yellow']}Continuing without markdown rendering.{COLORS['reset']}")
            args.prettify = False
    
    return has_renderer, args

def handle_cli_config_args(args):
    """Process CLI configuration arguments and determine command parameters.
    
    Args:
        args: The parsed command line arguments.
        
    Returns:
        tuple: (should_handle, action, option, value)
            - should_handle: True if --cli-config was specified and should be handled
            - action: The action to perform (set, get, unset, list, help)
            - option: The option name (or None)
            - value: The option value (or None)
    """
    if args.cli_config is None:
        return (False, None, None, None)
    
    # Show help if no arguments or "help" argument
    if len(args.cli_config) == 0 or (len(args.cli_config) > 0 and args.cli_config[0].lower() == "help"):
        return (True, "help", None, None)
    
    action = args.cli_config[0].lower()
    option = args.cli_config[1] if len(args.cli_config) > 1 else None
    value = args.cli_config[2] if len(args.cli_config) > 2 else None
    
    if action in ("set", "get", "unset", "list", "help"):
        return (True, action, option, value)
    else:
        # Unknown action, show help
        return (True, "help", None, None) 