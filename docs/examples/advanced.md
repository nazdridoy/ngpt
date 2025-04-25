# Advanced Examples

This page covers advanced usage examples for nGPT, demonstrating more sophisticated features and techniques for both the library and CLI.

## Advanced Configuration

### Working with Multiple API Providers

You can maintain multiple configurations for different API providers and switch between them easily:

```python
from ngpt import NGPTClient, load_config

# Load configurations for different providers
openai_config = load_config(config_index=0)  # OpenAI
groq_config = load_config(config_index=1)    # Groq
ollama_config = load_config(config_index=2)  # Local Ollama

# Create clients for each provider
openai_client = NGPTClient(**openai_config)
groq_client = NGPTClient(**groq_config)
ollama_client = NGPTClient(**ollama_config)

# Function to compare responses from different providers
def compare_providers(prompt):
    print(f"Prompt: {prompt}")
    print("\nOpenAI response:")
    openai_response = openai_client.chat(prompt, stream=False)
    print(openai_response)
    
    print("\nGroq response:")
    groq_response = groq_client.chat(prompt, stream=False)
    print(groq_response)
    
    print("\nOllama response:")
    ollama_response = ollama_client.chat(prompt, stream=False)
    print(ollama_response)

# Compare responses
compare_providers("Explain quantum entanglement in simple terms")
```

### Custom System Prompts

Customize the assistant's behavior with system prompts:

```python
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)

# Define custom messages with a system prompt
messages = [
    {"role": "system", "content": "You are a helpful coding assistant that specializes in Python. Always provide brief, efficient, and Pythonic solutions. Include examples where appropriate."},
    {"role": "user", "content": "How can I read and write CSV files?"}
]

# Send the chat with custom messages
response = client.chat("", messages=messages)
print(response)
```

Using preprompts in the CLI:

```bash
# Make the model respond as a specific expert
ngpt --preprompt "You are a Linux command line expert. Focus on efficient solutions." \
     "How do I find the largest files in a directory?"

# Set content and formatting constraints
ngpt --preprompt "Your responses should be concise and include code examples." \
     "How to parse JSON in JavaScript?"

# Create a specialized tutor for interactive sessions
ngpt --interactive --preprompt "You are a Python programming tutor. Explain concepts clearly and provide helpful examples."
```

### Conversation Logging

Save your conversation history to a file for reference:

```bash
# Basic interactive session with logging to a specific file
ngpt --interactive --log python_tutoring.log

# Create an automatic temporary log file
ngpt --interactive --log

# Combine logging with custom system prompt
ngpt --interactive \
     --preprompt "You are a data science expert helping analyze experimental results." \
     --log data_analysis_session.log

# Log a focused session on a specific topic
ngpt --interactive \
     --preprompt "You are helping plan the architecture for a microservices application." \
     --log architecture_planning.log

# Log non-interactive sessions
ngpt --log "Explain quantum computing"
```

The log file contains the complete conversation transcript, including:
- Session metadata (timestamp, command used)
- All user messages
- All AI responses
- System prompts when custom preprompts are used

This is particularly useful for:
- Documenting important planning discussions
- Saving educational sessions for later review
- Keeping records of complex problem-solving processes
- Sharing conversations with team members

## Advanced Conversation Management

### Managing Conversation History

Build and maintain conversation history for context-aware responses:

```python
from ngpt import NGPTClient, load_config

def conversation_with_memory():
    config = load_config()
    client = NGPTClient(**config)
    
    # Initialize conversation history
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Maintain context throughout the conversation."}
    ]
    
    print("Conversation with Memory")
    print("Type 'exit' to quit")
    print("-" * 50)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            break
        
        # Add user message to history
        messages.append({"role": "user", "content": user_input})
        
        # Get response
        print("Assistant: ", end="")
        response_text = ""
        for chunk in client.chat("", messages=messages, stream=True):
            print(chunk, end="", flush=True)
            response_text += chunk
        print()
        
        # Add assistant response to history
        messages.append({"role": "assistant", "content": response_text})
        
        # Optional: If conversation history gets too long, you could trim it
        # while keeping the system prompt and the most recent exchanges
        if len(messages) > 10:
            # Keep system prompt and 4 most recent exchanges (8 messages)
            messages = [messages[0]] + messages[-8:]

if __name__ == "__main__":
    conversation_with_memory()
```

