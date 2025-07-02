from importlib.metadata import version as get_version
__version__ = get_version("ngpt")

from ngpt.api.client import NGPTClient
from ngpt.core.config import (
    load_config, 
    get_config_path, 
    get_config_dir,
    load_configs,
    add_config_entry,
    remove_config_entry,
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_ENTRY,
    check_config
)
# Export CLI config functions for public API
from ngpt.core.cli_config import (
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

__all__ = [
    "NGPTClient", "__version__", 
    # Configuration utilities
    "load_config", "get_config_path", "get_config_dir",
    "load_configs", "add_config_entry", "remove_config_entry",
    "DEFAULT_CONFIG", "DEFAULT_CONFIG_ENTRY", "check_config",
    # CLI configuration utilities
    "load_cli_config", "set_cli_config_option", "get_cli_config_option", 
    "unset_cli_config_option", "apply_cli_config", "list_cli_config_options",
    "CLI_CONFIG_OPTIONS", "get_cli_config_dir", "get_cli_config_path"
]

# Import cli last to avoid circular imports
from ngpt.cli import main
__all__.append("main") 