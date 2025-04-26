# Configuration Utilities

nGPT provides a set of utilities for managing configuration files and settings. These functions allow you to load, create, edit, and remove configurations, as well as determine the appropriate paths for configuration files.

> **Note:** This documentation covers the general API configuration utilities. For CLI-specific configuration management, see the [CLI Configuration](cli_config.md) documentation.

## Configuration Paths

### get_config_dir()

Returns the directory where configuration files are stored based on the operating system. This function also ensures the directory exists by creating it if needed.

```python
from ngpt.utils.config import get_config_dir
from pathlib import Path

config_dir: Path = get_config_dir()
```

#### Returns

A `Path` object representing the configuration directory:
- **Windows**: `%APPDATA%\ngpt`
- **macOS**: `~/Library/Application Support/ngpt`
- **Linux**: `~/.config/ngpt` or `$XDG_CONFIG_HOME/ngpt`

#### Examples

```python
from ngpt.utils.config import get_config_dir

# Get the configuration directory
config_dir = get_config_dir()
print(f"Configuration directory: {config_dir}")

# The directory is guaranteed to exist as get_config_dir() creates it if needed
print(f"Files in directory: {list(config_dir.iterdir())}")
```

### get_config_path()

Returns the path to the configuration file.

```python
from ngpt.utils.config import get_config_path
from pathlib import Path

config_path: Path = get_config_path(custom_path: Optional[str] = None)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `custom_path` | `Optional[str]` | `None` | Optional custom path to the configuration file |

#### Returns

A `Path` object representing the path to the configuration file.

#### Examples

```python
from ngpt.utils.config import get_config_path

# Get the default configuration file path
config_path = get_config_path()
print(f"Configuration file: {config_path}")

# Get a custom configuration file path
custom_config_path = get_config_path("/path/to/custom/config.json")
print(f"Custom configuration file: {custom_config_path}")
```

## Loading Configurations

### load_configs()

Loads all configurations from the configuration file. If the file doesn't exist, a default configuration file is created.

```python
from ngpt.utils.config import load_configs
from typing import List, Dict, Any

configs: List[Dict[str, Any]] = load_configs(custom_path: Optional[str] = None)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `custom_path` | `Optional[str]` | `None` | Optional custom path to the configuration file |

#### Returns

A list of configuration dictionaries, each containing:
- `api_key`: The API key for the service
- `base_url`: The base URL for the API endpoint
- `provider`: A human-readable name for the provider
- `model`: The default model to use

#### Examples

```python
from ngpt.utils.config import load_configs

# Load all configurations
configs = load_configs()

# Print configuration details
for i, config in enumerate(configs):
    print(f"Configuration {i}:")
    print(f"  Provider: {config.get('provider', 'Unknown')}")
    print(f"  Base URL: {config.get('base_url', 'Unknown')}")
    print(f"  Model: {config.get('model', 'Unknown')}")
    print()

# Load configurations from a custom path
custom_configs = load_configs("/path/to/custom/config.json")
```

### load_config()

Loads a specific configuration by index or provider name and applies environment variables. If the specified configuration cannot be found, a default configuration or the first available configuration is returned.

```python
from ngpt.utils.config import load_config
from typing import Dict, Any

config: Dict[str, Any] = load_config(
    custom_path: Optional[str] = None,
    config_index: int = 0,
    provider: Optional[str] = None
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `custom_path` | `Optional[str]` | `None` | Optional custom path to the configuration file |
| `config_index` | `int` | `0` | Index of the configuration to load (0-based) |
| `provider` | `Optional[str]` | `None` | Provider name to identify the configuration to use (alternative to config_index) |

#### Returns

A dictionary with configuration values, potentially overridden by environment variables.

#### Environment Variables

The following environment variables can override configuration values:

| Environment Variable | Configuration Key |
|----------------------|-------------------|
| `OPENAI_API_KEY` | `api_key` |
| `OPENAI_BASE_URL` | `base_url` |
| `OPENAI_MODEL` | `model` |

#### Examples

```python
from ngpt.utils.config import load_config

# Load the default configuration (index 0)
config = load_config()
print(f"Using provider: {config.get('provider', 'Unknown')}")
print(f"Using model: {config.get('model', 'Unknown')}")

