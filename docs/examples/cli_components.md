# CLI Component Examples

This page provides practical examples of how to use nGPT's CLI components to build your own AI-powered command-line applications.

## Dependencies

All necessary dependencies are included when you install nGPT:

- **Markdown Rendering**: `rich` for syntax highlighting
- **Interactive Sessions**: `prompt_toolkit` for enhanced input handling
- **Terminal Formatting**: ANSI color support

You don't need to install any additional packages to use these components - just run `pip install ngpt` and all requirements will be automatically installed.

## Basic CLI Tool Example

Here's a simple CLI tool that uses nGPT to generate and explain code:

```python
#!/usr/bin/env python3
import sys
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.args import setup_argument_parser, validate_args
from ngpt.cli.renderers import prettify_markdown, has_markdown_renderer

def main():
    # Create parser with colorized help
    parser = setup_argument_parser()
    
    # Customize the parser for our specific needs
    parser.description = "Simple code generation tool"
    parser.add_argument("prompt", help="Code description")
    parser.add_argument("--language", "-l", default="python", help="Programming language")
    parser.add_argument("--explain", "-e", action="store_true", help="Include explanation")
    parser.add_argument("--prettify", "-p", action="store_true", help="Format output")
    
    args = parser.parse_args()
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check if markdown rendering is available when requested
    if args.prettify and not has_markdown_renderer(renderer='auto'):
        print("Warning: Prettify requested but no markdown renderer available.", file=sys.stderr)
        print("Install 'rich' or 'pygments' for syntax highlighting.", file=sys.stderr)
        args.prettify = False
    
    # Generate code
    print(f"Generating {args.language} code...")
    code = client.generate_code(args.prompt, language=args.language)
    
    # Display the code
    if args.prettify:
        markdown = f"```{args.language}\n{code}\n```"
        print(prettify_markdown(markdown, renderer='auto'))
    else:
        print("\nGenerated Code:")
        print(code)
    
    # Generate explanation if requested
    if args.explain:
        print("\nGenerating explanation...")
        prompt = f"Explain this {args.language} code:\n\n{code}"
        explanation = client.chat(prompt)
        
        if args.prettify:
            print(prettify_markdown(explanation, renderer='auto'))
        else:
            print("\nExplanation:")
            print(explanation)

if __name__ == "__main__":
    main()
```

Save this as `codegen.py` and use it like:

```bash
python codegen.py "function to calculate fibonacci numbers" --explain --prettify
```

## Using Interactive Chat Sessions

Create a custom chat application with specialized capabilities:

```python
#!/usr/bin/env python3
import argparse
import sys
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.interactive import interactive_chat_session
from ngpt.cli.formatters import ColoredHelpFormatter
from ngpt.cli.renderers import has_markdown_renderer

def main():
    parser = argparse.ArgumentParser(
        description="Specialized SQL Assistant",
        formatter_class=ColoredHelpFormatter
    )
    
    parser.add_argument("--dialect", "-d", default="postgresql", 
                        choices=["postgresql", "mysql", "sqlite", "sqlserver"],
                        help="SQL dialect to use")
    parser.add_argument("--sample", "-s", action="store_true",
                        help="Include sample data in responses")
    parser.add_argument("--prettify", "-p", action="store_true",
                        help="Prettify markdown output")
    
    args = parser.parse_args()
    
    # Check for required dependencies
    try:
        import prompt_toolkit
    except ImportError:
        print("Error: prompt_toolkit is required for interactive mode.", file=sys.stderr)
        print("Install with: pip install prompt_toolkit", file=sys.stderr)
        sys.exit(1)
    
    # Check renderer if prettify is requested
    if args.prettify and not has_markdown_renderer(renderer='auto'):
        print("Warning: Prettify requested but no markdown renderer available.", file=sys.stderr)
        print("Install 'rich' or 'pygments' for syntax highlighting.", file=sys.stderr)
        args.prettify = False
    
    # Create system prompt for SQL assistant
    system_prompt = f"""You are an expert {args.dialect} SQL assistant.
Provide clear, optimized SQL queries based on user requests.
{"Include example data in your responses when appropriate." if args.sample else ""}
Use the {args.dialect} syntax in all examples.
Format SQL with proper indentation and capitalization of keywords."""
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print welcome message
    print(f"SQL Assistant for {args.dialect} - Type /help for commands")
    print("Type your questions or requests for SQL queries.")
    print("-" * 60)
    
    # Start interactive session with custom system prompt
    try:
        interactive_chat_session(
            client=client,
            preprompt=system_prompt,
            prettify=args.prettify,
            renderer='auto'
        )
    except KeyboardInterrupt:
        print("\nSession terminated.")
    except Exception as e:
        print(f"\nError in interactive session: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save this as `sql-assistant.py` and use it:

```bash
python sql-assistant.py --dialect mysql --sample --prettify
```

## Streaming Markdown Example

Create a documentation generator with live markdown rendering:

```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.renderers import prettify_streaming_markdown, has_markdown_renderer
from ngpt.cli.formatters import ColoredHelpFormatter

