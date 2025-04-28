# nGPT as a CLI Framework

This guide explains how to leverage nGPT's CLI components to build your own command-line applications. nGPT provides a rich set of reusable CLI utilities that can accelerate the development of AI-powered command-line tools.

## Overview

nGPT's CLI module has been modularized into several components that you can incorporate into your own CLI applications:

- **Interactive Chat Interface**: A fully-featured chat UI with history management (`ngpt.cli.interactive`)
- **Markdown Rendering**: Beautiful formatting for markdown with syntax highlighting (`ngpt.cli.renderers`)
- **Real-time Streaming**: Tools for handling streaming content with live updates (`ngpt.cli.ui`)
- **CLI Configuration System**: Robust configuration management (`ngpt.utils.cli_config` and `ngpt.utils.config`)
- **Argument Parsing**: Sophisticated argument parsing and validation (`ngpt.cli.args`)
- **Terminal Utilities**: Helpers for colorized output and terminal formatting (`ngpt.cli.formatters`)
- **Mode-specific functionality**: Specialized code, shell, chat and text mode handlers (`ngpt.cli.modes`)

## Getting Started

To use nGPT as a CLI framework, first install it:

```bash
pip install ngpt
```

This will install nGPT with all required dependencies, including:
- `requests` for API communication
- `rich` for markdown rendering and syntax highlighting
- `prompt_toolkit` for interactive features
- `pyperclip` for clipboard interaction

## Available Components

### Argument Parsing

The `args` module provides utilities for building colorful, sophisticated command-line interfaces:

```python
from ngpt.cli.args import setup_argument_parser, validate_args, validate_markdown_renderer

# Create and configure the parser
parser = setup_argument_parser()
args = parser.parse_args()

# Validate arguments for correctness and compatibility
try:
    args = validate_args(args)
except ValueError as e:
    print(f"Error: {e}")
    sys.exit(1)
    
# Check if markdown renderer is available
has_renderer, args = validate_markdown_renderer(args)
if not has_renderer:
    print("Warning: No markdown renderer available. Using plain text.")
```

The argument parsing module provides these key functions:

- `setup_argument_parser()`: Creates a fully configured argument parser with rich formatting
- `parse_args()`: Parses command-line arguments
- `validate_args(args)`: Validates parsed arguments for correctness and compatibility
- `validate_markdown_renderer(args)`: Checks if markdown rendering is available
- `handle_cli_config_args(args)`: Processes CLI configuration commands

This modular approach makes it easy to create sophisticated CLI tools with consistent behavior.

### Interactive Chat Session

The `interactive_chat_session` function provides a complete interactive chat experience:

```python
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.interactive import interactive_chat_session

# Initialize client
config = load_config()
client = NGPTClient(**config)

# Start interactive session
interactive_chat_session(
    client=client,
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

This function handles:
- User input with prompt toolkit
- Displaying assistant responses
- Conversation history management
- Special commands like `/clear`, `/help`, etc.

#### Error Handling

The interactive chat session includes built-in error handling, but you should wrap the initialization of the client in a try/except block:

```python
try:
    config = load_config()
    client = NGPTClient(**config)
    interactive_chat_session(client=client)
except Exception as e:
    print(f"Error setting up chat session: {e}", file=sys.stderr)
    sys.exit(1)
```

### Markdown Rendering

nGPT provides utilities for rendering markdown with syntax highlighting:

```python
from ngpt.cli.renderers import prettify_markdown, has_markdown_renderer

# Check if renderer is available
if has_markdown_renderer(renderer='rich'):
    # Render markdown
    formatted_text = prettify_markdown(
        "# Hello World\n```python\nprint('Hello')\n```",
        renderer='rich'
    )
    print(formatted_text)
```

Available renderers include:
- `rich`: Uses the Rich library for colorful terminal output
- `glow`: Uses the Glow CLI tool if installed

You can check available renderers:

```python
from ngpt.cli.renderers import show_available_renderers
show_available_renderers()
```

#### Fallback Behavior

The markdown rendering system has built-in fallback logic:

```python
# Auto-select the best available renderer
formatted = prettify_markdown(markdown_text)

