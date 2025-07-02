"""
CLI handlers package.
"""

from ngpt.cli.handlers.role import handle_role_config, get_role_prompt
from ngpt.cli.handlers.cli_config_handler import handle_cli_config
from ngpt.cli.handlers.api_config_handler import handle_config_command, show_config
from ngpt.cli.handlers.models import list_models

__all__ = [
    'handle_role_config',
    'get_role_prompt',
    'handle_cli_config',
    'handle_config_command',
    'show_config',
    'list_models'
] 