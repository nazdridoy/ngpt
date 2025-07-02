# ngpt utils module

from ngpt.utils.web_search import (
    enhance_prompt_with_web_search,
    get_web_search_results,
    format_web_search_results_for_prompt
)

# Import role-related functions from the new handler location
from ngpt.cli.handlers.role import (
    handle_role_config,
    get_role_prompt,
)

__all__ = [
    # Web search utilities
    "enhance_prompt_with_web_search", "get_web_search_results", "format_web_search_results_for_prompt",
    # Role management utilities
    "handle_role_config", "get_role_prompt",
]
