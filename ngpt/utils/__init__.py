# ngpt utils module

from .log import create_logger, Logger
from .config import (
    load_config, 
    get_config_path, 
    get_config_dir, 
    load_configs, 
    add_config_entry, 
    remove_config_entry,
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_ENTRY
)
from .cli_config import (
    load_cli_config,
    set_cli_config_option,
    get_cli_config_option,
    unset_cli_config_option,
    apply_cli_config,
    list_cli_config_options,
    CLI_CONFIG_OPTIONS,
    get_cli_config_dir,
    get_cli_config_path
)
from .web_search import (
    enhance_prompt_with_web_search,
    get_web_search_results,
    format_web_search_results_for_prompt
)

__all__ = [
    "create_logger", "Logger",
    "load_config", "get_config_path", "get_config_dir", "load_configs", 
    "add_config_entry", "remove_config_entry", "DEFAULT_CONFIG", "DEFAULT_CONFIG_ENTRY",
    "load_cli_config", "set_cli_config_option", "get_cli_config_option", 
    "unset_cli_config_option", "apply_cli_config", "list_cli_config_options",
    "CLI_CONFIG_OPTIONS", "get_cli_config_dir", "get_cli_config_path",
    "enhance_prompt_with_web_search", "get_web_search_results", "format_web_search_results_for_prompt"
]
