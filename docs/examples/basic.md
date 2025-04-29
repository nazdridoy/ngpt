# Basic Examples

This page provides basic examples to help you get started with nGPT. These examples cover the fundamental functionality of the library.

## Setup

First, make sure you've installed nGPT and configured your API key:

```bash
# Install nGPT
pip install ngpt

# Configure nGPT (interactive)
ngpt --config
```

## Library Examples

### Basic Chat

The simplest way to use nGPT is to send a chat message and get a response:

```python
from ngpt import NGPTClient, load_config

# Load configuration from the config file
config = load_config()

# Initialize the client
client = NGPTClient(**config)

# Send a chat message
response = client.chat("Tell me about quantum computing")
print(response)
```

### Streaming Responses

For a better user experience, you can stream responses in real-time:

```python
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)

# Stream the response
print("Streaming response:")
for chunk in client.chat("Explain how neural networks work", stream=True):
    print(chunk, end="", flush=True)
print()  # Final newline
```

### Generating Code

Generate clean code without markdown formatting:

```python
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)

# Generate Python code
python_code = client.generate_code("function to calculate the factorial of a number")
print("Python code:")
print(python_code)
print()

# Generate JavaScript code
js_code = client.generate_code(
    "function to validate email addresses",
    language="javascript"
)
print("JavaScript code:")
print(js_code)
```

### Generating Shell Commands

Generate OS-aware shell commands:

```python
from ngpt import NGPTClient, load_config
import subprocess

config = load_config()
client = NGPTClient(**config)

# Generate a shell command
command = client.generate_shell_command("list all directories sorted by size")
print(f"Generated command: {command}")

# Execute the command (optional)
try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print("Command output:")
    print(result.stdout)
except Exception as e:
    print(f"Error executing command: {e}")
```

### Direct Initialization

You can also initialize the client directly without using a configuration file:

```python
from ngpt import NGPTClient

# Initialize with direct parameters
client = NGPTClient(
    api_key="your-api-key",  # Replace with your actual API key
    base_url="https://api.openai.com/v1/",
    provider="OpenAI",
    model="gpt-3.5-turbo"
)

response = client.chat("Hello, how are you?")
print(response)
```

### Using Web Search

If your API provider supports web search capability:

```python
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)

# Enable web search
response = client.chat(
    "What are the latest developments in quantum computing?",
    web_search=True
)
print(response)
```

### Using Custom System Prompts

Customize the model's behavior with system prompts:

```python
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)

# Use a custom system prompt
system_prompt = "You are a helpful coding assistant specializing in Python. Keep your answers concise and efficient."
response = client.chat(
    "How do I read a CSV file?",
    system_prompt=system_prompt
)
print(response)
```

## CLI Examples

### Basic Usage

```bash
# Simple chat
ngpt "Tell me about quantum computing"

# No streaming (wait for full response)
ngpt --no-stream "Explain the theory of relativity"

# Prettify markdown output
ngpt --prettify "Create a markdown table comparing different programming languages"

# Real-time markdown formatting with streaming
ngpt --stream-prettify "Explain machine learning algorithms with examples"

# Use a different provider 
ngpt --provider Groq "Explain quantum computing"
```

### Code Generation

```bash
# Generate Python code (default)
ngpt -c "function to calculate prime numbers"

# Generate specific language code
ngpt -c "create a React component that displays a counter" --language jsx

# Generate code with syntax highlighting
ngpt -c --prettify "implement a binary search tree"

# Generate code with real-time syntax highlighting
ngpt -c --stream-prettify "write a function to sort an array using quicksort"

# Set a custom temperature for more varied code
ngpt -c --temperature 0.8 "function to find palindromes in a string"
```

### Shell Commands

```bash
# Generate and execute a shell command
ngpt -s "find all JPG files in the current directory and subdirectories"

# Generate command to find large files
ngpt -s "show the 10 largest files in the home directory"

# Generate a command to monitor system resources
ngpt -s "show real-time CPU and memory usage"
```

### Interactive Chat

```bash
# Start an interactive chat session with conversation memory
ngpt -i

# Start an interactive session with prettified output
ngpt -i --prettify

# Start an interactive session with real-time markdown rendering
ngpt -i --stream-prettify

# Start an interactive session with a custom system prompt
ngpt -i --preprompt "You are a Python expert helping with data analysis"

# Start an interactive session with logging
ngpt -i --log conversation.log
```

### Multiline Input

```bash
# Open a multiline editor for a complex prompt
ngpt -t

# Open multiline editor with a preprompt
ngpt -t --preprompt "You are a markdown documentation expert"
```

