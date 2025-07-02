---
layout: default
title: Basic Examples
parent: Examples
nav_order: 1
permalink: /examples/basic/
---

# Basic Examples

This page provides practical examples of common nGPT usage patterns. These examples demonstrate the basic capabilities and how to use the most frequent commands.

![ngpt-s-c](https://raw.githubusercontent.com/nazdridoy/ngpt/main/previews/ngpt-s-c.png)

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
# Generate code with syntax highlighting
ngpt --code "create a binary search tree implementation"

# Generate code with real-time syntax highlighting (default)
ngpt --code "create a function to download a file from a URL"
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

### AI Text Humanization

```bash
# Humanize AI-generated text to make it undetectable by AI detectors
ngpt --rewrite --humanize "ChatGPT generated this text which is very formal and structured with perfect grammar."

# Humanize AI content from a file
cat ai_content.txt | ngpt --rewrite --humanize
```

### Customized Text Rewriting

```bash
# Rewrite text with a specific style guide
ngpt --rewrite --preprompt "You are a technical documentation expert. Follow these guidelines: 1) Use active voice, 2) Keep sentences under 20 words, 3) Use clear headings, 4) Include examples" "The system processes data through multiple stages. First, it validates input. Then it transforms data. Finally, it stores results."

# Rewrite text for a specific audience
ngpt --rewrite --preprompt "You are a teacher explaining complex topics to 8th graders. Use simple language, relatable examples, and avoid jargon" "Quantum entanglement is a physical phenomenon where particles become correlated in such a way that the quantum state of each particle cannot be described independently."

# Humanize text while maintaining academic tone
ngpt --rewrite --humanize --preprompt "You are an academic writer. Maintain scholarly language while making the text sound more natural and less AI-generated" "The implementation of machine learning algorithms in healthcare diagnostics has demonstrated significant improvements in accuracy rates across multiple studies."

# Humanize text for a specific writing style
ngpt --rewrite --humanize --preprompt "You are a creative blogger. Make the text engaging and conversational while preserving the technical accuracy" "Artificial intelligence is revolutionizing the healthcare industry by enhancing diagnostic accuracy and streamlining administrative processes."

# Rewrite text with specific formatting requirements
ngpt --rewrite --preprompt "You are a professional email writer. Format the text as a formal business email with proper greeting and closing" "I want to say that I think your product is good and I like it alot. Can you tell me more about the pricing?"
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

### Shell Redirection Examples

```bash
# Using here-string (<<<) for quick single-line input 
ngpt --pipe {} <<< "What is the best way to learn shell redirects?"

# Using standard input redirection to process file contents
ngpt --pipe "summarise {}" < README.md

# Using here-document (<<EOF) for multiline input
ngpt --pipe {} << EOF                                              
What is the best way to learn Golang?
Provide simple hello world example.
EOF
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

## Pipe Usage With Different Modes

The pipe flag can be used with several different modes for powerful combinations:

### With Standard Mode (Default)

```bash
# Summarize document content
cat README.md | ngpt --pipe "Summarize this document: {}"
```

### With Code Mode

```bash
# Generate optimized version of code
cat slow_function.py | ngpt --code --pipe "Optimize this function for performance: {}"

# Add tests to existing code
cat module.js | ngpt --code --language javascript --pipe "Write unit tests for this code: {}"
```

### With Shell Mode

```bash
# Generate command to process file content
cat error_logs.txt | ngpt --shell --pipe "Generate a command to count occurrences of each error type in these logs: {}"
```

### With Rewrite Mode

```bash
# Improve email drafts
cat draft_email.txt | ngpt --rewrite --pipe "Make this email more professional while maintaining the core message: {}"
```

### With Git Commit Message Mode

```bash
# Generate message from specific diff
git diff HEAD~1 | ngpt --gitcommsg --pipe
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
# Enable markdown formatting
ngpt "Create a markdown table showing the top 5 programming languages and their key features"

# Enable real-time markdown formatting (default)
ngpt "Explain the main Git commands with examples"

# Use markdown formatting (default)
ngpt "Create a tutorial for Docker basics"


```



```bash

# Use markdown formatting
ngpt "Explain REST API design principles"
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
# Compare outputs from different providers
ngpt --provider OpenAI --plaintext "Explain quantum computing" > openai.txt
ngpt --provider Groq --plaintext "Explain quantum computing" > groq.txt
```

## Configuration Examples

### Interactive Configuration

```
