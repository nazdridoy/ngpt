import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Any, List, Union, Tuple

# CLI config options with their types and default values
CLI_CONFIG_OPTIONS = {
    "language": {"type": "str", "default": "python", "context": ["code"]},
    "provider": {"type": "str", "default": None, "context": ["all"]},
    "temperature": {"type": "float", "default": 0.7, "context": ["all"]},
    "top_p": {"type": "float", "default": 1.0, "context": ["all"]},
    "max_tokens": {"type": "int", "default": None, "context": ["all"]},
    "log": {"type": "str", "default": None, "context": ["interactive", "text"]},
    "preprompt": {"type": "str", "default": None, "context": ["all"]},
    "no-stream": {"type": "bool", "default": False, "context": ["all"], "exclusive": ["prettify", "stream-prettify"]},
    "prettify": {"type": "bool", "default": False, "context": ["all"], "exclusive": ["no-stream", "stream-prettify"]},
    "stream-prettify": {"type": "bool", "default": False, "context": ["all"], "exclusive": ["no-stream", "prettify"]},
    "renderer": {"type": "str", "default": "auto", "context": ["all"]},
    "config-index": {"type": "int", "default": 0, "context": ["all"]},
    "web-search": {"type": "bool", "default": False, "context": ["all"]},
}

def get_cli_config_dir() -> Path:
    """Get the appropriate CLI config directory based on OS."""
    if sys.platform == "win32":
        # Windows
        config_dir = Path(os.environ.get("APPDATA", "")) / "ngpt"
    elif sys.platform == "darwin":
        # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "ngpt"
    else:
        # Linux and other Unix-like systems
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_dir = Path(xdg_config_home) / "ngpt"
        else:
            config_dir = Path.home() / ".config" / "ngpt"
    
    # Ensure the directory exists
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_cli_config_path() -> Path:
    """Get the path to the CLI config file."""
    return get_cli_config_dir() / "ngpt-cli.conf"

def load_cli_config() -> Dict[str, Any]:
    """Load CLI configuration from the config file."""
    config_path = get_cli_config_path()
    
    # Default empty config
    config = {}
    
    # Load from config file if it exists
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read CLI config file: {e}", file=sys.stderr)
    
    return config

def save_cli_config(config: Dict[str, Any]) -> bool:
    """Save CLI configuration to the config file."""
    config_path = get_cli_config_path()
    
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving CLI configuration: {e}", file=sys.stderr)
        return False

def set_cli_config_option(option: str, value: Any) -> Tuple[bool, str]:
    """Set a CLI configuration option.
    
    Args:
        option: The name of the option to set
        value: The value to set
        
    Returns:
        Tuple of (success, message)
    """
    # Check if option is valid
    if option not in CLI_CONFIG_OPTIONS:
        return False, f"Error: Unknown option '{option}'"
    
    # Load current config
    config = load_cli_config()
    
    # Parse and validate the value based on option type
    option_type = CLI_CONFIG_OPTIONS[option]["type"]
    
    try:
        if option_type == "str":
            parsed_value = str(value)
        elif option_type == "int":
            parsed_value = int(value)
        elif option_type == "float":
            parsed_value = float(value)
        elif option_type == "bool":
            if isinstance(value, bool):
                parsed_value = value
            elif value.lower() in ("true", "yes", "1", "t", "y"):
                parsed_value = True
            elif value.lower() in ("false", "no", "0", "f", "n"):
                parsed_value = False
            else:
                return False, f"Error: Invalid boolean value '{value}' for option '{option}'"
        else:
            return False, f"Error: Unsupported option type '{option_type}'"
        
        # Handle mutual exclusivity for boolean options
        if option_type == "bool" and "exclusive" in CLI_CONFIG_OPTIONS[option]:
            if parsed_value:  # If setting this option to True
                # Set all other exclusive options to False
                for excl_option in CLI_CONFIG_OPTIONS[option]["exclusive"]:
                    config[excl_option] = False
            # No special handling needed if setting to False, just update the value
        
        # Set the value in the config
        config[option] = parsed_value
        
        # Save the config
        if save_cli_config(config):
            return True, f"Successfully set {option}={parsed_value}"
        else:
            return False, "Error saving configuration"
            
    except (ValueError, TypeError) as e:
        return False, f"Error: {str(e)}"

def get_cli_config_option(option: str = None) -> Tuple[bool, Union[str, Dict[str, Any]]]:
    """Get a CLI configuration option or all options.
    
    Args:
        option: The name of the option to get, or None for all options
        
    Returns:
        Tuple of (success, value/message)
    """
    # Load current config
    config = load_cli_config()
    
    # Return all options if no specific option requested
    if option is None:
        return True, config
    
    # Check if option is valid
    if option not in CLI_CONFIG_OPTIONS:
        return False, f"Error: Unknown option '{option}'"
    
    # Return the option value if set, otherwise the default
    if option in config:
        return True, config[option]
    else:
        return True, CLI_CONFIG_OPTIONS[option]["default"]

def unset_cli_config_option(option: str) -> Tuple[bool, str]:
    """Unset a CLI configuration option.
    
    Args:
        option: The name of the option to unset
        
    Returns:
        Tuple of (success, message)
    """
    # Check if option is valid
    if option not in CLI_CONFIG_OPTIONS:
        return False, f"Error: Unknown option '{option}'"
    
    # Load current config
    config = load_cli_config()
    
    # Remove the option if it exists
    if option in config:
        del config[option]
        
        # Save the config
        if save_cli_config(config):
            return True, f"Successfully unset {option}"
        else:
            return False, "Error saving configuration"
    else:
        return True, f"Note: Option '{option}' was not set"

def apply_cli_config(args: Any, mode: str) -> Any:
    """Apply CLI configuration to args object, respecting context and not overriding explicit args.
    
    Args:
        args: The argparse namespace object
        mode: The current mode ('interactive', 'shell', 'code', 'text', or 'all' for default)
        
    Returns:
        Updated args object
    """
    # Load CLI config
    cli_config = load_cli_config()
    
    # Get command-line arguments provided by the user
    explicit_args = set(arg for arg in sys.argv[1:] if arg.startswith('--'))

    # For each option in CLI config, check if it should be applied
    for option, value in cli_config.items():
        # Skip if not a valid option
        if option not in CLI_CONFIG_OPTIONS:
            continue
            
        # Check context
        option_context = CLI_CONFIG_OPTIONS[option]["context"]
        if "all" not in option_context and mode not in option_context:
            continue
            
        # Convert dashes to underscores for argparse compatibility
        arg_name = option.replace("-", "_")
        
        # Skip if explicitly set via command line
        # Check common variants like --option
        cli_option = f"--{option}"
        if cli_option in explicit_args:
            continue
        
        # Check exclusivity constraints against *explicitly set* args
        # Don't apply a CLI config option if an exclusive option was explicitly set
        if "exclusive" in CLI_CONFIG_OPTIONS[option]:
            skip = False
            for excl_option in CLI_CONFIG_OPTIONS[option]["exclusive"]:
                excl_cli_option = f"--{excl_option}"
                if excl_cli_option in explicit_args:
                    skip = True
                    break # Skip applying this CLI config value
            if skip:
                continue
                
        # Apply the value from CLI config
        # Ensure the attribute exists on args before setting
        if hasattr(args, arg_name):
            setattr(args, arg_name, value)
    
    return args

def list_cli_config_options() -> List[str]:
    """List all available CLI configuration options."""
    return sorted(CLI_CONFIG_OPTIONS.keys()) 