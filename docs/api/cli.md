# CLI Components API Reference

This document provides a comprehensive API reference for nGPT's CLI components that can be reused in your own command-line applications.

## Overview

The `cli.py` module contains a variety of reusable components for building command-line interfaces with AI capabilities. These components are designed to be modular and can be used independently in your own projects.

## Core Components

### `interactive_chat_session`

```python
def interactive_chat_session(
    client,
    web_search=False,
    no_stream=False,
    temperature=0.7,
    top_p=1.0,
    max_tokens=None,
    log_file=None,
    preprompt=None,
    prettify=False,
    renderer='auto',
    stream_prettify=False
)
```

Creates an interactive chat session with the specified AI client.

**Parameters:**
- `client` (NGPTClient): The initialized client to use for chat interactions
- `web_search` (bool): Whether to enable web search capability
- `no_stream` (bool): Whether to disable streaming responses
- `temperature` (float): Temperature for generation (0.0-1.0)
- `top_p` (float): Top-p sampling value (0.0-1.0)
- `max_tokens` (int, optional): Maximum number of tokens to generate
- `log_file` (str, optional): Path to file for logging the conversation
- `preprompt` (str, optional): System prompt to use for the chat
- `prettify` (bool): Whether to prettify markdown in responses
- `renderer` (str): Markdown renderer to use ('auto', 'rich', 'glow')
- `stream_prettify` (bool): Whether to enable real-time markdown rendering

**Returns:** None

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli import interactive_chat_session

client = NGPTClient(**load_config())

interactive_chat_session(
    client=client,
    preprompt="You are a helpful assistant.",
    prettify=True,
    renderer='rich'
)
```

### `prettify_markdown`

```python
def prettify_markdown(text, renderer='auto')
```

Renders markdown text with syntax highlighting.

**Parameters:**
- `text` (str): The markdown text to render
- `renderer` (str): Which renderer to use ('auto', 'rich', 'glow')

**Returns:**
- str: The rendered text (may include ANSI color codes)

**Example:**
```python
from ngpt.cli import prettify_markdown

markdown = """# Hello World
```python
print('Hello, World!')
```"""

rendered = prettify_markdown(markdown, renderer='rich')
print(rendered)
```

### `prettify_streaming_markdown`

```python
def prettify_streaming_markdown(renderer='rich', is_interactive=False, header_text=None)
```

Creates a streaming markdown renderer that updates in real-time.

**Parameters:**
- `renderer` (str): Which renderer to use ('auto', 'rich', 'glow')
- `is_interactive` (bool): Whether this is being used in an interactive session
- `header_text` (str, optional): Header text to display above the content

**Returns:**
- object: A streaming markdown renderer object with an `update_content` method

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli import prettify_streaming_markdown

client = NGPTClient(**load_config())
streamer = prettify_streaming_markdown(renderer='rich')

client.chat(
    "Explain quantum computing with code examples",
    stream=True,
    stream_callback=streamer.update_content
)
```

### `ColoredHelpFormatter`

```python
class ColoredHelpFormatter(argparse.HelpFormatter)
```

An `argparse` formatter class that adds color to help text.

**Usage:**
```python
import argparse
from ngpt.cli import ColoredHelpFormatter

parser = argparse.ArgumentParser(
    description="My CLI application",
    formatter_class=ColoredHelpFormatter
)

parser.add_argument("--option", help="This help text will be colored")
```

## Utility Functions

### `has_glow_installed`

```python
def has_glow_installed()
```

Checks if the Glow CLI tool is installed on the system.

**Returns:**
- bool: True if Glow is installed, False otherwise

**Example:**
```python
from ngpt.cli import has_glow_installed

if has_glow_installed():
    print("Using Glow renderer")
else:
    print("Falling back to Rich renderer")
```

### `supports_ansi_colors`

```python
def supports_ansi_colors()
```

Detects if the current terminal supports ANSI color codes.

**Returns:**
- bool: True if terminal supports colors, False otherwise

**Example:**
```python
from ngpt.cli import supports_ansi_colors

if supports_ansi_colors():
    print("\033[1;32mSuccess!\033[0m")
else:
    print("Success!")
```

### `has_markdown_renderer`

```python
def has_markdown_renderer(renderer='auto')
```

Checks if the specified markdown renderer is available.

**Parameters:**
- `renderer` (str): The renderer to check ('auto', 'rich', 'glow')

