# Git Commit Message Generation

The `-g` or `--gitcommsg` mode in NGPT helps you generate high-quality, conventional commit messages using AI to analyze your git diffs.

## Basic Usage

```bash
# Generate commit message from staged changes
ngpt -g

# Generate commit message with context/directives
ngpt -g --preprompt "type:feat"

# Process large diffs in chunks with recursive analysis
ngpt --gitcommsg --rec-chunk

# Use a diff file instead of staged changes
ngpt -g --diff /path/to/changes.diff

# Enable logging for debugging
ngpt -g --log commit_log.txt
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--preprompt` | Context to guide AI (file types, commit type directive, focus) |
| `--rec-chunk` | Process large diffs in chunks with recursive analysis if needed |
| `--diff [FILE]` | Use diff from specified file instead of staged changes. If used without a value, uses the path from CLI config |
| `--log [FILE]` | Enable detailed logging (to specified file or auto-generated temp file) |
| `--chunk-size NUM` | Set number of lines per chunk (default: 200) |
| `--analyses-chunk-size NUM` | Set number of lines per chunk when recursively analyzing (default: 200) |
| `--max-msg-lines NUM` | Maximum number of lines in commit message before condensing (default: 20) |
| `--max-recursion-depth NUM` | Maximum recursion depth for message condensing (default: 3) |

## Context Directives

The `--preprompt` option is powerful and supports several directive types:

### Commit Type Directive

Force a specific commit type prefix:

```bash
# Force "feat:" prefix
ngpt -g --preprompt "type:feat"

# Force "fix:" prefix 
ngpt --gitcommsg --preprompt "type:fix"

# Force "docs:" prefix
ngpt -g --preprompt "type:docs"
```

### File Type Filtering

Focus only on specific file types:

```bash
# Focus only on JavaScript changes
ngpt -g --preprompt "javascript"

# Focus only on CSS files 
ngpt --gitcommsg --preprompt "css"

# Focus only on Python files
ngpt -g --preprompt "python"
```

The file type filter applies a strict filter to only include changes to files of that type or related to that technology in the analysis and commit message. Other file changes will be excluded from the message.

### Focus/Exclusion Directives

Control what to include or exclude:

```bash
# Focus only on authentication-related changes
ngpt -g --preprompt "focus on auth"

# Ignore formatting changes
ngpt --gitcommsg --preprompt "ignore formatting"

# Exclude test files from the summary
ngpt -g --preprompt "exclude tests"
```

Focus directives instruct the tool to exclusively analyze changes related to a specific feature or component, while exclusion directives tell it to completely ignore certain aspects like formatting changes or test files.

### Combined Directives

You can combine multiple directives:

```bash
# Force "feat:" prefix and focus only on UI changes
ngpt -g --preprompt "type:feat focus on UI"

# Force "fix:" prefix and ignore formatting changes
ngpt --gitcommsg --preprompt "type:fix ignore formatting"
```

## Chunking Mechanism

When processing large diffs with `--rec-chunk`, the chunking mechanism helps manage rate limits and token limits:

1. Diffs are split into chunks (default 200 lines) and processed separately
2. The partial analyses are then combined into a final commit message
3. If the combined analysis is still too large, it's recursively processed again
4. The AI will condense the message if it exceeds `--max-msg-lines` (default: 20)

This is particularly useful for large pull requests or commits with many changes.

### Advanced Chunking Control

For very large diffs or complex codebases, you can fine-tune the chunking process:

```bash
# Set a custom chunk size
ngpt -g --rec-chunk --chunk-size 150

# Set a different analysis chunk size (for processing intermediate results)
ngpt -g --rec-chunk --chunk-size 200 --analyses-chunk-size 150

# Control message length limits
ngpt --gitcommsg --rec-chunk --max-msg-lines 25

# Increase the recursion depth for extremely large diffs
ngpt -g --rec-chunk --max-recursion-depth 5
```

## CLI Configuration

You can set default values for gitcommsg options using the CLI configuration system:

```bash
# Enable recursive chunking by default
ngpt --cli-config set rec-chunk true

# Set a default diff file path (used with --diff flag)
ngpt --cli-config set diff /path/to/your/changes.diff

# Set a custom chunk size
ngpt --cli-config set chunk-size 150

# Set custom analysis chunk size
ngpt --cli-config set analyses-chunk-size 150  

# Set maximum lines in commit message
ngpt --cli-config set max-msg-lines 25

# Set maximum recursion depth
ngpt --cli-config set max-recursion-depth 5

# Set a context directive to always apply
ngpt --cli-config set preprompt "type:feat"
```

### Available CLI Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rec-chunk` | bool | false | Process large diffs in chunks with recursive analysis |
| `diff` | string | null | Path to diff file to use instead of staged changes |
| `chunk-size` | int | 200 | Number of lines per chunk when chunking is enabled |
| `analyses-chunk-size` | int | 200 | Number of lines per chunk when recursively chunking analyses |
| `max-msg-lines` | int | 20 | Maximum number of lines in commit message before condensing |
| `max-recursion-depth` | int | 3 | Maximum recursion depth for recursive chunking and message condensing |
| `preprompt` | string | null | Context to guide AI generation |

### Option Details

#### rec-chunk

When enabled, this option automatically processes large diffs in chunks and then combines the results:

```bash
# Enable recursive chunking by default
ngpt --cli-config set rec-chunk true
```

This is particularly useful for large commits or codebases, as it helps:
- Avoid token limits with large diffs
- Handle rate limiting better by breaking requests into smaller pieces
- Process very large changes that would otherwise fail

#### chunk-size and analyses-chunk-size

Controls how many lines are processed in each chunk:

```bash
# Set a custom chunk size for diff processing
ngpt --cli-config set chunk-size 150

# Set a custom chunk size for analysis processing
ngpt --cli-config set analyses-chunk-size 150
```

- `chunk-size`: Controls the size of raw diff chunks (smaller chunks for very large diffs)
- `analyses-chunk-size`: Controls the size of analysis chunks during recursive processing

Smaller chunks (100-150 lines) work better for very large diffs or models with stricter token limits, while larger chunks (300-500 lines) provide more context but may hit token limits.

#### max-msg-lines and max-recursion-depth

Controls the commit message condensing process:

```bash
# Allow longer commit messages
ngpt --cli-config set max-msg-lines 25

# Increase max recursion depth for extremely large diffs
ngpt --cli-config set max-recursion-depth 5
```

- `max-msg-lines`: Maximum number of lines in the final commit message before automatic condensing
- `max-recursion-depth`: Maximum number of recursive analysis or condensing rounds allowed

Higher recursion depth values allow processing larger diffs but may increase processing time.

#### preprompt

Provides contextual guidance for the AI when generating commit messages:

```bash
# Always focus on a specific aspect
ngpt --cli-config set preprompt "focus on API changes"

# Always use a specific commit type
ngpt --cli-config set preprompt "type:feat"

# Combined directives
ngpt --cli-config set preprompt "type:fix exclude tests"
```

This is useful when you consistently work on the same type of changes and want to standardize your commit messages.

### Using the Diff File Option

When you've set a default diff file using the CLI config:

```bash
# Set a default diff file
ngpt --cli-config set diff /path/to/changes.diff
```

The diff file from CLI config is only used when you specifically request it with the `--diff` flag without providing a path. You have three ways to control which diff is used:

1. **Use git staged changes** (ignore the CLI config diff):
   ```bash
   ngpt -g
   ```
   This will always use git staged changes regardless of your CLI config.

2. **Use the CLI config diff file**:
   ```bash
   ngpt -g --diff
   ```
   This explicitly tells ngpt to use the diff file specified in your CLI config.

3. **Use a specific diff file** (override CLI config):
   ```bash
   ngpt -g --diff /path/to/another.diff
   ```
   This overrides both git staged changes and your CLI config to use the specified file.

This approach gives you flexibility with a default diff file while maintaining explicit control over when it's used.

## Commit Message Format

The generated commit messages follow the conventional commit format:

```
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>
```