# Load a specific configuration by index
config_1 = load_config(config_index=1)
print(f"Using provider: {config_1.get('provider', 'Unknown')}")
print(f"Using model: {config_1.get('model', 'Unknown')}")

# Load a specific configuration by provider name
gemini_config = load_config(provider="Gemini")
print(f"Using provider: {gemini_config.get('provider', 'Unknown')}")
print(f"Using model: {gemini_config.get('model', 'Unknown')}")

# Load from a custom path
custom_config = load_config(custom_path="/path/to/custom/config.json")
```

## Default Configuration

nGPT provides default configuration values that are used when no configuration file exists or when specific settings are not provided.

```python
from ngpt.utils.config import DEFAULT_CONFIG, DEFAULT_CONFIG_ENTRY

# Print the default configuration entry
print(DEFAULT_CONFIG_ENTRY)
```

### DEFAULT_CONFIG_ENTRY

The `DEFAULT_CONFIG_ENTRY` constant defines the default values for a single configuration:

```python
DEFAULT_CONFIG_ENTRY = {
    "api_key": "",
    "base_url": "https://api.openai.com/v1/",
    "provider": "OpenAI",
    "model": "gpt-3.5-turbo"
}
```

### DEFAULT_CONFIG

The `DEFAULT_CONFIG` constant is a list containing the default configuration entry:

```python
DEFAULT_CONFIG = [DEFAULT_CONFIG_ENTRY]
```

This is used when creating a new configuration file or when falling back to defaults.

#### Examples

```python
from ngpt.utils.config import DEFAULT_CONFIG, DEFAULT_CONFIG_ENTRY, load_config

# Use default configuration as a base for a custom configuration
custom_config = DEFAULT_CONFIG_ENTRY.copy()
custom_config["model"] = "gpt-4o"
custom_config["provider"] = "Custom Provider"

# Load configuration with fallback to defaults
config = load_config()
# If no configuration file exists, this will use DEFAULT_CONFIG
```

## Creating Configurations

### create_default_config()

Creates a default configuration file with a single configuration entry.

```python
from ngpt.utils.config import create_default_config
from pathlib import Path

create_default_config(config_path: Path)
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `config_path` | `Path` | Path where the default configuration file should be created |

#### Examples

```python
from ngpt.utils.config import create_default_config, get_config_path
from pathlib import Path

# Create a default configuration file at the default location
config_path = get_config_path()
create_default_config(config_path)

# Create a default configuration file at a custom location
custom_path = Path("/path/to/custom/config.json")
create_default_config(custom_path)
```

## Editing Configurations

### add_config_entry()

Adds a new configuration entry or updates an existing one at the specified index. This function prompts the user interactively for configuration values.

```python
from ngpt.utils.config import add_config_entry
from pathlib import Path

add_config_entry(
    config_path: Path,
    config_index: Optional[int] = None
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config_path` | `Path` | | Path to the configuration file |
| `config_index` | `Optional[int]` | `None` | Index of the configuration to update (if None, adds a new entry) |

#### Interactive Prompts

The function prompts for:
- API Key
- Base URL
- Provider (ensures the provider name is unique)
- Model

#### Examples

```python
from ngpt.utils.config import add_config_entry, get_config_path

# Add a new configuration entry
config_path = get_config_path()
add_config_entry(config_path)  # This will prompt for input interactively

# Edit an existing configuration entry
add_config_entry(config_path, config_index=1)  # This will prompt for input interactively
```

## Removing Configurations

### remove_config_entry()

Removes a configuration entry at the specified index.

```python
from ngpt.utils.config import remove_config_entry
from pathlib import Path

success: bool = remove_config_entry(
    config_path: Path,
    config_index: int
)
```

#### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `config_path` | `Path` | Path to the configuration file |
| `config_index` | `int` | Index of the configuration to remove |

#### Returns

- `True` if the configuration was successfully removed
- `False` if the operation failed (e.g., invalid index or file access error)

#### Examples

```python
from ngpt.utils.config import remove_config_entry, get_config_path

# Remove a configuration entry
config_path = get_config_path()
success = remove_config_entry(config_path, config_index=1)

if success:
    print("Configuration removed successfully")
else:
    print("Failed to remove configuration")
```

### is_provider_unique()

Checks if a provider name is unique among configurations.

