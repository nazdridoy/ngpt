---
layout: default
title: nGPT Overview
nav_order: 2
permalink: /overview/
---

# nGPT Overview

## What is nGPT?

nGPT is a Swiss army knife for LLMs: powerful CLI and interactive chatbot in one package. Seamlessly work with OpenAI, Ollama, Groq, Claude, Gemini, or any OpenAI-compatible API to generate code, craft git commits, rewrite text, and execute shell commands. Fast, lightweight, and designed for both casual users and developers.

## Key Features

- **Versatile**: Powerful and easy-to-use CLI tool for various AI tasks
- **Lightweight**: Minimal dependencies with everything you need included
- **API Flexibility**: Works with OpenAI, Ollama, Groq, Claude, Gemini, and any OpenAI-compatible endpoint
- **Interactive Chat**: Continuous conversation with memory in modern UI
- **Streaming Responses**: Real-time output for better user experience
- **Web Search**: Enhance any model with contextual information from the web, using advanced content extraction to identify the most relevant information from web pages
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

## Core Modes

nGPT offers several specialized modes of operation:

### Basic Chat Mode
The default mode, where you send prompts and receive responses:
```bash
ngpt "Tell me about quantum computing"
```

### Interactive Mode
Start an ongoing conversation with memory:
```bash
ngpt -i
ngpt --interactive
```

### Code Generation Mode
Generate clean code without markdown formatting or explanations:
```bash
ngpt --code "function to calculate Fibonacci numbers"
ngpt -c "function to calculate Fibonacci numbers"
```

### Shell Command Mode
Generate and execute OS-aware shell commands:
```bash
ngpt --shell "list all files recursively"
ngpt -s "list all files recursively"
```

### Text Rewriting Mode
Improve the quality of text while preserving tone and meaning:
```bash
cat text.txt | ngpt --rewrite
cat text.txt | ngpt -r
```

### Git Commit Message Mode
Generate conventional, detailed commit messages from git diffs:
```bash
ngpt --gitcommsg
ngpt -g
```

### Multiline Text Input Mode
Open an interactive editor for complex prompts:
```bash
ngpt --text
ngpt -t
```

### Stdin Processing Mode
Process piped content using a placeholder:
```bash
cat README.md | ngpt --pipe "Summarize this document: {}"
cat README.md | ngpt -p "Summarize this document: {}"
```

## Architecture

nGPT is built as a streamlined CLI application with:

1. **Command-line Interface**: User-friendly interface with intuitive flags and options
2. **Configuration System**: Cross-platform solution for managing API keys, endpoints, and model preferences
3. **Rendering Engines**: Support for beautiful markdown and code rendering with syntax highlighting
4. **Interactive Components**: Tools for building interactive sessions with rich editing capabilities

## Use Cases

nGPT is ideal for:

- Quick interactions with language models from the terminal
- Generating and executing shell commands without remembering complex syntax
- Creating clean code snippets for various programming languages
- Improving text quality in documentation, emails, or reports
- Generating professional git commit messages that follow conventional formats
- Having ongoing conversations with AI assistants with memory
- Automating tasks through piping and shell integration

## Supported Providers

nGPT works with any provider that offers an OpenAI-compatible API, including:

- OpenAI
- Groq
- Ollama
- Claude (via compatible endpoints)
- Gemini (via compatible endpoints)
- Any other service with OpenAI-compatible endpoints

For more detailed information on using nGPT, see the [CLI Usage Guide](usage/cli_usage.md). 