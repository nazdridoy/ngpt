# CLI Components API Reference

This document provides a comprehensive API reference for nGPT's CLI components that can be reused in your own command-line applications.

## Overview

The CLI components for nGPT are organized into a modular structure under the `ngpt.cli` package. This makes it easier to use specific components without importing unnecessary dependencies.

## Module Structure

- `ngpt.cli`: Main CLI package
  - `ngpt.cli.main`: Main entry point for the CLI
  - `ngpt.cli.interactive`: Interactive chat session functionality
  - `ngpt.cli.formatters`: Text and markdown formatting utilities
  - `ngpt.cli.renderers`: Markdown rendering utilities
  - `ngpt.cli.config_manager`: Configuration management utilities
  - `ngpt.cli.ui`: UI components for terminal interfaces
  - `ngpt.cli.args`: Argument parsing utilities
  - `ngpt.cli.modes`: Operation-specific modules
    - `ngpt.cli.modes.chat`: Chat mode functionality
    - `ngpt.cli.modes.code`: Code generation mode functionality
    - `ngpt.cli.modes.shell`: Shell command generation mode functionality
    - `ngpt.cli.modes.text`: Text generation mode functionality
    - `ngpt.cli.modes.rewrite`: Text rewriting mode functionality
    - `ngpt.cli.modes.gitcommsg`: Git commit message generation functionality

## Interactive Chat Module

### `interactive_chat_session`

```python
from ngpt.cli.interactive import interactive_chat_session

def interactive_chat_session(
    client,
    web_search=False,
    no_stream=False,
    temperature=0.7,
    top_p=1.0,
    max_tokens=None,
    logger=None,
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
- `logger` (object, optional): A logger instance with `log(role, message)` and `get_log_path()` methods for logging the conversation.
- `preprompt` (str, optional): System prompt to use for the chat
- `prettify` (bool): Whether to prettify markdown in responses
- `renderer` (str): Markdown renderer to use ('auto', 'rich', 'glow')
- `stream_prettify` (bool): Whether to enable real-time markdown rendering

**Returns:** None

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.interactive import interactive_chat_session

client = NGPTClient(**load_config())

interactive_chat_session(
    client=client,
    preprompt="You are a helpful assistant.",
    prettify=True,
    renderer='rich'
)
```

## Formatters Module

### `prettify_markdown`

```python
from ngpt.cli.formatters import prettify_markdown

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
from ngpt.cli.formatters import prettify_markdown

markdown = """# Hello World
```python
print('Hello, World!')
```"""

rendered = prettify_markdown(markdown, renderer='rich')
print(rendered)
```

### `ColoredHelpFormatter`

```python
from ngpt.cli.formatters import ColoredHelpFormatter

class ColoredHelpFormatter(argparse.HelpFormatter)
```

An `argparse` formatter class that adds color to help text.

**Usage:**
```python
import argparse
from ngpt.cli.formatters import ColoredHelpFormatter, COLORS

parser = argparse.ArgumentParser(
    description="My CLI application",
    formatter_class=ColoredHelpFormatter
)

parser.add_argument("--option", help="This help text will be colored")

# Use color constants in your output
print(f"{COLORS['green']}Success!{COLORS['reset']}")
```

### `COLORS`

A dictionary of ANSI color codes that can be used for terminal output.

**Example:**
```python
from ngpt.cli.formatters import COLORS

print(f"{COLORS['green']}Success!{COLORS['reset']}")
print(f"{COLORS['red']}Error!{COLORS['reset']}")
print(f"{COLORS['yellow']}Warning!{COLORS['reset']}")
print(f"{COLORS['cyan']}Information{COLORS['reset']}")
```

## Renderers Module

### `prettify_streaming_markdown`

```python
from ngpt.cli.renderers import prettify_streaming_markdown

def prettify_streaming_markdown(renderer='rich', is_interactive=False, header_text=None)
```

Creates a streaming markdown renderer that updates in real-time with loading spinner functionality.

