# CLI Usage Guide

This guide provides comprehensive documentation on how to use nGPT as a command-line interface (CLI) tool.

## Installation

First, ensure you have nGPT installed:

```bash
pip install ngpt
```

For all features including rich markdown rendering and interactive mode:

```bash
pip install "ngpt[full]"
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
| `--model <name>` | Model to use for this request (overrides stored configuration) |
| `--config <path>` | Path to a custom configuration file or, when used without a value, enters interactive configuration mode |
| `--config-index <index>` | Index of the configuration to use (default: 0) |
| `--provider <name>` | Provider name to identify the configuration to use (alternative to --config-index) |
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
| `--renderer <name>` | Select which markdown renderer to use with --prettify (auto, rich, or glow) |
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
ngpt -s "find all PDF files in the current directory"
```

nGPT will generate an appropriate command based on your operating system, display it, and ask for confirmation before executing it.

#### OS-Awareness

The shell command generation is OS-aware and will generate appropriate commands for:
- Windows (cmd.exe or PowerShell)
- macOS (bash/zsh)
- Linux (bash/zsh)

For example:
```bash
# On Windows might generate
ngpt -s "list all files" 
# Generates: dir

# On Linux/macOS might generate
ngpt -s "list all files"
# Generates: ls -la
```

#### Command Confirmation

For safety, nGPT always asks for confirmation before executing commands:

1. The generated command is displayed
2. You're prompted to confirm (y/N) [Default NO]
3. Only after confirmation is the command executed

#### Bypassing Confirmation (Advanced)

For automation in scripts, you can bypass the confirmation prompt by piping "y" to the command:
```bash
echo "y" | ngpt -s "list files in /tmp directory"
```

**Note:** Use this with caution as it will execute whatever command is generated without review.

#### Command Examples

```bash
# Find large files
ngpt -s "find files larger than 100MB"

# System maintenance
ngpt -s "clean up temporary files"

# Network diagnostics
ngpt -s "check if port 8080 is open"
```

### Stdin Mode

nGPT can read input directly from stdin (standard input) using the `-p` or `--pipe` flag. This allows you to pipe the output of other commands into nGPT for processing.

```bash
# Basic stdin usage
echo "Who are you?" | ngpt -p "answer {}"
```

The content from stdin replaces the `{}` placeholder in your prompt. This is useful for:

- **Summarizing command output:**
  ```bash
  ls -la | ngpt -p "Explain what these files do based on their names: {}"
  ```

- **Analyzing log files:**
  ```bash
  cat error.log | ngpt -p "What's causing these errors? {}"
  ```

- **Summarizing documents:**
  ```bash
  cat README.md | ngpt -p "Summarize this documentation: {}"
  ```

- **Translating text:**
  ```bash
  cat french_text.txt | ngpt -p "Translate this French text to English: {}"
  ```

The `{}` placeholder will be replaced with stdin content. If the placeholder is not found in your prompt, stdin content will be appended to the end of your prompt with a warning.

### Text Rewriting

Use the `-r` or `--rewrite` flag to enhance text quality while preserving the original tone and meaning:

```bash
# Rewrite text from stdin
cat draft.txt | ngpt -r

# Rewrite text directly from command line
ngpt -r "Text to improve and polish"

# Open interactive editor for text entry
ngpt -r
```

The rewrite mode is designed to improve:
- Grammar and spelling
- Sentence structure
- Clarity and conciseness
- Natural flow

While preserving:
- Original meaning and information content
- Author's tone (formal/casual/technical/friendly/serious) 
- Perspective and point of view
- Style of expression when intentional
- Technical terminology, jargon, and domain-specific language
- Facts, data points, quotes, and references

It also maintains formatting elements like:
- Paragraph breaks and section structures
- Lists, bullet points, and numbering
- Code blocks with exact code preservation
- Markdown formatting (bold, italic, headers)
- URLs, email addresses, file paths, and variables

Rewrite mode works especially well for:
- Email drafts
- Documentation
- Blog posts
- Academic writing
- Resume bullet points

#### Understanding Output

Unlike regular chat mode, rewrite mode returns only the improved text without additional commentary, making it easy to use in scripts and pipelines.

#### Setting Custom Instructions

You can use the `--preprompt` option to guide the rewriting process:

