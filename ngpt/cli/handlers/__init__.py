"""
CLI handlers package.
"""

from ngpt.cli.handlers.role import handle_role_config, get_role_prompt
from ngpt.cli.handlers.cli_config_handler import handle_cli_config
from ngpt.cli.handlers.api_config_handler import handle_config_command, show_config
from ngpt.cli.handlers.models import list_models
from ngpt.cli.handlers.log_handler import setup_logger, cleanup_logger
from ngpt.cli.handlers.modes_handler import dispatch_mode
from ngpt.cli.handlers.client_handler import process_config_selection, initialize_client
from ngpt.cli.handlers.error_handler import handle_validation_error, handle_keyboard_interrupt, handle_exception

__all__ = [
    'handle_role_config',
    'get_role_prompt',
    'handle_cli_config',
    'handle_config_command',
    'show_config',
    'list_models',
    'setup_logger',
    'cleanup_logger',
    'dispatch_mode',
    'process_config_selection',
    'initialize_client',
    'handle_validation_error',
    'handle_keyboard_interrupt',
    'handle_exception'
] 