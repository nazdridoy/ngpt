# NGPTClient

`NGPTClient` is the primary class for interacting with OpenAI-compatible APIs. It provides methods for chat completion, code generation, shell command generation, and model listing.

## Initialization

```python
from ngpt import NGPTClient

client = NGPTClient(
    api_key: str = "",
    base_url: str = "https://api.openai.com/v1/",
    provider: str = "OpenAI",
    model: str = "gpt-3.5-turbo"
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | `str` | `""` | API key for authentication |
| `base_url` | `str` | `"https://api.openai.com/v1/"` | Base URL for the API endpoint |
| `provider` | `str` | `"OpenAI"` | Name of the provider (for reference only) |
| `model` | `str` | `"gpt-3.5-turbo"` | Default model to use for completion |

### Examples

```python
# Basic initialization with OpenAI
client = NGPTClient(api_key="your-openai-api-key")

# Using a different provider
client = NGPTClient(
    api_key="your-api-key",
    base_url="https://api.groq.com/openai/v1/",
    provider="Groq",
    model="llama3-70b-8192"
)

# Using a local Ollama instance
client = NGPTClient(
    api_key="",  # No key needed for local Ollama
    base_url="http://localhost:11434/v1/",
    provider="Ollama-Local",
    model="llama3"
)
```

## Chat Method

The main method for interacting with the AI model.

```python
response = client.chat(
    prompt: str,
    stream: bool = True,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    top_p: float = 1.0,
    messages: Optional[List[Dict[str, str]]] = None,
    web_search: bool = False,
    markdown_format: bool = False,
    stream_callback: Optional[callable] = None,
    **kwargs
) -> str
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | Required | The user's message |
| `stream` | `bool` | `True` | Whether to stream the response |
| `temperature` | `float` | `0.7` | Controls randomness in the response |
| `max_tokens` | `Optional[int]` | `None` | Maximum number of tokens to generate |
| `top_p` | `float` | `1.0` | Controls diversity via nucleus sampling |
| `messages` | `Optional[List[Dict[str, str]]]` | `None` | Optional list of message objects to override default behavior |
| `web_search` | `bool` | `False` | Whether to enable web search capability |
| `markdown_format` | `bool` | `False` | If True, allows markdown formatting in responses |
| `stream_callback` | `Optional[callable]` | `None` | Optional callback function for handling streaming updates |
| `**kwargs` | `Any` | `{}` | Additional arguments to pass to the API |

### Returns

If `stream=True`, returns chunks of the response as they are generated.
If `stream=False`, returns the complete response as a string.

### Examples

```python
# Basic usage
response = client.chat("Tell me about quantum computing")
print(response)

# Without streaming
response = client.chat("Tell me about quantum computing", stream=False)
print(response)

# With custom temperature (higher = more creative, lower = more deterministic)
response = client.chat("Write a poem about nature", temperature=0.9)
print(response)

# With token limit
response = client.chat("Explain the history of AI", max_tokens=100)
print(response)

# With conversation history
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, who are you?"},
    {"role": "assistant", "content": "I'm an AI assistant created to help answer questions and provide information."},
    {"role": "user", "content": "Tell me more about yourself"}
]
response = client.chat("", messages=messages)
print(response)

# Enable web search capability (if API supports it)
response = client.chat("What are the latest developments in quantum computing?", web_search=True)
print(response)

# Enable markdown formatting for rich text responses
response = client.chat("Create a table comparing programming languages", markdown_format=True)
print(response)  # Response will contain markdown formatting like tables, code blocks, etc.

# Using a callback function for streaming updates
def process_chunk(accumulated_text):
    # Process the accumulated text so far
    print(f"Received {len(accumulated_text)} characters so far")
    
response = client.chat(
    "Explain quantum computing",
    stream=True,
    stream_callback=process_chunk
)
```

## Generate Shell Command

Generates a shell command based on the prompt, optimized for the user's operating system.

