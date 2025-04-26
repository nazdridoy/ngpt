# API Reference

This section provides detailed documentation for the nGPT API, including all classes, methods, functions, and parameters.

## Overview

nGPT's API consists of several main components:

1. **NGPTClient**: The main client class used to interact with AI providers
2. **Configuration Utilities**: Functions for managing configuration files and settings
3. **CLI Components**: Modular CLI utilities that can be reused in custom applications
4. **CLI Configuration Utilities**: Functions for managing CLI-specific configurations
5. **Logging Utilities**: Tools for logging conversations and errors

## Table of Contents

- [NGPTClient](client.md) - Primary client for interacting with LLM APIs
  - [Initialization](client.md#initialization)
  - [Chat Method](client.md#chat-method)
  - [Generate Shell Command](client.md#generate-shell-command)
  - [Generate Code](client.md#generate-code)
  - [List Models](client.md#list-models)

- [Configuration](config.md) - Functions for managing configurations
  - [Loading Configurations](config.md#loading-configurations)
  - [Creating Configurations](config.md#creating-configurations)
  - [Editing Configurations](config.md#editing-configurations)
  - [Removing Configurations](config.md#removing-configurations)
  - [Configuration Paths](config.md#configuration-paths)
  - [Default Configuration](config.md#default-configuration)

- [CLI Components](cli.md) - CLI functionality
  - [Module Structure](cli.md#module-structure)
  - [Interactive Chat Module](cli.md#interactive-chat-module)
  - [Formatters Module](cli.md#formatters-module)
  - [Renderers Module](cli.md#renderers-module)
  - [UI Components](cli.md#ui-components)
  - [CLI Configuration Utilities](cli.md#cli-configuration-utilities)
  - [Operation Modes](cli.md#operation-modes)
    - [Chat Mode](cli.md#chat-mode)
    - [Code Mode](cli.md#code-mode)
    - [Shell Mode](cli.md#shell-mode)
    - [Text Mode](cli.md#text-mode)
    - [Rewrite Mode](cli.md#rewrite-mode)
    - [Git Commit Message Mode](cli.md#git-commit-message-mode)

- [CLI Configuration](cli_config.md) - Persistent CLI settings
  - [Loading Configuration](cli_config.md#load_cli_config)
  - [Setting Options](cli_config.md#set_cli_config_option)
  - [Getting Options](cli_config.md#get_cli_config_option)
  - [Removing Options](cli_config.md#unset_cli_config_option)
  - [Applying Configuration](cli_config.md#apply_cli_config)
  - [Available Options](cli_config.md#available-cli-configuration-options)
  - [Listing Options](cli_config.md#list_cli_config_options)
  - [Configuration Paths](cli_config.md#configuration-paths)

- [Logging](logging.md) - Logging utilities
  - [Creating Loggers](logging.md#create_logger)
  - [Logger Class](logging.md#logger-class)
  - [Log Levels](logging.md#log-levels)
  - [Log Formatting](logging.md#log-formatting)

## Quick Reference

```python
# Import core components
from ngpt import NGPTClient, load_config, __version__

# Import configuration utilities
from ngpt.utils.config import (
    load_configs,
    get_config_path,
    get_config_dir,
    add_config_entry,
    remove_config_entry,
    DEFAULT_CONFIG,
    DEFAULT_CONFIG_ENTRY
)

# Import CLI configuration utilities
from ngpt.utils.cli_config import (
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

# Import logging utilities
from ngpt.utils.log import create_logger, Logger

# Import CLI module components
from ngpt.cli.interactive import interactive_chat_session
from ngpt.cli.formatters import prettify_markdown, ColoredHelpFormatter, COLORS
from ngpt.cli.renderers import prettify_streaming_markdown, has_markdown_renderer
from ngpt.cli.ui import create_progress_bar, create_spinner

# Import operation modes
from ngpt.cli.modes.chat import chat_mode
from ngpt.cli.modes.code import code_mode
from ngpt.cli.modes.shell import shell_mode
from ngpt.cli.modes.text import text_mode
from ngpt.cli.modes.rewrite import rewrite_mode
from ngpt.cli.modes.gitcommsg import git_commit_message_mode

# Import main CLI entry point
from ngpt.cli import main
```

For complete documentation on using these components, see the linked reference pages. For examples of integrating nGPT into your applications, see the [Examples](../examples/) section. 