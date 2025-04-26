# nGPT

[![PyPI version](https://img.shields.io/pypi/v/ngpt.svg)](https://pypi.org/project/ngpt/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/ngpt.svg)](https://pypi.org/project/ngpt/)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://nazdridoy.github.io/ngpt/)

A lightweight Python CLI and library for interacting with OpenAI-compatible APIs, supporting both official and self-hosted LLM endpoints.

![2025-04-23_16-18-01](https://github.com/user-attachments/assets/b8e58926-5165-4352-b48b-9f4a982da86e)


## Table of Contents
- [Quick Start](#quick-start)
- [Features](#features)
- [Documentation](#documentation)
- [Installation](#installation)
- [Usage](#usage)
  - [Documentation](https://nazdridoy.github.io/ngpt/)
  - [CLI Tool](#as-a-cli-tool)
  - [Python Library](#as-a-library)
  - [CLI Framework](#as-a-cli-framework)
- [Configuration](#configuration)
  - [Command Line Options](#command-line-options)
  - [CLI Configuration](#cli-configuration)
  - [Interactive Configuration](#interactive-configuration)
  - [Configuration File](#configuration-file)
  - [Configuration Priority](#configuration-priority)
- [Contributing](#contributing)
- [License](#license)

## Quick Start

```bash
# Install with pip
pip install ngpt

# Or install with uv (faster)
uv pip install ngpt

# Or install globally as a CLI tool (recommended)
uv tool install ngpt

# Chat with default settings
ngpt "Tell me about quantum computing"

# Alternatively, run as a Python module
python -m ngpt "Tell me about quantum computing"

# Start an interactive chat session with conversation memory
ngpt -i

# Return response without streaming
ngpt --no-stream "Tell me about quantum computing"

# Generate code
ngpt --code "function to calculate the Fibonacci sequence"

# Generate code with syntax highlighting
ngpt --code --prettify "function to calculate the Fibonacci sequence"

# Generate code with real-time syntax highlighting
ngpt --code --stream-prettify "function to calculate the Fibonacci sequence"

# Generate and execute shell commands
ngpt --shell "list all files in the current directory"

# Read from stdin and use the content in your prompt
echo "What is this text about?" | ngpt --stdin "Analyze the following text: {}"

# Rewrite text to improve quality while preserving tone and meaning
echo "your text" | ngpt --rewrite

# Rewrite text from a command-line argument
ngpt --rewrite "your text to rewrite"

# Rewrite text from a file
cat file.txt | ngpt --rewrite

# Generate AI-powered git commit messages for staged changes
ngpt --gitcommsg

# Generate commit message with context
ngpt --gitcommsg -m "type:feat"

# Process large diffs in chunks with recursive analysis
ngpt --gitcommsg -r

# Process a diff file instead of staged changes
ngpt --gitcommsg --diff /path/to/changes.diff

# Generate a commit message with logging for debugging
ngpt --gitcommsg --log commit_log.txt

# Use interactive multiline editor to enter text to rewrite
ngpt --rewrite

# Display markdown responses with beautiful formatting
ngpt --prettify "Explain markdown syntax with examples"

# Display markdown responses with real-time formatting
ngpt --stream-prettify "Explain markdown syntax with examples"

# Use a specific markdown renderer
ngpt --prettify --renderer=rich "Create a markdown table"

# Use multiline editor for complex prompts
ngpt --text

# Use custom system prompt
ngpt --preprompt "You are a Linux expert" "How do I find large files?"

# Log your conversation to a file
ngpt --interactive --log conversation.log

# Create a temporary log file automatically
ngpt --log "Tell me about quantum computing"

# Process text from stdin using the {} placeholder
cat README.md | ngpt --stdin "Summarize this document: {}"

# Use different model providers by specifying the provider name
ngpt --provider Groq "Explain quantum computing"

# Compare outputs from different providers
ngpt --provider OpenAI "Explain quantum physics" > openai_response.txt
ngpt --provider Ollama "Explain quantum physics" > ollama_response.txt
```

For more examples and detailed usage, visit the [CLI Usage Guide](https://nazdridoy.github.io/ngpt/usage/cli_usage.html).

## Features

- ✅ **Versatile**: Use as a CLI tool, Python library, or CLI framework for building custom tools
- 🪶 **Lightweight**: Minimal dependencies with everything you need included
- 🔄 **API Flexibility**: Works with OpenAI, Ollama, Groq, Claude, and any compatible endpoint
- 💬 **Interactive Chat**: Continuous conversation with memory in modern UI
- 📊 **Streaming Responses**: Real-time output for better user experience
- 🔍 **Web Search**: Integrated with compatible API endpoints
- 📥 **Stdin Processing**: Process piped content by using `{}` placeholder in prompts
- 🎨 **Markdown Rendering**: Beautiful formatting of markdown and code with syntax highlighting
- ⚡ **Real-time Markdown**: Stream responses with live updating syntax highlighting and formatting
- ⚙️ **Multiple Configurations**: Cross-platform config system supporting different profiles
- 💻 **Shell Command Generation**: OS-aware command execution
- 🧠 **Text Rewriting**: Improve text quality while maintaining original tone and meaning
- 🧩 **Clean Code Generation**: Output code without markdown or explanations
- 📝 **Rich Multiline Editor**: Interactive multiline text input with syntax highlighting and intuitive controls
- 📑 **Git Commit Messages**: AI-powered generation of conventional, detailed commit messages from git diffs
- 🎭 **System Prompts**: Customize model behavior with custom system prompts
- 📃 **Conversation Logging**: Save your conversations to text files for later reference
- 🧰 **CLI Components**: Reusable components for building custom AI-powered command-line tools
- 🔌 **Modular Architecture**: Well-structured codebase with clean separation of concerns
- 🔄 **Provider Switching**: Easily switch between different LLM providers with a single parameter
- 🚀 **Performance Optimized**: Fast response times and minimal resource usage

See the [Feature Overview](https://nazdridoy.github.io/ngpt/overview.html) for more details.

## Documentation

Comprehensive documentation, including API reference, usage guides, and examples, is available at:

**[https://nazdridoy.github.io/ngpt/](https://nazdridoy.github.io/ngpt/)**

Key documentation sections:
- [Installation Guide](https://nazdridoy.github.io/ngpt/installation.html)
- [CLI Usage Guide](https://nazdridoy.github.io/ngpt/usage/cli_usage.html)
- [Library Usage Guide](https://nazdridoy.github.io/ngpt/usage/library_usage.html)
- [CLI Framework Guide](https://nazdridoy.github.io/ngpt/usage/cli_framework.html)
- [Configuration Guide](https://nazdridoy.github.io/ngpt/configuration.html)
- [Examples & Tutorials](https://nazdridoy.github.io/ngpt/examples/basic.html)

## Installation

```bash
# Installation with pip
pip install ngpt

# Or install with uv (faster installation)
uv pip install ngpt

# Or install globally as a CLI tool (recommended for command-line usage)
uv tool install ngpt
```

Requires Python 3.8 or newer.

For detailed installation instructions, see the [Installation Guide](https://nazdridoy.github.io/ngpt/installation.html).

## Usage

### As a CLI Tool

```bash
# Basic chat (default mode)
ngpt "Hello, how are you?"

# Interactive chat session with conversation history
ngpt -i

# Log conversation to a file
ngpt --interactive --log conversation.log

# Use custom system prompt to guide AI behavior
ngpt --preprompt "You are a Python programming tutor" "Explain decorators"

# Show version information
ngpt -v

# Show active configuration
ngpt --show-config

# Show all configurations
ngpt --show-config --all

# List available models for the active configuration
ngpt --list-models

# List models for a specific configuration
ngpt --list-models --config-index 1

# With custom options
ngpt --api-key your-key --base-url http://your-endpoint --model your-model "Hello"

# Enable web search (if your API endpoint supports it)
ngpt --web-search "What's the latest news about AI?"

# Generate and execute shell commands (using -s or --shell flag)
# OS-aware: generates appropriate commands for Windows, macOS, or Linux
ngpt -s "list all files in current directory"
# On Windows generates: dir
# On Linux/macOS generates: ls -la

# Generate clean code (using -c or --code flag)
# Returns only code without markdown formatting or explanations
ngpt -c "create a python function that calculates fibonacci numbers"

# Use multiline text editor for complex prompts (using -t or --text flag)
# Opens an interactive editor with syntax highlighting and intuitive controls
ngpt -t
```

For more CLI examples and detailed usage information, see the [CLI Usage Guide](https://nazdridoy.github.io/ngpt/usage/cli_usage.html).

### As a Library

```python
from ngpt import NGPTClient
from ngpt.utils.config import load_config

# Load the first configuration (index 0) from config file
config = load_config(config_index=0)

# Initialize the client with config
client = NGPTClient(**config)

# Or initialize with custom parameters
client = NGPTClient(
    api_key="your-key",
    base_url="http://your-endpoint",
    provider="openai",
    model="o3-mini"
)

# Chat
response = client.chat("Hello, how are you?")

# Chat with web search (if your API endpoint supports it)
response = client.chat("What's the latest news about AI?", web_search=True)

# Generate shell command
command = client.generate_shell_command("list all files")

# Generate code
code = client.generate_code("create a python function that calculates fibonacci numbers")
```

For more library examples and advanced usage, see the [Library Usage Guide](https://nazdridoy.github.io/ngpt/usage/library_usage.html).

#### Advanced Library Usage

```python
# Stream responses
for chunk in client.chat("Write a poem about Python", stream=True):
    print(chunk, end="", flush=True)

# Customize system prompt
response = client.chat(
    "Explain quantum computing",
    system_prompt="You are a quantum physics professor. Explain complex concepts simply."
)

# OS-aware shell commands
# Automatically generates appropriate commands for the current OS
command = client.generate_shell_command("find large files")
import subprocess
result = subprocess.run(command, shell=True, capture_output=True, text=True)
print(result.stdout)

# Clean code generation
# Returns only code without markdown or explanations
code = client.generate_code("function that converts Celsius to Fahrenheit")
print(code)

# Compare responses from different providers
openai_config = load_config(config_index=0)  # OpenAI
groq_config = load_config(config_index=1)    # Groq

openai_client = NGPTClient(**openai_config)
groq_client = NGPTClient(**groq_config)

openai_response = openai_client.chat("Explain quantum computing")
groq_response = groq_client.chat("Explain quantum computing")
```

For advanced usage patterns and integrations, check out the [Advanced Examples](https://nazdridoy.github.io/ngpt/examples/advanced.html).

### As a CLI Framework

nGPT can also be used as a framework to build your own AI-powered command-line tools. You can leverage nGPT's pre-built CLI components to quickly develop sophisticated CLI applications.

```python
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.interactive import interactive_chat_session
from ngpt.cli.renderers import prettify_markdown
from ngpt.cli.args import setup_argument_parser
import sys

# Create a custom CLI tool with colorized help
parser = setup_argument_parser()
parser.description = "Specialized Code Assistant"
parser.add_argument("prompt", nargs="?", help="Code description")
parser.add_argument("--language", "-l", default="python", help="Programming language")
parser.add_argument("--interactive", "-i", action="store_true", help="Start interactive mode")
args = parser.parse_args()

# Initialize client
client = NGPTClient(**load_config())

# Use interactive session for conversation
if args.interactive:
    system_prompt = f"You are an expert {args.language} developer. Provide clear, detailed answers."
    interactive_chat_session(client=client, preprompt=system_prompt, prettify=True)
elif args.prompt:
    # Generate and prettify code
    code = client.generate_code(args.prompt, language=args.language)
    print(prettify_markdown(f"```{args.language}\n{code}\n```"))
else:
    parser.print_help()
    sys.exit(1)
```

This allows you to build specialized AI tools like:
- Code generators for specific languages or frameworks
- Domain-specific assistants (SQL, legal, finance, etc.)
- Documentation generators
- Translation tools
- And much more

For detailed information about building CLI tools with nGPT, see the [CLI Framework Guide](https://nazdridoy.github.io/ngpt/usage/cli_framework.html) and explore the [CLI Component Examples](https://nazdridoy.github.io/ngpt/examples/cli_components.html).

## Configuration

### Command Line Options

You can configure nGPT using the following options:

#### Mode Options (Mutually Exclusive)

| Option | Description |
|--------|-------------|
| `-i, --interactive` | Start an interactive chat session with conversation memory and special commands |
| `-s, --shell` | Generate and execute shell commands appropriate for your operating system |
| `-c, --code` | Generate clean code without markdown formatting or explanations |
| `-t, --text` | Open interactive multiline editor for complex prompts with syntax highlighting |
| `--stdin` | Read from stdin and use content with prompt. Use {} in prompt as placeholder for stdin content |
| `--rewrite` | Rewrite text to improve quality while preserving original tone and meaning |
| `--gitcommsg` | Generate AI-powered git commit messages from staged changes or diff files |

#### Global Options

| Option | Description |
|--------|-------------|
| `--api-key KEY` | API key for the service |
| `--base-url URL` | Base URL for the API |
| `--model MODEL` | Model to use |
| `--web-search` | Enable web search capability (if your API endpoint supports it) |
| `--temperature VALUE` | Set temperature (controls randomness, default: 0.7) |
| `--top_p VALUE` | Set top_p (controls diversity, default: 1.0) |
| `--max_tokens NUMBER` | Set maximum response length in tokens |
| `--preprompt TEXT` | Set custom system prompt to control AI behavior |
| `--language LANG` | Programming language to generate code in (for code mode, default: python) |
| `--no-stream` | Return the whole response without streaming |
| `--prettify` | Render markdown responses and code with syntax highlighting and formatting |
| `--stream-prettify` | Enable streaming with markdown rendering (automatically uses Rich renderer) |
| `--renderer {auto,rich,glow}` | Select which markdown renderer to use with --prettify (default: auto) |
| `--log [FILE]` | Set filepath to log conversation to, or create a temporary log file if no path provided |

#### Configuration Options

| Option | Description |
|--------|-------------|
| `--config [PATH]` | Path to a custom config file or, if no value provided, enter interactive configuration mode |
| `--config-index INDEX` | Index of the configuration to use or edit (default: 0) |
| `--provider NAME` | Provider name to identify the configuration to use |
| `--remove` | Remove the configuration at the specified index (requires --config and --config-index or --provider) |
| `--show-config` | Show the current configuration(s) and exit |
| `--all` | Show details for all configurations (requires --show-config) |
| `--list-models` | List all available models for the current configuration and exit |
| `--list-renderers` | Show available markdown renderers for use with --prettify |
| `--cli-config [COMMAND]` | Manage CLI configuration (set, get, unset, list, help) |
| `-v, --version` | Show version information and exit |

For a complete reference of all available options, see the [CLI Usage Guide](https://nazdridoy.github.io/ngpt/usage/cli_usage.html).

### CLI Configuration

NGPT offers a CLI configuration system that allows you to set default values for command-line options:

```bash
# Set default options
ngpt --cli-config set language typescript
ngpt --cli-config set temperature 0.9
ngpt --cli-config set prettify true

# View current settings
ngpt --cli-config get

# Get a specific setting
ngpt --cli-config get language

# Remove a setting
ngpt --cli-config unset prettify

# List all available options
ngpt --cli-config list

# Show help information
ngpt --cli-config help
```

Key features of CLI configuration:
- **Context-Aware**: Settings are applied based on the current command mode (e.g., `language` only applies in code generation mode `-c`).
- **Priority**: When determining option values, NGPT uses the following priority order (highest to lowest):
  1. Command-line arguments
  2. Environment variables
  3. CLI configuration (ngpt-cli.conf)
  4. Main configuration file (ngpt.conf)
  5. Default values
- **Mutual Exclusivity**: For options like `no-stream`, `prettify`, and `stream-prettify`, setting one to `True` automatically sets the others to `False` in the configuration file, ensuring consistency.
- **Smart Selection**: The `provider` setting is used to select which configuration profile to use, offering a persistent way to select your preferred API.

Available options include:
- General options (all modes): `provider`, `temperature`, `top_p`, `max_tokens`, `preprompt`, `renderer`, `config-index`, `web-search`
- Mode-specific options: `language` (code mode only), `log` (interactive and text modes)
- Mutually exclusive options: `no-stream`, `prettify`, `stream-prettify`

#### Practical Examples

```bash
# Set Gemini as your default provider
ngpt --cli-config set provider Gemini
# Now you can run commands without specifying --provider
ngpt "Explain quantum computing"

# Configure code generation for TypeScript
ngpt --cli-config set language typescript
# Now in code mode, TypeScript will be used by default
ngpt -c "Write a function to sort an array"

# Set a higher temperature for more creative responses
ngpt --cli-config set temperature 0.9
```

The CLI configuration is stored in:
- Linux: `~/.config/ngpt/ngpt-cli.conf`
- macOS: `~/Library/Application Support/ngpt/ngpt-cli.conf`
- Windows: `%APPDATA%\ngpt\ngpt-cli.conf`

For more details, see the [CLI Configuration Guide](https://nazdridoy.github.io/ngpt/usage/cli_config.html).

### Interactive Configuration

The `--config` option without arguments enters interactive configuration mode, allowing you to add or edit configurations:

```bash
# Add a new configuration
ngpt --config

# Edit an existing configuration at index 1
ngpt --config --config-index 1

# Edit an existing configuration by provider name
ngpt --config --provider Gemini

# Remove a configuration at index 2
ngpt --config --remove --config-index 2

# Remove a configuration by provider name
ngpt --config --remove --provider Gemini

# Use a specific configuration by provider name
ngpt --provider OpenAI "Tell me about quantum computing"
```

In interactive mode:
- When editing an existing configuration, press Enter to keep the current values
- When creating a new configuration, press Enter to use default values
- For security, your API key is not displayed when editing configurations
- When removing a configuration, you'll be asked to confirm before deletion

For more details on configuring nGPT, see the [Configuration Guide](https://nazdridoy.github.io/ngpt/configuration.html).

### Configuration File

nGPT uses a configuration file stored in the standard user config directory for your operating system:

- **Linux**: `~/.config/ngpt/ngpt.conf` or `$XDG_CONFIG_HOME/ngpt/ngpt.conf`
- **macOS**: `~/Library/Application Support/ngpt/ngpt.conf`
- **Windows**: `%APPDATA%\ngpt\ngpt.conf`

The configuration file uses a JSON list format, allowing you to store multiple configurations. You can select which configuration to use with the `--config-index` argument (or by default, index 0 is used).

#### Multiple Configurations Example (`ngpt.conf`)
```json
[
  {
    "api_key": "your-openai-api-key-here",
    "base_url": "https://api.openai.com/v1/",
    "provider": "OpenAI",
    "model": "gpt-4o"
  },
  {
    "api_key": "your-groq-api-key-here",
    "base_url": "https://api.groq.com/openai/v1/",
    "provider": "Groq",
    "model": "llama3-70b-8192"
  },
  {
    "api_key": "your-ollama-key-if-needed",
    "base_url": "http://localhost:11434/v1/",
    "provider": "Ollama-Local",
    "model": "llama3"
  }
]
```

For details on the configuration file format and structure, see the [Configuration Guide](https://nazdridoy.github.io/ngpt/configuration.html).

### Configuration Priority

nGPT determines configuration values in the following order (highest priority first):

1. Command line arguments (`--api-key`, `--base-url`, `--model`, etc.)
2. Environment variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`)
3. CLI configuration file (`ngpt-cli.conf`, managed with `--cli-config`)
4. Main configuration file `ngpt.conf` or `custom-config-file`
5. Default values

## Contributing

We welcome contributions to nGPT! Whether it's bug fixes, feature additions, or documentation improvements, your help is appreciated.

To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Commit with clear messages following conventional commit guidelines
5. Push to your fork and submit a pull request

Please check the [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidelines on code style, pull request process, and development setup.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.