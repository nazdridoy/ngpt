import argparse
import sys
from ngpt.version import __version__
from ngpt.ui.colors import COLORS
from ngpt.ui.formatters import ColoredHelpFormatter

def setup_argument_parser():
    """Set up and return a fully configured argument parser for nGPT CLI."""
    # Colorize description - use a shorter description to avoid line wrapping issues
    description = f"{COLORS['cyan']}{COLORS['bold']}nGPT{COLORS['reset']} - AI-powered terminal toolkit for code, commits, commands & chat"
    
    # Minimalist, clean epilog design
    epilog = f"\n{COLORS['yellow']}nGPT {COLORS['bold']}v{__version__}{COLORS['reset']}  •  {COLORS['green']}Docs: {COLORS['bold']}https://nazdridoy.github.io/ngpt/usage/cli_usage{COLORS['reset']}"
    
    parser = argparse.ArgumentParser(description=description, formatter_class=ColoredHelpFormatter, 
                                    epilog=epilog, add_help=False)
    
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
    
    # Global options
    global_group = parser.add_argument_group('Global Options')
    
    # Add help and version to the global group
    global_group.add_argument('-h', '--help', action='help',
                             help='show this help message and exit')
    global_group.add_argument('-v', '--version', action=ColoredVersionAction, nargs=0, 
                             help='Show version information and exit')
    
    # Then add the other global options
    global_group.add_argument('--api-key', 
                              help='API key for the service')
    global_group.add_argument('--base-url', 
                              help='Base URL for the API')
    global_group.add_argument('--model', 
                              help='Model to use')
    global_group.add_argument('--web-search', action='store_true', 
                      help='Enable web search capability using DuckDuckGo to enhance prompts with relevant information')
    global_group.add_argument('--pipe', action='store_true',
                      help='Read from stdin and use content with prompt. Use {} in prompt as placeholder for stdin content. Can be used with any mode option except --text and --interactive')
    global_group.add_argument('--temperature', type=float, default=0.7,
                      help='Set temperature (controls randomness, default: 0.7)')
    global_group.add_argument('--top_p', type=float, default=1.0,
                      help='Set top_p (controls diversity, default: 1.0)')
    global_group.add_argument('--max_tokens', type=int, 
                      help='Set max response length in tokens')
    global_group.add_argument('--log', metavar='FILE', nargs='?', const=True,
                      help='Set filepath to log conversation to, or create a temporary log file if no path provided')
    
    # System prompt options (mutually exclusive)
    prompt_exclusive_group = global_group.add_mutually_exclusive_group()
    prompt_exclusive_group.add_argument('--preprompt', 
                      help='Set custom system prompt to control AI behavior')
    prompt_exclusive_group.add_argument('--role', 
                      help='Use a predefined role to set system prompt (mutually exclusive with --preprompt)')
    
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
    config_group.add_argument('--cli-config', nargs='*', metavar='COMMAND', 
                              help='Manage CLI configuration (set, get, unset, list, help)')
    config_group.add_argument('--role-config', nargs='*', metavar='ACTION', 
                              help='Manage custom roles (help, create, show, edit, list, remove) [role_name]')

    # Output display options
    output_group = parser.add_argument_group('Output Display Options')
    output_group.add_argument('--plaintext', action='store_true',
                      help='Disable streaming and markdown rendering (plain text output)')
    
    # Code Mode Options
    code_group = parser.add_argument_group('Code Mode Options')
    code_group.add_argument('--language', default="python", 
                      help='Programming language to generate code in (for code mode)')
    
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
    
    # Rewrite mode options
    rewrite_group = parser.add_argument_group('Rewrite Mode Options')
    rewrite_group.add_argument('--humanize', action='store_true',
                              help='Transform AI-generated text into human-like content that passes AI detection tools')
    
    # Interactive mode options
    interactive_group = parser.add_argument_group('Interactive Mode Options')
    
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
    mode_exclusive_group.add_argument('-r', '--rewrite', action='store_true',
                                      help='Rewrite text from stdin to be more natural while preserving tone and meaning')
    mode_exclusive_group.add_argument('-g', '--gitcommsg', action='store_true',
                                      help='Generate AI-powered git commit messages from staged changes or diff file')
    
    # Add positional argument for the prompt (optional)
    parser.add_argument('prompt', nargs='?', default=None,
                        help='The prompt to send to the language model')
    
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
    
    # Validate --remove usage
    if args.remove and (not args.config or (args.config_index == 0 and not args.provider)):
        raise ValueError("--remove requires --config and either --config-index or --provider")
    
    
    # Check for incompatible --pipe flag with certain modes
    if args.pipe and (args.text or args.interactive):
        raise ValueError("--pipe flag cannot be used with --text or --interactive modes. These modes already handle input directly.")
    
    # If pipe flag is used, check if input is available
    if args.pipe and sys.stdin.isatty():
        raise ValueError("--pipe was specified but no input is piped. Use echo 'content' | ngpt --pipe 'prompt with {}'")
    
    # Check if web search is enabled but BeautifulSoup isn't installed
    if args.web_search:
        try:
            import bs4
        except ImportError:
            raise ValueError("--web-search requires BeautifulSoup4 to be installed. Install with: pip install beautifulsoup4")
    
    return args

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
        return (True, "help", None, None)  # Show help for invalid actions

def handle_role_config_args(args):
    """Process role configuration arguments and determine command parameters.
    
    Args:
        args: The parsed command line arguments.
        
    Returns:
        tuple: (should_handle, action, role_name)
            - should_handle: True if --role-config was specified and should be handled
            - action: The action to perform (create, show, edit, list, remove, help)
            - role_name: The role name (or None)
    """
    if args.role_config is None:
        return (False, None, None)
    
    # Show help if no arguments or "help" argument
    if len(args.role_config) == 0 or (len(args.role_config) > 0 and args.role_config[0].lower() == "help"):
        return (True, "help", None)
    
    action = args.role_config[0].lower()
    role_name = args.role_config[1] if len(args.role_config) > 1 else None
    
    # Check if action needs role_name
    if action in ("create", "show", "edit", "remove") and not role_name:
        return (True, "help", None)  # Show help for missing role name
    
    if action in ("create", "show", "edit", "list", "remove", "help"):
        return (True, action, role_name)
    else:
        return (True, "help", None)  # Show help for invalid actions 