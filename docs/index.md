---
layout: default
title: nGPT Documentation
nav_order: 1
permalink: /
---

# nGPT Documentation

Welcome to the nGPT documentation. This guide will help you get started with nGPT, a Swiss army knife for LLMs that combines a powerful CLI and interactive chatbot in one package.


![ngpt-i](https://raw.githubusercontent.com/nazdridoy/ngpt/main/previews/ngpt-i.png)

## What is nGPT?

nGPT is a versatile command-line tool designed to interact with AI language models through various APIs. It provides a seamless interface for generating text, code, shell commands, and more, all from your terminal.

## Getting Started

For a quick start, refer to the [Installation](installation.md) and [CLI Usage](usage/cli_usage.md) guides.

## Key Features

- ✅ **Versatile**: Powerful and easy-to-use CLI tool for various AI tasks
- 🪶 **Lightweight**: Minimal dependencies with everything you need included
- 🔄 **API Flexibility**: Works with OpenAI, Ollama, Groq, Claude, Gemini, and any OpenAI-compatible endpoint
- 💬 **Interactive Chat**: Continuous conversation with memory in modern UI
- 📊 **Streaming Responses**: Real-time output for better user experience
- 🔍 **Web Search**: Enhance any model with contextual information from the web, using advanced content extraction to identify the most relevant information from web pages
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
- 🤖 **Custom Roles**: Create and use reusable AI roles for specialized tasks
- 📃 **Conversation Logging**: Save your conversations to text files for later reference
- 💾 **Session Management**: Save, load, and list interactive chat sessions.
- 🔌 **Modular Architecture**: Well-structured codebase with clean separation of concerns
- 🔄 **Provider Switching**: Easily switch between different LLM providers with a single parameter
- 🚀 **Performance Optimized**: Fast response times and minimal resource usage

## Quick Examples

```bash
# Basic chat
ngpt "Tell me about quantum computing"

# Interactive chat session
ngpt -i
# Inside interactive mode, you can use commands like:
# /help     - Show help menu
# /save     - Save the current session
# /load     - Load a previous session
# /sessions - List saved sessions
# /clear    - Clear the conversation
# /exit     - Exit the session (also 'exit', 'quit', 'bye' without '/')

# Generate code
ngpt --code "function to calculate Fibonacci numbers"

# Generate and execute shell commands
ngpt --shell "find large files in current directory"

# Generate git commit messages
ngpt --gitcommsg
```

For more examples and detailed instructions, please refer to the side panel for navigation through the documentation sections.