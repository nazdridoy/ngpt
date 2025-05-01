---
layout: default
title: Advanced Examples
parent: Examples
nav_order: 2
permalink: /examples/advanced/
---

# Advanced Examples

This page provides more complex and advanced examples of using nGPT's capabilities. These examples build on the [basic examples](basic.md) and demonstrate more sophisticated usage patterns.

## Advanced Chat Techniques

### Session-Based Workflows

Create focused chat sessions for specific tasks:

```bash
# Start a brainstorming session
ngpt -i --preprompt "You are a creative consultant. Help me brainstorm ideas. Be concise but insightful. Ask probing questions to expand my thinking." --log brainstorm_session.log

# Start a code review session
ngpt -i --preprompt "You are an expert software engineer reviewing my code. Ask me questions about my implementation and suggest improvements focusing on performance, security, and maintainability." --log code_review.log

# Start a learning session
ngpt -i --preprompt "You are a tutor teaching me about quantum computing. Start with the basics and progressively move to more advanced concepts. Check my understanding periodically." --log quantum_learning.log
```

### Custom Role Definitions

Create detailed role definitions for specialized assistance:

```bash
# Technical writing assistant
ngpt -i --preprompt "You are a technical documentation specialist with expertise in explaining complex concepts clearly and concisely. Help me document my API with these guidelines: 1) Use active voice, 2) Include examples for each endpoint, 3) Explain parameters thoroughly, 4) Highlight potential errors, 5) Keep explanations brief but complete."

# Product manager assistant
ngpt -i --preprompt "You are a product manager helping me refine feature ideas. For each feature I discuss, help me consider: 1) User value, 2) Implementation complexity, 3) Success metrics, 4) Potential risks, 5) Alternatives. Be critical but constructive."
```

### Dynamic System Prompts

Use detailed, structured system prompts to create specific behaviors:

```bash
# Create a detailed prompt from a file
cat structured_prompt.txt | ngpt -i --pipe "--preprompt {}"

# Technical review prompt
ngpt --preprompt "Act as a senior software engineer reviewing my code. 
Focus on:
1. Performance optimization
2. Security vulnerabilities
3. Maintainability issues
4. Best practices
5. Edge cases

For each issue you identify:
- Explain why it's a problem
- Rate severity (Low/Medium/High)
- Suggest a specific solution
- Provide a code example of the fix" "Here's my authentication function: [code snippet]"
```

## Advanced Shell Command Generation

### Complex Command Pipelines

Generate sophisticated command chains:

```bash
# Process and analyze log files
ngpt --shell "find all error logs from the last week, extract the most frequent error types, and create a summary report"

# Complex data processing
ngpt --shell "download CSV data from our API, filter rows where the status is 'failed', group by error type, calculate count and percentage for each group, and output as a JSON file"

# System monitoring script
ngpt --shell "create a script that monitors CPU, memory, and disk usage every 5 minutes, alerts if any exceeds 80%, and logs the results to a timestamped file"
```

### Creating Scripts from Natural Language

Generate complete scripts from descriptions:

```bash
# Python script generation
ngpt --shell "create a Python script that watches a directory for new files, processes any new images by resizing them and adding a watermark, then moves them to a 'processed' folder"

# Bash script for deployment
ngpt --shell "create a bash script for deploying our application that backs up the current version, pulls the latest code, runs tests, and rolls back automatically if any tests fail"
```

### Customizing for Different Environments

Generate commands with environment-specific considerations:

```bash
# Generate commands for a production environment
ngpt --shell --preprompt "You are generating commands for a production Linux server. Prioritize safety, use proper error handling, and never perform destructive operations without confirmation." "update all packages and reboot if necessary"

# Generate commands for a Docker environment
ngpt --shell --preprompt "You are working in a Docker environment. Use Docker and Docker Compose commands. Remember that filesystem changes inside containers are ephemeral unless volumes are used." "set up a development environment with Postgres and Redis"
```

## Advanced Code Generation

### Creating Complete Applications

Generate full application components:

