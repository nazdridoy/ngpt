# Configuration Guide

nGPT uses a flexible configuration system that supports multiple profiles for different API providers and models. This guide explains how to configure and manage your nGPT settings.

## API Key Setup

### OpenAI API Key
1. Create an account at [OpenAI](https://platform.openai.com/)
2. Navigate to API keys: https://platform.openai.com/api-keys
3. Click "Create new secret key" and copy your API key
4. Configure nGPT with your key:
   ```bash
   ngpt --config
   # Enter provider: OpenAI
   # Enter API key: your-openai-api-key
   # Enter base URL: https://api.openai.com/v1/
   # Enter model: gpt-3.5-turbo (or other model)
   ```

### Google Gemini API Key
1. Create or use an existing Google account
2. Go to [Google AI Studio](https://aistudio.google.com/)
3. Navigate to API keys in the left sidebar (or visit https://aistudio.google.com/app/apikey)
4. Create an API key and copy it
5. Configure nGPT with your key:
   ```bash
   ngpt --config
   # Enter provider: Gemini
   # Enter API key: your-gemini-api-key
   # Enter base URL: https://generativelanguage.googleapis.com/v1beta/openai
   # Enter model: gemini-2.0-flash
   ```

### Setting Up Ollama
1. Install Ollama from [ollama.ai](https://ollama.ai/)
2. Run Ollama locally (it should be running on http://localhost:11434)
3. Configure nGPT to use Ollama:
   ```bash
   ngpt --config
   # Enter provider: Ollama-Local
   # Enter API key: (leave blank or press Enter)
   # Enter base URL: http://localhost:11434/v1/
   # Enter model: llama3 (or another model you've pulled in Ollama)
   ```

### Setting Up Groq
1. Create an account at [Groq](https://console.groq.com/)
2. Navigate to API Keys and create a new key
3. Configure nGPT with your Groq key:
   ```bash
   ngpt --config
   # Enter provider: Groq
   # Enter API key: your-groq-api-key
   # Enter base URL: https://api.groq.com/openai/v1/
   # Enter model: llama3-70b-8192 (or another Groq model)
   ```

## Configuration File Location

nGPT stores its configuration in a JSON file located at:

- **Linux**: `~/.config/ngpt/ngpt.conf` or `$XDG_CONFIG_HOME/ngpt/ngpt.conf`
- **macOS**: `~/Library/Application Support/ngpt/ngpt.conf`
- **Windows**: `%APPDATA%\ngpt\ngpt.conf`

## Configuration Structure

The configuration file uses a JSON list format that allows you to store multiple configurations. Each configuration entry is a JSON object with the following fields:

```json
[
  {
    "api_key": "your-openai-api-key",
    "base_url": "https://api.openai.com/v1/",
    "provider": "OpenAI",
    "model": "gpt-4o"
  },
  {
    "api_key": "your-groq-api-key-here",
    "base_url": "https://api.groq.com/openai/v1/",
    "provider": "Groq",
    "model": "llama3-70b-8192"
  },
  {
    "api_key": "your-optional-ollama-key",
    "base_url": "http://localhost:11434/v1/",
    "provider": "Ollama-Local",
    "model": "llama3"
  }
]
```

### Configuration Fields

- **api_key**: Your API key for the service
- **base_url**: The base URL for the API endpoint
- **provider**: A human-readable name for the provider (used for display purposes)
- **model**: The default model to use with this configuration

## Configuration Priority

nGPT determines configuration values in the following order (highest priority first):

1. **Command-line arguments**: When specified directly with `--api-key`, `--base-url`, `--model`, etc.
2. **Environment variables**: 
   - `OPENAI_API_KEY` 
   - `OPENAI_BASE_URL`
   - `OPENAI_MODEL`
3. **CLI configuration file**: Stored in ngpt-cli.conf (see CLI Configuration section)
4. **Main configuration file**: Selected configuration (by default, index 0)
5. **Default values**: Fall back to built-in defaults

## Interactive Configuration

You can configure nGPT interactively using the CLI:

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

The interactive configuration will prompt you for values and guide you through the process.

## Command-Line Configuration

You can also set configuration options directly via command-line arguments:

### Key Configuration Flags

- `--api-key <key>`: Specify the API key directly.
- `--base-url <url>`: Specify the API endpoint URL.
- `--model <n>`: Specify the AI model name.
- `--config <path>`: Use a specific configuration file.
- `--config-index <index>`: Select a configuration profile by its index (0-based).
- `--provider <n>`: Select a configuration profile by its provider name.
- `--show-config [--all]`: Display the current (or all) configuration(s).
- `--list-models`: List models available for the selected configuration.
- `--list-renderers`: Show available markdown renderers for use with --prettify.
- `--config`: Enter interactive mode to add/edit/remove configurations.
  - Use with `--config-index <index>` or `--provider <n>` to edit.
  - Use with `--remove` and `--config-index <index>` or `--provider <n>` to remove.

### Mode Flags (mutually exclusive)

- `-i, --interactive`: Start an interactive chat session.
- `-s, --shell`: Generate and execute shell commands.
- `-c, --code`: Generate code.
  - `--language <lang>`: Specify the programming language for code generation (default: `python`).
- `-t, --text`: Use a multiline editor for input.
- `-p, --pipe`: Read from stdin and use content in your prompt with {} placeholder.
- `-r, --rewrite`: Rewrite text from stdin to be more natural while preserving tone and meaning.
- `-g, --gitcommsg`: Generate AI-powered git commit messages from staged changes or diff file.

### Output Control Flags

- `--no-stream`: Disable streaming output.
- `--prettify`: Enable formatted markdown/code output (disables streaming).
  - `--renderer <n>`: Choose the renderer (`auto`, `rich`, `glow`).
- `--stream-prettify`: Enable real-time formatted output while streaming (uses Rich).

### Generation Control Flags

- `--preprompt <text>`: Set a custom system prompt.
- `--log [file]`: Enable logging: use `--log` to create a temporary log file, or `--log PATH` for a specific location.
- `--temperature <value>`: Set the generation temperature (0.0-2.0, default: 0.7).
- `--top_p <value>`: Set the nucleus sampling top_p value (0.0-1.0, default: 1.0).
- `--max_tokens <number>`: Set the maximum number of tokens for the response.
- `--web-search`: Enable web search capability (if supported by the API).

### Git Commit Message Flags

- `--preprompt <text>`: Context to guide AI generation (e.g., file types, commit type).
- `-r, --rec-chunk`: Process large diffs in chunks with recursive analysis if needed.
- `--diff [file]`: Use diff from specified file instead of staged changes.
- `--chunk-size <number>`: Number of lines per chunk when chunking is enabled (default: 200).
- `--analyses-chunk-size <number>`: Number of lines per chunk when recursively chunking analyses (default: 200).
- `--max-msg-lines <number>`: Maximum number of lines in commit message before condensing (default: 20).
- `--max-recursion-depth <number>`: Maximum recursion depth for commit message condensing (default: 3).

### Other Flags

- `-v, --version`: Show the nGPT version.
- `--cli-config <command> [option] [value]`: Manage persistent CLI option defaults (`set`, `get`, `unset`, `list`, `help`).

```bash
# Example: Use specific API key, base URL, and model for a single command
ngpt --api-key "your-key" --base-url "https://api.example.com/v1/" --model "custom-model" "Your prompt here"

# Select a specific configuration by index
ngpt --config-index 2 "Your prompt here"

# Select a specific configuration by provider name
ngpt --provider Gemini "Your prompt here"

# Control response generation parameters
ngpt --temperature 0.8 --top_p 0.95 --max_tokens 300 "Write a creative story"

# Set a custom system prompt (preprompt)
ngpt --preprompt "You are a Linux command line expert. Focus on efficient solutions." "How do I find the largest files in a directory?"

# Log conversation to a specific file
ngpt --interactive --log conversation.log

# Create a temporary log file automatically
ngpt --log "Tell me about quantum computing"

# Process text from stdin using the {} placeholder
echo "What is this text about?" | ngpt -p "Analyze the following text: {}"

# Generate git commit message from staged changes
ngpt -g

# Generate git commit message from a diff file
ngpt -g --diff changes.diff
```

## Environment Variables

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

## Checking Current Configuration

To see your current configuration:

```bash
# Show active configuration
ngpt --show-config

# Show all configurations
ngpt --show-config --all
```

## Listing Available Models

To see a list of available models for your active configuration:

```bash
# List models for active configuration
ngpt --list-models

# List models for configuration at index 1
ngpt --list-models --config-index 1

# List models for a specific provider
ngpt --list-models --provider OpenAI
```

## CLI Configuration

nGPT also supports a CLI configuration system for setting default parameter values. See the [CLI Configuration Guide](usage/cli_config.md) for details.

## Troubleshooting

### Common Configuration Issues

**API Key Issues**
```bash
# Check if your API key is configured
ngpt --show-config

# Verify a connection to the API endpoint
curl -s -o /dev/null -w "%{http_code}" https://api.openai.com/v1/chat/completions

# Set a new API key temporarily
ngpt --api-key "your-key-here" "Test prompt"
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

## Next Steps

After configuring nGPT, explore:

- [CLI Usage Guide](usage/cli_usage.md) for general usage information
- [CLI Configuration Guide](usage/cli_config.md) for setting up default CLI options
- [Basic Examples](examples/basic.md) for common usage patterns 