"""
Handlers package for CLI command handlers.
"""

from ngpt.cli.handlers.role import (
    handle_role_config,
    get_role_prompt,
)

# Export public functions
__all__ = [
    # Role handlers
    "handle_role_config",
    "get_role_prompt",
] 