**Returns:**
- bool: True if the renderer is available, False otherwise

**Example:**
```python
from ngpt.cli import has_markdown_renderer

if has_markdown_renderer('rich'):
    print("Rich renderer is available")
```

### `show_available_renderers`

```python
def show_available_renderers()
```

Displays the available markdown renderers.

**Returns:** None

**Example:**
```python
from ngpt.cli import show_available_renderers

show_available_renderers()
```

### `handle_cli_config`

```python
def handle_cli_config(action, option=None, value=None)
```

Manages the CLI configuration settings.

**Parameters:**
- `action` (str): The action to perform ('get', 'set', 'unset', 'list')
- `option` (str, optional): The configuration option name
- `value` (str, optional): The value to set for the option

**Returns:**
- Various types depending on the action

**Example:**
```python
from ngpt.cli import handle_cli_config

# Get a setting
temperature = handle_cli_config('get', 'temperature')

# Set a setting
handle_cli_config('set', 'language', 'python')

# List all settings
settings = handle_cli_config('list')
```

### `show_cli_config_help`

```python
def show_cli_config_help()
```

Displays help information for CLI configuration.

**Returns:** None

**Example:**
```python
from ngpt.cli import show_cli_config_help

show_cli_config_help()
```

## Reference Tables

### Markdown Renderers

| Renderer | Package | Notes |
|----------|---------|-------|
| 'rich' | rich | Built-in if installed with `ngpt[full]` |
| 'glow' | External CLI tool | Requires separate installation |
| 'auto' | - | Auto-selects best available renderer |

### Terminal Features

The CLI components in nGPT automatically detect various terminal capabilities:

| Feature | Function | Description |
|---------|----------|-------------|
| Color support | `supports_ansi_colors()` | Detects terminal color support |
| Terminal size | Internal | Automatically adapts to terminal dimensions |
| Unicode support | Internal | Falls back to ASCII if Unicode not supported |

## Complete Example

Here's a complete example showing how to use multiple CLI components together:

```python
#!/usr/bin/env python3
import argparse
import sys
from ngpt import NGPTClient, load_config
from ngpt.cli import (
    ColoredHelpFormatter,
    prettify_markdown,
    prettify_streaming_markdown,
    has_markdown_renderer,
    supports_ansi_colors,
    handle_cli_config
)

def main():
    # Use colored help formatter
    parser = argparse.ArgumentParser(
        description="Custom AI Code Generator",
        formatter_class=ColoredHelpFormatter
    )
    
    # Add arguments
    parser.add_argument("prompt", nargs="?", help="Code description")
    parser.add_argument("--language", "-l", help="Programming language")
    parser.add_argument("--prettify", "-p", action="store_true", help="Prettify output")
    
    args = parser.parse_args()
    
    # Use settings from CLI config
    language = args.language or handle_cli_config('get', 'language') or "python"
    prettify = args.prettify
    
    if not args.prompt:
        parser.print_help()
        return
    
    # Print colored status message
    if supports_ansi_colors():
        print(f"\033[1;36mGenerating {language} code...\033[0m")
    else:
        print(f"Generating {language} code...")
    
    # Initialize the client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate code with a specific system prompt
    system_prompt = f"You are an expert {language} developer. Provide clean, well-structured code."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.prompt}
    ]
    
    # Check renderer availability
    has_renderer = has_markdown_renderer('rich' if prettify else 'auto')
    
    # Generate and display code
    if prettify and has_renderer:
        # Use streaming markdown renderer
        streamer = prettify_streaming_markdown(
            renderer='rich',
            header_text=f"{language.capitalize()} Code"
        )
        
        # Stream with real-time formatting
        full_code = ""
        for chunk in client.generate_code(
            args.prompt,
            language=language,
            stream=True
        ):
            full_code += chunk
            streamer.update_content(f"```{language}\n{full_code}\n```")
            
        # Save the language preference for next time
        if args.language:
            handle_cli_config('set', 'language', language)
    else:
        # Simple streaming output
        code = client.generate_code(args.prompt, language=language)
        print(f"\n{code}")

if __name__ == "__main__":
    main()
```

## See Also

- [CLI Framework Guide](../usage/cli_framework.md) - Guide to building CLI tools with nGPT components 
- [CLI Component Examples](../examples/cli_components.md) - Practical examples of using CLI components
- [NGPTClient API](client.md) - Reference for the client API used with CLI components 