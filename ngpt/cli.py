import argparse
import sys
import os
from .client import NGPTClient
from .config import load_config, get_config_path, load_configs, add_config_entry, remove_config_entry
from . import __version__

# Optional imports for enhanced UI
try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.layout.containers import HSplit, Window
    from prompt_toolkit.layout.layout import Layout
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.application import Application
    from prompt_toolkit.widgets import TextArea
    from prompt_toolkit.layout.margins import ScrollbarMargin
    from prompt_toolkit.filters import to_filter
    from prompt_toolkit.history import InMemoryHistory
    import shutil
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

def show_config_help():
    """Display help information about configuration."""
    print("\nConfiguration Help:")
    print("  1. Create a config file at one of these locations:")
    if sys.platform == "win32":
        print(f"     - %APPDATA%\\ngpt\\ngpt.conf")
    elif sys.platform == "darwin":
        print(f"     - ~/Library/Application Support/ngpt/ngpt.conf")
    else:
        print(f"     - ~/.config/ngpt/ngpt.conf")
    
    print("  2. Format your config file as JSON:")
    print("""     [
       {
         "api_key": "your-api-key-here",
         "base_url": "https://api.openai.com/v1/",
         "provider": "OpenAI",
         "model": "gpt-3.5-turbo"
       },
       {
         "api_key": "your-second-api-key",
         "base_url": "http://localhost:1337/v1/",
         "provider": "Another Provider",
         "model": "different-model"
       }
     ]""")
    
    print("  3. Or set environment variables:")
    print("     - OPENAI_API_KEY")
    print("     - OPENAI_BASE_URL")
    print("     - OPENAI_MODEL")
    
    print("  4. Or provide command line arguments:")
    print("     ngpt --api-key your-key --base-url https://api.example.com --model your-model \"Your prompt\"")
    
    print("  5. Use --config-index to specify which configuration to use or edit:")
    print("     ngpt --config-index 1 \"Your prompt\"")
    
    print("  6. Use --config without arguments to add a new configuration:")
    print("     ngpt --config")
    print("     Or specify an index to edit an existing configuration:")
    print("     ngpt --config --config-index 1")
    print("  7. Remove a configuration at a specific index:")
    print("     ngpt --config --remove --config-index 1")
    print("  8. List available models for the current configuration:")
    print("     ngpt --list-models")

def check_config(config):
    """Check config for common issues and provide guidance."""
    if not config.get("api_key"):
        print("Error: API key is not set.")
        show_config_help()
        return False
        
    # Check for common URL mistakes
    base_url = config.get("base_url", "")
    if base_url and not (base_url.startswith("http://") or base_url.startswith("https://")):
        print(f"Warning: Base URL '{base_url}' doesn't start with http:// or https://")
    
    return True