**Parameters:**
- `renderer` (str): Which renderer to use ('auto', 'rich', 'glow')
- `is_interactive` (bool): Whether this is being used in an interactive session
- `header_text` (str, optional): Header text to display above the content

**Returns:**
- tuple: (live_display, update_function, setup_spinner_func) if successful, (None, None, None) otherwise
  - `live_display`: The rich.Live display object for controlling the display lifecycle
  - `update_function`: Function to call with updated content that will refresh the display
  - `setup_spinner_func`: Function to set up a spinner while waiting for first content

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.renderers import prettify_streaming_markdown
import threading

client = NGPTClient(**load_config())

# Get components for streaming display with spinner
live_display, update_function, setup_spinner = prettify_streaming_markdown(renderer='rich')

# Set up spinner (optional)
stop_spinner_event = threading.Event()
stop_spinner_func = None
if setup_spinner:
    stop_spinner_func = setup_spinner(stop_spinner_event, "Waiting for response...")

# The update_function will automatically:
# 1. Start the live display when first content arrives
# 2. Stop the spinner when first content arrives
# 3. Update the display with new content

# Use with client
response = client.chat(
    "Explain quantum computing",
    stream=True,
    stream_callback=update_function
)

# Ensure spinner is stopped if no content was received
if not stop_spinner_event.is_set():
    stop_spinner_event.set()

# Stop the display when done
if live_display:
    live_display.stop()
```

### `has_markdown_renderer`

```python
from ngpt.cli.renderers import has_markdown_renderer

def has_markdown_renderer(renderer='auto')
```

Checks if the specified markdown renderer is available.

**Parameters:**
- `renderer` (str): The renderer to check ('auto', 'rich', 'glow')

**Returns:**
- bool: True if the renderer is available, False otherwise

**Example:**
```python
from ngpt.cli.renderers import has_markdown_renderer

if has_markdown_renderer('rich'):
    print("Rich renderer is available")
```

### `show_available_renderers`

```python
from ngpt.cli.renderers import show_available_renderers

def show_available_renderers()
```

Displays the available markdown renderers.

**Returns:** None

**Example:**
```python
from ngpt.cli.renderers import show_available_renderers

show_available_renderers()
```

### `has_glow_installed`

```python
from ngpt.cli.renderers import has_glow_installed

def has_glow_installed()
```

Checks if the Glow CLI tool is installed on the system.

**Returns:**
- bool: True if Glow is installed, False otherwise

**Example:**
```python
from ngpt.cli.renderers import has_glow_installed

if has_glow_installed():
    print("Using Glow renderer")
else:
    print("Falling back to Rich renderer")
```

### `supports_ansi_colors`

```python
from ngpt.cli.formatters import supports_ansi_colors

def supports_ansi_colors()
```

Detects if the current terminal supports ANSI color codes.

**Returns:**
- bool: True if terminal supports colors, False otherwise

**Example:**
```python
from ngpt.cli.formatters import supports_ansi_colors

if supports_ansi_colors():
    print("\033[1;32mSuccess!\033[0m")
else:
    print("Success!")
```

## CLI Configuration Utilities

### `handle_cli_config`

```python
from ngpt.cli.main import handle_cli_config

def handle_cli_config(action, option=None, value=None)
```

Manages the CLI configuration settings.

**Parameters:**
- `action` (str): The action to perform ('get', 'set', 'unset', 'list', 'help')
- `option` (str, optional): The configuration option name
- `value` (str, optional): The value to set for the option

**Returns:**
- Various types depending on the action

**Example:**
```python
from ngpt.cli.main import handle_cli_config

# Get a setting
temperature = handle_cli_config('get', 'temperature')

# Set a setting
handle_cli_config('set', 'language', 'python')

# List all settings
settings = handle_cli_config('list')

# Show help
handle_cli_config('help')
```

### `show_cli_config_help`

```python
from ngpt.cli.main import show_cli_config_help

def show_cli_config_help()
```

Displays help information for CLI configuration.

**Returns:** None

**Example:**
```python
from ngpt.cli.main import show_cli_config_help

