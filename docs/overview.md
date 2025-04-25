# nGPT Overview

## What is nGPT?

nGPT is a lightweight Python library and command-line interface (CLI) tool designed for interacting with OpenAI-compatible APIs. It provides a simple, flexible way to communicate with various large language model (LLM) endpoints, including official OpenAI services and self-hosted alternatives.

## Key Features

- **Dual-Purpose Design**: Use nGPT as either a CLI tool for quick interactions or as a Python library integrated into your applications.

- **Lightweight Implementation**: Built with minimal dependencies (primarily `requests`), making it easy to install and integrate.

- **API Flexibility**: Works seamlessly with OpenAI's official API as well as compatible endpoints like Ollama, Groq, self-hosted models, and more.

- **Interactive Chat**: Supports ongoing conversations with memory in an easy-to-use interface.

- **Streaming Responses**: Provides real-time output for a better user experience.

- **Web Search Integration**: Works with compatible API endpoints that support web search capabilities.

- **Markdown Rendering**: Beautiful formatting of markdown responses and syntax highlighting for code.

- **Real-time Markdown Rendering**: Stream responses with live updating syntax highlighting and formatting using the `--stream-prettify` option.

- **Multiple Configuration Support**: Maintain different API configurations for various services or models.

- **Shell Command Generation**: Generate OS-aware commands that work on your specific platform.

- **Clean Code Generation**: Output code without markdown formatting or explanations.

- 📝 **Rich Multiline Editor**: Interactive multiline text input with syntax highlighting and intuitive controls
- 🎭 **System Prompts**: Customize model behavior with custom system prompts
- 📃 **Conversation Logging**: Automatically or manually log conversations with timestamps and role information
- 🧰 **CLI Components**: Reusable components for building custom AI-powered command-line tools

## Architecture

nGPT is built around a few core components:

1. **NGPTClient**: The main class that handles communication with the LLM API endpoints.

2. **Configuration System**: A cross-platform solution for managing API keys, endpoints, and model preferences.

3. **CLI Interface**: A user-friendly command-line interface for direct interaction with LLMs.

## Use Cases

nGPT is ideal for:

- Developers who need a simple, lightweight library for integrating LLM capabilities into their Python applications
- Users who want a convenient CLI tool for quick interactions with language models
- Projects that require flexibility to work with different LLM providers
- Applications that need to generate and potentially execute shell commands or code snippets

## Supported Providers

nGPT works with any provider that offers an OpenAI-compatible API, including:

- OpenAI
- Groq
- Ollama
- Self-hosted models (using compatible API servers)
- Any other service with OpenAI-compatible endpoints

For more detailed information on using nGPT, see the [Library Usage](usage/library_usage.md) and [CLI Usage](usage/cli_usage.md) guides. 