```bash
# Generate a RESTful API controller
ngpt --code --language typescript --preprompt "Generate a complete TypeScript Express controller for a user management API with the following endpoints: register, login, getProfile, updateProfile, and deleteAccount. Include input validation, error handling, and authentication checks." "user controller"

# Generate a React component
ngpt --code --language javascript --preprompt "Create a React functional component for a data table with sorting, filtering, and pagination. Use React hooks, include PropTypes, and add comprehensive comments." "DataTable component"
```

### Language-Specific Optimizations

Generate code with language-specific best practices:

```bash
# Generate Python with type hints
ngpt --code --language python --preprompt "Generate Python code with type hints (using the typing module). Follow PEP 8 style guidelines. Include docstrings in Google format." "function to parse and validate configuration from a YAML file"

# Generate Rust with memory safety considerations
ngpt --code --language rust --preprompt "Generate Rust code that's memory safe and efficient. Avoid unnecessary clones, use proper error handling with Result types, and leverage Rust's ownership system." "function to process a large file in chunks"
```

### Iterative Code Development

Use nGPT to refine code iteratively:

```bash
# Get initial implementation
ngpt --code "implementation of quicksort algorithm" > quicksort.py

# Request optimization
cat quicksort.py | ngpt --pipe "Optimize this quicksort implementation for better performance: {}" > quicksort_optimized.py

# Request tests
cat quicksort_optimized.py | ngpt --code --pipe "Write unit tests for this quicksort implementation: {}" > test_quicksort.py
```

## Advanced Text Rewriting

### Style Transformations

Transform text to match specific styles or formats:

```bash
# Academic to casual transformation
cat academic_paper.txt | ngpt --pipe "Transform this academic text into a casual blog post while preserving all the key information: {}"

# Technical to marketing transformation
cat technical_specs.txt | ngpt --pipe "Convert these technical specifications into compelling marketing copy that highlights benefits for non-technical users: {}"

# Long-form to bullet points
cat detailed_report.txt | ngpt --pipe "Convert this detailed report into a concise bullet-point summary capturing all key points: {}"
```

### Audience-Specific Rewrites

Adapt content for different audiences:

```bash
# Rewrite for developers
cat product_overview.txt | ngpt --pipe "Rewrite this product overview specifically for software developers, emphasizing API capabilities, integration options, and technical specifications: {}"

# Rewrite for executives
cat technical_proposal.txt | ngpt --pipe "Rewrite this technical proposal for a C-level executive audience, focusing on business value, ROI, and strategic advantages while minimizing technical details: {}"

# Rewrite for beginners
cat advanced_tutorial.txt | ngpt --pipe "Rewrite this advanced tutorial for absolute beginners. Explain all jargon, add more context, and break complex concepts into simpler steps: {}"
```

### Specialized Content Enhancement

Improve specific types of content:

```bash
# Enhance error messages
cat error_messages.txt | ngpt --pipe "Improve these error messages to be more user-friendly, clear, and actionable: {}"

# Enhance API documentation
cat api_docs.txt | ngpt --pipe "Enhance this API documentation with better explanations, more examples, and clearer parameter descriptions: {}"

# Enhance product descriptions
cat product_descriptions.txt | ngpt --pipe "Improve these product descriptions by adding more vivid language, highlighting unique features, and addressing common customer pain points: {}"
```

## Advanced Git Commit Message Generation

### Working with Large Codebases

Process large changes effectively:

```bash
# Generate commit message for large refactoring
git add .
ngpt --gitcommsg --rec-chunk --chunk-size 300 --preprompt "type:refactor This is a major refactoring of the authentication system to support multi-factor authentication."

# Analyze only specific components
git diff --staged -- src/components/ src/services/ > component_changes.diff
ngpt --gitcommsg --diff component_changes.diff
```

### Specialized Commit Types

Generate messages for specific types of changes:

```bash
# Major feature release
ngpt --gitcommsg --preprompt "type:feat This is a major feature release that should be highlighted in the changelog."

# Breaking change
ngpt --gitcommsg --preprompt "type:feat This includes a breaking change to the API. Previous endpoints for user authentication are no longer supported."

# Performance improvement
ngpt --gitcommsg --preprompt "type:perf This commit focuses on performance improvements to the database query system."
```

