from importlib.metadata import version as get_version
__version__ = get_version("ngpt")

from .client import NGPTClient
from .utils.config import load_config, get_config_path, get_config_dir
from .utils.cli_config import (
    load_cli_config,
    set_cli_config_option,
    get_cli_config_option,
    unset_cli_config_option,
    apply_cli_config
)

__all__ = [
    "NGPTClient", "__version__", "load_config", "get_config_path", "get_config_dir",
    "load_cli_config", "set_cli_config_option", "get_cli_config_option", 
    "unset_cli_config_option", "apply_cli_config"
]

# Import cli last to avoid circular imports
from .cli import main
__all__.append("main") 