# Explicit fallback handling
if has_markdown_renderer(renderer='rich'):
    formatted = prettify_markdown(markdown_text, renderer='rich')
elif has_markdown_renderer(renderer='glow'):
    formatted = prettify_markdown(markdown_text, renderer='glow')
else:
    # No fancy renderer available, just print plain text
    formatted = markdown_text
```

### Real-time Markdown Streaming

For real-time rendering of streaming content, the `prettify_streaming_markdown` function returns an object with an `update_content` method:

```python
from ngpt.cli.renderers import prettify_streaming_markdown
from ngpt import NGPTClient
from ngpt.utils.config import load_config

client = NGPTClient(**load_config())

# Create a streamer object
streamer = prettify_streaming_markdown(
    renderer='rich',
    is_interactive=False,
    header_text="AI Response:"
)

# Use the streamer's update_content method with the client
full_response = ""
for chunk in client.chat("Explain quantum computing with code examples", stream=True):
    full_response += chunk
    # Call the update_content method on the streamer object
    streamer.update_content(full_response)
```

This creates a live-updating display that refreshes as new content arrives. The function returns a class instance with an `update_content` method, not the method itself.

### CLI Configuration Management

nGPT provides a comprehensive configuration management system:

```python
from ngpt.utils.cli_config import (
    load_cli_config,
    set_cli_config_option,
    get_cli_config_option,
    unset_cli_config_option,
    apply_cli_config
)

# Get a configuration value
value = get_cli_config_option('temperature')

# Set a configuration value
set_cli_config_option('temperature', '0.8')

# Apply CLI configuration to args
args = apply_cli_config(args)

# For CLI tools, use the config_manager module
from ngpt.cli.config_manager import handle_cli_config, show_cli_config_help

# Show help
show_cli_config_help()

# List all configuration options
options = handle_cli_config('list')
```

#### Error Handling for Configuration

```python
try:
    value = get_cli_config_option('temperature')
    if value is None:
        # Option not set, use default
        value = 0.7
except Exception as e:
    print(f"Error accessing configuration: {e}", file=sys.stderr)
    # Use fallback value
    value = 0.7
```

### Terminal Formatting Utilities

Colorize your CLI output with terminal utilities:

```python
from ngpt.cli.formatters import ColoredHelpFormatter, supports_ansi_colors, COLORS
import argparse

# Check if terminal supports colors
if supports_ansi_colors():
    # Use colored output
    print(f"{COLORS['green']}Success!{COLORS['reset']}")
else:
    # Fallback to plain text
    print("Success!")

# Create a parser with colorized help
parser = argparse.ArgumentParser(
    description="My custom CLI application",
    formatter_class=ColoredHelpFormatter
)

# Add arguments
parser.add_argument("--option", help="This help text will be formatted with colors")
```

The `ColoredHelpFormatter` automatically adapts to the terminal's capabilities and will fall back to standard formatting if colors aren't supported.

### Using Mode-specific Functionality

nGPT provides specialized mode handlers for different types of operations:

```python
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.modes.chat import chat_mode
from ngpt.cli.modes.code import code_mode
from ngpt.cli.modes.shell import shell_mode
from ngpt.cli.modes.text import text_mode
from ngpt.cli.modes.rewrite import rewrite_mode

# Initialize the client
client = NGPTClient(**load_config())

# Chat mode - general conversation
chat_mode(client, prompt="Tell me about quantum computing", 
          prettify=True, renderer="rich")

# Code mode - generate code in specific language
code_mode(client, prompt="Create a binary search tree", 
          language="python", stream=True)
          
# Shell mode - generate and execute shell commands
shell_mode(client, prompt="Find all PNG files in current directory")

# Text mode - handle multiline text input
text_mode(client, prettify=True)

# Rewrite mode - improve text quality while preserving meaning and tone
rewrite_mode(client, text="We was hoping you could help with this issue what we are having.", 
             prettify=True, stream=True)