### Integration with Development Workflow

Set up efficient workflows with nGPT:

```bash
# Review changes then generate commit
git diff --staged | less
ngpt --gitcommsg --log commit_process.log

# Create a draft commit message for team review
ngpt --gitcommsg --no-stream > draft_commit.txt
vim draft_commit.txt
git commit -F draft_commit.txt
```

## Advanced Configuration and Workflow

### Provider-Specific Workflows

Customize workflows for different providers:

```bash
# Set up provider-specific CLI configurations
ngpt --cli-config set provider OpenAI
ngpt --cli-config set temperature 0.7
ngpt --cli-config set model gpt-4

# Switch to a different configuration for different tasks
ngpt --provider Groq --model llama3-70b-8192 "Explain quantum computing"
ngpt --provider OpenAI --model gpt-4o-mini "Generate a short poem"
```

### Environment Variables for CI/CD

Use environment variables in automated environments:

```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"
export OPENAI_MODEL="gpt-4"
export OPENAI_BASE_URL="https://api.openai.com/v1/"

# Use in a script without hardcoded credentials
echo "Generating documentation..."
cat api_endpoints.json | ngpt --pipe "Generate markdown documentation for these API endpoints: {}" > API.md
```

### Pipes and Redirection in Scripts

Create sophisticated processing pipelines:

```bash
#!/bin/bash
# Example script for processing documentation

# Extract code examples
grep -r "```" docs/ > code_examples.txt

# Generate test cases from examples
cat code_examples.txt | ngpt --pipe "Generate test cases for these code examples: {}" > test_cases.txt

# Generate documentation from test cases
cat test_cases.txt | ngpt --pipe "Generate documentation explaining these test cases: {}" > test_docs.md
```

## Workflow Recipes

These examples combine multiple nGPT features to solve real-world problems:

### Code Review Workflow

```bash
#!/bin/bash
# Automated code review script

# Get diff of changes
git diff main... > changes.diff

# Generate initial review
cat changes.diff | ngpt --pipe "Review this code diff and identify potential issues: {}" > review.md

# Generate focused test cases for the changes
cat changes.diff | ngpt --pipe "Generate test cases to verify these code changes: {}" > tests.md

# Generate summary with key points
cat review.md | ngpt --pipe "Summarize these code review findings into 3-5 key points: {}" > summary.md

echo "Code review complete. See review.md, tests.md, and summary.md"
```

### Documentation Generation Workflow

```bash
#!/bin/bash
# Generate comprehensive documentation for a project

# Generate project overview
ngpt --preprompt "You are a technical writer creating documentation" "Create a project overview for our application called SkyTracker, which is a cloud resource monitoring tool" > docs/overview.md

# Generate API documentation from source files
find src/api -name "*.js" -exec cat {} \; | ngpt --pipe "Generate API documentation from these source files: {}" > docs/api.md

# Generate user guide from features list
cat features.txt | ngpt --pipe "Create a user guide based on these features: {}" > docs/user-guide.md

# Generate FAQ
cat issues.txt | ngpt --pipe "Generate a FAQ based on these common issues: {}" > docs/faq.md

echo "Documentation generation complete"
```

### Data Analysis Workflow

```bash
#!/bin/bash
# Analyze data and generate reports

# Extract insights from CSV data
cat data.csv | ngpt --pipe "Analyze this CSV data and identify key trends and insights: {}" > analysis.md

# Generate visualizations recommendations
cat analysis.md | ngpt --pipe "Recommend specific visualizations for these insights: {}" > visualizations.md

# Create executive summary
cat analysis.md | ngpt --pipe "Create a 1-page executive summary of these analytical findings: {}" > executive-summary.md

echo "Data analysis workflow complete"
```

## Next Steps

For more information on specific nGPT capabilities, refer to:

- [CLI Usage Guide](../usage/cli_usage.md)
- [CLI Configuration Guide](../usage/cli_config.md)
- [Git Commit Message Guide](../usage/gitcommsg.md) 