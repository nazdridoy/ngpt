# CLI Usage Guide

This guide provides comprehensive documentation on how to use nGPT as a command-line interface (CLI) tool.

## Installation

First, ensure you have nGPT installed:

```bash
pip install ngpt
```

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

## Common Options

Here are the most commonly used options:

| Option | Description |
|--------|-------------|
| `-i, --interactive` | Start an interactive chat session with conversation memory |
| `-n, --no-stream` | Return the whole response without streaming |
| `-s, --shell` | Generate and execute shell commands |
| `-c, --code` | Generate clean code without markdown formatting |
| `-t, --text` | Open interactive multiline editor for complex prompts |
| `-v, --version` | Show version information |
| `--preprompt` | Set custom system prompt to control AI behavior |
| `--log` | Set filepath to log conversation to (for interactive modes) |
| `--web-search` | Enable web search capability (if supported by your API) |
| `--temperature` | Set temperature (controls randomness, default: 0.7) |
| `--top_p` | Set top_p (controls diversity, default: 1.0) |
| `--max_tokens` | Set maximum response length in tokens |
| `--prettify` | Render markdown responses and code with syntax highlighting |
| `--stream-prettify` | Enable real-time markdown rendering with syntax highlighting while streaming |
| `--renderer` | Select which markdown renderer to use (auto, rich, or glow) |
| `--list-renderers` | Show available markdown renderers on your system |
| `--config-index` | Index of the configuration to use (default: 0) |
| `--provider` | Provider name to identify the configuration to use (alternative to --config-index) |

## Feature Details

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

You can log your conversation to a file for later reference:

```bash
ngpt -i --log conversation.log
```

This saves the entire conversation, including both user inputs and AI responses, to the specified file.

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

### Generating Shell Commands

Generate and execute shell commands appropriate for your operating system:

```bash
ngpt -s "find all PDF files in the current directory"
```

nGPT will generate an appropriate command based on your operating system, display it, and ask for confirmation before executing it.

### Generating Code

Generate clean code without markdown or explanations:

```bash
ngpt -c "function that calculates the Fibonacci sequence"
```

This returns only the code, without any surrounding markdown formatting or explanations.

### Multiline Text Input

Open an interactive editor for entering complex, multiline prompts:

```bash
ngpt -t
```

This opens an editor where you can:
- Write and edit multiline text
- Press Ctrl+D or F10 to submit the text
- Press Esc to cancel

### Markdown Rendering

Display markdown responses with beautiful formatting and syntax highlighting:

```bash
ngpt --prettify "Explain markdown syntax with examples"
```

This instructs the AI to generate properly formatted markdown responses, which are then rendered with appropriate formatting, including:
- Syntax highlighting for code blocks
- Proper rendering of tables
- Formatted headers, lists, and other markdown elements

You can specify which markdown renderer to use:

```bash
# Use Rich (Python library) renderer
ngpt --prettify --renderer=rich "Create a markdown table comparing programming languages"

# Use Glow (terminal-based) renderer
ngpt --prettify --renderer=glow "Write documentation with code examples"

# Use automatic selection (default is Rich if available)
ngpt --prettify --renderer=auto "Explain blockchain with code examples"
```

Combine with code generation for syntax-highlighted code:

```bash
ngpt -c --prettify "function to calculate the Fibonacci sequence"
```

When using `--prettify` with code generation, the AI will output code in markdown format with proper syntax highlighting based on the language.

### Real-time Markdown Rendering

Display markdown responses with real-time formatting and syntax highlighting while streaming:

```bash
ngpt --stream-prettify "Explain quantum computing with code examples"
```

This provides an enhanced experience by rendering markdown in real-time as content arrives, offering both the benefits of streaming and formatted output simultaneously. This feature uses Rich for live updates and beautiful formatting.

You can also combine this with code generation:

```bash
ngpt -c --stream-prettify "write a function to implement merge sort in Python"
```

This is particularly useful for longer code generation tasks, as you can see the code being formatted with syntax highlighting in real-time.

Notes on `--stream-prettify`:
- Requires Rich to be installed (`pip install "ngpt[full]"` or `pip install rich`)
- Only works with the Rich renderer (even if you specify another renderer)
- Works in both regular and interactive modes
- Creates a more dynamic and responsive UI experience

See available renderers on your system:

```bash
ngpt --list-renderers
```

### Using Web Search

Enable web search capability (if your API endpoint supports it):

```bash
ngpt --web-search "What are the latest developments in quantum computing?"
```

This allows the AI to access current information from the web when generating a response.

## Configuration Options

### Viewing Current Configuration

Show your current active configuration:

```bash
ngpt --show-config
```

Show all stored configurations:

```bash
ngpt --show-config --all
```

### Setting Configuration Options

Select a specific configuration by index:

```bash
ngpt --config-index 1 "Your prompt here"
```

Select a specific configuration by provider name:

```bash
ngpt --provider Gemini "Your prompt here"
```

Specify API credentials directly:

```bash
ngpt --api-key "your-key" --base-url "https://api.example.com/v1/" --model "model-name" "Your prompt here"
```