```bash
# Make the tone more professional
cat email.txt | ngpt -r --preprompt "Make this more professional and concise"

# Add SEO optimization
cat blog.md | ngpt -r --preprompt "Optimize this for SEO while maintaining readability"
```

#### Advanced Rewrite Options

The rewrite mode uses a specialized system prompt that carefully preserves original content while improving its quality. The default system prompt instructs the AI to:

- Fix grammar, spelling, and punctuation errors
- Improve sentence structure and flow
- Enhance clarity and readability
- Make language more concise and precise
- Replace awkward phrasings with more natural alternatives
- Break up overlong sentences
- Convert passive voice to active when appropriate
- Remove redundancies and filler words

It also adapts to different content types:
- Technical content: Prioritizes precision and clarity
- Casual text: Maintains conversational flow
- Formal writing: Preserves professionalism
- Emotional content: Maintains emotional resonance

When using custom instructions with `--preprompt`, these supplement rather than replace the underlying rewrite directives.

### Git Commit Message Generation

The `-g` or `--gitcommsg` flag allows you to generate conventional, high-quality commit messages based on your git staged changes or diff files:

```bash
# Generate commit message from staged changes
ngpt -g

# Generate commit message with a specific commit type
ngpt -g -m "type:feat"

# Process large diffs in chunks with recursive analysis
ngpt -g --rec-chunk

# Use a specific diff file instead of staged changes
ngpt -g --diff /path/to/changes.diff

# Enable logging for debugging
ngpt -g --log commit_log.txt
```

#### Message Context Directives

Use the `--preprompt` option to guide the AI with various directives:

```bash
# Force a specific commit type prefix
ngpt -g -m "type:feat"
ngpt -g -m "type:fix"

# Focus only on specific file types
ngpt -g -m "javascript"
ngpt -g -m "python"

# Focus on or exclude specific aspects
ngpt -g -m "focus on auth"
ngpt -g -m "ignore formatting"
ngpt -g -m "exclude tests"

# Combine multiple directives
ngpt -g -m "type:feat focus on UI"
```

#### Processing Large Diffs

For large diffs or pull requests, use recursive chunking to handle token limits and rate limits:

```bash
# Set custom chunk size
ngpt -g --rec-chunk --chunk-size 150

# Set custom analyses chunk size
ngpt -g --rec-chunk --analyses-chunk-size 150

# Set maximum message lines before condensing
ngpt -g --rec-chunk --max-msg-lines 25

# Set recursion depth for very large diffs
ngpt -g --rec-chunk --max-recursion-depth 5
```

#### Using Diff Files

Instead of using staged changes, you can provide a diff file:

```bash
# Use a specific diff file
ngpt -g --diff /path/to/changes.diff

# Use a default diff file from CLI configuration
ngpt -g --diff
```

#### Automatic Clipboard Copy

When a commit message is successfully generated, the tool attempts to copy it to your clipboard for easy pasting into your git commit command.

#### Requirements

- Git must be installed and available in your PATH
- You must be in a git repository
- For automatic commit message generation, you need staged changes (`git add`)

For detailed documentation on git commit message generation, see the [Git Commit Message Guide](gitcommsg.md).

