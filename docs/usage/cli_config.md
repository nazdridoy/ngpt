# CLI Configuration

NGPT offers a CLI configuration system that allows you to set default values for command-line options. This means you don't have to specify the same options repeatedly for common tasks.

## Configuration Priority

When running NGPT, options are applied in the following order of priority (highest to lowest):

1. Command-line arguments (e.g., `--model gpt-4`, `--provider Gemini`)
2. Environment variables (e.g., `OPENAI_API_KEY`)
3. CLI configuration file (`ngpt-cli.conf`, managed via `--cli-config`)
4. Main configuration file (`ngpt.conf` or custom config file, selected via index or provider name)
5. Default values hardcoded in the application

## Managing CLI Configuration

You can manage your CLI configuration using the `--cli-config` command:

```bash
# Set a default value
ngpt --cli-config set OPTION VALUE

# Get a current value
ngpt --cli-config get OPTION

# Show all current settings
ngpt --cli-config get

# Remove a setting
ngpt --cli-config unset OPTION

# List all available options
ngpt --cli-config list

# Show help information
ngpt --cli-config
# or
ngpt --cli-config help
```

## Available Options

The available configuration options are organized by context:

### General Options (All Modes)

These options apply to all modes:

- `provider` - Provider name to identify the configuration to use
- `temperature` - Controls randomness in the response (default: 0.7)
- `top_p` - Controls diversity via nucleus sampling (default: 1.0)
- `max_tokens` - Maximum number of tokens to generate
- `preprompt` - Custom system prompt to control AI behavior
- `renderer` - Markdown renderer to use (auto, rich, or glow)
- `config-index` - Index of the configuration to use (default: 0)
- `web-search` - Enable web search capability (default: false)

These options are mutually exclusive:
- `no-stream` - Return the whole response without streaming
- `prettify` - Render markdown responses and code with syntax highlighting
- `stream-prettify` - Enable streaming with markdown rendering

*Note on Exclusivity:* When you use `--cli-config set` to set one of `no-stream`, `prettify`, or `stream-prettify` to `true`, the other two options in this group will automatically be set to `false` in your `ngpt-cli.conf` file.

### Mode-Specific Options

Some options only apply in specific modes:

- `language` - Programming language for code generation (only for code mode)
- `log` - Filepath to log conversation (for interactive and text modes)

### Context-Aware Application

Each option configured via `--cli-config` is only applied if it's relevant to the current execution mode and if it wasn't already specified as a command-line argument.

## Smart Profile Selection

One of the most powerful features of CLI configuration is the ability to set your preferred model provider, which will then be automatically selected when running any command:

```bash
# Set your preferred provider
ngpt --cli-config set provider Gemini

# Now all commands will use the Gemini provider by default
ngpt "Tell me about quantum computing"
# This uses the Gemini provider without having to specify --provider Gemini
```

This works because NGPT checks the CLI configuration for `provider` (or `config-index`) before loading the main configuration profile, and then uses that value when selecting which profile to load.

## Programmatic Access to CLI Configuration

You can also access and modify the CLI configuration programmatically in your applications:

```python
from ngpt.utils.cli_config import (
    load_cli_config,
    set_cli_config_option,
    get_cli_config_option,
    unset_cli_config_option,
    apply_cli_config
)

# Load the CLI configuration
cli_config = load_cli_config()
print(f"Current CLI config: {cli_config}")

# Set a configuration option
success, message = set_cli_config_option('temperature', '0.8')
print(message)  # "Option 'temperature' set to '0.8'"

# Get a configuration option
success, value = get_cli_config_option('temperature')
print(f"Temperature value: {value}")  # "Temperature value: 0.8"

# Unset a configuration option
success, message = unset_cli_config_option('temperature')
print(message)  # "Option 'temperature' removed from configuration"

# Apply CLI configuration to arguments
args = parser.parse_args()
args = apply_cli_config(args)
```

For more information about the CLI configuration API, see the [CLI Framework Documentation](./cli_framework.md).

## Examples

### Setting Default Options

```bash
# Set default language to TypeScript for code generation
ngpt --cli-config set language typescript

# Always use a higher temperature for more creative responses
ngpt --cli-config set temperature 0.9

# Always enable pretty markdown rendering
ngpt --cli-config set prettify true

# Set default provider to use
ngpt --cli-config set provider Gemini
```

### Using CLI Configuration

After setting CLI configuration options, you can run commands without specifying those options:

```bash
# Before configuration:
ngpt -c --language typescript "write a sorting function"

# After setting language=typescript in CLI config:
ngpt -c "write a sorting function"
# The TypeScript language will be used automatically
```

### Context-Aware Application

Each option is only applied in the appropriate context:

- The `language` option only affects code generation mode (`-c`)
- The `log` option only affects interactive and text modes (`-i`, `-t`)

## CLI Configuration File

The CLI configuration is stored in a JSON file at:

- Linux: `~/.config/ngpt/ngpt-cli.conf`
- macOS: `~/Library/Application Support/ngpt/ngpt-cli.conf`
- Windows: `%APPDATA%\ngpt\ngpt-cli.conf`

The file contains a simple JSON object with option-value pairs. You can edit this file directly if needed, but using the `--cli-config` command is the recommended approach.

## Implementation Details

The CLI configuration system is designed to efficiently handle both main profile selection and specific option settings:

1. Command line arguments are explicitly provided by the user and take highest priority.
2. CLI configuration is loaded early in the execution process to influence which profile is selected.
3. Mutual exclusivity is enforced when setting options via `--cli-config set`.
4. Option values are only applied to the current command if they are relevant to its mode. 