### Interactive Configuration

Add a new configuration interactively:

```bash
ngpt --config
```

Edit an existing configuration by index:

```bash
ngpt --config --config-index 1
```

Edit an existing configuration by provider name:

```bash
ngpt --config --provider Gemini
```

Remove a configuration by index:

```bash
ngpt --config --remove --config-index 2
```

Remove a configuration by provider name:

```bash
ngpt --config --remove --provider Gemini
```

### Model Management

List all available models for the current configuration:

```bash
ngpt --list-models
```

List models for a specific configuration:

```bash
ngpt --list-models --config-index 1
```

## Advanced Usage

### Combining Options

You can combine various options:

```bash
# Generate code with web search capability
ngpt -c --web-search "function to get current weather using an API"

# Use a specific model and no streaming
ngpt --model gpt-4o-mini -n "Explain quantum entanglement"

# Interactive session with custom prompt and logging
ngpt -i --preprompt "You are a data science tutor" --log datasci_tutoring.txt

# Generate code with syntax highlighting
ngpt -c --prettify "create a sorting algorithm"

# Generate code with real-time syntax highlighting
ngpt -c --stream-prettify "implement a binary search tree in JavaScript"

# Render markdown with web search for up-to-date information
ngpt --prettify --web-search "Create a markdown table of recent SpaceX launches"

# Interactive session with markdown rendering
ngpt -i --prettify --renderer=rich

# Interactive session with real-time markdown rendering
ngpt -i --stream-prettify
```

### Using a Custom Configuration File

Specify a custom configuration file location:

```bash
ngpt --config /path/to/custom-config.json "Your prompt here"
```

### Setting Temperature

Control the randomness of responses:

```bash
# More deterministic responses
ngpt --temperature 0.2 "Write a poem about autumn"

# More creative responses
ngpt --temperature 0.9 "Write a poem about autumn"
```

### Setting Top-p (Nucleus Sampling)

Control the diversity of responses by adjusting the nucleus sampling parameter:

```bash
# More focused on likely responses
ngpt --top_p 0.5 "Give me ideas for a birthday party"

# Include more diverse possibilities
ngpt --top_p 1.0 "Give me ideas for a birthday party"
```

### Limiting Response Length

Set the maximum response length in tokens:

```bash
# Get a concise response
ngpt --max_tokens 100 "Explain quantum computing"

# Allow for a longer, more detailed response
ngpt --max_tokens 500 "Write a comprehensive guide to machine learning"
```

## Examples by Task

### Creative Writing

```bash
# Generate a short story
ngpt "Write a 300-word sci-fi story about time travel"

# Write poetry
ngpt "Write a haiku about mountains"
```

### Programming Help

```bash
# Get programming help
ngpt "How do I read a file line by line in Python?"

# Generate code
ngpt -c "create a function that validates email addresses using regex"
```

### Research and Learning

```bash
# Learn about a topic
ngpt "Explain quantum computing for beginners"

# Get current information (with web search)
ngpt --web-search "What are the latest advancements in AI?"

# Learn with a specialized tutor using custom prompt
ngpt --preprompt "You are an expert physicist explaining concepts to a beginner. Use analogies and simple language." "Explain quantum entanglement"
```

### Productivity

```bash
# Generate a shell command
ngpt -s "find large files over 100MB and list them by size"

# Create a structured document
ngpt -t
# (Enter multiline text for generating a complex document)

# Log an important session for reference
ngpt -i --log project_planning.log --preprompt "You are a project management expert helping plan a software project"
```

## Troubleshooting

### API Connection Issues

If you're having trouble connecting to the API:

```bash
# Check your current configuration
ngpt --show-config

# Try specifying the base URL directly
ngpt --base-url "https://api.example.com/v1/" "Test connection"
```
### Authorization Problems

If you're experiencing authentication issues:

```bash
# Update your API key
ngpt --config --config-index 0
# Enter your new API key when prompted

# Or specify API key directly (not recommended for sensitive keys)
ngpt --api-key "your-new-api-key" "Test prompt"
```

### Command Not Found

If the `ngpt` command is not found after installation:

- Ensure Python's bin directory is in your PATH
- Try using `python -m ngpt` instead of just `ngpt`

## Tips and Best Practices

1. **Use the right tool for the job**:
   - Use `-c` for clean code generation
   - Use `-s` for shell commands
   - Use `-t` for complex, multiline inputs

2. **Craft effective prompts**:
   - Be specific about what you want
   - Provide context and examples when relevant
   - Specify format, style, or constraints

3. **Leverage configuration profiles**:
   - Set up different profiles for different API providers
   - Use lower-cost models for simpler tasks
   - Reserve more powerful models for complex tasks

4. **Protect API keys**:
   - Store API keys in your configuration file
   - Avoid passing API keys directly on the command line
   - Use environment variables when appropriate

5. **Improve efficiency**:
   - Use `-n` (no streaming) for faster responses in scripts
   - Use interactive mode when having a conversation
   - Exit interactive sessions when not in use to save API costs 
