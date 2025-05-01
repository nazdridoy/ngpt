# CLI Usage Guide

This guide provides comprehensive documentation on how to use nGPT as a command-line interface (CLI) tool.

## Basic Usage

The most basic way to use nGPT from the command line is to provide a prompt:

```bash
ngpt "Tell me about quantum computing"
```

This will send your prompt to the configured AI model and stream the response to your terminal.

## Command Overview

```bash
ngpt [OPTIONS] [PROMPT]
```

Where:
- `[OPTIONS]` are command-line flags that modify behavior
- `[PROMPT]` is your text prompt to the AI (optional with certain flags)

## All CLI Options

Below is a comprehensive list of all available command-line options, organized by category:

### Core Mode Options

| Option | Description |
|--------|-------------|
| `-i, --interactive` | Start an interactive chat session with conversation memory and special commands |
| `-s, --shell` | Generate and execute shell commands appropriate for your operating system |
| `-c, --code` | Generate clean code without markdown formatting or explanations |
| `-t, --text` | Open interactive multiline editor for complex prompts with syntax highlighting |
| `-p, --pipe` | Read from stdin and use content in your prompt with {} placeholder |
| `-r, --rewrite` | Rewrite text to improve quality while preserving original tone and meaning |
| `-g, --gitcommsg` | Generate AI-powered git commit messages for staged changes or from a diff file |

### Configuration Management

| Option | Description |
|--------|-------------|
| `--api-key <key>` | API key for the service (overrides stored configuration) |
| `--base-url <url>` | Base URL for the API endpoint (overrides stored configuration) |
| `--model <n>` | Model to use for this request (overrides stored configuration) |
| `--config <path>` | Path to a custom configuration file or, when used without a value, enters interactive configuration mode |
| `--config-index <index>` | Index of the configuration to use (default: 0) |
| `--provider <n>` | Provider name to identify the configuration to use (alternative to --config-index) |
| `--show-config` | Show current configuration details and exit |
| `--all` | Used with `--show-config` to display all configurations instead of just the active one |
| `--list-models` | List all available models for the selected configuration (can be combined with --config-index) |
| `--remove` | Remove the configuration at the specified index (requires --config and --config-index or --provider) |
| `--cli-config <cmd>` | Manage persistent CLI option defaults with commands: `set`, `get`, `unset`, `list`, `help` |

### Response Formatting

| Option | Description |
|--------|-------------|
| `--no-stream` | Return the whole response without streaming (useful for scripts) |
| `--prettify` | Render markdown responses and code with syntax highlighting (disables streaming) |
| `--stream-prettify` | Enable real-time markdown rendering with syntax highlighting while streaming (uses Rich) |
| `--renderer <n>` | Select which markdown renderer to use with --prettify (auto, rich, or glow) |
| `--list-renderers` | Show available markdown renderers for use with --prettify |

### Generation Control

| Option | Description |
|--------|-------------|
| `--preprompt <text>` | Set custom system prompt to control AI behavior and guide responses |
| `--web-search` | Enable web search capability if supported by your API endpoint |
| `--temperature <value>` | Set temperature parameter controlling randomness (0.0-2.0, default: 0.7) |
| `--top_p <value>` | Set top_p parameter controlling diversity (0.0-1.0, default: 1.0) |
| `--max_tokens <number>` | Set maximum response length in tokens |
| `--language <lang>` | Programming language to generate code in when using -c/--code (default: python) |

### Utility Options

| Option | Description |
|--------|-------------|
| `--log [file]` | Enable logging: use `--log` to create a temporary log file, or `--log PATH` for a specific location |
| `-v, --version` | Show version information and exit |
| `-h, --help` | Show help message and exit |

## Mode Details

### Basic Chat

Send a simple prompt and get a response:

```bash
ngpt "What is the capital of France?"
```

The response will be streamed in real-time to your terminal.

### Interactive Chat

Start an interactive chat session with conversation memory:

```bash
ngpt -i
```

This opens a continuous chat session where the AI remembers previous exchanges. In interactive mode:

- Type your messages and press Enter to send
- Use arrow keys to navigate message history
- Press Ctrl+C to exit the session

#### Conversation Logging

You can log your conversation in several ways:

```bash
# Log to a specific file
ngpt -i --log conversation.log

# Automatically create a temporary log file
ngpt -i --log
```

When using `--log` without a path, nGPT creates a temporary log file with a timestamp in the name:
- On Linux/macOS: `/tmp/ngpt-YYYYMMDD-HHMMSS.log`
- On Windows: `%TEMP%\ngpt-YYYYMMDD-HHMMSS.log`