def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation from code",
        formatter_class=ColoredHelpFormatter
    )
    
    parser.add_argument("file", type=str, help="Code file to document")
    parser.add_argument("--output", "-o", type=str, help="Output markdown file")
    parser.add_argument("--level", "-l", choices=["basic", "detailed", "comprehensive"],
                        default="detailed", help="Documentation detail level")
    
    args = parser.parse_args()
    
    # Check if Rich is available for streaming prettification
    try:
        import rich
    except ImportError:
        print("Warning: Rich library not found. Install with: pip install rich", file=sys.stderr)
        print("Continuing without live markdown formatting...", file=sys.stderr)
        has_rich = False
    else:
        has_rich = True
    
    # Check if input file exists
    input_path = Path(args.file)
    if not input_path.exists():
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Determine language from file extension
    language = input_path.suffix.lstrip('.')
    
    # Read code file
    try:
        with open(input_path, 'r') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Detail level descriptions
    detail_prompts = {
        "basic": "Create a basic documentation with overview and main functions",
        "detailed": "Create documentation with function descriptions, parameters, and examples",
        "comprehensive": "Create comprehensive documentation with detailed explanations, examples, edge cases, and best practices"
    }
    
    # Create prompt
    prompt = f"""Generate {args.level} documentation in markdown format for this {language} code.
{detail_prompts[args.level]}
Include a title, description, usage examples, and function/class documentation.

CODE:
```{language}
{code}
```"""
    
    print(f"Generating {args.level} documentation for {args.file}...")
    
    # Collect the full response
    full_response = ""
    
    # Use streaming markdown renderer if Rich is available
    if has_rich and has_markdown_renderer(renderer='rich'):
        # Create a streaming markdown renderer
        live_display, update_function, setup_spinner = prettify_streaming_markdown(
            renderer='rich',
            header_text=f"Documentation for {args.file}"
        )
        
        # Setup spinner for waiting period
        import threading
        stop_spinner_event = threading.Event()
        stop_spinner_func = None
        if setup_spinner:
            stop_spinner_func = setup_spinner(stop_spinner_event, "Generating documentation...")
        
        # Stream the response with live updating
        try:
            for chunk in client.chat(prompt, stream=True):
                full_response += chunk
                update_function(full_response)
            
            # Ensure spinner is stopped if still running
            if not stop_spinner_event.is_set():
                stop_spinner_event.set()
            
            # Stop the display when done
            if live_display:
                live_display.stop()
        except Exception as e:
            # Ensure spinner is stopped on error
            if not stop_spinner_event.is_set():
                stop_spinner_event.set()
            print(f"\nError generating documentation: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Simple streaming without live markdown rendering
        print("Generating documentation...")
        try:
            for chunk in client.chat(prompt, stream=True):
                full_response += chunk
                print(chunk, end="", flush=True)
            print()  # Final newline
        except Exception as e:
            print(f"\nError generating documentation: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Save to file if specified
    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(full_response)
            print(f"\nDocumentation saved to {args.output}")
        except Exception as e:
            print(f"\nError saving to file: {e}", file=sys.stderr)
    
    print("\nDocumentation generation complete.")

if __name__ == "__main__":
    main()
```

Save this as `docgen.py` and use it like:

```bash
python docgen.py my_script.py --output documentation.md --level comprehensive
```

## Using Multiline Editor

Here's an example of using nGPT's multiline editor for collecting user input:

```python
#!/usr/bin/env python3
import argparse
import sys
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.ui import multiline_editor
from ngpt.cli.renderers import prettify_markdown
from ngpt.cli.formatters import ColoredHelpFormatter

def main():
    parser = argparse.ArgumentParser(
        description="Code review assistant with multiline input",
        formatter_class=ColoredHelpFormatter
    )
    
    parser.add_argument("--language", "-l", default="python", help="Code language")
    parser.add_argument("--prettify", "-p", action="store_true", help="Prettify output")
    
    args = parser.parse_args()
    
    # Check for required dependencies
    try:
        import prompt_toolkit
    except ImportError:
        print("Error: prompt_toolkit is required for multiline editor.", file=sys.stderr)
        print("Install with: pip install prompt_toolkit", file=sys.stderr)
        sys.exit(1)
    
    print(f"Code Review Assistant for {args.language}")
    print("Please enter or paste your code in the editor below.")
    print("Press Ctrl+D to submit, or Ctrl+C to cancel.")
    
    try:
        # Open multiline editor for code input
        code = multiline_editor(
            lexer_name=args.language,
            message="Enter your code:",
            default_text=f"# Enter your {args.language} code here\n"
        )
        
        if not code.strip():
            print("No code entered. Exiting.")
            return
            
        # Initialize client
        config = load_config()
        client = NGPTClient(**config)
        
        # Create review prompt
        prompt = f"""Review this {args.language} code and provide feedback:
1. Identify any bugs or issues
2. Suggest code improvements
3. Comment on style and best practices

```{args.language}
{code}
```
"""
        
        print("\nAnalyzing code...")
        response = client.chat(prompt)
        
        # Display the response
        if args.prettify:
            print("\nReview Results:")
            print(prettify_markdown(response, renderer='auto'))
        else:
            print("\nReview Results:")
            print(response)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save this as `code-review.py` and use it:

```bash
python code-review.py --language javascript --prettify
```

## Building a Text Rewriting Tool

This example creates a text improvement tool that uses nGPT's rewrite mode to enhance text quality while preserving the original meaning and tone:

```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.ui import multiline_editor
from ngpt.cli.renderers import prettify_markdown, prettify_streaming_markdown
from ngpt.cli.formatters import ColoredHelpFormatter, COLORS

def main():
    parser = argparse.ArgumentParser(
        description="Text improvement assistant",
        formatter_class=ColoredHelpFormatter
    )
    
    # Command line arguments
    parser.add_argument("text", nargs="?", help="Text to rewrite (optional)")
    parser.add_argument("--file", "-f", help="Read text from file")
    parser.add_argument("--output", "-o", help="Save output to file")
    parser.add_argument("--type", "-t", choices=["formal", "casual", "academic", "creative", "general"],
                      default="general", help="Style of rewriting")
    parser.add_argument("--stream", "-s", action="store_true", 
                      help="Stream results with live updates")
    parser.add_argument("--prettify", "-p", action="store_true", 
                      help="Format output with markdown rendering")
    
    args = parser.parse_args()
    
    # Get input text
    text = ""
    if args.text:
        # Text from command line
        text = args.text
    elif args.file:
        # Text from file
        try:
            file_path = Path(args.file)
            if not file_path.exists():
                print(f"Error: File '{args.file}' not found", file=sys.stderr)
                sys.exit(1)
            with open(file_path, 'r') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # No text provided, use multiline editor
        try:
            import prompt_toolkit
        except ImportError:
            print("Error: prompt_toolkit is required for multiline editor", file=sys.stderr)
            print("Install with: pip install prompt_toolkit", file=sys.stderr)
            sys.exit(1)
        
        print(f"{COLORS['cyan']}Text Improvement Assistant{COLORS['reset']}")
        print("Enter or paste the text you want to improve.")
        print("Press Ctrl+D to submit, or Esc to cancel.")
        
        try:
            text = multiline_editor(
                message="Enter text to rewrite:",
                default_text="",
                lexer_name="markdown"  # Use markdown for general text
            )
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            sys.exit(0)
        
        if not text.strip():
            print("No text entered. Exiting.")
            sys.exit(0)
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"{COLORS['yellow']}Error initializing AI client: {e}{COLORS['reset']}", 
              file=sys.stderr)
        sys.exit(1)
    
    # Style instructions
    style_guide = {
        "formal": "Use formal language, proper grammar, and professional tone.",
        "casual": "Use conversational, friendly tone while improving clarity.",
        "academic": "Use academic language with precise terminology and citations where appropriate.",
        "creative": "Make the text more engaging and vibrant while maintaining meaning.",
        "general": "Improve clarity and correctness while preserving the original tone."
    }
    
    # System prompt for rewriting
    system_prompt = f"""You are a text improvement assistant. 
Rewrite the text to improve quality while preserving the original meaning and intent.
{style_guide[args.type]}
Focus on:
1. Fixing grammar and spelling errors
2. Improving clarity and readability
3. Enhancing flow and structure
4. Maintaining the author's voice and meaning
Return ONLY the improved text without explanations or notes."""
    
    print(f"\n{COLORS['cyan']}Rewriting text ({args.type} style)...{COLORS['reset']}")
    
    # Process with AI
    try:
        if args.stream:
            # Stream with live updates
            if args.prettify:
                live_display, update_function, setup_spinner = prettify_streaming_markdown(
                    renderer='rich',
                    header_text="Improved Text"
                )
                
                # Setup spinner for waiting period
                import threading
                stop_spinner_event = threading.Event()
                stop_spinner_func = None
                if setup_spinner:
                    stop_spinner_func = setup_spinner(stop_spinner_event, "Improving text...")
                
                full_response = ""
                for chunk in client.chat(
                    text,
                    system_prompt=system_prompt,
                    stream=True
                ):
                    full_response += chunk
                    update_function(full_response)
                
                # Ensure spinner is stopped if still running
                if not stop_spinner_event.is_set():
                    stop_spinner_event.set()
                
                # Stop the display when done
                if live_display:
                    live_display.stop()
                
                improved_text = full_response
            else:
                # Simple streaming
                print(f"\n{COLORS['green']}Improved Text:{COLORS['reset']}\n")
                improved_text = ""
                for chunk in client.chat(
                    text,
                    system_prompt=system_prompt,
                    stream=True
                ):
                    improved_text += chunk
                    print(chunk, end="", flush=True)
                print()  # Final newline
        else:
            # Get complete response
            improved_text = client.chat(
                text,
                system_prompt=system_prompt
            )
            
            if args.prettify:
                print(f"\n{COLORS['green']}Improved Text:{COLORS['reset']}\n")
                print(prettify_markdown(improved_text))
            else:
                print(f"\n{COLORS['green']}Improved Text:{COLORS['reset']}\n")
                print(improved_text)
        
        # Save to file if requested
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(improved_text)
                print(f"\n{COLORS['green']}Improved text saved to {args.output}{COLORS['reset']}")
            except Exception as e:
                print(f"{COLORS['yellow']}Error saving to file: {e}{COLORS['reset']}", 
                      file=sys.stderr)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"\n{COLORS['yellow']}Error: {e}{COLORS['reset']}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save this as `text-improver.py` and use it like:

```bash
# Use multiline editor for input
python text-improver.py --type formal --prettify

# Provide text directly from command line
python text-improver.py "I aint never seen nothing like it" --type formal --prettify

# Read from file and save to another file
python text-improver.py --file rough_draft.txt --output improved.txt --type academic

# Stream results with live updates
python text-improver.py --file notes.txt --type casual --stream --prettify
```

## Advanced CLI Configuration Example

Create a CLI tool with persistent configuration:

```python
#!/usr/bin/env python3
import argparse
import sys
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.main import handle_cli_config
from ngpt.cli.formatters import ColoredHelpFormatter

def main():
    parser = argparse.ArgumentParser(
        description="AI Resume Builder with Persistent Configuration",
        formatter_class=ColoredHelpFormatter
    )
    
    # Command subparsers
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Config subcommand
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("action", choices=["get", "set", "list"], help="Configuration action")
    config_parser.add_argument("option", nargs="?", help="Configuration option name")
    config_parser.add_argument("value", nargs="?", help="Configuration option value")
    
    # Build subcommand
    build_parser = subparsers.add_parser("build", help="Build a resume")
    build_parser.add_argument("--name", help="Your name")
    build_parser.add_argument("--skills", help="Comma-separated list of skills")
    build_parser.add_argument("--experience", help="Years of experience")
    build_parser.add_argument("--format", choices=["markdown", "latex", "text"], 
                            help="Output format")
    build_parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    # Handle config command
    if args.command == "config":
        try:
            if args.action == "list":
                options = handle_cli_config("list")
                print("Available configuration options:")
                for option in options:
                    value = handle_cli_config("get", option)
                    print(f"  {option}: {value}")
                return
            
            elif args.action == "get":
                if not args.option:
                    print("Error: Option name required for 'get'", file=sys.stderr)
                    return
                value = handle_cli_config("get", args.option)
                print(f"{args.option}: {value}")
                return
            
            elif args.action == "set":
                if not args.option or not args.value:
                    print("Error: Both option name and value required for 'set'", file=sys.stderr)
                    return
                handle_cli_config("set", args.option, args.value)
                print(f"Set {args.option} to {args.value}")
                return
        except Exception as e:
            print(f"Error handling configuration: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Handle build command (or default)
    elif args.command == "build" or not args.command:
        try:
            # Get values, prioritizing command line args over stored config
            name = args.name or handle_cli_config("get", "name") or ""
            skills = args.skills or handle_cli_config("get", "skills") or ""
            experience = args.experience or handle_cli_config("get", "experience") or ""
            output_format = args.format or handle_cli_config("get", "format") or "markdown"
            
            # Validate required fields
            if not name:
                print("Error: Name is required. Provide with --name or set with 'config set name VALUE'", 
                      file=sys.stderr)
                return
            
            # Initialize client
            try:
                config = load_config()
                client = NGPTClient(**config)
            except Exception as e:
                print(f"Error initializing AI client: {e}", file=sys.stderr)
                sys.exit(1)
            
            # Build prompt
            prompt = f"""Create a professional resume for {name}.
Skills: {skills}
Experience: {experience} years
Format: {output_format}

Generate a complete, professional resume that highlights these skills and experience level.
"""
            
            print(f"Generating resume in {output_format} format...")
            response = client.chat(prompt)
            
            # Save to file or display
            if args.output:
                try:
                    with open(args.output, 'w') as f:
                        f.write(response)
                    print(f"Resume saved to {args.output}")
                except Exception as e:
                    print(f"Error saving to file: {e}", file=sys.stderr)
            else:
                print("\n" + "=" * 60)
                print(response)
                print("=" * 60)
            
            # Save values used to config for future use
            if args.name:
                handle_cli_config("set", "name", args.name)
            if args.skills:
                handle_cli_config("set", "skills", args.skills)
            if args.experience:
                handle_cli_config("set", "experience", args.experience)
            if args.format:
                handle_cli_config("set", "format", args.format)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

Save this as `resume-builder.py` and use it:

```bash
# Set configuration values
python resume-builder.py config set name "John Doe"
python resume-builder.py config set skills "Python, JavaScript, AI, Data Analysis"
python resume-builder.py config set experience "5"
python resume-builder.py config set format "markdown"

# Build resume using stored config
python resume-builder.py build --output resume.md

# Or override with command-line arguments
python resume-builder.py build --name "Jane Smith" --format latex --output resume.tex
```

## Creating a Translation Tool

Build a CLI translation tool with nGPT components:

```python
#!/usr/bin/env python3
import argparse
import sys
import os
from pathlib import Path
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.renderers import prettify_markdown, supports_ansi_colors
from ngpt.cli.formatters import ColoredHelpFormatter

def main():
    parser = argparse.ArgumentParser(
        description="AI-powered text translation tool",
        formatter_class=ColoredHelpFormatter
    )
    
    parser.add_argument("text", nargs="?", help="Text to translate")
    parser.add_argument("--file", "-f", help="File to translate")
    parser.add_argument("--target", "-t", required=True, help="Target language")
    parser.add_argument("--source", "-s", help="Source language (auto-detect if not specified)")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--format", choices=["plain", "markdown"], default="plain",
                       help="Output format")
    
    args = parser.parse_args()
    
    # Get text either from argument or file
    text = ""
    if args.text:
        text = args.text
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"Error initializing AI client: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create system prompt for translation
    system_prompt = f"""You are a professional translator.
Translate the following text {f"from {args.source}" if args.source else ""} to {args.target}.
Preserve formatting, tone, and meaning as much as possible.
Return only the translated text without explanations.
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]
    
    # Colorized output for terminal
    if supports_ansi_colors():
        print(f"\033[1;36mTranslating to {args.target}...\033[0m")
    else:
        print(f"Translating to {args.target}...")
    
    # Get translation
    try:
        translation = client.chat("", messages=messages)
        
        # Format output if requested
        if args.format == "markdown":
            translation = prettify_markdown(translation, renderer='auto')
        
        # Save to file or display
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(translation)
                print(f"Translation saved to {args.output}")
            except Exception as e:
                print(f"Error saving to file: {e}", file=sys.stderr)
        else:
            print("\n" + "=" * 60)
            print(translation)
            print("=" * 60)
    except Exception as e:
        print(f"Error during translation: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save this as `translate.py` and use it like:

```bash
python translate.py "Hello world" --target Spanish
python translate.py --file document.txt --target French --output document_fr.txt
```

## CLI with Multi-Modal Support

If your API endpoint supports image processing, here's an example of a tool that can analyze images:

```python
#!/usr/bin/env python3
import argparse
import sys
import base64
import os
from pathlib import Path
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.renderers import prettify_streaming_markdown, has_markdown_renderer
from ngpt.cli.formatters import ColoredHelpFormatter

def encode_image(image_path):
    """Encode image file as base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def main():
    parser = argparse.ArgumentParser(
        description="AI Image Analysis Tool",
        formatter_class=ColoredHelpFormatter
    )
    
    parser.add_argument("image", help="Path to image file")
    parser.add_argument("--task", "-t", choices=["describe", "analyze", "extract-text", "identify"],
                       default="describe", help="Analysis task")
    
    args = parser.parse_args()
    
    # Check if image exists
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file '{args.image}' not found.", file=sys.stderr)
        sys.exit(1)
    
    # Check if file is an image
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    if image_path.suffix.lower() not in image_extensions:
        print(f"Warning: File '{args.image}' may not be an image file.", file=sys.stderr)
    
    # Check if Rich is available for streaming prettification
    if not has_markdown_renderer(renderer='rich'):
        print("Warning: Rich library not found. Install with: pip install rich", file=sys.stderr)
        print("Continuing without live markdown formatting...", file=sys.stderr)
        has_rich = False
    else:
        has_rich = True
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"Error initializing AI client: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Encode image
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        print(f"Error encoding image: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create task-specific prompt
    task_prompts = {
        "describe": "Describe this image in detail. What does it show?",
        "analyze": "Analyze this image. Identify key elements, colors, composition, and potential meaning.",
        "extract-text": "Extract and transcribe any text visible in this image.",
        "identify": "Identify what this image shows. If it contains landmarks, people, animals, or objects, name them specifically."
    }
    
    # Create messages with image
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": task_prompts[args.task]},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
        ]}
    ]
    
    print(f"Analyzing image: {args.image}")
    print(f"Task: {args.task}\n")
    
    # Collect the full response
    full_response = ""
    
    # Note: This example assumes your API supports vision capabilities
    # It needs to be used with an endpoint that supports this feature
    try:
        if has_rich:
            # Create a streaming markdown renderer
            markdown_streamer = prettify_streaming_markdown(
                renderer='rich',
                header_text=f"Image Analysis Results"
            )
            
            # Stream with live updating
            for chunk in client.chat("", messages=messages, stream=True):
                full_response += chunk
                markdown_streamer.update_content(full_response)
        else:
            # Simple streaming without live markdown rendering
            for chunk in client.chat("", messages=messages, stream=True):
                full_response += chunk
                print(chunk, end="", flush=True)
            print()  # Final newline
            
        print("\nAnalysis complete.")
    except Exception as e:
        print(f"\nError during image analysis: {e}", file=sys.stderr)
        print("Note: This example requires an API endpoint that supports image analysis.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save this as `image-analyzer.py` and use it:

```bash
python image-analyzer.py photo.jpg --task describe
python image-analyzer.py diagram.png --task extract-text
```

## Git Commit Message Generator

Create a CLI tool that uses nGPT to generate high-quality git commit messages from staged changes:

```python
#!/usr/bin/env python3
import sys
import subprocess
from ngpt import NGPTClient
from ngpt.utils.config import load_config
from ngpt.cli.formatters import COLORS
import pyperclip

def get_git_diff():
    """Get staged changes from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
            
        # Check if there are staged changes
        if not result.stdout.strip():
            print(f"{COLORS['yellow']}No staged changes found. Stage changes with 'git add' first.{COLORS['reset']}")
            return None
            
        return result.stdout
    except Exception as e:
        print(f"{COLORS['yellow']}Error getting git diff: {str(e)}{COLORS['reset']}")
        return None

def main():
    # Get staged changes
    diff_content = get_git_diff()
    if not diff_content:
        sys.exit(1)
    
    # Initialize client
    try:
        config = load_config()
        client = NGPTClient(**config)
    except Exception as e:
        print(f"{COLORS['red']}Error initializing AI client: {e}{COLORS['reset']}", file=sys.stderr)
        sys.exit(1)
    
    # Create system prompt for commit message generation
    system_prompt = """You are an expert Git commit message writer. Your task is to analyze the git diff and create a precise, factual commit message following the conventional commit format.

FORMAT:
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>

COMMIT TYPES:
- feat: New user-facing features
- fix: Bug fixes or error corrections
- refactor: Code restructuring (no behavior change)
- style: Formatting/whitespace changes only
- docs: Documentation only
- test: Test-related changes
- perf: Performance improvements
- build: Build system changes
- ci: CI/CD pipeline changes
- chore: Routine maintenance tasks

RULES:
1. BE 100% FACTUAL - Mention ONLY code explicitly shown in the diff
2. NEVER invent or assume changes not directly visible in the code
3. EVERY bullet point MUST reference specific files/functions/lines
4. Keep summary line under 50 characters (mandatory)
5. Focus on technical specifics, avoid general statements"""
    
    # Create prompt for commit message generation
    prompt = f"""Analyze this git diff and create a conventional commit message:

{diff_content}"""

    print(f"{COLORS['green']}Generating commit message...{COLORS['reset']}")
    
    # Generate commit message
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        commit_message = client.chat(
            prompt=prompt,
            messages=messages
        )
        
        # Display the result
        print(f"\n{COLORS['green']}✨ Generated Commit Message:{COLORS['reset']}\n")
        print(commit_message)
        
        # Copy to clipboard
        try:
            pyperclip.copy(commit_message)
            print(f"\n{COLORS['green']}(Copied to clipboard){COLORS['reset']}")
        except:
            pass
        
    except Exception as e:
        print(f"{COLORS['red']}Error generating commit message: {e}{COLORS['reset']}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Save this as `commit-msg.py` and use it after staging changes:

```bash
git add .
python commit-msg.py
```

The tool will:
1. Fetch the diff of staged changes
2. Generate a conventional commit message based on the changes
3. Display the message and copy it to your clipboard
4. You can then use the commit message with `git commit -m "paste_message_here"`

For larger projects, you might want to add more options such as:
- Filtering by file type
- Customizing commit types
- Providing additional context for the AI

The complete implementation in nGPT includes features like chunking for handling large diffs and specialized prompts for different types of code changes.

## Error Handling Best Practices

When using nGPT CLI components, follow these error handling best practices:

1. **Check for Dependencies**:
   ```python
   try:
       import rich
   except ImportError:
       print("Warning: Rich library not found. Install with: pip install rich", file=sys.stderr)
       # Fallback behavior
   ```

2. **Handle API Errors**:
   ```python
   try:
       response = client.chat(prompt)
   except Exception as e:
       print(f"Error communicating with AI service: {e}", file=sys.stderr)
       sys.exit(1)
   ```

3. **Graceful Keyboard Interrupts**:
   ```python
   try:
       # Your code here
   except KeyboardInterrupt:
       print("\nOperation cancelled by user.")
       sys.exit(0)
   ```

4. **Verify Rendering Capabilities**:
   ```python
   if has_markdown_renderer(renderer='rich'):
       # Use rich rendering
   else:
       # Fallback to plain text
   ```

## Conclusion

These examples demonstrate how nGPT's CLI components can be reused to build a wide variety of specialized AI-powered command-line tools. The modular design allows you to leverage high-quality components for:

- Beautiful terminal UI with colored output
- Interactive sessions with conversation history
- Markdown rendering with syntax highlighting
- Persistent configuration management
- Streaming responses with live updates
- Multiline text editing with syntax highlighting

To learn more about the available components and their capabilities, see the [CLI Framework Guide](../usage/cli_framework.md) and the [API Reference](../api/cli.md). 