# Git commit message mode - generate conventional commit messages from git diff
from ngpt.cli.modes.gitcommsg import gitcommsg_mode

# Generate commit message from staged changes
gitcommsg_mode(client, args)

# With context for focusing on specific changes
from argparse import Namespace
args = Namespace(
    diff=None,  # Use staged changes
    preprompt="focus on UI components, type:feat",
    log=None,
    chunk_size=200,
    rec_chunk=True,
    max_msg_lines=20
)
gitcommsg_mode(client, args)
```

Each mode handler encapsulates the specialized behavior for that particular mode of operation.

## Complex Example: Building a Custom AI CLI

Here's a complete example of building a specialized AI CLI tool using nGPT components:

```python
#!/usr/bin/env python
import argparse
import sys
from pathlib import Path
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.formatters import ColoredHelpFormatter, COLORS
from ngpt.cli.interactive import interactive_chat_session
from ngpt.cli.renderers import prettify_markdown, prettify_streaming_markdown, has_markdown_renderer

def main():
    # Set up argument parser with colorized help
    parser = argparse.ArgumentParser(
        description="CodeAI - Generate and explain code using AI",
        formatter_class=ColoredHelpFormatter
    )
    
    # Add arguments
    parser.add_argument("prompt", nargs="?", help="Code description or question")
    parser.add_argument("-l", "--language", default="python", help="Programming language")
    parser.add_argument("-i", "--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("-e", "--explain", action="store_true", help="Explain existing code")
    parser.add_argument("-f", "--file", type=str, help="Read from or write to file")
    parser.add_argument("-p", "--prettify", action="store_true", help="Prettify output")
    
    args = parser.parse_args()
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"{COLORS['yellow']}Error initializing AI client: {e}{COLORS['reset']}", 
              file=sys.stderr)
        sys.exit(1)
    
    # Interactive mode
    if args.interactive:
        print(f"{COLORS['green']}CodeAI Interactive Mode - Type /help for commands{COLORS['reset']}")
        preprompt = f"You are an expert {args.language} developer. Provide concise, clear code examples."
        interactive_chat_session(
            client=client,
            preprompt=preprompt,
            prettify=args.prettify,
            renderer='rich' if has_markdown_renderer(renderer='rich') else 'auto'
        )
        return
    
    # Explain mode - read code from file
    if args.explain and args.file:
        try:
            with open(args.file, 'r') as f:
                code = f.read()
            
            prompt = f"Explain this {args.language} code:\n\n{code}"
            
            if args.prettify and has_markdown_renderer():
                print(f"{COLORS['cyan']}Analyzing code...{COLORS['reset']}")
                streamer = prettify_streaming_markdown(renderer='rich')
                full_response = ""
                for chunk in client.chat(prompt, stream=True):
                    full_response += chunk
                    streamer.update_content(full_response)
            else:
                print(f"{COLORS['cyan']}Analyzing code...{COLORS['reset']}")
                response = client.chat(prompt)
                print(f"\n{COLORS['green']}Explanation:{COLORS['reset']}")
                print(response)
        except Exception as e:
            print(f"{COLORS['yellow']}Error: {e}{COLORS['reset']}", file=sys.stderr)
            sys.exit(1)
        return
    
    # Generate code mode
    if args.prompt:
        preprompt = f"You are an expert {args.language} developer. Generate clean, well-documented {args.language} code."
        
        if args.file:
            # Generate code and save to file
            print(f"{COLORS['cyan']}Generating {args.language} code...{COLORS['reset']}")
            code = client.generate_code(
                args.prompt,
                language=args.language
            )
            
            try:
                with open(args.file, 'w') as f:
                    f.write(code)
                print(f"{COLORS['green']}Code written to {args.file}{COLORS['reset']}")
            except Exception as e:
                print(f"{COLORS['yellow']}Error writing to file: {e}{COLORS['reset']}", 
                      file=sys.stderr)
                sys.exit(1)
        else:
            # Generate and display code
            print(f"{COLORS['cyan']}Generating {args.language} code...{COLORS['reset']}\n")
            
            if args.prettify and has_markdown_renderer():
                markdown = f"```{args.language}\n"
                
                # Stream and capture code
                code = ""
                for chunk in client.generate_code(
                    args.prompt,
                    language=args.language,
                    stream=True
                ):
                    code += chunk
                
                markdown += code + "\n```"
                print(prettify_markdown(markdown))
            else:
                # Simple streaming output
                for chunk in client.generate_code(
                    args.prompt,
                    language=args.language,
                    stream=True
                ):
                    print(chunk, end="", flush=True)
                print()  # Final newline
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

