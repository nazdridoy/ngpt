import argparse
import sys
import os
from ngpt.api.client import NGPTClient
from ngpt.core.config import load_config, check_config
from ngpt.core.cli_config import (
    apply_cli_config,
    load_cli_config
)
from ngpt.core.log import create_logger
from ngpt import __version__

from ngpt.ui.formatters import COLORS
from ngpt.cli.modes import (
    interactive_chat_session,
    chat_mode,
    code_mode,
    shell_mode,
    text_mode,
    rewrite_mode,
    gitcommsg_mode
)
from ngpt.cli.args import parse_args, validate_args, handle_cli_config_args, setup_argument_parser, handle_role_config_args

# Import handlers
from ngpt.cli.handlers import (
    handle_role_config,
    get_role_prompt,
    handle_cli_config,
    handle_config_command,
    show_config,
    list_models
)

def main():
    """Main entry point for the CLI application."""
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
    
    # Handle role configuration command
    should_handle_role_config, action, role_name = handle_role_config_args(args)
    if should_handle_role_config:
        handle_role_config(action, role_name)
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
        handle_config_command(args.config, effective_config_index, effective_provider, args.remove)
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
        show_config(args.config, effective_config_index, effective_provider, args.all)
        return
    
    # For interactive mode, we'll allow continuing without a specific prompt
    if not getattr(args, 'prompt', None) and not (args.shell or args.code or args.text or args.interactive or args.show_config or args.list_models or args.rewrite or args.gitcommsg):
        # Simply use the parser's help
        parser = setup_argument_parser()
        parser.print_help()
        return
        
    # Check configuration (using the potentially overridden active_config)
    if not args.show_config and not args.list_models and not check_config(active_config):
        return
    
    # Get system prompt from role if specified
    if args.role:
        role_prompt = get_role_prompt(args.role)
        if role_prompt:
            args.preprompt = role_prompt
        else:
            # If role doesn't exist, exit
            return
    
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
            list_models(client, active_config)
            return
        
        # Handle modes
        if args.interactive:
            # Apply CLI config for interactive mode
            args = apply_cli_config(args, "interactive")
            
            # Interactive chat mode
            interactive_chat_session(client, args, logger=logger)
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
        
        # Choose chat mode by default if no other specific mode is selected
        else:
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