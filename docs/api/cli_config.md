# CLI Configuration Utilities

This document provides a comprehensive API reference for nGPT's CLI configuration utilities that can be used to manage persistent CLI settings.

## Overview

nGPT provides a set of utilities for managing CLI-specific configuration settings that persist between invocations of the command-line tool. These utilities allow you to get, set, and unset configuration options, as well as apply them to command-line arguments.

## Core Functions

### `load_cli_config`

```python
from ngpt.utils.cli_config import load_cli_config

def load_cli_config():
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

def set_cli_config_option(option, value):
```

Sets a CLI configuration option.

**Parameters:**
- `option` (str): The name of the option to set
- `value` (str): The value to set for the option

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

def get_cli_config_option(option=None):
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

def unset_cli_config_option(option):
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

def apply_cli_config(args, options=None, context="all"):
```

Applies CLI configuration options to the provided argument namespace.

**Parameters:**
- `args` (namespace): The argument namespace (from argparse)
- `options` (list, optional): List of option names to apply (applies all if None)
- `context` (str): The context for applying the configuration (e.g., "all", "chat", "code", "shell", "text")

**Returns:**
- None: Modifies the args namespace in-place

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
apply_cli_config(args, context="code")

# Use the updated arguments
print(f"Temperature: {args.temperature}")
print(f"Language: {args.language}")
```

## Available CLI Configuration Options

The following options are available for configuration:

| Option | Type | Context | Description |
|--------|------|---------|-------------|
| `temperature` | float | all | Controls randomness in the response (0.0-1.0) |
| `top-p` | float | all | Controls diversity via nucleus sampling (0.0-1.0) |
| `no-stream` | bool | all | Disables streaming responses |
| `max-tokens` | int | all | Maximum number of tokens to generate |
| `web-search` | bool | all | Enables web search capability |
| `prettify` | bool | all | Enables markdown prettification |
| `renderer` | string | all | Markdown renderer to use ('auto', 'rich', 'glow') |
| `language` | string | code | Programming language for code generation |
| `execute` | bool | shell | Whether to execute generated shell commands |
| `markdown-format` | bool | all | Format responses with markdown |
| `provider` | string | all | Default provider to use |
| `config-index` | int | all | Default configuration index to use |
| `model` | string | all | Default model to use |

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
    apply_cli_config
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
    apply_cli_config(args, context="code")
    
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