```python
command = client.generate_shell_command(
    prompt: str,
    web_search: bool = False,
    temperature: float = 0.4,
    top_p: float = 0.95,
    max_tokens: Optional[int] = None
) -> str
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | Required | Description of the command to generate |
| `web_search` | `bool` | `False` | Whether to enable web search capability |
| `temperature` | `float` | `0.4` | Controls randomness in the response |
| `top_p` | `float` | `0.95` | Controls diversity via nucleus sampling |
| `max_tokens` | `Optional[int]` | `None` | Maximum number of tokens to generate |

### Returns

A string containing the generated shell command appropriate for the user's OS.

### Examples

```python
# Generate a command to find large files
command = client.generate_shell_command("find all files larger than 100MB")
print(f"Generated command: {command}")

# Execute the generated command
import subprocess
result = subprocess.run(command, shell=True, capture_output=True, text=True)
print(f"Output: {result.stdout}")

# With web search for more current command syntax
command = client.generate_shell_command(
    "show Docker container resource usage in a nice format",
    web_search=True
)
```

## Generate Code

Generates code based on the prompt.

```python
code = client.generate_code(
    prompt: str,
    language: str = "python",
    web_search: bool = False,
    temperature: float = 0.4,
    top_p: float = 0.95,
    max_tokens: Optional[int] = None,
    markdown_format: bool = False,
    stream: bool = False,
    stream_callback: Optional[callable] = None
) -> str
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | Required | Description of the code to generate |
| `language` | `str` | `"python"` | Programming language to generate code in |
| `web_search` | `bool` | `False` | Whether to enable web search capability |
| `temperature` | `float` | `0.4` | Controls randomness in the response |
| `top_p` | `float` | `0.95` | Controls diversity via nucleus sampling |
| `max_tokens` | `Optional[int]` | `None` | Maximum number of tokens to generate |
| `markdown_format` | `bool` | `False` | If True, returns code with markdown formatting including syntax highlighting |
| `stream` | `bool` | `False` | Whether to stream the response in chunks |
| `stream_callback` | `Optional[callable]` | `None` | Optional callback function for handling streaming updates |

### Returns

A string containing the generated code. If `markdown_format` is `False`, returns plain text code. If `markdown_format` is `True`, returns code formatted in markdown with appropriate syntax highlighting.

### Examples

```python
# Generate Python code (default, plain text)
python_code = client.generate_code("function to calculate fibonacci numbers")
print(python_code)

# Generate JavaScript code
js_code = client.generate_code(
    "function to validate email addresses using regex",
    language="javascript"
)
print(js_code)

# Generate code with markdown formatting for documentation or display
markdown_code = client.generate_code(
    "class that implements a binary search tree",
    language="python",
    markdown_format=True
)
# This will output code wrapped in markdown code blocks with syntax highlighting
print(markdown_code)

# Generate code with web search for latest best practices
react_code = client.generate_code(
    "create a React component that fetches and displays data from an API",
    language="jsx",
    web_search=True
)

# Generate code with streaming for real-time updates
def update_ui(code_so_far):
    # Update a UI with the code generated so far
    print(f"Generated {len(code_so_far)} characters...")

client.generate_code(
    "implement a quicksort algorithm",
    language="python",
    stream=True,
    stream_callback=update_ui
)
```

## List Models

Retrieves the list of available models from the API.

```python
models = client.list_models() -> list
```

### Returns

A list of available model objects or an empty list if the request failed.

### Examples

```python
# Get available models
models = client.list_models()

# Print model IDs
if models:
    print("Available models:")
    for model in models:
        print(f"- {model.get('id')}")
else:
    print("No models available or could not retrieve models")

# Filter for specific models
gpt4_models = [m for m in models if "gpt-4" in m.get('id', '')]
for model in gpt4_models:
    print(f"GPT-4 model: {model.get('id')}")
```

## Error Handling

The `NGPTClient` methods include basic error handling for common issues:

- HTTP errors (401, 404, 429, etc.)
- Connection errors
- Timeout errors
- JSON parsing errors

For production code, it's recommended to implement your own error handling:

```python
import requests

try:
    response = client.chat("Tell me about quantum computing")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed. Check your API key.")
    elif e.response.status_code == 429:
        print("Rate limit exceeded. Please wait and try again.")
    else:
        print(f"HTTP error: {e}")
except requests.exceptions.ConnectionError:
    print("Connection error. Check your internet and base URL.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

## See Also

- [Configuration](config.md) - Documentation for managing API configurations
- [CLI Components](cli.md) - Documentation for using CLI components with the client
- [CLI Configuration](cli_config.md) - Documentation for CLI configuration utilities 