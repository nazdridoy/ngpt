from ngpt.core.cli_config import apply_cli_config
from ngpt.cli.modes import (
    interactive_chat_session,
    chat_mode,
    code_mode,
    shell_mode,
    text_mode,
    rewrite_mode,
    gitcommsg_mode
)

def dispatch_mode(client, args, logger=None):
    """
    Dispatch to the appropriate mode handler based on arguments.
    
    Args:
        client: Initialized NGPTClient instance
        args: Command line arguments
        logger: Logger instance or None
    """
    # Handle modes based on arguments
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