## Working with Different Renderer Options

nGPT supports multiple markdown renderers:

### Rich Renderer

Using the Rich library for terminal output:

```python
from ngpt.cli.renderers import prettify_markdown

# Rich renderer with custom styling
formatted = prettify_markdown(markdown_text, renderer='rich')
print(formatted)
```

### Glow Renderer

If you have the Glow CLI tool installed:

```python
from ngpt.cli.renderers import prettify_markdown, has_glow_installed

if has_glow_installed():
    formatted = prettify_markdown(markdown_text, renderer='glow')
    print(formatted)
```

### Auto Selection

Let nGPT choose the best available renderer:

```python
from ngpt.cli.renderers import prettify_markdown

formatted = prettify_markdown(markdown_text, renderer='auto')
print(formatted)
```

## Detecting Terminal Capabilities

nGPT provides utilities to detect terminal capabilities:

```python
from ngpt.cli.formatters import supports_ansi_colors

if supports_ansi_colors():
    # Use colored output
    print("\033[1;32mSuccess!\033[0m")
else:
    # Fallback to plain text
    print("Success!")
```

## Text Input Components

nGPT includes utilities for handling user input:

### Prompt Input

For simple single-line input:

```python
from prompt_toolkit import prompt

user_input = prompt("Enter your query: ")
```

### Multiline Input

When nGPT is installed with full dependencies, it provides components for rich multiline editing in the interactive session. These components are used internally by the `interactive_chat_session` function.

## Advanced Usage: Creating a Web Search Tool

This example creates a specialized web search tool using nGPT components:

```python
#!/usr/bin/env python
import argparse
import sys
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.renderers import has_markdown_renderer, prettify_streaming_markdown
from ngpt.cli.formatters import COLORS

def main():
    # Set up colorized argument parser
    parser = argparse.ArgumentParser(
        description="AI-powered web search tool"
    )
    
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("-p", "--prettify", action="store_true", help="Prettify output")
    
    args = parser.parse_args()
    
    if not args.query:
        parser.print_help()
        return
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"{COLORS['yellow']}Error: {e}{COLORS['reset']}", file=sys.stderr)
        sys.exit(1)
    
    # System prompt that encourages citations
    system_prompt = """You are a web research assistant. 
    For each query, search the internet and provide:
    1. A concise summary of the most important information
    2. Key facts with references to their sources
    3. Direct quotes should be in blockquotes
    Use markdown formatting for better readability."""
    
    print(f"{COLORS['cyan']}Searching for: {args.query}{COLORS['reset']}\n")
    
    # Create messages with system prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.query}
    ]
    
    if args.prettify and has_markdown_renderer():
        # Stream with real-time markdown rendering
        streamer = prettify_streaming_markdown(
            renderer='rich',
            header_text="Search Results"
        )
        
        full_response = ""
        for chunk in client.chat(
            "",
            messages=messages,
            web_search=True,
            stream=True
        ):
            full_response += chunk
            streamer.update_content(full_response)
    else:
        # Regular streaming output
        print(f"{COLORS['green']}Results:{COLORS['reset']}")
        for chunk in client.chat(
            "",
            messages=messages,
            web_search=True,
            stream=True
        ):
            print(chunk, end="", flush=True)
        print()  # Final newline

if __name__ == "__main__":
    main()
```

## Logging and Debugging

nGPT provides comprehensive logging capabilities through the `utils.log` module:

