"""
CLI handlers package.
"""

from .role import handle_role_config, get_role_prompt
from .cli_config_handler import handle_cli_config
from .api_config_handler import handle_config_command, show_config
from .models import list_models
from .log_handler import setup_logger, cleanup_logger
from .modes_handler import dispatch_mode
from .client_handler import process_config_selection, initialize_client
from .error_handler import handle_validation_error, handle_keyboard_interrupt, handle_exception
from .session_handler import (
    handle_session_management, 
    clear_conversation_history, 
    auto_save_session,
    SessionManager
)

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
    'handle_exception',
    'handle_session_management',
    'clear_conversation_history',
    'auto_save_session',
    'SessionManager',
] 