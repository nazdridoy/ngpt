# CLI Configuration Utilities

This document provides a comprehensive API reference for nGPT's CLI configuration utilities that can be used to manage persistent CLI settings.

## Overview

nGPT provides a set of utilities for managing CLI-specific configuration settings that persist between invocations of the command-line tool. These utilities allow you to get, set, and unset configuration options, as well as apply them to command-line arguments.

## Core Functions

### `load_cli_config`

```python
from ngpt.utils.cli_config import load_cli_config

def load_cli_config() -> Dict[str, Any]:
```

Loads the CLI configuration from the configuration file.

**Returns:**
- dict: The CLI configuration options and their values

**Example:**
```python
from ngpt.utils.cli_config import load_cli_config

# Load the CLI configuration
cli_config = load_cli_config()
print(f"Current CLI configuration: {cli_config}")
```

### `set_cli_config_option`

```python
from ngpt.utils.cli_config import set_cli_config_option

def set_cli_config_option(option: str, value: Any) -> Tuple[bool, str]:
```

Sets a CLI configuration option.

**Parameters:**
- `option` (str): The name of the option to set
- `value` (Any): The value to set for the option

**Returns:**
- tuple: (success, message) where success is a boolean indicating whether the operation was successful and message is a string explaining the result

**Example:**
```python
from ngpt.utils.cli_config import set_cli_config_option

# Set the default temperature for generation
success, message = set_cli_config_option('temperature', '0.8')
print(message)

# Set the default language for code generation
success, message = set_cli_config_option('language', 'javascript')
print(message)
```

### `get_cli_config_option`

```python
from ngpt.utils.cli_config import get_cli_config_option

def get_cli_config_option(option: str = None) -> Tuple[bool, Union[str, Dict[str, Any]]]:
```

Gets the value of a CLI configuration option, or all options if none is specified.

**Parameters:**
- `option` (str, optional): The name of the option to get. If None, returns all options.

**Returns:**
- tuple: (success, value) where success is a boolean indicating whether the operation was successful and value is the value of the option or a dictionary of all options

**Example:**
```python
from ngpt.utils.cli_config import get_cli_config_option

# Get a specific option
success, temperature = get_cli_config_option('temperature')
if success:
    print(f"Temperature: {temperature}")
else:
    print(f"Error: {temperature}")  # Contains error message if failed

# Get all options
success, all_options = get_cli_config_option()
if success:
    for opt, val in all_options.items():
        print(f"{opt}: {val}")
```

### `unset_cli_config_option`

```python
from ngpt.utils.cli_config import unset_cli_config_option

def unset_cli_config_option(option: str) -> Tuple[bool, str]:
```

Removes a CLI configuration option.

**Parameters:**
- `option` (str): The name of the option to unset

**Returns:**
- tuple: (success, message) where success is a boolean indicating whether the operation was successful and message is a string explaining the result

**Example:**
```python
from ngpt.utils.cli_config import unset_cli_config_option

# Remove the temperature setting
success, message = unset_cli_config_option('temperature')
print(message)
```

### `apply_cli_config`

```python
from ngpt.utils.cli_config import apply_cli_config

def apply_cli_config(args: Any, mode: str) -> Any:
```

Applies CLI configuration options to the provided argument namespace based on the current mode, respecting context and not overriding explicit args.

**Parameters:**
- `args` (Any): The argument namespace (from argparse)
- `mode` (str): The current mode ('interactive', 'shell', 'code', 'text', 'gitcommsg', or 'all' for default)

**Returns:**
- Any: The updated argument namespace

**Example:**
```python
import argparse
from ngpt.utils.cli_config import apply_cli_config

# Create an argument parser
parser = argparse.ArgumentParser()
parser.add_argument("--temperature", type=float, default=0.7)
parser.add_argument("--language", default="python")
parser.add_argument("--markdown-format", action="store_true")
args = parser.parse_args()

# Apply CLI configuration for code generation context
apply_cli_config(args, mode="code")

# Use the updated arguments
print(f"Temperature: {args.temperature}")
print(f"Language: {args.language}")
```

### `list_cli_config_options`

```python
from ngpt.utils.cli_config import list_cli_config_options

def list_cli_config_options() -> List[str]:
```

Lists all available CLI configuration options.

**Returns:**
- list: A sorted list of option names

**Example:**
```python
from ngpt.utils.cli_config import list_cli_config_options

# Get all available options
options = list_cli_config_options()
print("Available configuration options:")
for option in options:
    print(f"- {option}")
```

### `get_cli_config_dir`

```python
from ngpt.utils.cli_config import get_cli_config_dir

def get_cli_config_dir() -> Path:
```

Gets the directory where the CLI configuration is stored.

**Returns:**
- Path: The path to the CLI configuration directory

**Example:**
```python
from ngpt.utils.cli_config import get_cli_config_dir

# Get the CLI config directory
config_dir = get_cli_config_dir()
print(f"CLI configuration directory: {config_dir}")
```

### `get_cli_config_path`

```python
from ngpt.utils.cli_config import get_cli_config_path

def get_cli_config_path() -> Path:
```

