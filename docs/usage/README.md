# Usage Guide

This section contains comprehensive documentation on how to use nGPT, a Swiss army knife for LLMs that combines a powerful CLI, interactive chatbot, and flexible library in one package. Learn how to seamlessly work with OpenAI, Ollama, Groq, Claude, Gemini, or any OpenAI-compatible API to generate code, craft git commits, rewrite text, and execute shell commands.

## Table of Contents

- [CLI Usage](cli_usage.md) - Learn how to use nGPT from the command line
- [Library Usage](library_usage.md) - Learn how to integrate nGPT into your Python projects
- [CLI Framework](cli_framework.md) - Learn how to build your own CLI tools with nGPT components
- [CLI Configuration](cli_config.md) - Learn how to configure default CLI options
- [Git Commit Message Generation](gitcommsg.md) - Learn how to generate high-quality commit messages using AI

## Overview

nGPT offers three primary ways to use it:

### 1. Command-Line Interface (CLI)

nGPT provides a powerful and intuitive command-line interface that allows you to:

- Chat with AI models using simple commands
- Conduct interactive chat sessions with conversation memory
- Generate and execute shell commands
- Generate clean code without markdown formatting
- Generate conventional git commit messages from diffs
- Configure API settings and preferences
- And more...

See the [CLI Usage](cli_usage.md) guide for detailed documentation.

### 2. Python Library

nGPT can be imported as a Python library, allowing you to:

- Integrate AI capabilities into your Python applications
- Chat with AI models programmatically
- Generate code and shell commands
- Create git commit messages from diffs
- Stream responses in real-time
- Use multiple configurations for different providers
- And more...

See the [Library Usage](library_usage.md) guide for detailed documentation and examples.

### 3. CLI Framework

nGPT can be used as a framework to build your own command-line tools:

- Leverage pre-built components for terminal UI 
- Create interactive chat applications with conversation history
- Implement beautiful markdown rendering with syntax highlighting
- Use real-time streaming with live updates
- Add persistent configuration management
- And more...

See the [CLI Framework](cli_framework.md) guide for detailed documentation.

## Quick Reference

### CLI Quick Start

```bash
# Basic chat
ngpt "Tell me about quantum computing"

# Interactive chat session
ngpt -i

# Generate shell command
ngpt --shell "list all PDF files recursively"

# Generate code
ngpt --code "function to calculate prime numbers"

# Generate git commit message from staged changes
ngpt --gitcommsg

# Generate commit message with context directive
ngpt -g --preprompt "type:feat focus on UI"
```

### Library Quick Start

```python
from ngpt import NGPTClient, load_config

# Load configuration--gitcommsg
config = load_config()

# Initialize client
client = NGPTClient(**config)

# Chat with AI
response = client.chat("Tell me about quantum computing")
print(response)

# Generate code
code = client.generate_code("function to calculate prime numbers")
print(code)

# Generate shell command
command = client.generate_shell_command("list all PDF files recursively")
print(command)

# Generate git commit message from diff content
diff_content = open("changes.diff").read()  # or get from 'git diff --staged'
commit_msg = client.generate_git_commit_message(diff_content)
print(commit_msg)
```

### CLI Framework Quick Start

```python
from ngpt import NGPTClient, load_config
from ngpt.cli.interactive import interactive_chat_session
from ngpt.cli.formatters import ColoredHelpFormatter
import argparse

# Create parser with colorized help
parser = argparse.ArgumentParser(
    description="My custom AI assistant",
    formatter_class=ColoredHelpFormatter
)

# Initialize client
client = NGPTClient(**load_config())

# Use nGPT interactive session with custom prompt
interactive_chat_session(
    client=client,
    preprompt="You are a specialized AI assistant for my custom tool",
    prettify=True
)
```

For more detailed information, see the specific usage guides. 