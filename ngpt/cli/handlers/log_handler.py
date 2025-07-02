import os
import sys
from ngpt.core.log import create_logger
from ngpt.ui.colors import COLORS

def setup_logger(args):
    """
    Initialize and setup logger if --log is specified.
    
    Args:
        args: Command line arguments
        
    Returns:
        Logger instance or None
    """
    logger = None
    if args.log is None:
        return None
        
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
    
    return logger

def cleanup_logger(logger):
    """
    Clean up logger if it exists.
    
    Args:
        logger: Logger instance or None
    """
    if logger:
        logger.close() 