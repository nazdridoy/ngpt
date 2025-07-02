---
layout: default
title: CLI Usage Guide
parent: Usage
nav_order: 2
permalink: /usage/cli_usage/
---

# CLI Usage Guide

This guide provides comprehensive documentation on how to use nGPT as a command-line interface (CLI) tool.

![ngpt-s-c](https://raw.githubusercontent.com/nazdridoy/ngpt/main/previews/ngpt-s-c.png)

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

You can set configuration options directly via command-line arguments:

```console
❯ ngpt -h

usage: ngpt [-h] [-v] [--api-key API_KEY] [--base-url BASE_URL] [--model MODEL] [--web-search] [--pipe]
            [--temperature TEMPERATURE] [--top_p TOP_P] [--max_tokens MAX_TOKENS] [--log [FILE]]
            [--preprompt PREPROMPT | --role ROLE] [--config [CONFIG]] [--config-index CONFIG_INDEX]
            [--provider PROVIDER] [--remove] [--show-config] [--all] [--list-models] [--cli-config [COMMAND ...]]
            [--role-config [ACTION ...]] [--plaintext] [--language LANGUAGE] [--rec-chunk] [--diff [FILE]]
            [--chunk-size CHUNK_SIZE] [--analyses-chunk-size ANALYSES_CHUNK_SIZE] [--max-msg-lines MAX_MSG_LINES]
            [--max-recursion-depth MAX_RECURSION_DEPTH] [--humanize] [-i | -s | -c | -t | -r | -g]
            [prompt]

nGPT - AI-powered terminal toolkit for code, commits, commands & chat

positional arguments::

[PROMPT]                            The prompt to send to the language model

Global Options::

-h, --help                          show this help message and exit
-v, --version                       Show version information and exit
--api-key API_KEY                   API key for the service
--base-url BASE_URL                 Base URL for the API
--model MODEL                       Model to use
--web-search                        Enable web search capability using DuckDuckGo to enhance prompts with relevant
                                    information
--pipe                              Read from stdin and use content with prompt. Use {} in prompt as placeholder
                                    for stdin content. Can be used with any mode option except --text and
                                    --interactive
--temperature TEMPERATURE           Set temperature (controls randomness, default: 0.7)
--top_p TOP_P                       Set top_p (controls diversity, default: 1.0)
--max_tokens MAX_TOKENS             Set max response length in tokens
--log [FILE]                        Set filepath to log conversation to, or create a temporary log file if no path
                                    provided
--preprompt PREPROMPT               Set custom system prompt to control AI behavior
--role ROLE                         Use a predefined role to set system prompt (mutually exclusive with
                                    --preprompt)

Configuration Options::

--config [CONFIG]                   Path to a custom config file or, if no value provided, enter interactive
                                    configuration mode to create a new config
--config-index CONFIG_INDEX         Index of the configuration to use or edit (default: 0)
--provider PROVIDER                 Provider name to identify the configuration to use
--remove                            Remove the configuration at the specified index (requires --config and
                                    --config-index or --provider)
--show-config                       Show the current configuration(s) and exit
--all                               Show details for all configurations (requires --show-config)
--list-models                       List all available models for the current configuration and exit
--cli-config [COMMAND ...]          Manage CLI configuration (set, get, unset, list, help)
--role-config [ACTION ...]          Manage custom roles (help, create, show, edit, list, remove) [role_name]

Output Display Options::

--plaintext                         Disable streaming and markdown rendering (plain text output)

Code Mode Options::

--language LANGUAGE                 Programming language to generate code in (for code mode)

Git Commit Message Options::

--rec-chunk                         Process large diffs in chunks with recursive analysis if needed
--diff [FILE]                       Use diff from specified file instead of staged changes. If used without a path,
                                    uses the path from CLI config.
--chunk-size CHUNK_SIZE             Number of lines per chunk when chunking is enabled (default: 200)
--analyses-chunk-size ANALYSES_CHUNK_SIZE
                                    Number of lines per chunk when recursively chunking analyses (default: 200)
--max-msg-lines MAX_MSG_LINES       Maximum number of lines in commit message before condensing (default: 20)
--max-recursion-depth MAX_RECURSION_DEPTH
                                    Maximum recursion depth for commit message condensing (default: 3)

Rewrite Mode Options::

--humanize                          Transform AI-generated text into human-like content that passes AI detection
                                    tools

Modes (mutually exclusive)::

-i, --interactive                   Start an interactive chat session
-s, --shell                         Generate and execute shell commands
-c, --code                          Generate code
-t, --text                          Enter multi-line text input (submit with Ctrl+D)
-r, --rewrite                       Rewrite text from stdin to be more natural while preserving tone and meaning
-g, --gitcommsg                     Generate AI-powered git commit messages from staged changes or diff file

```

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
- Use `help` to see a list of available commands.

#### Session Management

In interactive mode, you can manage your chat sessions with the following commands:

- **`save`**: Saves the current conversation to a timestamped JSON file in the `history` subdirectory of your configuration folder.
- **`load`**: Lists recent sessions and prompts you to select one to load, restoring the conversation history.
- **`sessions`**: Displays a list of all saved sessions.
- **`clear`**: Clears the current conversation history.
- **`history`**: Shows the full history of the current conversation.
- **`exit`**: Exits the interactive session.
- **`help`**: Shows the help menu with all available commands.

Example:
```
> save
Session saved to /home/user/.config/ngpt/history/session_2024-10-26_12-30-00.json

> load
Saved Sessions:
  [0] session_2024-10-26_12-30-00.json
  [1] session_2024-10-25_18-00-00.json
Enter the number of the session to load: 0
Session loaded from ...
```

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

#### Multiline Text Input in Interactive Mode

Enable multiline input in interactive chat mode:

```bash
ngpt -i
```

In interective mode you can:
- Use the "ml" command to enter multiline text mode
- Type or paste complex, multi-paragraph prompts
- Press Ctrl+D (or Ctrl+Z on Windows) to submit the multiline input
- Exit multiline mode anytime by typing ".exit" on a new line

This is especially useful when:
- Providing code samples for the AI to analyze
- Entering complex contexts or scenarios
- Pasting error logs or output for debugging help
- Composing detailed questions with multiple parts

Example usage:
```
> ml
(multiline mode - press Ctrl+D to submit)
Here's the error I'm getting:

TypeError: cannot convert 'NoneType' object to int
  File "app.py", line 45, in process_data
    result = data['count'] + 5

Can you help me understand what's wrong?
^D
```

#### Combining with Other Options

Interactive mode can be combined with other options for enhanced functionality:

```bash
# Interactive mode with custom system prompt
ngpt -i --preprompt "You are a Python programming tutor"

# Interactive mode with web search
ngpt -i --web-search

# Interactive mode with markdown formatting
ngpt -i

# Interactive mode with real-time markdown formatting (default)
ngpt -i
```

### Custom Roles

nGPT supports creating and using custom roles to define specialized AI personas for different tasks. Custom roles are saved configurations that can be reused across multiple sessions.

Basic usage:
```bash
# Create a new role
ngpt --role-config create expert_coder

# Use a role
ngpt --role expert_coder "Write a function to validate email addresses"
```

For detailed documentation on creating and managing roles, including examples and best practices, see the [Custom Roles Guide](roles.md).

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
ngpt --code "create a sorting algorithm"
```

Or with real-time syntax highlighting:

```bash
ngpt --code "create a binary search tree implementation"
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

#### Humanizing AI Text

Transform AI-generated content to sound more natural and human-like:

```bash
# Humanize AI-generated text from argument
ngpt --rewrite --humanize "Artificial intelligence is revolutionizing the healthcare industry by enhancing diagnostic accuracy."

# Humanize AI content from a file
cat ai_generated_article.txt | ngpt --rewrite --humanize
```

The humanize option helps with:
- Making AI-generated content pass AI detection tools
- Adding natural human writing patterns and style variations
- Breaking predictable AI writing structures
- Creating content that reads authentically human


#### Customized Text Rewriting

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

# Rewrite text in a journalistic style
ngpt --rewrite --preprompt "You are an investigative journalist. Write in a clear, objective style with a focus on facts and evidence" "The new AI system has shown promising results in early testing, with accuracy rates exceeding 95% in controlled environments."

# Humanize text while maintaining technical accuracy
ngpt --rewrite --humanize --preprompt "You are a senior software engineer explaining complex concepts to junior developers. Use analogies and real-world examples while keeping technical details precise" "The microservices architecture pattern involves breaking down applications into smaller, independent services that communicate through well-defined APIs."

# Rewrite text in a persuasive style
ngpt --rewrite --preprompt "You are a marketing copywriter. Write compelling, persuasive content that highlights benefits and creates urgency" "Our new product offers several features that can help improve productivity and save time."

# Humanize text for social media
ngpt --rewrite --humanize --preprompt "You are a social media influencer. Write engaging, authentic content that resonates with your audience while maintaining credibility" "The latest research shows that regular exercise can significantly improve mental health and cognitive function."

# Rewrite text for a specific industry
ngpt --rewrite --preprompt "You are a healthcare professional writing for medical journals. Use appropriate medical terminology while ensuring clarity for a general medical audience" "The patient presented with symptoms consistent with acute respiratory distress syndrome, including dyspnea and hypoxemia."
```

### Git Commit Message Generation

Generate conventional, detailed commit messages from git diffs:

```bash
# Generate from staged changes
ngpt --gitcommsg

# Process large diffs in chunks with recursive analysis
ngpt --gitcommsg --rec-chunk

# Use a diff file instead of staged changes
ngpt --gitcommsg --diff path/to/diff_file

# Use piped diff content from stdin
git diff HEAD~1 | ngpt --gitcommsg --pipe

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

This is powerful for integrating nGPT into shell scripts and automation workflows.

### Pipe Usage With Different Modes

The `--pipe` flag can be combined with several modes (except `--text` and `--interactive`) for powerful workflows:

```bash
# Standard chat mode with pipe
cat README.md | ngpt --pipe "Summarize this document in bullet points: {}"

# Code generation mode with pipe
cat algorithm.py | ngpt --code --pipe "Optimize this algorithm and add comments: {}"

# Shell command generation with pipe
cat server_logs.txt | ngpt --shell --pipe "Generate a command to extract all error messages from these logs: {}"

# Rewrite mode with pipe (explicit placeholder)
cat draft_email.txt | ngpt --rewrite --pipe "Make this email more professional while keeping key points: {}"

# Rewrite mode with pipe (implicit - will use entire content)
cat draft_email.txt | ngpt --rewrite

# Git commit message generation from piped diff
git diff HEAD~1 | ngpt --gitcommsg --pipe
```

Each mode handles piped content appropriately for that context:
- In code mode: Uses piped code as a starting point for modification
- In shell mode: Generates commands that process the piped content
- In rewrite mode: Treats the piped content as the text to be rewritten
- In gitcommsg mode: Uses piped content as the diff to analyze

## Formatting Options

### Plain Text Output

By default, responses are streamed in real-time with markdown rendering. To disable streaming and markdown rendering:

```bash
ngpt --plaintext "Explain quantum computing"
```

This is useful for:
- Scripts that process the complete output
- Redirecting output to files
- Situations where you prefer to see the full response at once
- Plain text output without formatting

### Markdown Rendering

By default, nGPT provides real-time markdown formatting and syntax highlighting:

```bash
# Disable streaming and markdown rendering (plain text)
ngpt --plaintext "Explain quantum computing"

# Enable markdown formatting (default)
ngpt "Create a markdown table showing top 5 programming languages"

# Enable real-time markdown formatting (default)
ngpt "Explain Big O notation with code examples"
```

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

### Environment Variables

You can set the following environment variables to override configuration:

```bash
# Set API key
export OPENAI_API_KEY="your-api-key"

# Set base URL
export OPENAI_BASE_URL="https://api.alternative.com/v1/"

# Set model
export OPENAI_MODEL="alternative-model"
```

These will take precedence over values in the configuration file but can be overridden by command-line arguments.

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

# Shell command with plain text output
ngpt --shell --plaintext "find all large files and create a report"

# Git commit message with markdown formatting (default)
ngpt --gitcommsg

# Use a custom role with web search
ngpt --role technical_writer --web-search "Write documentation for a REST API"
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
# Compare outputs from different providers
ngpt --provider OpenAI --plaintext "Explain quantum computing" > openai.txt
ngpt --provider Groq --plaintext "Explain quantum computing" > groq.txt
ngpt --provider Ollama --plaintext "Explain quantum computing" > ollama.txt
```

### Piping and Redirection

nGPT works well with Unix pipes and redirection:

```bash
# Save output to file
ngpt "Write a short story about AI" > story.txt

# Process file content
cat data.csv | ngpt --pipe "Analyze this CSV data and provide insights: {}" > analysis.txt

# Using here-string (<<<) for quick single-line input 
ngpt --pipe {} <<< "What is the best way to learn shell redirects?"

# Using standard input redirection to process file contents
ngpt --pipe "summarise {}" < README.md

# Using here-document (<<EOF) for multiline input
ngpt --pipe {} << EOF                                              
What is the best way to learn Golang?
Provide simple hello world example.
EOF

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

**Model Availability Issues**
```bash
# Check which models are available
ngpt --list-models

# Try a different model
ngpt --model gpt-3.5-turbo "Test prompt"
```

**Base URL Issues**
```bash
# Check if your base URL is correct
ngpt --show-config

# Try an alternative base URL
ngpt --base-url "https://alternative-endpoint.com/v1/" "Test prompt"
```

### Securing Your Configuration

Your API keys are stored in the configuration file. To ensure they remain secure:

1. Ensure the configuration file has appropriate permissions: `chmod 600 ~/.config/ngpt/ngpt.conf`
2. For shared environments, consider using environment variables instead
3. Don't share your configuration file or API keys with others
4. If you suspect your key has been compromised, regenerate it from your API provider's console

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
- Explore [Custom Roles Guide](roles.md)
- Explore [Git Commit Message Generation](gitcommsg.md)
- Try [Basic Examples](../examples/basic.md)
- Check [Advanced Examples](../examples/advanced.md)