## Error Handling and Retry Logic

Implement robust error handling and retry logic for production applications:

```python
import time
import requests
from ngpt import NGPTClient, load_config

def chat_with_retries(prompt, max_retries=3, backoff_factor=2):
    config = load_config()
    client = NGPTClient(**config)
    
    retries = 0
    while retries <= max_retries:
        try:
            return client.chat(prompt, stream=False)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit error
                wait_time = backoff_factor ** retries
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            elif e.response.status_code == 500:  # Server error
                wait_time = backoff_factor ** retries
                print(f"Server error. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                raise  # Re-raise other HTTP errors
        except requests.exceptions.ConnectionError:
            wait_time = backoff_factor ** retries
            print(f"Connection error. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            print(f"Unexpected error: {e}")
            raise
    
    raise Exception("Maximum retry attempts exceeded")

# Use the function
try:
    response = chat_with_retries("Explain the concept of neural networks")
    print(response)
except Exception as e:
    print(f"Failed after retries: {e}")
```

## Advanced Code Generation

### Code Generation with Constraints

Generate code with specific requirements or constraints:

```python
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)

# Generate code with specific requirements
prompt = """
Create a Python function that:
1. Takes a list of dictionaries as input, where each dictionary has 'name' and 'score' keys
2. Sorts the list by score in descending order
3. Returns only the top 3 items
4. Must use list comprehensions and lambda functions
5. Must include type hints
6. Must include docstring with examples
"""

code = client.generate_code(prompt)
print(code)

# Execute the generated code to verify it works
exec(code)  # This will define the function
# Now test the function
test_data = [
    {"name": "Alice", "score": 95},
    {"name": "Bob", "score": 85},
    {"name": "Charlie", "score": 90},
    {"name": "Dave", "score": 80},
    {"name": "Eve", "score": 88}
]
# Assuming the function is called 'top_scorers'
result = locals()['top_scorers'](test_data)
print("\nFunction test result:")
print(result)
```

## Advanced Shell Command Generation

### Piping Shell Command Output

Generate and pipe shell commands for more complex operations:

```python
from ngpt import NGPTClient, load_config
import subprocess
import sys

config = load_config()
client = NGPTClient(**config)

def execute_piped_commands(description):
    command = client.generate_shell_command(description)
    print(f"Generated command: {command}")
    
    # Ask for confirmation
    confirm = input("Execute this command? (y/n): ")
    if confirm.lower() != 'y':
        return
    
    try:
        # Execute command and pipe output directly to stdout
        process = subprocess.Popen(command, shell=True, stdout=sys.stdout)
        process.communicate()
        return process.returncode
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1

# Example usage
execute_piped_commands("Find the 5 largest files in the current directory and its subdirectories, format the sizes in human-readable format")
```

## Parameter Optimization

### Temperature Control

Control the randomness of responses by adjusting the temperature:

```python
from ngpt import NGPTClient, load_config

config = load_config()
client = NGPTClient(**config)

prompt = "Write a short poem about autumn"

print("With low temperature (0.2) - more focused, deterministic:")
response_low = client.chat(prompt, temperature=0.2, stream=False)
print(response_low)
print("\n" + "-" * 50 + "\n")

print("With medium temperature (0.7) - balanced:")
response_medium = client.chat(prompt, temperature=0.7, stream=False)
print(response_medium)
print("\n" + "-" * 50 + "\n")

print("With high temperature (1.0) - more random, creative:")
response_high = client.chat(prompt, temperature=1.0, stream=False)
print(response_high)
```

## Advanced CLI Usage

### Working with Real-time Markdown Rendering

Use the stream-prettify feature for an enhanced user experience with formatted markdown in real-time:

```bash
# Basic streaming markdown
ngpt --stream-prettify "Compare and contrast different sorting algorithms with examples"

# Real-time code generation with syntax highlighting
ngpt -c --stream-prettify --language typescript "implement a React hook for managing form state"

# Interactive session with real-time markdown rendering
ngpt -i --stream-prettify
```

Combining stream-prettify with web search for up-to-date formatted information:

