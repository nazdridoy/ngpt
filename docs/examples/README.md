# Code Examples

This directory contains comprehensive examples demonstrating how to use nGPT in various scenarios. These examples showcase both the library's API and the command-line interface.

## Table of Contents

- [Basic Examples](basic.md) - Simple examples to get started with nGPT
- [Advanced Examples](advanced.md) - More complex examples with advanced features
- [Custom Integrations](integrations.md) - Examples of integrating nGPT into larger applications
- [CLI Component Examples](cli_components.md) - Examples of building custom CLI tools using nGPT components

## Getting Started

To run these examples, you'll need to:

1. Install nGPT: `pip install ngpt`
2. Configure your API key: `ngpt --config` or set the `OPENAI_API_KEY` environment variable
3. Ensure you have the required dependencies for specific examples

## Example Categories

### Basic Examples

These examples demonstrate the fundamental functionality of nGPT:

- Simple chat interactions
- Code generation
- Shell command generation
- Basic configuration
- Markdown formatting

### Advanced Examples

These examples show more sophisticated use of nGPT:

- Streaming responses
- Conversation management
- Working with multiple API providers
- Error handling and retries
- Custom system prompts
- Web search integration

### Custom Integrations

These examples demonstrate how to integrate nGPT into larger applications:

- Web application integration
- Command-line tool development
- Chatbot development
- Workflow automation
- API service integration

### CLI Component Examples

These examples show how to use nGPT's CLI components to build your own command-line tools:

- Custom code generation tools
- Specialized chat assistants
- Documentation generators
- Tools with persistent configuration
- Translation utilities
- Image analysis applications

## Quick Reference

Here's a quick reference to the most important examples:

```python
# Basic chat example
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)
response = client.chat("Tell me about quantum computing")
print(response)

# Code generation example with specific language
code = client.generate_code("function to calculate fibonacci numbers", language="javascript")
print(code)

# Shell command example with web search enabled
command = client.generate_shell_command(
    "find all files modified in the last week", 
    web_search=True
)
print(command)

# Streaming example with markdown formatting
for chunk in client.chat(
    "Explain neural networks", 
    stream=True, 
    markdown_format=True
):
    print(chunk, end="", flush=True)

# CLI component reuse example
from ngpt.cli.formatters import ColoredHelpFormatter
from ngpt.cli.renderers import prettify_markdown
import argparse

parser = argparse.ArgumentParser(
    description="My custom AI tool",
    formatter_class=ColoredHelpFormatter
)

# Using CLI modes example
from ngpt.cli.modes.chat import chat_mode
from ngpt.cli.modes.code import code_mode
from ngpt.cli.modes.shell import shell_mode

# Interactive session example with web search
from ngpt.cli.interactive import interactive_chat_session
```

Explore the individual example pages for more detailed code samples and explanations. 