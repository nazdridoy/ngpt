# API Reference

This section provides detailed documentation for the nGPT API, including all classes, methods, functions, and parameters.

## Overview

nGPT's API consists of two main components:

1. **NGPTClient**: The main client class used to interact with AI providers
2. **Configuration Utilities**: Functions for managing configuration files and settings

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

## Quick Reference

```python
# Import core components
from ngpt import NGPTClient, load_config

# Import configuration utilities
from ngpt.utils.config import (
    load_configs,
    get_config_path,
    get_config_dir,
    add_config_entry,
    remove_config_entry
)

# Import version information
from ngpt import __version__
```

For complete documentation on using these components, see the linked reference pages. 