```python
from ngpt.utils.config import is_provider_unique
from typing import List, Dict, Any, Optional

is_unique: bool = is_provider_unique(
    configs: List[Dict[str, Any]],
    provider: str,
    exclude_index: Optional[int] = None
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `configs` | `List[Dict[str, Any]]` | Required | List of configuration dictionaries |
| `provider` | `str` | Required | Provider name to check for uniqueness |
| `exclude_index` | `Optional[int]` | `None` | Optional index to exclude from the check (useful when updating an existing config) |

#### Returns

`True` if the provider name is unique among all configurations, `False` otherwise.

#### Examples

```python
from ngpt.utils.config import load_configs, is_provider_unique

# Load all configurations
configs = load_configs()

# Check if a provider name is unique
provider_name = "New Provider"
if is_provider_unique(configs, provider_name):
    print(f"'{provider_name}' is a unique provider name")
else:
    print(f"'{provider_name}' is already used by another configuration")

# Check if provider name is unique when updating an existing config
existing_idx = 1
update_provider = "Updated Provider"
if is_provider_unique(configs, update_provider, exclude_index=existing_idx):
    print(f"'{update_provider}' is unique and can be used to update config at index {existing_idx}")
else:
    print(f"'{update_provider}' is already used by another configuration")
```

## CLI Configuration Integration

nGPT provides a separate set of utilities for managing CLI-specific configuration settings. These are documented in [CLI Configuration](cli_config.md).

```python
# Import API configuration utilities
from ngpt.utils.config import load_config, get_config_path

# Import CLI configuration utilities
from ngpt.utils.cli_config import load_cli_config, set_cli_config_option

# Use both configuration systems together
api_config = load_config()  # Load API configuration
cli_config = load_cli_config()  # Load CLI configuration

client = NGPTClient(**api_config)  # Create client with API config

# Use CLI configuration for settings
temperature = cli_config.get('temperature', 0.7)
language = cli_config.get('language', 'python')

# Generate code with both configurations applied
code = client.generate_code(
    "function to sort a list",
    language=language,
    temperature=float(temperature)
)
```

## Complete Examples

### Managing Multiple Configurations

```python
from ngpt.utils.config import (
    get_config_path,
    load_configs,
    add_config_entry,
    remove_config_entry
)
from pathlib import Path

# Get the configuration file path
config_path = get_config_path()

# Load existing configurations
configs = load_configs()
print(f"Found {len(configs)} configurations")

# Display existing configurations
for i, config in enumerate(configs):
    print(f"Configuration {i}: {config.get('provider', 'Unknown')} - {config.get('model', 'Unknown')}")

# Add a new configuration
add_config_entry(config_path)  # This will prompt for input interactively

# Load updated configurations
updated_configs = load_configs()
print(f"Now have {len(updated_configs)} configurations")

# Remove the last configuration
if len(updated_configs) > 1:
    remove_config_entry(config_path, len(updated_configs) - 1)
    print("Removed the last configuration")

# Verify the change
final_configs = load_configs()
print(f"Finally have {len(final_configs)} configurations")
```

### Using Environment Variables

nGPT respects environment variables for configuration values. The following variables are supported:

- `OPENAI_API_KEY`: Overrides the `api_key` setting
- `OPENAI_BASE_URL`: Overrides the `base_url` setting
- `OPENAI_MODEL`: Overrides the `model` setting

```python
import os
from ngpt.utils.config import load_config

# Set environment variables
os.environ["OPENAI_API_KEY"] = "your-api-key"
os.environ["OPENAI_MODEL"] = "gpt-4o"

# Load configuration (environment variables will override file settings)
config = load_config()
print(f"API Key: {'*' * 8}")  # Don't print actual key
print(f"Model: {config.get('model')}")  # Will show 'gpt-4o' from environment
```

## Configuration Priority

nGPT determines configuration values in the following order (highest priority first):

1. Command-line arguments (when using the CLI)
2. Environment variables
3. CLI configuration settings (for CLI-specific options)
4. Configuration file values
5. Default values

This allows for flexible configuration management across different environments and use cases.

## See Also

- [CLI Configuration](cli_config.md) - Documentation for CLI-specific configuration utilities
- [NGPTClient API](client.md) - Reference for the client API that uses these configurations
- [CLI Components](cli.md) - Documentation for CLI components that use these configurations 