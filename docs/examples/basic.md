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
```

### Shell Commands

```bash
# Generate and execute a shell command
ngpt -s "find all JPG files in the current directory and subdirectories"
```

### Interactive Chat

```bash
# Start an interactive chat session with conversation memory
ngpt -i
```

### Multiline Input

```bash
# Open a multiline editor for a complex prompt
ngpt -t
```

## Using CLI Config

nGPT now supports persistent CLI configuration:

```bash
# Set default configuration options
ngpt --cli-config set temperature 0.7
ngpt --cli-config set language typescript

# Use the defaults (no need to specify options)
ngpt -c "function to sort an array"  # Will use typescript
```

## Using Different Modes

nGPT now supports different modes which can also be utilized in your code:

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

## Using Web Search

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

Or using the CLI:

```bash
ngpt --web-search "What are the latest developments in quantum computing?"
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

## Next Steps

Once you're comfortable with these basic examples, check out the [Advanced Examples](advanced.md) for more sophisticated use cases. 