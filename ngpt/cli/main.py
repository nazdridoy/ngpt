import sys
from ngpt.core.cli_config import load_cli_config
from ngpt.core.config import check_config
from ngpt.ui.colors import COLORS
from ngpt.cli.args import parse_args, validate_args, handle_cli_config_args, setup_argument_parser, handle_role_config_args

# Import handlers
from ngpt.cli.handlers import (
    handle_role_config,
    get_role_prompt,
    handle_cli_config,
    handle_config_command,
    show_config,
    list_models,
    setup_logger,
    cleanup_logger,
    dispatch_mode,
    initialize_client,
    handle_validation_error,
    handle_keyboard_interrupt,
    handle_exception
)

def main():
    """Main entry point for the CLI application."""
    # Parse command line arguments using args.py
    args = parse_args()
    
    try:
        args = validate_args(args)
    except ValueError as e:
        handle_validation_error(e)
    
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
    
    # Initialize logger
    logger = setup_logger(args)
    
    # Handle interactive configuration mode
    if args.config is True:  # --config was used without a value
        handle_config_command(args.config, args.config_index, args.provider, args.remove)
        return
    
    # Show config if requested
    if args.show_config:
        show_config(args.config, args.config_index, args.provider, args.all)
        return
    
    # For interactive mode, we'll allow continuing without a specific prompt
    if not getattr(args, 'prompt', None) and not (args.shell or args.code or args.text or args.interactive or args.show_config or args.list_models or args.rewrite or args.gitcommsg):
        # Simply use the parser's help
        parser = setup_argument_parser()
        parser.print_help()
        return
    
    # Initialize client and get active config
    client, active_config = initialize_client(args, cli_config)
        
    # Check configuration
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
    
    try:
        # Handle listing models
        if args.list_models:
            list_models(client, active_config)
            return
        
        # Dispatch to appropriate mode
        dispatch_mode(client, args, logger=logger)
    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        handle_exception(e)
    finally:
        # Clean up logger
        cleanup_logger(logger) 