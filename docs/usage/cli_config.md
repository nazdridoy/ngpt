---
layout: default
title: CLI Configuration Guide
parent: Usage
nav_order: 2
permalink: /usage/cli_config/
---

# CLI Configuration Guide

nGPT offers a CLI configuration system that allows you to set persistent default values for command-line options. This guide explains how to use and manage CLI configurations.

## Overview

The CLI configuration system is separate from your API configuration (which stores API keys, base URLs, and models). Instead, it stores your preferred default values for CLI parameters like `temperature`, `language`, or `renderer`.

This is especially useful when you:

- Repeatedly use the same parameter values
- Have preferred settings for specific tasks
- Want to create different workflows based on context

## Configuration File Location

The CLI configuration is stored in a platform-specific location:

- **Linux**: `~/.config/ngpt/ngpt-cli.conf` or `$XDG_CONFIG_HOME/ngpt/ngpt-cli.conf`
- **macOS**: `~/Library/Application Support/ngpt/ngpt-cli.conf`
- **Windows**: `%APPDATA%\ngpt\ngpt-cli.conf`

## Basic Commands

The CLI configuration is managed through the `--cli-config` command:

```bash
ngpt --cli-config COMMAND [ARGS...]
```

Where `COMMAND` is one of:
- `help` - Show help message
- `set` - Set a configuration value
- `get` - Get a configuration value
- `unset` - Remove a configuration value
- `list` - List available configurable options

## Setting Configuration Values

To set a default value for a parameter:

```bash
ngpt --cli-config set OPTION VALUE
```

For example:

```bash
# Set default temperature to 0.9
ngpt --cli-config set temperature 0.9

# Set default language for code generation to JavaScript
ngpt --cli-config set language javascript

# Set default provider to Gemini
ngpt --cli-config set provider Gemini

# Enable web search by default
ngpt --cli-config set web-search true

# Set default renderer for prettify
ngpt --cli-config set renderer glow
```

Boolean values can be set using `true` or `false`:

```bash
# Enable streaming markdown rendering by default
ngpt --cli-config set stream-prettify true

# Disable streaming by default
ngpt --cli-config set no-stream true
```

## Getting Configuration Values

To view the current value of a specific setting:

```bash
ngpt --cli-config get OPTION
```

For example:

```bash
# Check current temperature setting
ngpt --cli-config get temperature
```

To view all current settings:

```bash
ngpt --cli-config get
```

This will display all your configured CLI defaults.

## Removing Configuration Values

To remove a setting and revert to the built-in default:

```bash
ngpt --cli-config unset OPTION
```

For example:

```bash
# Remove custom temperature setting
ngpt --cli-config unset temperature
```

## Listing Available Options

To see all configurable options:

```bash
ngpt --cli-config list
```

This displays the available options, their types, default values, and any conflicts with other options.

## Configuration Context and Exclusivity

Some options only apply in specific modes:

- `language` only applies to code generation mode
- `rec-chunk` only applies to git commit message mode

Some options are mutually exclusive:

- `no-stream`, `prettify`, and `stream-prettify` cannot be used together
- `provider` and `config-index` cannot be used together

The CLI configuration system enforces these rules to prevent incompatible combinations.

## Available Options

### General Options (All Modes)

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `config-index` | int | 0 | Index of the configuration to use |
| `provider` | string | - | Provider name to use (alternative to config-index) |
| `temperature` | float | 0.7 | Controls randomness (0.0-2.0) |
| `top_p` | float | 1.0 | Controls diversity (0.0-1.0) |
| `max_tokens` | int | - | Maximum response length in tokens |
| `preprompt` | string | - | Custom system prompt |
| `log` | string | - | Log file path |
| `web-search` | bool | false | Enable web search capability |
| `no-stream` | bool | false | Disable streaming |
| `prettify` | bool | false | Enable markdown rendering |
| `stream-prettify` | bool | false | Enable real-time markdown rendering |
| `renderer` | string | auto | Markdown renderer to use (auto, rich, or glow) |

### Mode-Specific Options

#### Code Generation Mode
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `language` | string | python | Programming language for code generation |

#### Git Commit Message Mode
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rec-chunk` | bool | false | Process large diffs in chunks recursively |
| `diff` | string | - | Path to diff file |
| `chunk-size` | int | 200 | Lines per chunk when chunking is enabled |
| `analyses-chunk-size` | int | 200 | Lines per chunk when recursively chunking analyses |
| `max-msg-lines` | int | 20 | Maximum lines in commit message before condensing |
| `max-recursion-depth` | int | 3 | Maximum recursion depth for commit message condensing |

## Examples

### Setting Up a Development Environment

```bash
# Set Python as default language
ngpt --cli-config set language python

# Enable pretty markdown rendering by default
ngpt --cli-config set prettify true

# Set temperature for more deterministic responses
ngpt --cli-config set temperature 0.3
```

### Setting Up a Creative Writing Environment

```bash
# Increase temperature for more creative responses
ngpt --cli-config set temperature 1.2

# Reduce top_p for more focused but varied outputs
ngpt --cli-config set top_p 0.9

# Enable web search for more informed responses
ngpt --cli-config set web-search true
```

### Setting Up for Git Workflow

```bash
# Enable recursive chunking for large diffs
ngpt --cli-config set rec-chunk true

# Increase chunk size for more context
ngpt --cli-config set chunk-size 300

# Limit commit message lines
ngpt --cli-config set max-msg-lines 15
```

## Priority Order

CLI configuration values are applied with this priority (highest to lowest):

1. Command-line arguments (directly passed to ngpt)
2. CLI configuration settings (from ngpt-cli.conf)
3. Built-in defaults

This means you can always override your configured defaults by specifying options directly on the command line.

## Notes and Tips

- Settings are applied based on context (e.g., language only applies to code generation mode)
- Boolean options can be set to `true` or `false` (both case-insensitive)
- Sensitive data like API keys should NOT be stored in CLI configuration; use the main configuration system instead
- The configuration file is a simple JSON file that can be manually edited if necessary
- Changes to configuration take effect immediately in new commands

## Troubleshooting

### Configuration Not Applied

If your configuration is not being applied:

1. Verify the setting exists with `ngpt --cli-config list`
2. Check the current value with `ngpt --cli-config get OPTION`
3. Ensure you're not overriding it with a command-line argument
4. Check for exclusive options that might conflict

### Resetting All Configuration

To reset all CLI configuration to defaults:

1. Delete the configuration file:
   ```bash
   # Linux/macOS
   rm ~/.config/ngpt/ngpt-cli.conf
   
   # Windows (PowerShell)
   Remove-Item $env:APPDATA\ngpt\ngpt-cli.conf
   ```
2. Or unset each option individually:
   ```bash
   ngpt --cli-config get | grep -v "Available options" | cut -d':' -f1 | xargs -I{} ngpt --cli-config unset {}
   ``` 