show_cli_config_help()
```

### `apply_cli_config`

```python
from ngpt.utils.cli_config import apply_cli_config

def apply_cli_config(args, options=None, context="all")
```

Applies CLI configuration to command line arguments.

**Parameters:**
- `args` (namespace): The argument namespace (from argparse)
- `options` (list, optional): List of option names to apply (applies all if None)
- `context` (str): The context for applying the configuration (e.g., "all", "chat", "code")

**Example:**
```python
import argparse
from ngpt.utils.cli_config import apply_cli_config

parser = argparse.ArgumentParser()
parser.add_argument("--temperature", type=float, default=0.7)
parser.add_argument("--language", default="python")
args = parser.parse_args()

# Apply CLI configuration
apply_cli_config(args, context="code")
```

## Operation Modes

### Chat Mode

```python
from ngpt.cli.modes.chat import chat_mode

def chat_mode(
    client,
    prompt,
    temperature=0.7,
    top_p=1.0,
    max_tokens=None,
    no_stream=False,
    prettify=False,
    renderer='auto',
    web_search=False,
    logger=None,
    markdown_format=True,
    preprompt=None
)
```

Executes a chat operation with the given client.

**Parameters:**
- `client` (NGPTClient): The initialized client for the operation
- `prompt` (str): The user's input message
- `temperature` (float): Temperature setting (0.0-1.0)
- `top_p` (float): Top-p sampling value (0.0-1.0)
- `max_tokens` (int, optional): Maximum tokens to generate
- `no_stream` (bool): Whether to disable streaming
- `prettify` (bool): Whether to prettify markdown output
- `renderer` (str): Markdown renderer to use
- `web_search` (bool): Whether to enable web search
- `logger` (object, optional): Logger instance
- `markdown_format` (bool): Allow markdown in responses
- `preprompt` (str, optional): System prompt to use

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.chat import chat_mode

client = NGPTClient(**load_config())
chat_mode(
    client=client,
    prompt="Tell me about quantum computing",
    prettify=True,
    renderer='rich'
)
```

### Code Mode

```python
from ngpt.cli.modes.code import code_mode

def code_mode(
    client,
    prompt,
    language="python",
    temperature=0.4,
    top_p=0.95,
    max_tokens=None,
    no_stream=False,
    web_search=False,
    prettify=False,
    renderer='auto',
    markdown_format=True,
    output_file=None,
    logger=None
)
```

Executes a code generation operation with the given client.

**Parameters:**
- `client` (NGPTClient): The initialized client for the operation
- `prompt` (str): Description of the code to generate
- `language` (str): Programming language to generate in
- `temperature` (float): Temperature setting (0.0-1.0)
- `top_p` (float): Top-p sampling value (0.0-1.0)
- `max_tokens` (int, optional): Maximum tokens to generate
- `no_stream` (bool): Whether to disable streaming
- `web_search` (bool): Whether to enable web search
- `prettify` (bool): Whether to prettify markdown output
- `renderer` (str): Markdown renderer to use
- `markdown_format` (bool): Format output as markdown
- `output_file` (str, optional): File to write the generated code to
- `logger` (object, optional): Logger instance

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.code import code_mode

client = NGPTClient(**load_config())
code_mode(
    client=client,
    prompt="Write a function to find prime numbers using the Sieve of Eratosthenes",
    language="python",
    prettify=True
)
```

### Shell Mode

```python
from ngpt.cli.modes.shell import shell_mode

def shell_mode(
    client,
    prompt,
    execute=False,
    web_search=False,
    temperature=0.4,
    max_tokens=None,
    logger=None
)
```

Executes a shell command generation operation with the given client.

**Parameters:**
- `client` (NGPTClient): The initialized client for the operation
- `prompt` (str): Description of the shell command to generate
- `execute` (bool): Whether to execute the generated command
- `web_search` (bool): Whether to enable web search
- `temperature` (float): Temperature setting (0.0-1.0)
- `max_tokens` (int, optional): Maximum tokens to generate
- `logger` (object, optional): Logger instance

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.shell import shell_mode

client = NGPTClient(**load_config())
shell_mode(
    client=client,
    prompt="Find all Python files modified in the last week",
    execute=False  # Set to True to execute the command
)
```