Where the types include:
- `feat`: New user-facing features
- `fix`: Bug fixes or error corrections
- `refactor`: Code restructuring (no behavior change)
- `style`: Formatting/whitespace changes only
- `docs`: Documentation only
- `test`: Test-related changes
- `perf`: Performance improvements
- `build`: Build system changes
- `ci`: CI/CD pipeline changes
- `chore`: Routine maintenance tasks
- `revert`: Reverting previous changes
- `add`: New files without user-facing features
- `remove`: Removing files/code
- `update`: Changes to existing functionality
- `security`: Security-related changes
- `config`: Configuration changes
- `ui`: User interface changes
- `api`: API-related changes

## How It Works

The git commit message generation process follows these steps:

1. Retrieves diff content (from staged changes or specified diff file)
2. If recursive chunking is enabled:
   - Splits the diff into smaller chunks (based on --chunk-size)
   - Analyzes each chunk separately
   - Combines the analyses into an intermediate result
   - Further analyzes the combined result to generate a final commit message
3. If not chunking, sends the entire diff to the AI for analysis
4. Post-processes the response to ensure it follows the conventional commit format
5. For large messages, condenses the output if it exceeds --max-msg-lines
6. Attempts to copy the result to the clipboard for easy pasting

## Technical Analysis Process

The commit message generation involves a sophisticated technical analysis of your code changes:

1. The tool analyzes the raw diff with a specialized technical analysis system prompt that instructs the AI to:
   - Create a detailed technical summary of all changes
   - Be 100% factual and only mention code explicitly shown in the diff
   - Identify exact function names, method names, class names, and line numbers
   - Use format 'filename:function_name()' or 'filename:line_number' for references
   - Include all significant changes with proper technical details
   - Focus on technical specifics, avoiding general statements

2. The analysis produces structured output with:
   - List of affected files with full paths
   - Detailed technical changes with specific code locations
   - Brief technical description of what the changes accomplish

3. This technical analysis is then used to generate the conventional commit message with the appropriate type prefixes and detailed references.

4. For large changes with recursive chunking, each chunk gets its own technical analysis before being combined into a unified understanding.

This process ensures that commit messages are accurate, detailed, and follow best practices with proper file and function references.

## Example Output

```
feat(auth): Add OAuth2 authentication flow

- [feat] Implement OAuth2 provider in auth/oauth.py:get_oauth_client()
- [feat] Add token validation in auth/utils.py:validate_token()
- [test] Add integration tests for OAuth flow in tests/auth/test_oauth.py
- [docs] Update authentication docs in README.md
```

The generated commit messages include:
1. Type prefix (feat, fix, docs, etc.)
2. Optional scope in parentheses
3. Brief summary
4. Detailed bullet points with file and function references

## GitHub Visualization

The conventional commit messages generated by `--gitcommsg` work great with GitHub, but you can enhance the visualization further with the **GitHub Commit Labels** userscript.

This userscript automatically adds beautiful colored labels for conventional commit types, making your commit history more readable and visually appealing.

### Installation and Features

1. Install a userscript manager like Tampermonkey for your browser
2. Install the [GitHub Commit Labels](https://greasyfork.org/en/scripts/526153-github-commit-labels) userscript

Key features:
- Adds colored labels to conventional commit messages
- Supports all standard commit types (feat, fix, docs, etc.)
- Works with GitHub's light, dark, and dark dimmed themes
- Adds helpful tooltips showing detailed descriptions
- Highlights breaking changes using `type!:` or `type(scope)!:`

The userscript automatically detects the conventional commit format produced by `ngpt --gitcommsg`, enhancing the readability of your commit history on GitHub.

## Logging

To debug issues or review the AI's analysis process, use the `--log` option:

```bash
# Log to a specific file
ngpt -g --log commit_log.txt

# Create a temporary log file automatically
ngpt -g --log
```

The log will include:
- Complete diff content
- Analysis chunks
- System prompts
- API requests and responses
- Error messages (if any)

## Requirements

- Git must be installed and available in your PATH
- You must be in a git repository
- For commit message generation, you need staged changes (`git add`)

## Error Handling

The tool handles various error conditions:
- No staged changes (prompts you to stage changes with `git add`)
- Invalid diff file (displays error and exits)
- API rate limits (implements automatic retries with exponential backoff)
- Token limit errors (suggests using the chunking mechanism)

## Automatic Clipboard Copy

When a commit message is successfully generated, the tool attempts to copy it to your clipboard for easy pasting into your git commit command. 