The log file contains timestamps, roles, and the full content of all messages exchanged, making it easy to reference conversations later.

Logging works in all modes (not just interactive):

```bash
# Log in standard chat mode
ngpt --log "Tell me about quantum computing"

# Log in code generation mode 
ngpt --code --log "function to calculate prime numbers"

# Log in shell command mode
ngpt --shell --log "find large files in current directory"
```

#### Combining with Other Options

Interactive mode can be combined with other options for enhanced functionality:

```bash
# Interactive mode with custom system prompt
ngpt -i --preprompt "You are a Python programming tutor"

# Interactive mode with web search
ngpt -i --web-search

# Interactive mode with pretty markdown rendering
ngpt -i --prettify

# Interactive mode with real-time markdown rendering
ngpt -i --stream-prettify
```

### Custom System Prompts

Use custom system prompts to guide the AI's behavior and responses:

```bash
ngpt --preprompt "You are a Linux command line expert. Focus on efficient solutions." "How do I find the largest files in a directory?"
```

This replaces the default "You are a helpful assistant" system prompt with your custom instruction.

You can also use custom prompts in interactive mode:

```bash
ngpt -i --preprompt "You are a Python programming tutor. Explain concepts clearly and provide helpful examples."
```

Custom prompts can be used to:
- Set the AI's persona or role
- Provide background information or context
- Specify output format preferences
- Set constraints or guidelines

### Shell Command Generation

Generate and execute shell commands appropriate for your operating system:

```bash
ngpt --shell "find all jpg files in this directory and resize them to 800x600"
```

In shell command mode, nGPT:
1. Generates the appropriate command for your OS
2. Displays the command
3. Asks for confirmation before executing it
4. Shows the command output

This is especially useful for complex commands that you can't remember the syntax for, or for OS-specific commands that work differently on different platforms.

### Code Generation

Generate clean code without markdown formatting or explanations:

```bash
ngpt --code "create a function that calculates prime numbers up to n"
```

By default, this generates Python code. To specify a different language:

```bash
ngpt --code --language javascript "create a function that calculates prime numbers up to n"
```

You can combine code generation with pretty formatting:

```bash
ngpt --code --prettify "create a sorting algorithm"
```

Or with real-time syntax highlighting:

```bash
ngpt --code --stream-prettify "create a binary search tree implementation"
```

### Text Rewriting

Improve the quality of text while preserving tone and meaning:

```bash
# Rewrite text from a command-line argument
ngpt --rewrite "This is text that I want to make better without changing its main points."

# Rewrite text from stdin
cat text.txt | ngpt --rewrite

# Use multiline editor to enter and rewrite text
ngpt --rewrite
```

The rewrite mode is perfect for:
- Improving email drafts
- Polishing documentation
- Enhancing readability of technical content
- Fixing grammar and style issues

### Git Commit Message Generation

Generate conventional, detailed commit messages from git diffs:

```bash
# Generate from staged changes
ngpt --gitcommsg

# Process large diffs in chunks with recursive analysis
ngpt --gitcommsg --rec-chunk

# Use a diff file instead of staged changes
ngpt --gitcommsg --diff path/to/diff_file

# With custom context
ngpt --gitcommsg --preprompt "type:feat"
```

The generated commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) format with:
- Type (feat, fix, docs, etc.)
- Scope (optional)
- Subject line
- Detailed description
- Breaking changes (if any)

This helps maintain consistent, informative commit history in your projects.

### Multiline Text Input

For complex prompts, use the multiline text editor:

```bash
ngpt --text
```

This opens an interactive editor with:
- Syntax highlighting
- Line numbers
- Copy/paste support
- Simple editing commands
- Submission with Ctrl+D

### Processing Stdin

Process piped content by using the `{}` placeholder in your prompt:

```bash
# Summarize a document
cat README.md | ngpt --pipe "Summarize this document in bullet points: {}"

# Analyze code
cat script.py | ngpt --pipe "Explain what this code does and suggest improvements: {}"

# Review text
cat essay.txt | ngpt --pipe "Provide feedback on this essay: {}"
```

This is powerful for integrating nGPT into shell scripts and automation workflows.

## Formatting Options

### No Streaming

By default, responses are streamed in real-time. To receive the complete response at once:

```bash
ngpt --no-stream "Explain quantum computing"
```

This is useful for:
- Scripts that process the complete output
- Redirecting output to files
- Situations where you prefer to see the full response at once

### Markdown Rendering

Enable beautiful markdown formatting and syntax highlighting:

```bash
# Regular markdown rendering (disables streaming)
ngpt --prettify "Create a markdown table showing top 5 programming languages"

# Real-time markdown rendering (streams with live formatting)
ngpt --stream-prettify "Explain Big O notation with code examples"
```

You can select different renderers:

```bash
# Use Rich renderer (default)
ngpt --prettify --renderer=rich "Create a markdown tutorial"

# Use Glow renderer (if installed)
ngpt --prettify --renderer=glow "Explain markdown syntax"

# Let ngpt select the best available (auto)
ngpt --prettify --renderer=auto "Create a technical document outline"
```

## Configuration Management

### Interactive Configuration

Enter interactive configuration mode to set up API keys and endpoints:

```bash
# Add a new configuration
ngpt --config

# Edit configuration at index 1
ngpt --config --config-index 1

# Edit configuration by provider name
ngpt --config --provider OpenAI

# Remove configuration
ngpt --config --remove --config-index 2
```

### Show Configuration

View your current configuration:

```bash
# Show active configuration
ngpt --show-config

# Show all configurations
ngpt --show-config --all
```

### List Available Models

List models available for your configuration:

```bash
# List models for active configuration
ngpt --list-models

# List models for configuration at index 1
ngpt --list-models --config-index 1

# List models for a specific provider
ngpt --list-models --provider OpenAI
```

### CLI Configuration

Set persistent defaults for command-line options:

```bash
# Show help
ngpt --cli-config help

# Set default value
ngpt --cli-config set temperature 0.8

# Get current value
ngpt --cli-config get temperature

# Show all CLI settings
ngpt --cli-config get

# Remove setting
ngpt --cli-config unset temperature
```

For more details, see the [CLI Configuration Guide](cli_config.md).

## Advanced Usage

### Combining Options

Many options can be combined for powerful workflows:

```bash
# Generate code with web search and custom system prompt
ngpt --code --web-search --preprompt "You are an expert Python developer" "create a function to download and process JSON data from an API"

# Interactive chat with logging and custom temperature
ngpt -i --log chat.log --temperature 0.9

# Shell command with no streaming
ngpt --shell --no-stream "find all large files and create a report"

# Git commit message with pretty formatting
ngpt --gitcommsg --prettify
```

### Provider Selection

Switch between different AI providers:

```bash
# Use OpenAI
ngpt --provider OpenAI "Explain quantum computing"

# Use Groq
ngpt --provider Groq "Explain quantum computing"

# Use Ollama
ngpt --provider Ollama "Explain quantum computing"
```

You can compare responses by saving to files:

```bash
ngpt --provider OpenAI --no-stream "Explain quantum computing" > openai.txt
ngpt --provider Groq --no-stream "Explain quantum computing" > groq.txt
ngpt --provider Ollama --no-stream "Explain quantum computing" > ollama.txt
diff -y openai.txt groq.txt | less
```

### Piping and Redirection

nGPT works well with Unix pipes and redirection:

```bash
# Save output to file
ngpt "Write a short story about AI" > story.txt

# Process file content
cat data.csv | ngpt -p "Analyze this CSV data and provide insights: {}" > analysis.txt

# Chain commands
ngpt --code "function to parse CSV" | grep -v "#" > parse_csv.py
```

### Web Search Integration

Enhance prompts with information from the web:

```bash
ngpt --web-search "What are the latest developments in quantum computing?"
```

Note: Web search requires that your API endpoint supports this capability.

## Troubleshooting

### Common Issues

**API Key Issues**
```bash
# Check if API key is set
ngpt --show-config

# Set API key temporarily
ngpt --api-key "your-key-here" "Test prompt"

# Enter interactive configuration to update key
ngpt --config
```

**Connection Problems**
```bash
# Check connection to API endpoint
curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/chat/completions

# Use a different base URL
ngpt --base-url "https://alternative-endpoint.com/v1/" "Test prompt"
```

**Performance Issues**
```bash
# Use a smaller, faster model
ngpt --model gpt-3.5-turbo "Quick question"

# Limit max tokens for faster responses
ngpt --max_tokens 100 "Give me a brief explanation"
```

### Getting Help

For command-line help:
```bash
ngpt --help
```

Visit the [GitHub repository](https://github.com/nazdridoy/ngpt) for:
- Latest documentation
- Issue reporting
- Feature requests
- Contributions

## Next Steps

- Learn about [CLI Configuration](cli_config.md)
- Explore [Git Commit Message Generation](gitcommsg.md)
- Try [Basic Examples](../examples/basic.md)
- Check [Advanced Examples](../examples/advanced.md) 