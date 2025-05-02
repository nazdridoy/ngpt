---
layout: default
title: Git Commit Message Generation
parent: Usage
nav_order: 3
permalink: /usage/gitcommsg/
---

# Git Commit Message Generation

nGPT offers a powerful feature for automatically generating conventional, detailed commit messages from git diffs. This guide explains how to use and customize this functionality.

## Overview

The git commit message generation feature (`-g` or `--gitcommsg` flag) analyzes your staged changes (or a provided diff file) and generates a comprehensive commit message following the [Conventional Commits](https://www.conventionalcommits.org/) format.

This helps create professional, standardized commit messages with minimal effort, which improves repository history readability and integrates well with automated tools like semantic versioning.

## Basic Usage

To generate a commit message from your currently staged changes:

```bash
ngpt -g
```

or

```bash
ngpt --gitcommsg
```

This will:
1. Extract the diff from your staged changes
2. Analyze the changes to understand what was modified
3. Generate an appropriate commit message with type, scope, subject, and description
4. Display the message ready for use in your git commit

## Example Output

Here's an example of the generated output:

```
feat(auth): implement OAuth2 authentication flow

- [feat] Create new AuthService class to handle token management
- [feat] Implement login/logout functionality in UserController
- [feat] Add configuration options for OAuth providers
- [Update] Update user model to store OAuth tokens
- [feat] Add unit tests for authentication flow

```

## Full Command Options

```
ngpt --gitcommsg [OPTIONS]
```

Available options:

| Option | Description |
|--------|-------------|
| `--rec-chunk` | Process large diffs in chunks with recursive analysis |
| `--diff [FILE]` | Use diff from specified file instead of staged changes |
| `--chunk-size N` | Number of lines per chunk when chunking is enabled (default: 200) |
| `--analyses-chunk-size N` | Number of lines per chunk when recursively chunking analyses (default: 200) |
| `--max-msg-lines N` | Maximum number of lines in commit message before condensing (default: 20) |
| `--max-recursion-depth N` | Maximum recursion depth for commit message condensing (default: 3) |
| `--preprompt TEXT` | Provide context or directives for message generation |
| `--log [FILE]` | Log the analysis process for debugging |

## Working with Large Diffs

For large changes, the basic approach might not capture all details. Use the recursive chunking feature:

```bash
ngpt -g --rec-chunk
```

This splits the diff into manageable chunks, analyzes each separately, and then recursively synthesizes a cohesive commit message.

You can adjust chunk sizes for large diffs:

```bash
ngpt -g --rec-chunk --chunk-size 300 --analyses-chunk-size 250
```

This helps balance detail and coherence when processing extensive changes.

## Using a Diff File

Instead of analyzing staged changes, you can use a pre-saved diff file:

```bash
# Generate a diff file
git diff > my-changes.diff

# Use the diff file to generate a commit message
ngpt -g --diff my-changes.diff
```

You can also set a default diff file in your CLI configuration:

```bash
ngpt --cli-config set diff /path/to/default.diff
```

This is useful for:
- Analyzing changes without staging them
- Working with historical diffs
- Sharing change analysis across machines
- Creating template-based workflows

## Guiding Message Generation

You can use the `--preprompt` option to provide context or directives for the message generation:

```bash
# Indicate it's a feature implementation
ngpt -g --preprompt "type:feat"

# Specify the scope and intent
ngpt -g --preprompt "type:fix scope:authentication This fixes the broken login flow"

# Provide project context
ngpt -g --preprompt "This is part of the user management system refactoring"
```

## Limiting Message Length

By default, nGPT limits commit messages to a reasonable length. You can customize this:

```bash
# Limit to 10 lines
ngpt -g --max-msg-lines 10

# Allow longer messages
ngpt -g --max-msg-lines 30
```

For very large changes, nGPT might need to use recursive condensing to create a concise message. You can adjust this:

```bash
ngpt -g --max-recursion-depth 4
```

## Logging the Analysis Process

For complex diffs, it can be helpful to see the analysis process:

```bash
# Log to a specific file
ngpt -g --log commit_analysis.log

# Create a temporary log file automatically
ngpt -g --log
```

This is valuable when:
- The generated message doesn't seem to capture the changes properly
- You want to understand the analysis process
- You're debugging issues with message generation

## Integration with Git Workflow

You can integrate nGPT with your git workflow in several ways:

### Using as Git Prepare-Commit-Msg Hook

Create a git hook in `.git/hooks/prepare-commit-msg`:

```bash
#!/bin/bash
# Skip if commit message is already provided
if [ -z "$(cat $1 | grep -v '^#')" ]; then
  # Generate commit message with nGPT and write to commit message file
  ngpt -g --no-stream | tee $1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/prepare-commit-msg
```

### Creating an Alias

Add a git alias in your `.gitconfig`:

```
[alias]
  ai-commit = "!ngpt -g | git commit -F -"
```

Now you can use:
```bash
git add .
git ai-commit
```

### Using with Conventional Commit Tools

nGPT works well with tools like Commitizen. You can generate a message with nGPT and then use it as a template in Commitizen.

## Best Practices

- **Stage Carefully**: Only stage the changes you want included in a single logical commit
- **Review Before Committing**: Always review the generated message before using it
- **Use Recursive Chunking**: For large changes, enable recursive chunking for better analysis
- **Provide Context**: Use `--preprompt` to give hints about the type or scope of your changes
- **Customize for Your Project**: Consider creating project-specific aliases or scripts

## Troubleshooting

### Message Quality Issues

If the generated messages don't accurately reflect your changes:

1. Try with `--rec-chunk` for better analysis of large diffs
2. Provide more context with `--preprompt`
3. Break very large changes into smaller, logical commits
4. Use `--log` to understand the analysis process

### Performance Issues

For large repositories or diffs:

1. Use a more focused diff (e.g., specific files)
2. Adjust chunk sizes to balance speed and detail
3. Consider using a more powerful LLM model by switching providers

### Formatting Issues

If commit message formatting doesn't match your project's style:

1. Provide an example format in the preprompt
2. Post-process the output with additional tools
3. Create a custom processing script for project-specific needs

## Examples

### Basic Feature Implementation

```bash
# Stage changes
git add src/components/Login.jsx src/services/auth.js

# Generate commit message
ngpt -g --preprompt "type:feat"
```

### Complex Bug Fix with Recursive Chunking

```bash
# Stage all related changes
git add .

# Generate detailed analysis
ngpt -g --rec-chunk --preprompt "type:fix scope:performance" --log perf_fix.log
```

### Documentation Update

```bash
# Stage documentation changes
git add docs/ README.md

# Generate focused commit message
ngpt -g --preprompt "type:docs This updates the API documentation"
```

### GitHub Commit Labels Integration

For better visualization of conventional commit messages on GitHub, you can use the [GitHub Commit Labels](https://greasyfork.org/en/scripts/526153-github-commit-labels) userscript, which adds colorful labels to your commits based on the conventional commit type. 