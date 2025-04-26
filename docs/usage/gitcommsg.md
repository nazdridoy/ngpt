# Git Commit Message Generation

The `--gitcommsg` mode in NGPT helps you generate high-quality, conventional commit messages using AI to analyze your git diffs.

## Basic Usage

```bash
# Generate commit message from staged changes
ngpt --gitcommsg

# Generate commit message with context/directives
ngpt --gitcommsg -m "type:feat"

# Process large diffs in chunks with recursive analysis
ngpt --gitcommsg -r

# Use a diff file instead of staged changes
ngpt --gitcommsg --diff /path/to/changes.diff

# Enable logging for debugging
ngpt --gitcommsg --log
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `-m, --message-context` | Context to guide AI (file types, commit type directive, focus) |
| `-r, --recursive-chunk` | Process large diffs in chunks with recursive analysis if needed |
| `--diff FILE` | Use diff from specified file instead of staged changes |
| `--log [FILE]` | Enable detailed logging (to specified file or auto-generated temp file) |
| `--chunk-size NUM` | Set number of lines per chunk (default: 200) |
| `--max-depth NUM` | Maximum recursion depth for recursive chunking (default: 3) |

## Context Directives

The `-m/--message-context` option is powerful and supports several directive types:

### Commit Type Directive

Force a specific commit type prefix:

```bash
# Force "feat:" prefix
ngpt --gitcommsg -m "type:feat"

# Force "fix:" prefix 
ngpt --gitcommsg -m "type:fix"

# Force "docs:" prefix
ngpt --gitcommsg -m "type:docs"
```

### File Type Filtering

Focus only on specific file types:

```bash
# Focus only on JavaScript changes
ngpt --gitcommsg -m "javascript"

# Focus only on CSS files 
ngpt --gitcommsg -m "css"

# Focus only on Python files
ngpt --gitcommsg -m "python"
```

### Focus/Exclusion Directives

Control what to include or exclude:

```bash
# Focus only on authentication-related changes
ngpt --gitcommsg -m "focus on auth"

# Ignore formatting changes
ngpt --gitcommsg -m "ignore formatting"

# Exclude test files from the summary
ngpt --gitcommsg -m "exclude tests"
```

### Combined Directives

You can combine multiple directives:

```bash
# Force "feat:" prefix and focus only on UI changes
ngpt --gitcommsg -m "type:feat focus on UI"

# Force "fix:" prefix and ignore formatting changes
ngpt --gitcommsg -m "type:fix ignore formatting"
```

## Chunking Mechanism

When processing large diffs with `-r/--recursive-chunk`, the chunking mechanism helps manage rate limits and token limits:

1. Diffs are split into 200-line chunks and processed separately
2. The partial analyses are then combined into a final commit message
3. If the combined analysis is still too large, it's recursively processed again

This is particularly useful for large pull requests or commits with many changes.

## CLI Configuration

You can set default values for gitcommsg options:

```bash
# Set default chunk size
ngpt --cli-config set chunk-size 150

# Enable recursive chunking by default
ngpt --cli-config set recursive-chunk true
```

## Example Output

```
feat(auth): Add OAuth2 authentication flow

- [feat] Implement OAuth2 provider in auth/oauth.py:get_oauth_client()
- [feat] Add token validation in auth/utils.py:validate_token()
- [test] Add integration tests for OAuth flow in tests/auth/test_oauth.py
- [docs] Update authentication docs in README.md
```

The generated commit messages follow the conventional commit format with:
1. Type prefix (feat, fix, docs, etc.)
2. Optional scope in parentheses
3. Brief summary
4. Detailed bullet points with file and function references

## Requirements

- Git must be installed and available in your PATH
- You must be in a git repository
- For commit message generation, you need staged changes (`git add`)

## Error Handling

The command includes robust error handling:
- Checks if in a git repository
- Verifies staged changes exist
- Includes automatic retries with exponential backoff for API failures
- Provides detailed logs when `--log` is enabled 