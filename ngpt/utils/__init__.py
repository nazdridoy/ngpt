# ngpt utils module

from .web_search import (
    enhance_prompt_with_web_search,
    get_web_search_results,
    format_web_search_results_for_prompt
)

from .roles import (
    handle_role_config,
    get_role_prompt,
    create_role,
    edit_role,
    show_role,
    list_roles,
    remove_role,
)

__all__ = [
    # Web search utilities
    "enhance_prompt_with_web_search", "get_web_search_results", "format_web_search_results_for_prompt",
    # Role management utilities
    "handle_role_config", "get_role_prompt", "create_role", "edit_role", "show_role", "list_roles", "remove_role",
]