```python
import logging
from ngpt.utils.log import create_logger

# Set up logging
logger = create_logger("/path/to/log.txt")
logger.open()

# Log events
logger.log_system("System initialization")
logger.log_user("User input: Hello")
logger.log_assistant("Assistant response: Hi there")

# Close logger when done
logger.close()
```

You can also use Python's standard logging module:

```python
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use nGPT components with logging available
from ngpt.cli.renderers import prettify_markdown
try:
    result = prettify_markdown(text)
except Exception as e:
    logging.error(f"Failed to render markdown: {e}")
    result = text  # Fallback to plain text
```

## Conclusion

nGPT's CLI components provide a rich toolkit for building your own AI-powered command-line applications. By leveraging these pre-built components, you can rapidly develop sophisticated CLI tools with features like:

- Interactive chat interfaces
- Beautiful markdown rendering
- Real-time streaming with live updates
- Configuration management
- Colorized terminal output

For more examples, see the [CLI Component Examples](../examples/cli_components.md) section. 

## Error Handling Best Practices

When using nGPT CLI components, follow these error handling best practices:

1. **Check for Dependencies**:
   ```python
   try:
       import rich
   except ImportError:
       print("Warning: Rich library not found. Install with: pip install rich", file=sys.stderr)
       # Fallback behavior
   ```

2. **Handle API Errors**:
   ```python
   try:
       response = client.chat(prompt)
   except Exception as e:
       print(f"Error communicating with AI service: {e}", file=sys.stderr)
       sys.exit(1)
   ```

3. **Graceful Keyboard Interrupts**:
   ```python
   try:
       # Your code here
   except KeyboardInterrupt:
       print("Operation cancelled by user.")
       sys.exit(0)
   ```

4. **Verify Rendering Capabilities**:
   ```python
   if has_markdown_renderer(renderer='rich'):
       # Use rich rendering
   else:
       # Fallback to plain text
   ```

To learn more about the available components and their capabilities, see the [CLI Framework Guide](../usage/cli_framework.md) and the [API Reference](../api/cli.md). 

## Git Commit Message Generation

The `gitcommsg_mode` provides AI-powered generation of conventional commit messages from git diffs:

```python
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.modes.gitcommsg import gitcommsg_mode
from argparse import Namespace

# Initialize client
client = NGPTClient(**load_config())

# Create args with desired options
args = Namespace(
    diff=None,  # Use staged git changes
    preprompt="focus on authentication",
    log="commit_generation.log",  # Optional logging
    chunk_size=200,  # Lines per chunk for large diffs
    rec_chunk=True,  # Enable recursive chunking
    max_msg_lines=20  # Maximum lines in final message
)

# Generate commit message
gitcommsg_mode(client, args)
```

### Key Features

- **Staged Changes Analysis**: Analyzes git staged changes by default
- **External Diff Files**: Can process diff files with `args.diff="path/to/diff.txt"`
- **Context Directives**: Supports focusing on specific changes with `--preprompt`
- **Diff Chunking**: Handles large diffs by processing in chunks
- **Clipboard Integration**: Automatically copies result to clipboard when available

### Context Directives

The `--preprompt` option supports several helpful directives:

```python
# Focus on specific file types
args.preprompt = "javascript"  # Focus on JS files

# Specify commit type
args.preprompt = "type:feat"  # Force "feat:" prefix

# Focus on specific components
args.preprompt = "focus on authentication"

# Exclude certain changes
args.preprompt = "exclude tests"

# Combine directives
args.preprompt = "type:fix focus on API exclude logging"
```

### Processing Large Diffs

For large repositories with extensive changes:

```python
args = Namespace(
    diff=None,
    chunk_size=200,  # Process 200 lines at a time
    rec_chunk=True,  # Enable recursive processing
    max_msg_lines=20,  # Condense final message if needed
    analyses_chunk_size=300  # Size for recursive analysis chunks
)
gitcommsg_mode(client, args)
```

### Detailed Logging

Enable detailed logging for debugging or auditing:

```python
import tempfile
log_file = f"{tempfile.gettempdir()}/gitcommsg_{int(time.time())}.log"
args.log = log_file
```

The log includes prompts, responses, and all processing steps for complete transparency. 