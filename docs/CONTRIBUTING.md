---
title: Contributing to NGPT
description: Guidelines and instructions for contributing to the NGPT project
---

# Contributing to NGPT

Thank you for your interest in contributing to NGPT! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/ngpt.git`
3. Navigate to the project directory: `cd ngpt`
4. Set up Python environment:
   - It's recommended to use a virtual environment
   - Create a virtual environment: `python -m venv .venv`
   - Activate the virtual environment:
     - Windows: `.venv\Scripts\activate`
     - Unix/MacOS: `source .venv/bin/activate`
5. Install dependencies: `pip install -e .` 
6. Open the project in your preferred code editor

## Code Structure

- `ngpt/` - Main package directory
  - `__init__.py` - Package initialization
  - `__main__.py` - Entry point when run as a module
  - `client.py` - Client implementation for API interaction
  - `cli/` - Command-line interface implementation
    - `__init__.py`
    - `main.py` - Main CLI application logic
    - `args.py` - Argument parsing setup
    - `config_manager.py` - CLI configuration handling
    - `formatters.py` - Output formatting logic
    - `interactive.py` - Interactive mode implementation
    - `modes/` - Different operational modes
      - `__init__.py` - Modes initialization
      - `chat.py` - Chat mode functionality
      - `code.py` - Code generation mode
      - `gitcommsg.py` - Git commit message generation
      - `shell.py` - Shell command generation
      - `text.py` - Text generation mode
      - `rewrite.py` - Text rewriting mode
    - `renderers.py` - Output rendering logic (e.g., markdown)
    - `ui.py` - User interface elements (e.g., prompts, spinners)
  - `utils/` - Utility modules
    - `__init__.py`
    - `config.py` - API endpoint and general configuration management
    - `cli_config.py` - CLI-specific option configuration management
    - `log.py` - Logging setup and utilities
- `docs/` - Documentation files
  - `api/` - API reference documentation
  - `examples/` - Example code and usage
  - `usage/` - Usage guides and tutorials
- `.github/` - GitHub workflows and templates
- `pyproject.toml` - Project configuration and dependencies

## Code Style Guidelines

- Follow PEP 8 style guidelines for Python code
- Use consistent indentation (4 spaces)
- Write descriptive docstrings for functions and classes
- Add type hints where appropriate
- Add comments for complex logic

## Pull Request Guidelines

Before submitting a pull request, please make sure that:
  
- Your code follows the project's coding conventions
- You have tested your changes thoroughly
- All existing tests pass (if applicable)
- The commit messages are clear and follow conventional commit guidelines as specified in [COMMIT_GUIDELINES.md](COMMIT_GUIDELINES.md)
- You have provided a detailed explanation of the changes in the pull request description

## Submitting Changes

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Test thoroughly
4. Commit with clear messages: `git commit -m "feat: description"`
5. Push to your fork: `git push origin feature/your-feature-name`
6. Open a Pull Request against the main repository

## Testing

Before submitting your changes, please test:

- Basic functionality
- Any new features you've added
- Any components you've modified
- Ensure all tests pass if there's a test suite

## Issue Reporting

When opening an issue, please:

- Use a clear and descriptive title
- Provide a detailed description of the issue, including the environment and steps to reproduce
- Include any relevant logs or code snippets
- Specify your Python version and operating system
- Search the repository for similar issues before creating a new one

## Feature Requests

Feature requests are welcome! To submit a feature request:

- Use a clear and descriptive title
- Provide a detailed description of the proposed feature
- Explain why this feature would be useful to NGPT users
- If possible, suggest how it might be implemented

## Questions and Discussions

For questions about the project that aren't bugs or feature requests, please use GitHub Discussions instead of opening an issue. This helps keep the issue tracker focused on bugs and features.

## License

By contributing to this project, you agree that your contributions will be licensed under the same [LICENSE](LICENSE) as the project.
