import argparse
import sys
import os
from ..client import NGPTClient
from ..utils.config import load_config, get_config_path, load_configs, add_config_entry, remove_config_entry
from ..utils.cli_config import (
    set_cli_config_option, 
    get_cli_config_option, 
    unset_cli_config_option, 
    apply_cli_config,
    list_cli_config_options,
    CLI_CONFIG_OPTIONS,
    load_cli_config
)
from ..utils.log import create_logger
from .. import __version__

from .formatters import COLORS
from .renderers import show_available_renderers
from .config_manager import check_config
from .modes.interactive import interactive_chat_session
from .modes.chat import chat_mode
from .modes.code import code_mode
from .modes.shell import shell_mode
from .modes.text import text_mode
from .modes.rewrite import rewrite_mode
from .modes.gitcommsg import gitcommsg_mode
from .args import parse_args, validate_args, handle_cli_config_args, setup_argument_parser, validate_markdown_renderer

def show_cli_config_help():
    """Display help information about CLI configuration."""
    print(f"\n{COLORS['green']}{COLORS['bold']}CLI Configuration Help:{COLORS['reset']}")
    print(f"  {COLORS['cyan']}Command syntax:{COLORS['reset']}")
    print(f"    {COLORS['yellow']}ngpt --cli-config help{COLORS['reset']}                - Show this help message")
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
        "shell": [],
        "gitcommsg": []  # Add gitcommsg context
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
        ("shell", "Shell mode"),
        ("gitcommsg", "Git commit message mode")  # Add gitcommsg mode
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
    print(f"    {COLORS['yellow']}ngpt --cli-config set recursive-chunk true{COLORS['reset']} - Enable recursive chunking for git commit messages")
    print(f"    {COLORS['yellow']}ngpt --cli-config set diff /path/to/file.diff{COLORS['reset']} - Set default diff file for git commit messages")
    print(f"    {COLORS['yellow']}ngpt --cli-config get temperature{COLORS['reset']}          - Check the current temperature setting")
    print(f"    {COLORS['yellow']}ngpt --cli-config get{COLORS['reset']}                      - Show all current CLI settings")
    print(f"    {COLORS['yellow']}ngpt --cli-config unset language{COLORS['reset']}           - Remove language setting")
    
    print(f"\n  {COLORS['cyan']}Notes:{COLORS['reset']}")
    print(f"    - CLI configuration is stored in:")
    print(f"      • Linux: {COLORS['yellow']}~/.config/ngpt/ngpt-cli.conf{COLORS['reset']}")
    print(f"      • macOS: {COLORS['yellow']}~/Library/Application Support/ngpt/ngpt-cli.conf{COLORS['reset']}")
    print(f"      • Windows: {COLORS['yellow']}%APPDATA%\\ngpt\\ngpt-cli.conf{COLORS['reset']}")
    print(f"    - Settings are applied based on context (e.g., language only applies to code generation mode)")
    print(f"    - Command-line arguments always override CLI configuration")
    print(f"    - Some options are mutually exclusive and will not be applied together")