```bash
# Get latest news with beautified formatting in real-time
ngpt --stream-prettify --web-search "What are the latest developments in AI research?"
```

### Custom Script with argparse

Create a custom script that uses nGPT with argparse for a better CLI experience:

```python
#!/usr/bin/env python3
# save as enhanced_ngpt.py

import argparse
import sys
from ngpt import NGPTClient, load_config
from ngpt.cli.formatters import COLORS, ColoredHelpFormatter
from ngpt.cli.renderers import prettify_streaming_markdown
from ngpt.cli.modes.code import code_mode
from ngpt.cli.modes.shell import shell_mode

def main():
    parser = argparse.ArgumentParser(
        description="Enhanced nGPT Interface",
        formatter_class=ColoredHelpFormatter
    )
    parser.add_argument("prompt", nargs="?", help="The prompt to send")
    parser.add_argument("-f", "--file", help="Read prompt from file")
    parser.add_argument("-o", "--output", help="Save response to file")
    parser.add_argument("-c", "--config-index", type=int, default=0, help="Configuration index to use")
    parser.add_argument("-t", "--temperature", type=float, default=0.7, help="Temperature (0.0-1.0)")
    parser.add_argument("-m", "--model", help="Override the model to use")
    parser.add_argument("-s", "--shell", action="store_true", help="Generate shell command")
    parser.add_argument("--code", action="store_true", help="Generate code")
    parser.add_argument("--language", default="python", help="Language for code generation")
    parser.add_argument("--prettify", action="store_true", help="Enable markdown formatting")
    
    args = parser.parse_args()
    
    # Get prompt from file or command line
    if args.file:
        try:
            with open(args.file, 'r') as f:
                prompt = f.read()
        except Exception as e:
            print(f"{COLORS['yellow']}Error reading file: {e}{COLORS['reset']}", file=sys.stderr)
            return 1
    elif args.prompt:
        prompt = args.prompt
    else:
        parser.print_help()
        return 1
    
    # Load configuration
    try:
        config = load_config(config_index=args.config_index)
        
        # Override model if specified
        if args.model:
            config['model'] = args.model
            
        client = NGPTClient(**config)
    except Exception as e:
        print(f"{COLORS['yellow']}Error initializing client: {e}{COLORS['reset']}", file=sys.stderr)
        return 1
    
    # Process based on mode
    try:
        if args.shell:
            # Use shell mode
            shell_mode(client, prompt)
        elif args.code:
            # Use code mode
            code_mode(client, prompt, language=args.language)
        else:
            # Standard chat mode
            if args.prettify:
                # Set up streaming markdown renderer
                streamer = prettify_streaming_markdown(renderer='rich')
                response = client.chat(
                    prompt, 
                    temperature=args.temperature,
                    stream=True,
                    stream_callback=streamer.update_content
                )
                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(response)
                    print(f"{COLORS['green']}Response saved to {args.output}{COLORS['reset']}")
            else:
                # Simple mode
                if args.output:
                    # No streaming if saving to file
                    response = client.chat(prompt, temperature=args.temperature, stream=False)
                    with open(args.output, 'w') as f:
                        f.write(response)
                    print(f"{COLORS['green']}Response saved to {args.output}{COLORS['reset']}")
                else:
                    # Stream to console
                    full_response = ""
                    for chunk in client.chat(prompt, temperature=args.temperature, stream=True):
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    print()  # Final newline
                
        return 0
    except Exception as e:
        print(f"{COLORS['yellow']}Error: {e}{COLORS['reset']}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Usage:

```bash
# Make the script executable
chmod +x enhanced_ngpt.py

# Basic usage
./enhanced_ngpt.py "Tell me about quantum computing"

# Read prompt from file
./enhanced_ngpt.py -f prompt.txt

# Generate code and save to file
./enhanced_ngpt.py --code "function to calculate fibonacci numbers" -o fibonacci.py

# Use a specific model and configuration
./enhanced_ngpt.py -c 1 -m gpt-4o "Explain neural networks"

# Use with markdown formatting
./enhanced_ngpt.py -p "Explain quantum computing with code examples"
```

## Next Steps

Check out the [Custom Integrations](integrations.md) examples to learn how to integrate nGPT into larger applications and systems. 