### Text Mode

```python
from ngpt.cli.modes.text import text_mode

def text_mode(
    client,
    prompt,
    temperature=0.7,
    top_p=1.0,
    max_tokens=None,
    no_stream=False,
    web_search=False,
    logger=None
)
```

Executes a text generation operation with the given client.

**Parameters:**
- `client` (NGPTClient): The initialized client for the operation
- `prompt` (str): The user's input message
- `temperature` (float): Temperature setting (0.0-1.0)
- `top_p` (float): Top-p sampling value (0.0-1.0)
- `max_tokens` (int, optional): Maximum tokens to generate
- `no_stream` (bool): Whether to disable streaming
- `web_search` (bool): Whether to enable web search
- `logger` (object, optional): Logger instance

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.text import text_mode

client = NGPTClient(**load_config())
text_mode(
    client=client,
    prompt="Write a summary of quantum computing"
)
```

### Rewrite Mode

```python
from ngpt.cli.modes.rewrite import rewrite_mode

def rewrite_mode(
    client,
    args,
    logger=None
)
```

Executes a text rewriting operation to improve text quality while preserving meaning and tone.

**Parameters:**
- `client` (NGPTClient): The initialized client for the operation
- `args` (namespace): Parsed command-line arguments including:
  - `prompt` (str, optional): Text to rewrite from command line
  - `temperature` (float): Temperature setting (0.0-1.0)
  - `top_p` (float): Top-p sampling value (0.0-1.0)
  - `max_tokens` (int, optional): Maximum tokens to generate
  - `no_stream` (bool): Whether to disable streaming
  - `prettify` (bool): Whether to prettify markdown output
  - `stream_prettify` (bool): Enable real-time markdown rendering
  - `renderer` (str): Markdown renderer to use
  - `web_search` (bool): Whether to enable web search
- `logger` (object, optional): Logger instance

**Input Methods:**
The rewrite mode supports three input methods:
1. Stdin (piped input): Content read from stdin if available
2. Command-line argument: Text provided via args.prompt
3. Multiline editor: If neither stdin nor prompt is available, opens interactive editor

**Features:**
- **Text Quality Improvement**: Fixes grammar, flow, readability while preserving meaning
- **Multiline Editor**: Interactive editor with syntax highlighting for entering text when no input is piped or provided as argument
- **Clipboard Integration**: Offers to copy rewritten text to clipboard with cross-platform support
- **Format Preservation**: Maintains original formatting including code blocks, lists, and markdown

**Example with Stdin:**
```python
import sys
import subprocess
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.rewrite import rewrite_mode
import argparse

client = NGPTClient(**load_config())

# Create args namespace with required parameters
args = argparse.Namespace()
args.prompt = None
args.temperature = 0.7
args.top_p = 1.0
args.max_tokens = None
args.no_stream = False
args.prettify = True
args.stream_prettify = False
args.renderer = 'rich'
args.web_search = False

# Redirect stdin from a string or file
original_stdin = sys.stdin
sys.stdin = open('text_to_rewrite.txt', 'r')

# Call rewrite mode
rewrite_mode(client=client, args=args)

# Restore stdin
sys.stdin = original_stdin
```

**Example with Command-line Argument:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.rewrite import rewrite_mode
import argparse

client = NGPTClient(**load_config())

# Create args namespace with required parameters
args = argparse.Namespace()
args.prompt = "We was hoping you could help with this issue what we are having with the server."
args.temperature = 0.7
args.top_p = 1.0
args.max_tokens = None
args.no_stream = False
args.prettify = True
args.stream_prettify = False
args.renderer = 'rich'
args.web_search = False

rewrite_mode(
    client=client,
    args=args
)
```

**Example with Multiline Editor:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.rewrite import rewrite_mode
import argparse
import sys

client = NGPTClient(**load_config())