def handle_cli_config(action, option=None, value=None):
    """Handle CLI configuration commands."""
    if action == "help":
        show_cli_config_help()
        return
    
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
    # Parse command line arguments using args.py
    args = parse_args()
    
    try:
        args = validate_args(args)
    except ValueError as e:
        print(f"{COLORS['bold']}{COLORS['yellow']}error: {COLORS['reset']}{str(e)}\n")
        sys.exit(2)
    
    # Handle CLI configuration command
    should_handle_cli_config, action, option, value = handle_cli_config_args(args)
    if should_handle_cli_config:
        handle_cli_config(action, option, value)
        return
    
    # Handle --renderers flag to show available markdown renderers
    if args.list_renderers:
        show_available_renderers()
        return
    
    # Load CLI configuration early
    cli_config = load_cli_config()
    
    # Initialize logger if --log is specified
    logger = None
    if args.log is not None:
        # Check if the log value is a string that looks like a prompt (incorrectly parsed)
        likely_prompt = False
        likely_path = False
        
        if isinstance(args.log, str) and args.prompt is None:
            # Check if string looks like a path
            if args.log.startswith('/') or args.log.startswith('./') or args.log.startswith('../') or args.log.startswith('~'):
                likely_path = True
            # Check if string has a file extension
            elif '.' in os.path.basename(args.log):
                likely_path = True
            # Check if parent directory exists
            elif os.path.exists(os.path.dirname(args.log)) and os.path.dirname(args.log) != '':
                likely_path = True
            # Check if string ends with a question mark (very likely a prompt)
            elif args.log.strip().endswith('?'):
                likely_prompt = True
            # As a last resort, if it has spaces and doesn't look like a path, assume it's a prompt
            elif ' ' in args.log and not likely_path:
                likely_prompt = True
                
        if likely_prompt and not likely_path:
            # This is likely a prompt, not a log path
            args.prompt = args.log
            # Change log to True to create a temp file
            args.log = True
        
        # Skip logger initialization for gitcommsg mode as it creates its own logger
        if not args.gitcommsg:
            # If --log is True, it means it was used without a path value
            log_path = None if args.log is True else args.log
            logger = create_logger(log_path)
            if logger:
                logger.open()
                print(f"{COLORS['green']}Logging session to: {logger.get_log_path()}{COLORS['reset']}")
                # If it's a temporary log file, inform the user
                if logger.is_temporary():
                    print(f"{COLORS['green']}Created temporary log file.{COLORS['reset']}")
    
    # Priority order for config selection:
    # 1. Command-line arguments (args.provider, args.config_index)
    # 2. CLI configuration (cli_config["provider"], cli_config["config-index"])
    # 3. Default values (None, 0)
    
    # Get provider/config-index from CLI config if not specified in args
    effective_provider = args.provider
    effective_config_index = args.config_index
    
    # Only apply CLI config for provider/config-index if not explicitly set on command line
    # If --config-index is explicitly provided, we should ignore provider from CLI config
    config_index_from_cli = '--config-index' in sys.argv
    provider_from_cli = '--provider' in sys.argv
    
    if not provider_from_cli and 'provider' in cli_config and not config_index_from_cli:
        effective_provider = cli_config['provider']
    
    if not config_index_from_cli and 'config-index' in cli_config and not provider_from_cli:
        effective_config_index = cli_config['config-index']
    
    # Check for mutual exclusivity between provider and config-index
    if effective_config_index != 0 and effective_provider:
        from_cli_config = not provider_from_cli and 'provider' in cli_config
        provider_source = "CLI config file (ngpt-cli.conf)" if from_cli_config else "command-line arguments"
        error_msg = f"--config-index and --provider cannot be used together. Provider from {provider_source}."
        print(f"{COLORS['bold']}{COLORS['yellow']}error: {COLORS['reset']}{error_msg}\n")
        sys.exit(2)

    # Handle interactive configuration mode
    if args.config is True:  # --config was used without a value
        config_path = get_config_path()
        
        # Handle configuration removal if --remove flag is present
        if args.remove:
            # Validate that config_index is explicitly provided
            if '--config-index' not in sys.argv and not effective_provider:
                print(f"{COLORS['bold']}{COLORS['yellow']}error: {COLORS['reset']}--remove requires explicitly specifying --config-index or --provider\n")
                sys.exit(2)
            
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
                        print(f"  Choice [{i+1}] → Config #{idx}: {configs[idx].get('model', 'Unknown model')}")
                    
                    try:
                        choice = input("Choose a configuration to remove (or press Enter to cancel): ")
                        if choice and choice.isdigit() and 1 <= int(choice) <= len(matching_configs):
                            config_index = matching_configs[int(choice)-1]
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
        
        # Check if --config-index was explicitly specified in command line args
        config_index_explicit = '--config-index' in sys.argv
        provider_explicit = '--provider' in sys.argv
        
        # When only --config is used (without explicit --config-index or --provider),
        # always create a new configuration regardless of CLI config settings
        if not config_index_explicit and not provider_explicit:
            # Always create a new config when just --config is used
            configs = load_configs(str(config_path))
            print(f"Creating new configuration at index {len(configs)}")
            add_config_entry(config_path, None)
            return
        
        # If explicitly specified indexes or provider, continue with editing behavior
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
        elif effective_config_index != 0 or config_index_explicit:
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
    if not args.prompt and not (args.shell or args.code or args.text or args.interactive or args.show_config or args.list_models or args.rewrite or args.gitcommsg):
        # Simply use the parser's help
        parser = setup_argument_parser()
        parser.print_help()
        return
        
    # Check configuration (using the potentially overridden active_config)
    if not args.show_config and not args.list_models and not check_config(active_config):
        return
    
    # Check if --prettify is used but no markdown renderer is available
    # This will warn the user immediately if they request prettify but don't have the tools
    has_renderer, args = validate_markdown_renderer(args)
    if not has_renderer:
        show_available_renderers()
    
    # Initialize client using the potentially overridden active_config
    client = NGPTClient(
        api_key=active_config.get("api_key", args.api_key),
        base_url=active_config.get("base_url", args.base_url),
        provider=active_config.get("provider"),
        model=active_config.get("model", args.model)
    )
    
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
                preprompt=args.preprompt,
                prettify=args.prettify,
                renderer=args.renderer,
                stream_prettify=args.stream_prettify,
                logger=logger
            )
        elif args.shell:
            # Apply CLI config for shell mode
            args = apply_cli_config(args, "shell")
            
            # Shell command generation mode
            shell_mode(client, args, logger=logger)
                    
        elif args.code:
            # Apply CLI config for code mode
            args = apply_cli_config(args, "code")
            
            # Code generation mode
            code_mode(client, args, logger=logger)
        
        elif args.text:
            # Apply CLI config for text mode
            args = apply_cli_config(args, "text")
            
            # Text mode (multiline input)
            text_mode(client, args, logger=logger)
        
        elif args.pipe:
            # Apply CLI config for pipe mode (similar to chat mode)
            args = apply_cli_config(args, "all")
            
            # Pipe mode (using the chat mode with stdin input)
            chat_mode(client, args, logger=logger)
        
        elif args.rewrite:
            # Apply CLI config for rewrite mode
            args = apply_cli_config(args, "all")
            
            # Rewrite mode (process stdin)
            rewrite_mode(client, args, logger=logger)
        
        elif args.gitcommsg:
            # Apply CLI config for gitcommsg mode
            args = apply_cli_config(args, "gitcommsg")
            
            # Git commit message generation mode
            gitcommsg_mode(client, args, logger=logger)
        
        else:
            # Default to chat mode
            # Apply CLI config for default chat mode
            args = apply_cli_config(args, "all")
            
            # Standard chat mode
            chat_mode(client, args, logger=logger)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting gracefully.")
        # Make sure we exit with a non-zero status code to indicate the operation was cancelled
        sys.exit(130)  # 130 is the standard exit code for SIGINT (Ctrl+C)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with error code
    finally:
        # Close the logger if it exists
        if logger:
            logger.close() 