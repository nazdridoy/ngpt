# Installation Guide

This guide provides detailed instructions for installing nGPT on various platforms.

## Basic Installation

### Using pip

nGPT can be installed using pip:

```bash
pip install ngpt
```

### Using uv

For faster installation and better dependency resolution, you can use [uv](https://github.com/astral-sh/uv):

```bash
# Install uv if you don't have it yet
curl -sSf https://astral.sh/uv/install.sh | sh

# Install ngpt with uv
uv pip install ngpt
```

### Using uv tool (Recommended for CLI usage)

Since nGPT is primarily used as a command-line tool, you can install it globally using uv's tool installer:

```bash
# Install uv if you don't have it yet
curl -sSf https://astral.sh/uv/install.sh | sh

# Install ngpt as a global tool
uv tool install ngpt
```

This method:
- Installs nGPT globally so it's available from any directory
- Isolates the installation from your other Python environments
- Automatically manages dependencies
- Provides the fastest installation experience

Any of these methods will install nGPT with all its dependencies, including support for markdown rendering and interactive sessions.

## Requirements

nGPT requires:

- Python 3.8 or newer
- `requests` library for API communication (v2.31.0 or newer)
- `rich` library for markdown formatting and syntax highlighting (v10.0.0 or newer)
- `prompt_toolkit` library for interactive features (v3.0.0 or newer)
- `pyperclip` library for clipboard operations (v1.8.0 or newer)

All required dependencies are automatically installed when you install nGPT.

## Platform-Specific Notes

### Linux/macOS

On Linux and macOS, you can install nGPT using either pip or uv:

```bash
# Using pip
pip install ngpt

# Using uv
uv pip install ngpt
```

Or, if you prefer using pipx for isolated application installations:

```bash
pipx install ngpt
```

### Arch Linux AUR

nGPT is available in the Arch User Repository (AUR). If you're using Arch Linux or an Arch-based distribution (like Manjaro, EndeavourOS, etc.), you can install nGPT from the AUR using your preferred AUR helper:

```bash
# Using paru
paru -S ngpt

# Or using yay
yay -S ngpt
```

This will install nGPT and all required dependencies managed by the Arch packaging system.

### Windows

On Windows, you can install nGPT using pip or uv:

```bash
# Using pip
pip install ngpt

# Using uv
uv pip install ngpt
```

### Installation in a Virtual Environment

It's often a good practice to install packages in a virtual environment:

#### Using pip with venv

```bash
# Create a virtual environment
python -m venv ngpt-env

# Activate the environment
# On Windows:
ngpt-env\Scripts\activate
# On Linux/macOS:
source ngpt-env/bin/activate

# Install nGPT
pip install ngpt
```

#### Using uv with virtualenv

uv can create and manage virtual environments:

```bash
# Create and activate a virtual environment + install in one step
uv venv ngpt-env
source ngpt-env/bin/activate  # On Linux/macOS
# Or on Windows:
# ngpt-env\Scripts\activate

# Install ngpt
uv pip install ngpt
```

## Optional: Installing from Source

If you want to install the latest development version from the source code:

```bash
# Clone the repository
git clone https://github.com/nazdridoy/ngpt.git
cd ngpt

# Using pip
pip install -e .

# Or using uv
uv pip install -e .
```

## Verifying Installation

To verify that nGPT is installed correctly, run:

```bash
ngpt --version
```

You should see the version number of nGPT displayed.

Alternatively, you can run nGPT as a Python module:

```bash
python -m ngpt --version
```

This method is especially useful when:
- The `ngpt` command is not in your PATH
- You're working in a virtual environment
- You want to ensure you're using the correct Python interpreter

All the functionality available through the `ngpt` command is also available through `python -m ngpt`.

## Updating nGPT

To update to the latest version:

```bash
# Using pip
pip install --upgrade ngpt

# Using uv
uv pip install --upgrade ngpt

# Using AUR (Arch Linux)
paru -Syu ngpt
# Or
yay -Syu ngpt
```

## Glow for Enhanced Markdown (Optional)

For an enhanced markdown rendering experience, you can install the Glow terminal markdown viewer:

### macOS

```bash
brew install glow
```

### Linux

```bash
# Debian/Ubuntu
sudo apt-get install glow

# Arch Linux
yay -S glow

# Using Go
go install github.com/charmbracelet/glow@latest
```

### Windows

```bash
# Using Scoop
scoop install glow

# Using Chocolatey
choco install glow
```

nGPT will automatically detect and use Glow if it's installed on your system, but it's not required as the built-in Rich renderer provides excellent markdown formatting.

## API Keys

After installation, you'll need to configure your API key. See the [Configuration Guide](configuration.md) for details.

## Troubleshooting

### Common Installation Issues

#### Package not found

If you encounter "Package not found" errors, make sure your package manager is up to date:

```bash
# For pip
pip install --upgrade pip

# For uv
curl -sSf https://astral.sh/uv/install.sh | sh
```

#### Permission Errors

If you see permission errors when installing:

```bash
# Using pip
# On Linux/macOS
pip install --user ngpt

# Or use a virtual environment (recommended)
python -m venv ngpt-env
source ngpt-env/bin/activate
pip install ngpt

# Using uv (avoids many permission issues)
uv pip install --user ngpt
# Or with virtual environment
uv venv ngpt-env
source ngpt-env/bin/activate
uv pip install ngpt
```

#### Rich or Prompt Toolkit Issues

If you experience issues with the Rich library or Prompt Toolkit:

```bash
# Using pip
pip uninstall rich prompt_toolkit pyperclip
pip install rich prompt_toolkit pyperclip
pip install ngpt

# Using uv
uv pip uninstall rich prompt_toolkit pyperclip
uv pip install rich prompt_toolkit pyperclip
uv pip install ngpt
```

### Getting Help

If you continue to experience installation issues:

1. Check the [GitHub Issues](https://github.com/nazdridoy/ngpt/issues) to see if others have encountered the same problem
2. Open a new issue if your problem hasn't been reported 