# Create args namespace with required parameters
args = argparse.Namespace()
args.prompt = None
args.temperature = 0.7
args.top_p = 1.0
args.max_tokens = None
args.no_stream = False
args.prettify = True
args.stream_prettify = False
args.renderer = 'rich'
args.web_search = False

# Ensure stdin appears to be a TTY
# (This will trigger the multiline editor in a real terminal)
# Note: This is just to illustrate how the condition works
if sys.stdin.isatty():
    print("Multiline editor will open in a real terminal")
    rewrite_mode(client=client, args=args)
else:
    print("This example would open a multiline editor in a real terminal")
```

### Git Commit Message Mode

```python
from ngpt.cli.modes.gitcommsg import gitcommsg_mode

def gitcommsg_mode(client, args, logger=None)
```

Executes a git commit message generation operation to create commit messages based on staged changes in a git repository.

**Parameters:**
- `client` (NGPTClient): The initialized client for the operation
- `args` (namespace): Parsed command-line arguments including:
  - `diff_file` (str, optional): Path to diff file to use instead of git diff --staged
  - `preprompt` (str, optional): Custom system prompt to guide AI behavior (used here as context for gitcommsg)
  - `temperature` (float): Temperature setting (0.0-1.0) 
  - `max_tokens` (int, optional): Maximum tokens to generate
  - `chunk_size` (int): Number of lines per chunk for large diffs
  - `analyses_chunk_size` (int): Number of lines per chunk for recursive analysis chunks
  - `max_msg_lines` (int): Maximum lines in the generated commit message
  - `max_recursion_depth` (int): Maximum recursion depth for message condensing
  - `rec_chunk` (bool): Whether to use recursive chunking for large diffs
  - `web_search` (bool): Whether to enable web search
- `logger` (object, optional): Logger instance

**Features:**
- **Git Diff Analysis**: Analyzes staged git changes to create relevant commit messages
- **Conventional Commit Format**: Follows standard commit message format (type(scope): message)
- **Chunking Strategy**: Handles large diffs by splitting into manageable chunks
- **Recursive Analysis**: Optional analysis of complex changes
- **Context Directives**: Supports filtering and focusing on specific file types/components
- **Technical Detail Extraction**: Extracts function names, line numbers, and specific changes

**Example:**
```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.gitcommsg import gitcommsg_mode
import argparse

client = NGPTClient(**load_config())

# Create args namespace with required parameters
args = argparse.Namespace()
args.diff_file = None  # Use git staged changes
args.preprompt = "type:feat focus on authentication"
args.temperature = 0.4
args.max_tokens = None
args.chunk_size = 200
args.analyses_chunk_size = 200
args.max_msg_lines = 20
args.max_recursion_depth = 3
args.rec_chunk = True
args.web_search = False

gitcommsg_mode(
    client=client,
    args=args
)
```

**Context Directive Examples:**
- `type:feat` - Set commit type to feature
- `focus on authentication` - Focus only on authentication-related changes
- `ignore tests` - Exclude test changes from the commit message
- `javascript` - Focus only on JavaScript file changes

**Output Example:**
```
feat(auth): implement JWT authentication and user session management

- Add generateToken function in auth/jwt.js
- Create validateJWTMiddleware in middleware/auth.js
- Add token refresh endpoint in routes/auth.js
- Update user model to store refresh tokens
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

# Import CLI components
from ngpt.cli.formatters import ColoredHelpFormatter, prettify_markdown, supports_ansi_colors, COLORS
from ngpt.cli.renderers import prettify_streaming_markdown, has_markdown_renderer
from ngpt.cli.main import handle_cli_config

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
        print(f"{COLORS['cyan']}Generating {language} code...{COLORS['reset']}")
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

- [CLI Configuration](cli_config.md) - Documentation for persistent CLI configuration utilities
- [CLI Framework Guide](../usage/cli_framework.md) - Guide to building CLI tools with nGPT components 
- [CLI Component Examples](../examples/cli_components.md) - Practical examples of using CLI components
- [NGPTClient API](client.md) - Reference for the client API used with CLI components