> **Tip**: For better visualization of conventional commit messages on GitHub, you can use the [GitHub Commit Labels](https://greasyfork.org/en/scripts/526153-github-commit-labels) userscript, which adds colorful labels to your commits.

### Generating Code

Generate clean code without markdown or explanations:

```bash
ngpt -c "function that calculates the Fibonacci sequence"
```

This returns only the code, without any surrounding markdown formatting or explanations.

#### Language Selection

You can specify the programming language using the `--language` option:

```bash
# Generate code in JavaScript
ngpt -c --language javascript "function to sort an array of numbers"

# Generate code in Java
ngpt -c --language java "class representing a simple bank account"

# Generate code in TypeScript
ngpt -c --language typescript "async function to fetch data from an API"

# Generate code in Go
ngpt -c --language go "function to read a file"

# Generate code in Rust
ngpt -c --language rust "struct and implementation for a linked list"
```

The default language is Python if not specified.

#### Saving Generated Code

You can pipe the output directly to a file:

```bash
# Save generated Python code to a file
ngpt -c "function to calculate prime numbers" > primes.py

# Save generated JavaScript code
ngpt -c --language javascript "function to validate email" > validate.js
```

#### Combining with Other Options

Code generation can be combined with other options:

```bash
# Generate code with syntax highlighting
ngpt -c --prettify "implement quicksort algorithm"

# Generate code with real-time syntax highlighting
ngpt -c --stream-prettify "create a binary search tree class"

# Generate code with web search capability
ngpt -c --web-search "implement the latest React hooks pattern"

# Generate code with custom system prompt
ngpt -c --preprompt "Focus on writing clean, well-documented code with clear comments" "implement dijkstra's algorithm"

# Set temperature for more creative coding solutions
ngpt -c --temperature 0.8 "generate different ways to solve the fibonacci sequence"
```

### Multiline Text Input

Open an interactive editor for entering complex, multiline prompts:

```bash
ngpt -t
```

This opens an editor where you can:
- Write and edit multiline text with proper indentation
- Paste long or ill-formatted text
- Press Ctrl+D or F10 to submit the text
- Press Esc to cancel

### Markdown Rendering

Display markdown responses with beautiful formatting and syntax highlighting:

```bash
ngpt --prettify "Explain markdown syntax with examples"
```

#### Renderer Options

nGPT supports multiple renderers for displaying formatted markdown:

1. **Rich** (Python library): 
   - Works in most terminals
   - Supports syntax highlighting
   - Animated streaming with `--stream-prettify`
   
2. **Glow** (terminal-based):
   - More advanced markdown rendering
   - Better table support
   - Must be installed separately (https://github.com/charmbracelet/glow)

3. **Auto** (default):
   - Automatically selects the best available renderer
   - Falls back to plain text if no renderers are available

```bash
# Use Rich renderer
ngpt --prettify --renderer=rich "Create a markdown table comparing programming languages"

# Use Glow renderer
ngpt --prettify --renderer=glow "Write documentation with code examples"

# Use automatic selection (default is Rich if available)
ngpt --prettify --renderer=auto "Explain blockchain with code examples"
```

#### Real-time Markdown Streaming

For a more dynamic experience, you can watch as formatted markdown and syntax highlighting are applied in real-time while the response is streaming:

```bash
ngpt --stream-prettify "Explain quantum computing with code examples"
```

This provides both the benefits of streaming (seeing the response as it's generated) and formatting (proper markdown rendering and syntax highlighting).

```bash
# Differences between --prettify and --stream-prettify
ngpt --prettify "Explain algorithms"         # Shows fully formatted result at the end
ngpt --stream-prettify "Explain algorithms"  # Shows formatted result as it arrives
```
Notes on `--stream-prettify`:
- Requires Rich to be installed (`pip install "ngpt[full]"` or `pip install rich`)
- Only works with the Rich renderer (even if you specify another renderer)
- Works in both regular and interactive modes
- Creates a more dynamic and responsive UI experience

#### Checking Available Renderers

To see which renderers are available on your system:

```bash
ngpt --list-renderers
```

This will display information about which renderers are installed and which one will be used as the default.

### Environment Variables

nGPT respects several environment variables that can be used to configure its behavior without modifying the configuration file or using command-line arguments:

```bash
# API credentials
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.alternative.com/v1/"
export OPENAI_MODEL="gpt-4"

```

#### Environment Variable Precedence

Environment variables take precedence over configuration file values but are overridden by command-line arguments:

1. Command-line arguments (highest priority)
2. Environment variables
3. CLI configuration (ngpt-cli.conf)
4. Main configuration file (ngpt.conf)
5. Default values (lowest priority)

For automation and scripting, environment variables are often the most convenient way to set credentials.

### Using Web Search

Enable web search capability (if your API endpoint supports it):

```bash
ngpt --web-search "What are the latest developments in quantum computing?"
```

This allows the AI to access current information from the web when generating a response. This is particularly useful for:

- Getting up-to-date information on current events
- Answering questions about recent developments
- Finding the latest documentation or reference material
- Fact-checking information against online sources

Note that web search capability depends on your API provider supporting this feature.

```bash
# Combine web search with other options
ngpt --web-search --prettify "Create a summary of today's top news"

# Use web search in interactive mode
ngpt -i --web-search

# Use web search for code generation
ngpt -c --web-search "implement the latest JavaScript fetch API pattern"
```

## Configuration Options

### Command Line Configuration

The `--cli-config` option provides a way to set persistent default values for command-line options:

```bash
# Set default values
ngpt --cli-config set temperature 0.8
ngpt --cli-config set renderer rich
ngpt --cli-config set language javascript

# View current settings
ngpt --cli-config get

# Get a specific setting
ngpt --cli-config get temperature

# Remove a setting
ngpt --cli-config unset language

# List all available options that can be configured
ngpt --cli-config list

# Show help information about CLI configuration
ngpt --cli-config help
```

Key features:
- Stored settings apply automatically to future commands
- Context-sensitive options (e.g., language only applies in code generation mode)
- Settings follow priority order: command-line > environment variables > CLI config > main config > defaults

### Configuration Management

#### Viewing Configuration

View your current active configuration:

```bash
# Show active configuration details
ngpt --show-config

# Show all stored configurations
ngpt --show-config --all
```

#### Selecting Configurations

Select a specific stored configuration by index or provider name:

```bash
# Use configuration at index 1
ngpt --config-index 1 "Your prompt here"

# Use configuration with provider name "Gemini"
ngpt --provider Gemini "Your prompt here"
```

#### Direct Configuration Override

Specify API credentials directly for a single command (overrides stored configuration):

```bash
ngpt --api-key "your-key" --base-url "https://api.example.com/v1/" --model "model-name" "Your prompt here"
```

#### Interactive Configuration

The `--config` option without arguments enters interactive configuration mode:

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
```

In interactive mode:
- When editing an existing configuration, press Enter to keep the current values
- When creating a new configuration, press Enter to use default values
- For security, your API key is not displayed when editing configurations
- When removing a configuration, you'll be asked to confirm before deletion

#### Available CLI Configuration Options

The list of options that can be set with `--cli-config` includes:

##### General options (all modes):
- `api-key` - API key for the service
- `base-url` - Base URL for the API
- `config-index` - Index of the configuration to use
- `language` - Programming language for code generation
- `max_tokens` - Maximum tokens in response
- `model` - Model to use
- `no-stream` - Disable streaming responses
- `preprompt` - Custom system prompt
- `prettify` - Enable markdown rendering
- `provider` - Provider name to identify configuration
- `renderer` - Markdown renderer to use
- `stream-prettify` - Enable streaming with markdown rendering
- `temperature` - Temperature setting (0.0-2.0)
- `top_p` - Top-p parameter (0.0-1.0)
- `web-search` - Enable web search capability

##### Options for Git commit message mode:
- `preprompt` - Context to guide AI generation
- `rec-chunk` - Process large diffs in chunks with recursive analysis
- `diff` - Path to diff file to use instead of staged changes
- `chunk-size` - Number of lines per chunk when chunking is enabled
- `analyses-chunk-size` - Number of lines per chunk for recursive analysis
- `max-msg-lines` - Maximum number of lines in commit message before condensing
- `max-recursion-depth` - Maximum recursion depth for message condensing

#### Custom Configuration File

Use a configuration file at a non-standard location:

```bash
ngpt --config /path/to/custom-config.json "Your prompt here"
```

### Model Management

List all available models for the current configuration:

```bash
# List models for active configuration
ngpt --list-models

# List models for a specific configuration by index
ngpt --list-models --config-index 1

# List models for a specific configuration by provider name
ngpt --list-models --provider Gemini
```

This is useful for:
- Discovering what models are available from your provider
- Confirming API connectivity
- Checking model names before setting them in your configuration

### Version Information

Display the version of nGPT and related environment details:

```bash
ngpt -v
# or
ngpt --version
```

## Advanced Usage

### Combining Options

You can combine various options:

```bash
# Generate code with web search capability
ngpt -c --web-search "function to get current weather using an API"

# Use a specific model and no streaming
ngpt --model gpt-4o-mini --no-stream "Explain quantum entanglement"

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

### Writing & Editing

```bash
# Improve email drafts
cat draft_email.txt | ngpt -r

# Enhance documentation clarity
cat documentation.md | ngpt -r

# Improve resume bullet points
ngpt -r "Responsible for managing team of 5 developers and ensuring project deadlines were met"

# Edit academic writing for clarity
cat thesis_chapter.txt | ngpt -r

# Polish blog posts
cat blog_draft.md | ngpt -r
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
  - This works because of the package's `__main__.py` module
  - It's particularly useful in virtual environments or when the command isn't in your PATH
  - All the same arguments and options work with this method: `python -m ngpt -i --prettify`

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
   - Use `--no-stream` for faster responses in scripts
   - Use interactive mode when having a conversation
   - Exit interactive sessions when not in use to save API costs
