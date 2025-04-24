import argparse
import sys
import os
from ..client import NGPTClient
from ..config import load_config, get_config_path, load_configs, add_config_entry, remove_config_entry
from ..cli_config import (
    set_cli_config_option, 
    get_cli_config_option, 
    unset_cli_config_option, 
    apply_cli_config,
    list_cli_config_options,
    CLI_CONFIG_OPTIONS,
    load_cli_config
)
from .. import __version__

from .formatters import COLORS, ColoredHelpFormatter
from .renderers import has_markdown_renderer, warn_if_no_markdown_renderer, show_available_renderers
from .config_manager import show_config_help, check_config
from .interactive import interactive_chat_session
from .modes.chat import chat_mode
from .modes.code import code_mode
from .modes.shell import shell_mode
from .modes.text import text_mode

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
            
            # Shell command generation mode
            shell_mode(client, args)
                    
        elif args.code:
            # Apply CLI config for code mode
            args = apply_cli_config(args, "code")
            
            # Code generation mode
            code_mode(client, args)
        
        elif args.text:
            # Apply CLI config for text mode
            args = apply_cli_config(args, "text")
            
            # Text mode (multiline input)
            text_mode(client, args)
        
        else:
            # Default to chat mode
            # Apply CLI config for default chat mode
            args = apply_cli_config(args, "all")
            
            # Standard chat mode
            chat_mode(client, args)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting gracefully.")
        # Make sure we exit with a non-zero status code to indicate the operation was cancelled
        sys.exit(130)  # 130 is the standard exit code for SIGINT (Ctrl+C)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with error code 