Gets the path to the CLI configuration file.

**Returns:**
- Path: The path to the CLI configuration file

**Example:**
```python
from ngpt.utils.cli_config import get_cli_config_path

# Get the CLI config file path
config_path = get_cli_config_path()
print(f"CLI configuration file: {config_path}")
```

### `save_cli_config`

```python
from ngpt.utils.cli_config import save_cli_config

def save_cli_config(config: Dict[str, Any]) -> bool:
```

Saves CLI configuration to the config file.

**Parameters:**
- `config` (Dict[str, Any]): The configuration dictionary to save

**Returns:**
- bool: True if the operation was successful, False otherwise

**Example:**
```python
from ngpt.utils.cli_config import load_cli_config, save_cli_config

# Load existing config
config = load_cli_config()

# Modify config
config['temperature'] = 0.9

# Save the updated config
success = save_cli_config(config)
if success:
    print("Configuration saved successfully")
else:
    print("Failed to save configuration")
```

## Available CLI Configuration Options

The following options are available for configuration:

| Option | Type | Context | Description |
|--------|------|---------|-------------|
| `temperature` | float | all | Controls randomness in the response (0.0-1.0) |
| `top_p` | float | all | Controls diversity via nucleus sampling (0.0-1.0) |
| `no-stream` | bool | all | Disables streaming responses |
| `prettify` | bool | all | Enables markdown prettification |
| `stream-prettify` | bool | all | Enables streaming prettification |
| `max_tokens` | int | all | Maximum number of tokens to generate |
| `web-search` | bool | all | Enables web search capability |
| `renderer` | string | all | Markdown renderer to use ('auto', 'rich', 'glow') |
| `language` | string | code | Programming language for code generation |
| `provider` | string | all | Default provider to use |
| `config-index` | int | all | Default configuration index to use |
| `log` | string | all | Path to log file |
| `preprompt` | string | all | Custom preprompt to use |
| `rec-chunk` | bool | gitcommsg | Enable recursive chunking for large diffs |
| `diff` | string | gitcommsg | Path to diff file |
| `chunk-size` | int | gitcommsg | Maximum number of lines per chunk |
| `analyses-chunk-size` | int | gitcommsg | Maximum number of lines per chunk for analyses |
| `max-msg-lines` | int | gitcommsg | Maximum number of lines in commit message |
| `max-recursion-depth` | int | gitcommsg | Maximum recursion depth for message condensing |

## Configuration File Location

The CLI configuration file is located at:
- **Windows**: `%APPDATA%\ngpt\ngpt-cli.conf`
- **macOS**: `~/Library/Application Support/ngpt/ngpt-cli.conf`
- **Linux**: `~/.config/ngpt/ngpt-cli.conf` or `$XDG_CONFIG_HOME/ngpt/ngpt-cli.conf`

## Example: Creating a Custom CLI Tool with Persistent Configuration

```python
#!/usr/bin/env python
import argparse
from ngpt import NGPTClient, load_config
from ngpt.utils.cli_config import (
    load_cli_config,
    set_cli_config_option,
    get_cli_config_option,
    apply_cli_config,
    unset_cli_config_option
)
from ngpt.cli.formatters import ColoredHelpFormatter, COLORS

def main():
    # Create argument parser with custom formatting
    parser = argparse.ArgumentParser(
        description="My custom AI assistant with persistent configuration",
        formatter_class=ColoredHelpFormatter
    )
    
    # Add arguments
    parser.add_argument("prompt", nargs="?", help="The prompt to send to the AI")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for generation")
    parser.add_argument("--language", default="python", help="Language for code generation")
    parser.add_argument("--save-config", action="store_true", help="Save current settings as defaults")
    parser.add_argument("--reset-config", action="store_true", help="Reset to default settings")
    
    args = parser.parse_args()
    
    # Apply existing CLI configuration (for code generation context)
    apply_cli_config(args, mode="code")
    
    # If user wants to save current settings
    if args.save_config:
        set_cli_config_option('temperature', str(args.temperature))
        set_cli_config_option('language', args.language)
        print(f"{COLORS['green']}Configuration saved.{COLORS['reset']}")
        return
        
    # If user wants to reset settings
    if args.reset_config:
        unset_cli_config_option('temperature')
        unset_cli_config_option('language')
        print(f"{COLORS['green']}Configuration reset.{COLORS['reset']}")
        return
    
    # Regular operation - load config and create client
    config = load_config()
    client = NGPTClient(**config)
    
    if args.prompt:
        # Generate code with configured settings
        code = client.generate_code(
            args.prompt,
            language=args.language,
            temperature=args.temperature
        )
        print(code)
    else:
        # Show current configuration
        success, all_options = get_cli_config_option()
        if success:
            print(f"{COLORS['green']}Current configuration:{COLORS['reset']}")
            for opt, val in all_options.items():
                print(f"  {COLORS['cyan']}{opt}{COLORS['reset']}: {val}")
        print(f"\nUse with a prompt: my-tool 'create a function to calculate prime numbers'")

if __name__ == "__main__":
    main() 