def interactive_chat_session(client, web_search=False, no_stream=False):
    """Run an interactive chat session with conversation history."""
    # Define ANSI color codes for terminal output
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "cyan": "\033[36m",
        "green": "\033[32m", 
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "gray": "\033[90m",
        "bg_blue": "\033[44m",
        "bg_cyan": "\033[46m"
    }
    
    # Get terminal width for better formatting
    try:
        term_width = shutil.get_terminal_size().columns
    except:
        term_width = 80  # Default fallback
    
    # Improved visual header with better layout
    header = f"{COLORS['cyan']}{COLORS['bold']}🤖 nGPT Interactive Chat Session 🤖{COLORS['reset']}"
    print(f"\n{header}")
    
    # Create a separator line - use a consistent separator length for all lines
    separator_length = min(40, term_width - 10)
    separator = f"{COLORS['gray']}{'─' * separator_length}{COLORS['reset']}"
    print(separator)
    
    # Group commands into categories with better formatting
    print(f"\n{COLORS['cyan']}Navigation:{COLORS['reset']}")
    print(f"  {COLORS['yellow']}↑/↓{COLORS['reset']} : Browse input history")
    
    print(f"\n{COLORS['cyan']}Session Commands:{COLORS['reset']}")
    print(f"  {COLORS['yellow']}history{COLORS['reset']} : Show conversation history")
    print(f"  {COLORS['yellow']}clear{COLORS['reset']}   : Reset conversation")
    print(f"  {COLORS['yellow']}exit{COLORS['reset']}    : End session")
    
    print(f"\n{separator}\n")
    
    # Custom separator - use the same length for consistency
    def print_separator():
        print(f"\n{separator}\n")
    
    # Initialize conversation history
    system_prompt = "You are a helpful assistant."
    conversation = []
    system_message = {"role": "system", "content": system_prompt}
    conversation.append(system_message)
    
    # Initialize prompt_toolkit history
    prompt_history = InMemoryHistory() if HAS_PROMPT_TOOLKIT else None
    
    # Decorative chat headers with rounded corners
    def user_header():
        return f"{COLORS['cyan']}{COLORS['bold']}╭─ 👤 You {COLORS['reset']}"
    
    def ngpt_header():
        return f"{COLORS['green']}{COLORS['bold']}╭─ 🤖 nGPT {COLORS['reset']}"
    
    # Function to display conversation history
    def display_history():
        if len(conversation) <= 1:  # Only system message
            print(f"\n{COLORS['yellow']}No conversation history yet.{COLORS['reset']}")
            return
            
        print(f"\n{COLORS['cyan']}{COLORS['bold']}Conversation History:{COLORS['reset']}")
        print(separator)
        
        # Skip system message
        message_count = 0
        for i, msg in enumerate(conversation):
            if msg["role"] == "system":
                continue
                
            if msg["role"] == "user":
                message_count += 1
                print(f"\n{user_header()}")
                print(f"{COLORS['cyan']}│ [{message_count}] {COLORS['reset']}{msg['content']}")
            elif msg["role"] == "assistant":
                print(f"\n{ngpt_header()}")
                print(f"{COLORS['green']}│ {COLORS['reset']}{msg['content']}")
        
        print(f"\n{separator}")  # Consistent separator at the end
    
    # Function to clear conversation history
    def clear_history():
        nonlocal conversation
        conversation = [{"role": "system", "content": system_prompt}]
        print(f"\n{COLORS['yellow']}Conversation history cleared.{COLORS['reset']}")
        print(separator)  # Add separator for consistency
    
    try:
        while True:
            # Get user input
            if HAS_PROMPT_TOOLKIT:
                # Custom styling for prompt_toolkit
                style = Style.from_dict({
                    'prompt': 'ansicyan bold',
                    'input': 'ansiwhite',
                })
                
                # Create key bindings for Ctrl+C handling
                kb = KeyBindings()
                @kb.add('c-c')
                def _(event):
                    event.app.exit(result=None)
                    raise KeyboardInterrupt()
                
                # Get user input with styled prompt - using proper HTML formatting
                user_input = pt_prompt(
                    HTML("<ansicyan><b>╭─ 👤 You:</b></ansicyan> "),
                    style=style,
                    key_bindings=kb,
                    history=prompt_history
                )
            else:
                user_input = input(f"{user_header()}: {COLORS['reset']}")
            
            # Check for exit commands
            if user_input.lower() in ('exit', 'quit', 'bye'):
                print(f"\n{COLORS['green']}Ending chat session. Goodbye!{COLORS['reset']}")
                break
            
            # Check for special commands
            if user_input.lower() == 'history':
                display_history()
                continue
            
            if user_input.lower() == 'clear':
                clear_history()
                continue
            
            # Skip empty messages but don't raise an error
            if not user_input.strip():
                continue
            
            # Add user message to conversation
            user_message = {"role": "user", "content": user_input}
            conversation.append(user_message)
            
            # Print assistant indicator with formatting
            if not no_stream:
                print(f"\n{ngpt_header()}: {COLORS['reset']}", end="", flush=True)
            else:
                print(f"\n{ngpt_header()}: {COLORS['reset']}", flush=True)
            
            # Get AI response with conversation history
            response = client.chat(
                prompt=user_input,
                messages=conversation,
                stream=not no_stream,
                web_search=web_search
            )
            
            # Add AI response to conversation history
            if response:
                assistant_message = {"role": "assistant", "content": response}
                conversation.append(assistant_message)
                
                # Print response if not streamed
                if no_stream:
                    print(response)
            
            # Print separator between exchanges
            print_separator()
            
    except KeyboardInterrupt:
        print(f"\n\n{COLORS['green']}Chat session ended by user. Goodbye!{COLORS['reset']}")
    except Exception as e:
        print(f"\n{COLORS['yellow']}Error during chat session: {str(e)}{COLORS['reset']}")
        # Print traceback for debugging if it's a serious error
        import traceback
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="nGPT - A CLI tool for interacting with custom OpenAI API endpoints")
    
    # Version flag
    parser.add_argument('-v', '--version', action='version', version=f'nGPT {__version__}', help='Show version information and exit')
    
    # Config options
    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument('--config', nargs='?', const=True, help='Path to a custom config file or, if no value provided, enter interactive configuration mode to create a new config')
    config_group.add_argument('--config-index', type=int, default=0, help='Index of the configuration to use or edit (default: 0)')
    config_group.add_argument('--remove', action='store_true', help='Remove the configuration at the specified index (requires --config and --config-index)')
    config_group.add_argument('--show-config', action='store_true', help='Show the current configuration(s) and exit')
    config_group.add_argument('--all', action='store_true', help='Show details for all configurations (requires --show-config)')
    config_group.add_argument('--list-models', action='store_true', help='List all available models for the current configuration and exit')
    
    # Global options
    global_group = parser.add_argument_group('Global Options')
    global_group.add_argument('--api-key', help='API key for the service')
    global_group.add_argument('--base-url', help='Base URL for the API')
    global_group.add_argument('--model', help='Model to use')
    global_group.add_argument('--web-search', action='store_true', 
                      help='Enable web search capability (Note: Your API endpoint must support this feature)')
    global_group.add_argument('-n', '--no-stream', action='store_true',
                      help='Return the whole response without streaming')
    
    # Mode flags (mutually exclusive)
    mode_group = parser.add_argument_group('Modes (mutually exclusive)')
    mode_exclusive_group = mode_group.add_mutually_exclusive_group()
    mode_exclusive_group.add_argument('-i', '--interactive', action='store_true', help='Start an interactive chat session')
    mode_exclusive_group.add_argument('-s', '--shell', action='store_true', help='Generate and execute shell commands')
    mode_exclusive_group.add_argument('-c', '--code', action='store_true', help='Generate code')
    mode_exclusive_group.add_argument('-t', '--text', action='store_true', help='Enter multi-line text input (submit with Ctrl+D)')
    # Note: --show-config is handled separately and implicitly acts as a mode
    
    # Language option for code mode
    parser.add_argument('--language', default="python", help='Programming language to generate code in (for code mode)')
    
    # Prompt argument
    parser.add_argument('prompt', nargs='?', default=None, help='The prompt to send')
    
    args = parser.parse_args()
    
    # Validate --all usage
    if args.all and not args.show_config:
        parser.error("--all can only be used with --show-config")

    # Handle interactive configuration mode
    if args.config is True:  # --config was used without a value
        config_path = get_config_path()
        
        # Handle configuration removal if --remove flag is present
        if args.remove:
            # Validate that config_index is explicitly provided
            if '--config-index' not in sys.argv:
                parser.error("--remove requires explicitly specifying --config-index")
            
            # Show config details before asking for confirmation
            configs = load_configs(str(config_path))
            
            # Check if index is valid
            if args.config_index < 0 or args.config_index >= len(configs):
                print(f"Error: Configuration index {args.config_index} is out of range. Valid range: 0-{len(configs)-1}")
                return
            
            # Show the configuration that will be removed
            config = configs[args.config_index]
            print(f"Configuration to remove (index {args.config_index}):")
            print(f"  Provider: {config.get('provider', 'N/A')}")
            print(f"  Model: {config.get('model', 'N/A')}")
            print(f"  Base URL: {config.get('base_url', 'N/A')}")
            print(f"  API Key: {'[Set]' if config.get('api_key') else '[Not Set]'}")
            
            # Ask for confirmation
            try:
                print("\nAre you sure you want to remove this configuration? [y/N] ", end='')
                response = input().lower()
                if response in ('y', 'yes'):
                    remove_config_entry(config_path, args.config_index)
                else:
                    print("Configuration removal cancelled.")
            except KeyboardInterrupt:
                print("\nConfiguration removal cancelled by user.")
            
            return
        
        # Regular config addition/editing (existing code)
        # If --config-index was not explicitly specified, create a new entry by passing None
        # This will cause add_config_entry to create a new entry at the end of the list
        # Otherwise, edit the existing config at the specified index
        config_index = None if args.config_index == 0 and '--config-index' not in sys.argv else args.config_index
        
        # Load existing configs to determine the new index if creating a new config
        configs = load_configs(str(config_path))
        if config_index is None:
            print(f"Creating new configuration at index {len(configs)}")
        else:
            print(f"Editing existing configuration at index {config_index}")
        
        add_config_entry(config_path, config_index)
        return
    
    # Load configuration using the specified index (needed for active config display)
    active_config = load_config(args.config, args.config_index)
    
    # Command-line arguments override config settings for active config display
    # This part is kept to ensure the active config display reflects potential overrides,
    # even though the overrides don't affect the stored configurations displayed with --all.
    if args.api_key:
        active_config["api_key"] = args.api_key
    if args.base_url:
        active_config["base_url"] = args.base_url
    if args.model:
        active_config["model"] = args.model
    
    # Show config if requested
    if args.show_config:
        config_path = get_config_path(args.config)
        configs = load_configs(args.config)
        
        print(f"Configuration file: {config_path}")
        print(f"Total configurations: {len(configs)}")
        print(f"Active configuration index: {args.config_index}")

        # Temporarily initialize a client to get the detected provider for each config
        def get_detected_provider(config):
            base_url = config.get('base_url', '')
            temp_client = NGPTClient(
                api_key=config.get('api_key', ''),
                base_url=base_url,
                provider=config.get('provider', 'N/A'),
                model=config.get('model', 'N/A')
            )
            detected = temp_client._detect_provider_from_url(base_url)
            return detected if detected else config.get('provider', 'N/A')

        if args.all:
            # Show details for all configurations
            print("\nAll configuration details:")
            for i, cfg in enumerate(configs):
                active_str = '(Active)' if i == args.config_index else ''
                detected_provider = get_detected_provider(cfg)
                provider_str = f" [{detected_provider}]" if detected_provider else ""
                
                print(f"\n--- Configuration Index {i} {active_str} ---")
                print(f"  API Key: {'[Set]' if cfg.get('api_key') else '[Not Set]'}{provider_str}")
                print(f"  Base URL: {cfg.get('base_url', 'N/A')}")
                print(f"  Provider: {cfg.get('provider', 'N/A')}")
                print(f"  Model: {cfg.get('model', 'N/A')}")
        else:
            # Show active config details and summary list
            detected_provider = get_detected_provider(active_config)
            provider_str = f" [{detected_provider}]" if detected_provider else ""
            
            print("\nActive configuration details:")
            print(f"  API Key: {'[Set]' if active_config.get('api_key') else '[Not Set]'}{provider_str}")
            print(f"  Base URL: {active_config.get('base_url', 'N/A')}")
            print(f"  Provider: {active_config.get('provider', 'N/A')}")
            print(f"  Model: {active_config.get('model', 'N/A')}")
            
            if len(configs) > 1:
                print("\nAvailable configurations:")
                for i, cfg in enumerate(configs):
                    active_marker = "*" if i == args.config_index else " "
                    detected = get_detected_provider(cfg)
                    detected_str = f" [{detected}]" if detected else ""
                    print(f"[{i}]{active_marker} {cfg.get('provider', 'N/A')} - {cfg.get('model', 'N/A')} ({'[API Key Set]' if cfg.get('api_key') else '[API Key Not Set]'}{detected_str})")
        
        return
    
    # For interactive mode, we'll allow continuing without a specific prompt
    if not args.prompt and not (args.shell or args.code or args.text or args.interactive or args.show_config or args.list_models):
        parser.print_help()
        return
        
    # Check configuration (using the potentially overridden active_config)
    if not args.show_config and not args.list_models and not check_config(active_config):
        return
    
    # Initialize client using the potentially overridden active_config
    client = NGPTClient(**active_config)
    
    try:
        # Handle listing models
        if args.list_models:
            print("Retrieving available models...")
            models = client.list_models()
            if models:
                print(f"\nAvailable models for {active_config.get('provider', 'API')}:")
                print("-" * 50)
                for model in models:
                    if "id" in model:
                        owned_by = f" ({model.get('owned_by', 'Unknown')})" if "owned_by" in model else ""
                        current = " [active]" if model["id"] == active_config["model"] else ""
                        print(f"- {model['id']}{owned_by}{current}")
                print("\nUse --model MODEL_NAME to select a specific model")
            else:
                print("No models available or could not retrieve models.")
            return
        
        # Handle modes
        if args.interactive:
            # Interactive chat mode
            interactive_chat_session(client, web_search=args.web_search, no_stream=args.no_stream)
        elif args.shell:
            if args.prompt is None:
                try:
                    print("Enter shell command description: ", end='')
                    prompt = input()
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            else:
                prompt = args.prompt
                
            command = client.generate_shell_command(prompt, web_search=args.web_search)
            if not command:
                return  # Error already printed by client
                
            print(f"\nGenerated command: {command}")
            
            try:
                print("Do you want to execute this command? [y/N] ", end='')
                response = input().lower()
            except KeyboardInterrupt:
                print("\nCommand execution cancelled by user.")
                return
                
            if response == 'y' or response == 'yes':
                import subprocess
                try:
                    try:
                        print("\nExecuting command... (Press Ctrl+C to cancel)")
                        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                        print(f"\nOutput:\n{result.stdout}")
                    except KeyboardInterrupt:
                        print("\nCommand execution cancelled by user.")
                except subprocess.CalledProcessError as e:
                    print(f"\nError:\n{e.stderr}")
                    
        elif args.code:
            if args.prompt is None:
                try:
                    print("Enter code description: ", end='')
                    prompt = input()
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            else:
                prompt = args.prompt
                
            generated_code = client.generate_code(prompt, args.language, web_search=args.web_search)
            if generated_code:
                print(f"\nGenerated code:\n{generated_code}")
            
        elif args.text:
            # Multi-line text input mode
            if args.prompt is not None:
                prompt = args.prompt
            else:
                try:
                    if HAS_PROMPT_TOOLKIT:
                        print("\033[94m\033[1m" + "Multi-line Input Mode" + "\033[0m")
                        print("Press Ctrl+D to submit, Ctrl+C to exit")
                        print("Use arrow keys to navigate, Enter for new line")
                        
                        # Create key bindings
                        kb = KeyBindings()
                        
                        # Explicitly bind Ctrl+D to exit
                        @kb.add('c-d')
                        def _(event):
                            event.app.exit(result=event.app.current_buffer.text)
                            
                        # Explicitly bind Ctrl+C to exit
                        @kb.add('c-c')
                        def _(event):
                            event.app.exit(result=None)
                            print("\nInput cancelled by user. Exiting gracefully.")
                            sys.exit(130)
                        
                        # Get terminal dimensions
                        term_width, term_height = shutil.get_terminal_size()
                        
                        # Create a styled TextArea
                        text_area = TextArea(
                            style="class:input-area",
                            multiline=True,
                            wrap_lines=True,
                            width=term_width - 4,
                            height=min(20, term_height - 8),
                            prompt=HTML("<ansicyan>>>> </ansicyan>"),
                            scrollbar=True,
                            focus_on_click=True,
                            lexer=None,
                        )
                        text_area.window.right_margins = [ScrollbarMargin(display_arrows=True)]
                        
                        # Create a title bar
                        title_bar = FormattedTextControl(
                            HTML("<style bg='ansicyan' fg='ansiblack'><b> NGPT Multi-line Editor </b></style>")
                        )
                        
                        # Create a status bar with key bindings info
                        status_bar = FormattedTextControl(
                            HTML("<ansiblue><b>Ctrl+D</b></ansiblue>: Submit | <ansiblue><b>Ctrl+C</b></ansiblue>: Cancel | <ansiblue><b>↑↓←→</b></ansiblue>: Navigate")
                        )
                        
                        # Create the layout
                        layout = Layout(
                            HSplit([
                                Window(title_bar, height=1),
                                Window(height=1, char="-", style="class:separator"),
                                text_area,
                                Window(height=1, char="-", style="class:separator"),
                                Window(status_bar, height=1),
                            ])
                        )
                        
                        # Create a style
                        style = Style.from_dict({
                            "separator": "ansigray",
                            "input-area": "bg:ansiblack fg:ansiwhite",
                            "cursor": "bg:ansiwhite fg:ansiblack",
                        })
                        
                        # Create and run the application
                        app = Application(
                            layout=layout,
                            full_screen=False,
                            key_bindings=kb,
                            style=style,
                            mouse_support=True,
                        )
                        
                        prompt = app.run()
                        
                        if not prompt or not prompt.strip():
                            print("Empty prompt. Exiting.")
                            return
                    else:
                        # Fallback to standard input with a better implementation
                        print("Enter your multi-line prompt (press Ctrl+D to submit):")
                        print("Note: Install 'prompt_toolkit' package for an enhanced input experience")
                        
                        # Use a more robust approach for multiline input without prompt_toolkit
                        lines = []
                        while True:
                            try:
                                line = input()
                                lines.append(line)
                            except EOFError:  # Ctrl+D was pressed
                                break
                        
                        prompt = "\n".join(lines)
                        if not prompt.strip():
                            print("Empty prompt. Exiting.")
                            return
                        
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            
            print("\nSubmission successful. Waiting for response...")
            response = client.chat(prompt, stream=not args.no_stream, web_search=args.web_search)
            if args.no_stream and response:
                print(response)
            
        else:
            # Default to chat mode
            if args.prompt is None:
                try:
                    print("Enter your prompt: ", end='')
                    prompt = input()
                except KeyboardInterrupt:
                    print("\nInput cancelled by user. Exiting gracefully.")
                    sys.exit(130)
            else:
                prompt = args.prompt
            response = client.chat(prompt, stream=not args.no_stream, web_search=args.web_search)
            if args.no_stream and response:
                print(response)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Exiting gracefully.")
        # Make sure we exit with a non-zero status code to indicate the operation was cancelled
        sys.exit(130)  # 130 is the standard exit code for SIGINT (Ctrl+C)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit with error code

if __name__ == "__main__":
    main() 