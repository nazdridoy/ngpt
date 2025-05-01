---
layout: default
title: Basic Examples
parent: Examples
nav_order: 1
permalink: /examples/basic/
---

# Basic Examples

This page provides practical examples of common nGPT usage patterns. These examples demonstrate the basic capabilities and how to use the most frequent commands.

## Chat Examples

### Simple Question and Answer

```bash
# Ask a simple question
ngpt "What is quantum computing?"

# Ask for an explanation of a concept
ngpt "Explain the difference between REST and GraphQL"

# Get a definition
ngpt "Define 'artificial intelligence' in simple terms"
```

### Custom System Prompts

```bash
# Specify a role for the AI
ngpt --preprompt "You are a Linux expert" "How do I find all files larger than 100MB?"

# Add specific instructions
ngpt --preprompt "Answer with bullet points only" "What are the benefits of cloud computing?"

# Create a specific personality
ngpt --preprompt "You are a pirate. Speak like a pirate in every response." "Tell me about the weather today"
```

### Interactive Chat Session

```bash
# Start basic interactive session
ngpt -i

# Interactive session with custom system prompt
ngpt -i --preprompt "You are a helpful math tutor who explains concepts step by step"

# Interactive session with logging
ngpt -i --log math_tutoring.log
```

## Code Generation Examples

### Generate Code in Various Languages

```bash
# Generate Python code (default)
ngpt --code "create a function that checks if a number is prime"

# Generate JavaScript code
ngpt --code --language javascript "create a function that checks if a number is prime"

# Generate Rust code
ngpt --code --language rust "create a function that checks if a number is prime"
```

### Generate Code with Specific Requirements

```bash
# Generate a function with specific parameters
ngpt --code "write a function that sorts an array of objects by a given property name"

# Generate an algorithm implementation
ngpt --code "implement the merge sort algorithm"

# Generate a class with multiple methods
ngpt --code "create a UserManager class with methods for add, remove, update, and find"
```

### Rendering Code with Syntax Highlighting

```bash
# Generate code with pretty formatting
ngpt --code --prettify "create a binary search tree implementation"

# Generate code with real-time syntax highlighting
ngpt --code --stream-prettify "create a function to download a file from a URL"
```

## Shell Command Generation Examples

### Basic Commands

```bash
# Find files
ngpt --shell "find all JPG files in the current directory and subdirectories"

# Process text
ngpt --shell "extract all email addresses from input.txt and save to emails.txt"

# System management
ngpt --shell "show current memory and CPU usage"
```

### OS-Specific Commands

These commands will be adapted for your specific operating system:

```bash
# List files (will use 'dir' on Windows or 'ls -la' on Linux/macOS)
ngpt --shell "list all files in the current directory"

# Find processes (will use appropriate command for your OS)
ngpt --shell "find all processes using more than 100MB of memory"

# Create directory structure (will adapt for your OS)
ngpt --shell "create a directory structure for a web project with HTML, CSS, and JS folders"
```

## Text Rewriting Examples

### Basic Text Improvement

```bash
# Rewrite text provided as an argument
ngpt --rewrite "I want to say that I think your product is good and I like it alot."

# Rewrite text from a file
cat email.txt | ngpt --rewrite
```

### Interactive Text Rewriting

```bash
# Open multiline editor for text input
ngpt --rewrite
```

### Directed Rewriting

```bash
# Rewrite with specific instructions
cat text.txt | ngpt --pipe "Rewrite the following text to be more formal: {}"

# Rewrite to a specific style
cat informal.txt | ngpt --pipe "Rewrite the following to match academic writing style: {}"
```

## Stdin Processing Examples

### Text Analysis

```bash
# Analyze a document
cat report.md | ngpt --pipe "Summarize the following document: {}"

# Analyze code
cat script.py | ngpt --pipe "Explain what this code does and suggest improvements: {}"

# Extract information
cat emails.txt | ngpt --pipe "Extract all company domains from these email addresses: {}"
```

### Content Transformation

```bash
# Convert formats
cat data.json | ngpt --pipe "Convert this JSON to YAML: {}"

# Translate content
cat spanish.txt | ngpt --pipe "Translate this Spanish text to English: {}"

# Change writing style
cat technical.txt | ngpt --pipe "Rewrite this technical content for a non-technical audience: {}"
```

## Git Commit Message Examples

### Basic Usage

```bash
# Generate commit message from staged changes
git add .
ngpt --gitcommsg
```

### Detailed Analysis

```bash
# Process large changes in chunks
git add .
ngpt --gitcommsg --rec-chunk
```

### Guided Message Generation

```bash
# Indicate type and scope
git add src/auth/*
ngpt --gitcommsg --preprompt "type:feat scope:authentication"

# Provide specific context
git add .
ngpt --gitcommsg --preprompt "This refactors the payment processing module"
```

## Formatting Examples

### Markdown Rendering

```bash
# Render markdown with syntax highlighting
ngpt --prettify "Create a markdown table showing the top 5 programming languages and their key features"

# Real-time markdown rendering
ngpt --stream-prettify "Explain the main Git commands with examples"
```

### Renderer Selection

```bash
# Use Rich renderer (default)
ngpt --prettify --renderer=rich "Create a tutorial for Docker basics"

# Use Glow renderer (if installed)
ngpt --prettify --renderer=glow "Explain REST API design principles"
```

## Provider Selection Examples

### Using Different Providers

```bash
# Use OpenAI
ngpt --provider OpenAI "What are the advantages of transformer models?"

# Use Groq
ngpt --provider Groq "What are the advantages of transformer models?"

# Use Ollama
ngpt --provider Ollama "What are the advantages of transformer models?"
```

### Provider Comparison

```bash
# Compare responses by redirecting to files
ngpt --provider OpenAI --no-stream "Explain quantum computing" > openai.txt
ngpt --provider Groq --no-stream "Explain quantum computing" > groq.txt
diff -y openai.txt groq.txt | less
```

## Configuration Examples

### Interactive Configuration

```bash
# Add new configuration
ngpt --config

# Edit configuration at index 1
ngpt --config --config-index 1

# Edit configuration by provider name
ngpt --config --provider Groq
```

### CLI Configuration

```bash
# Set default temperature
ngpt --cli-config set temperature 0.8

# Set default language for code generation
ngpt --cli-config set language javascript

# Enable web search by default
ngpt --cli-config set web-search true
```

## Combining Options

### Chat with Web Search

```bash
# Get up-to-date information
ngpt --web-search "What are the latest developments in quantum computing?"

# Research with custom system prompt
ngpt --web-search --preprompt "You are a financial advisor" "How has inflation affected the housing market this year?"
```

### Advanced Code Generation

```bash
# Generate code with web search and custom temperature
ngpt --code --web-search --temperature 0.2 "create a function to convert a CSV file to JSON"

# Generate code with specific instructions
ngpt --code --language typescript --preprompt "You are an expert in TypeScript and React" "create a custom hook for form validation"
```

### Advanced Shell Command Generation

```bash
# Generate complex command with custom system prompt
ngpt --shell --preprompt "You are a Linux sysadmin expert" "find all files modified in the last 24 hours and create a report of their sizes"

# Generate and log the command and output
ngpt --shell --log commands.log "create a backup of all configuration files in /etc"
```

## Next Steps

For more advanced examples and detailed explanations of specific features, see:

- [Advanced Examples](advanced.md)
- [CLI Usage Guide](../usage/cli_usage.md)
- [CLI Configuration Guide](../usage/cli_config.md)
- [Git Commit Message Guide](../usage/gitcommsg.md) 