### Working with STDIN

```bash
# Process text from stdin
cat file.txt | ngpt -p "Summarize this: {}"

# Analyze code from stdin
cat script.py | ngpt -p "Review this Python code and suggest improvements: {}"

# Process JSON data
curl https://api.example.com/data | ngpt -p "Parse this JSON data and explain what it contains: {}"
```

### Text Rewriting

```bash
# Rewrite a text to improve quality
ngpt --rewrite "This is a draft text that needs to be better written with improved grammar and style"

# Rewrite text from a file
cat draft.txt | ngpt -r

# Rewrite with specific guidance
echo "Text to improve" | ngpt -r --preprompt "Improve this text while making it more formal and professional"
```

### Git Commit Message Generation

```bash
# Generate commit message for staged changes
ngpt --gitcommsg

# Generate commit message with specific type
ngpt -g --preprompt "type:feat"

# Generate message for large changes with recursive analysis
ngpt -g --rec-chunk

# Process a specific diff file
ngpt -g --diff changes.diff

# Log the commit message generation process
ngpt -g --log commit_debug.log
```

> **Tip**: For better visualization of conventional commit messages on GitHub, you can use the [GitHub Commit Labels](https://greasyfork.org/en/scripts/526153-github-commit-labels) userscript, which adds colorful labels to your commits.

## Using CLI Config

nGPT supports persistent CLI configuration for setting default values:

```bash
# Set default configuration options
ngpt --cli-config set temperature 0.7
ngpt --cli-config set language typescript

# Use the defaults (no need to specify options)
ngpt -c "function to sort an array"  # Will use typescript

# View current settings
ngpt --cli-config get

# Remove a setting
ngpt --cli-config unset language

# List all available CLI configuration options
ngpt --cli-config list
```

## Working with Multiple Providers

nGPT allows easy switching between different LLM providers:

```bash
# List all configured providers
ngpt --show-config --all

# Use a specific provider by name
ngpt --provider OpenAI "Explain quantum computing"
ngpt --provider Groq "Explain quantum computing"
ngpt --provider Claude "Explain quantum computing"

# Set a default provider in CLI config
ngpt --cli-config set provider Groq

# Compare results
ngpt --provider OpenAI "Explain quantum entanglement" > openai_result.txt
ngpt --provider Groq "Explain quantum entanglement" > groq_result.txt
```

## Using Different Modes

nGPT supports different modes which can also be utilized in your code:

```python
from ngpt import NGPTClient, load_config
from ngpt.cli.modes.chat import chat_mode
from ngpt.cli.modes.code import code_mode

config = load_config()
client = NGPTClient(**config)

# Use chat mode
chat_mode(client, "Tell me about quantum computing", prettify=True)

# Use code mode
code_mode(client, "function to calculate factorial", language="python")
```

## Complete Example: Simple Chatbot

Here's a complete example of a simple chatbot:

```python
from ngpt import NGPTClient, load_config

def simple_chatbot():
    # Initialize client
    config = load_config()
    client = NGPTClient(**config)
    
    print("Simple Chatbot")
    print("Type 'exit' to quit")
    print("-" * 50)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        
        print("Bot: ", end="")
        for chunk in client.chat(user_input, stream=True):
            print(chunk, end="", flush=True)
        print()  # Final newline

if __name__ == "__main__":
    simple_chatbot()
```

Save this script as `simple_chatbot.py` and run it with `python simple_chatbot.py`.

## Building a Simple Document Analyzer

Here's an example of a document analyzer using nGPT:

```python
import sys
from ngpt import NGPTClient, load_config

def analyze_document(file_path):
    # Read the file
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Initialize the client
    config = load_config()
    client = NGPTClient(**config)
    
    # Create analysis prompt
    prompt = f"""
    Analyze the following document and provide:
    1. A concise summary (max 3 sentences)
    2. Key topics/themes
    3. Tone analysis
    4. Suggested improvements (if applicable)
    
    Document content:
    {content}
    """
    
    # Get analysis
    print("Analyzing document...")
    response = client.chat(prompt)
    print("\nDocument Analysis:")
    print("-" * 50)
    print(response)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_document.py <file_path>")
        sys.exit(1)
    analyze_document(sys.argv[1])
```

Save this script as `analyze_document.py` and run it with `python analyze_document.py your_document.txt`.

## Next Steps

Once you're comfortable with these basic examples, check out the [Advanced Examples](advanced.md) for more sophisticated use cases. 