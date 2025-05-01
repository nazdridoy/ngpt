# nGPT Documentation

Welcome to the documentation for nGPT, a Swiss army knife for LLMs: powerful CLI and interactive chatbot in one package. Seamlessly work with OpenAI, Ollama, Groq, Claude, Gemini, or any OpenAI-compatible API to generate code, craft git commits, rewrite text, and execute shell commands. Fast, lightweight, and designed for both casual users and developers.

## Table of Contents

- [Overview](overview.md)
- [Installation](installation.md)
- [Usage](usage/cli_usage.md)
  - [CLI Usage](usage/cli_usage.md)
  - [CLI Configuration](usage/cli_config.md)
  - [Git Commit Messages](usage/gitcommsg.md)
- [Examples](examples/basic.md)
  - [Basic Examples](examples/basic.md)
  - [Advanced Examples](examples/advanced.md)
- [Configuration](configuration.md)
- [Contributing](CONTRIBUTING.md)
- [License](LICENSE.md)

## Getting Started

For a quick start, refer to the [Installation](installation.md) and [CLI Usage](usage/cli_usage.md) guides.

## Key Features

- **Versatile**: Powerful and easy-to-use CLI tool for various AI tasks
- **Lightweight**: Minimal dependencies with everything you need included
- **API Flexibility**: Works with OpenAI, Ollama, Groq, Claude, Gemini, and any compatible endpoint
- **Interactive Chat**: Continuous conversation with memory in modern UI
- **Streaming Responses**: Real-time output for better user experience
- **Web Search**: Enhance any model with contextual information from the web
- **Stdin Processing**: Process piped content by using `{}` placeholder in prompts
- **Markdown Rendering**: Beautiful formatting of markdown and code with syntax highlighting
- **Real-time Markdown**: Stream responses with live updating syntax highlighting and formatting
- **Multiple Configurations**: Cross-platform config system supporting different profiles
- **Shell Command Generation**: OS-aware command execution
- **Text Rewriting**: Improve text quality while maintaining original tone and meaning
- **Clean Code Generation**: Output code without markdown or explanations
- **Rich Multiline Editor**: Interactive multiline text input with syntax highlighting and intuitive controls
- **Git Commit Messages**: AI-powered generation of conventional, detailed commit messages from git diffs
- **System Prompts**: Customize model behavior with custom system prompts
- **Conversation Logging**: Save your conversations to text files for later reference
- **Provider Switching**: Easily switch between different LLM providers with a single parameter
- **Performance Optimized**: Fast response times and minimal resource usage

## Quick Examples

```bash
# Basic chat
ngpt "Tell me about quantum computing"

# Interactive chat session
ngpt -i

# Generate code
ngpt --code "function to calculate Fibonacci numbers"

# Generate and execute shell commands
ngpt --shell "find large files in current directory"

# Generate git commit messages
ngpt --gitcommsg
```

For more examples and detailed instructions, explore the documentation sections listed above. 