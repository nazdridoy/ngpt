import os
import shutil
import traceback
import threading
import sys
import time
import json
import uuid
import re
from datetime import datetime
from ngpt.core.config import get_config_dir
from ngpt.ui.colors import COLORS
from ngpt.ui.renderers import prettify_streaming_markdown, TERMINAL_RENDER_LOCK, setup_plaintext_spinner, cleanup_plaintext_spinner, create_spinner_handling_callback
from ngpt.ui.tui import spinner, get_multiline_input
from ngpt.utils.web_search import enhance_prompt_with_web_search
from ngpt.cli.handlers.session_handler import handle_session_management, clear_conversation_history, auto_save_session

# Optional imports for enhanced UI
try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.completion import WordCompleter # Import WordCompleter
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

def interactive_chat_session(client, args, logger=None):
    """Start an interactive chat session with the client.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance for logging the conversation
    """
    # Extract arguments from args object
    web_search = args.web_search
    temperature = args.temperature
    top_p = args.top_p
    max_tokens = args.max_tokens
    preprompt = args.preprompt
    multiline_enabled = True  # Could be made configurable in the future
    
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

    def show_help():
        """Displays the help menu."""
        print(separator)
        # Group commands into categories with better formatting
        print(f"\n{COLORS['cyan']}Navigation:{COLORS['reset']}")
        print(f"  {COLORS['yellow']}↑/↓{COLORS['reset']} : Browse input history")
        
        print(f"\n{COLORS['cyan']}Session Commands (prefix with '/'):{COLORS['reset']}")
        print(f"  {COLORS['yellow']}/reset{COLORS['reset']}   : Reset Session")
        print(f"  {COLORS['yellow']}/exit{COLORS['reset']}    : End session")
        print(f"  {COLORS['yellow']}/sessions{COLORS['reset']}: List saved sessions")
        print(f"  {COLORS['yellow']}/help{COLORS['reset']}    : Show this help message")
        
        if multiline_enabled:
            print(f"  {COLORS['yellow']}/ml{COLORS['reset']}      : Open multiline editor")
        
        # Add a dedicated keyboard shortcuts section
        print(f"\n{COLORS['cyan']}Keyboard Shortcuts:{COLORS['reset']}")
        if multiline_enabled:
            print(f"  {COLORS['yellow']}Ctrl+E{COLORS['reset']}   : Open multiline editor")
        print(f"  {COLORS['yellow']}Ctrl+C{COLORS['reset']}   : Interrupt/exit session")
        
        print(f"\n{separator}\n")

    def show_welcome():
        # Enhanced welcome screen with better visual structure
        box_width = min(term_width - 4, 80)  # Limit box width for better appearance
        
        print(f"\n{COLORS['cyan']}{COLORS['bold']}╭{'─' * box_width}╮{COLORS['reset']}")
        
        # Logo and welcome message
        logo_lines = [
            " ███╗   ██╗ ██████╗ ██████╗ ████████╗",
            " ████╗  ██║██╔════╝ ██╔══██╗╚══██╔══╝",
            " ██╔██╗ ██║██║  ███╗██████╔╝   ██║   ",
            " ██║╚██╗██║██║   ██║██╔═══╝    ██║   ",
            " ██║ ╚████║╚██████╔╝██║        ██║   ",
            " ╚═╝  ╚═══╝ ╚═════╝ ╚═╝        ╚═╝   "
        ]
        
        # Print logo with proper centering
        for line in logo_lines:
            padding = (box_width - len(line)) // 2
            print(f"{COLORS['cyan']}{COLORS['bold']}│{COLORS['reset']}{' ' * padding}{COLORS['green']}{line}{' ' * (box_width - len(line) - padding)}{COLORS['cyan']}{COLORS['bold']}│{COLORS['reset']}")
        
        # Add a blank line after logo
        print(f"{COLORS['cyan']}{COLORS['bold']}│{' ' * box_width}│{COLORS['reset']}")
        
        # Version info
        from ngpt.version import __version__
        version_info = f"v{__version__}"
        version_padding = (box_width - len(version_info)) // 2
        print(f"{COLORS['cyan']}{COLORS['bold']}│{COLORS['reset']}{' ' * version_padding}{COLORS['yellow']}{version_info}{' ' * (box_width - len(version_info) - version_padding)}{COLORS['cyan']}{COLORS['bold']}│{COLORS['reset']}")
        
        # Status line - improved model detection
        model_name = None
        
        # Try to get model from client object
        if hasattr(client, 'model'):
            model_name = client.model
        # Try to get from client config
        elif hasattr(client, 'config') and hasattr(client.config, 'model'):
            model_name = client.config.model
        # Fallback to args
        elif hasattr(args, 'model') and args.model:
            model_name = args.model
            
        # Truncate model name if it's too long (max 40 characters)
        if model_name and len(model_name) > 40:
            model_name = model_name[:37] + "..."
        
        model_info = f"Model: {model_name}" if model_name else "Default model"
        status_line = f"Temperature: {temperature} | {model_info}"
        if len(status_line) > box_width:
            status_line = f"Temp: {temperature} | {model_info}"  # Shorten if needed
        status_padding = (box_width - len(status_line)) // 2
        print(f"{COLORS['cyan']}{COLORS['bold']}│{COLORS['reset']}{' ' * status_padding}{COLORS['gray']}{status_line}{' ' * (box_width - len(status_line) - status_padding)}{COLORS['cyan']}{COLORS['bold']}│{COLORS['reset']}")
        
        print(f"{COLORS['cyan']}{COLORS['bold']}╰{'─' * box_width}╯{COLORS['reset']}")
        
        # Show help info after the welcome box
        show_help()
        
        # Show logging info if logger is available
        if logger:
            print(f"{COLORS['green']}Logging conversation to: {logger.get_log_path()}{COLORS['reset']}")
        
        # Display a note about web search if enabled
        if web_search:
            print(f"{COLORS['green']}Web search capability is enabled.{COLORS['reset']}")
        
        # Display a note about markdown rendering
        if args.plaintext:
            print(f"{COLORS['yellow']}Note: Using plain text mode (--plaintext). For markdown rendering, remove --plaintext flag.{COLORS['reset']}")
    
    # Show the welcome screen
    show_welcome()
    
    # Custom separator - use the same length for consistency
    def print_separator():
        # Make sure there's exactly one newline before and after
        # Use sys.stdout.write for direct control, avoiding any extra newlines
        with TERMINAL_RENDER_LOCK:
            sys.stdout.write(f"\n{separator}\n")
            sys.stdout.flush()
    
    # Initialize conversation history
    system_prompt = preprompt if preprompt else "You are a helpful assistant."
    
    # Add markdown formatting instruction to system prompt if not in plaintext mode
    if not args.plaintext:
        if system_prompt:
            system_prompt += " You can use markdown formatting in your responses where appropriate."
        else:
            system_prompt = "You are a helpful assistant. You can use markdown formatting in your responses where appropriate."
    
    conversation = []
    system_message = {"role": "system", "content": system_prompt}
    conversation.append(system_message)

    # Initialize current session tracking
    current_session_id = None
    current_session_filepath = None
    current_session_name = None
    first_user_prompt = None
    
    # Log system prompt if logging is enabled
    if logger and preprompt:
        logger.log("system", system_prompt)
    
    # Initialize prompt_toolkit history
    prompt_history = InMemoryHistory() if HAS_PROMPT_TOOLKIT else None
    
    # Decorative chat headers with rounded corners
    def user_header():
        return f"{COLORS['cyan']}{COLORS['bold']}╭─ 👤 You {COLORS['reset']}"
    
    def ngpt_header():
        return f"{COLORS['green']}{COLORS['bold']}╭─ 🤖 nGPT {COLORS['reset']}"
    
    # Define reserved commands once - moved out of conditional blocks
    reserved_commands = [
        '/reset', '/sessions', '/help', '/ml',
        '/exit'
    ]
    
    # Function to clear conversation history
    def clear_history():
        nonlocal conversation, current_session_id, current_session_filepath, current_session_name
        conversation = clear_conversation_history(conversation, system_prompt)
        current_session_id = None
        current_session_filepath = None
        current_session_name = None
        with TERMINAL_RENDER_LOCK:
            print(f"\n{COLORS['yellow']}Conversation history cleared. A new session will be created on next exchange.{COLORS['reset']}")
            print(separator)
    
    # --- Session Management Functions ---

    def session_manager():
        """Interactive session manager for the /sessions command."""
        nonlocal conversation, current_session_id, current_session_filepath, current_session_name
        
        # Call the session management handler
        result = handle_session_management(logger=logger)
        
        # If a session was loaded, update our local variables
        if result is not None:
            session_id, session_filepath, session_name, loaded_conversation = result
            conversation = loaded_conversation
            current_session_id = session_id
            current_session_filepath = session_filepath
            current_session_name = session_name
            
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
                
                # Add Ctrl+E binding for multiline input
                @kb.add('c-e')
                def open_multiline_editor(event):
                    # Exit the prompt and return a special value that indicates we want multiline
                    event.app.exit(result="/ml")
                
                # Get user input with styled prompt - using proper HTML formatting
                user_input = pt_prompt(
                    HTML("<ansicyan><b>╭─ 👤 You:</b></ansicyan> "),
                    style=style,
                    key_bindings=kb,
                    history=prompt_history,
                    # Add completer for fuzzy suggestions with reserved commands only
                    completer=WordCompleter(reserved_commands, ignore_case=True, sentence=True)
                )
            else:
                user_input = input(f"{user_header()}: {COLORS['reset']}")
            
            # Check for exit commands (no prefix for these for convenience)
            if user_input.lower() in ('/exit', 'exit', 'quit', 'bye'):
                print(f"\n{COLORS['green']}Ending chat session. Goodbye!{COLORS['reset']}")
                break
            
            # Check if input starts with / but is not a reserved command
            if user_input.startswith('/') and not any(user_input.lower().startswith(cmd.lower()) for cmd in reserved_commands):
                print(f"{COLORS['red']}Unknown command: {user_input}{COLORS['reset']}")
                continue
            
            # Check for special commands (now require a '/' prefix)
            if user_input.lower() == '/reset':
                clear_history()
                continue
            
            if user_input.lower() == '/sessions':
                session_manager()
                continue

            if user_input.lower() == '/help':
                show_help()
                continue
                
            # Handle multiline input from either /ml command or Ctrl+E shortcut
            if multiline_enabled and user_input.lower() == "/ml":
                print(f"{COLORS['cyan']}Opening multiline editor. Press Ctrl+D to submit.{COLORS['reset']}")
                multiline_input = get_multiline_input()
                if multiline_input is None:
                    # Input was cancelled
                    print(f"{COLORS['yellow']}Multiline input cancelled.{COLORS['reset']}")
                    continue
                elif not multiline_input.strip():
                    print(f"{COLORS['yellow']}Empty message skipped.{COLORS['reset']}")
                    continue
                else:
                    # Use the multiline input as user_input
                    user_input = multiline_input
                    print(f"{user_header()}")
                    print(f"{COLORS['cyan']}│ {COLORS['reset']}{user_input}")
            
            # Skip empty messages but don't raise an error
            if not user_input.strip():
                print(f"{COLORS['yellow']}Empty message skipped. Type 'exit' to quit.{COLORS['reset']}")
                continue
            
            # Store first user prompt if not set
            if first_user_prompt is None and not user_input.startswith('/'):
                first_user_prompt = user_input
            
            # Add user message to conversation
            user_message = {"role": "user", "content": user_input}
            conversation.append(user_message)
            
            # Log user message if logging is enabled
            if logger:
                logger.log("user", user_input)
                
            # Enhance prompt with web search if enabled
            enhanced_prompt = user_input
            if web_search:
                try:
                    # Start spinner for web search
                    stop_spinner = threading.Event()
                    spinner_thread = threading.Thread(
                        target=spinner, 
                        args=("Searching the web for information...",), 
                        kwargs={"stop_event": stop_spinner, "color": COLORS['cyan']}
                    )
                    spinner_thread.daemon = True
                    spinner_thread.start()
                    
                    try:
                        enhanced_prompt = enhance_prompt_with_web_search(user_input, logger=logger)
                        # Stop the spinner
                        stop_spinner.set()
                        spinner_thread.join()
                        # Clear the spinner line completely
                        sys.stdout.write("\r" + " " * shutil.get_terminal_size().columns + "\r")
                        sys.stdout.flush()
                        print(f"{COLORS['green']}Enhanced input with web search results.{COLORS['reset']}")
                    except Exception as e:
                        # Stop the spinner before re-raising
                        stop_spinner.set()
                        spinner_thread.join()
                        raise e
                    
                    # Update the user message in conversation with enhanced prompt
                    for i in range(len(conversation) - 1, -1, -1):
                        if conversation[i]["role"] == "user" and conversation[i]["content"] == user_input:
                            conversation[i]["content"] = enhanced_prompt
                            break
                    
                    # Log the enhanced prompt if logging is enabled
                    if logger:
                        # Use "web_search" role instead of "system" for clearer logs
                        logger.log("web_search", enhanced_prompt.replace(user_input, "").strip())
                except Exception as e:
                    print(f"{COLORS['yellow']}Warning: Failed to enhance prompt with web search: {str(e)}{COLORS['reset']}")
                    # Continue with the original prompt if web search fails
            
            # Print assistant indicator with formatting - but only if we're not going to show a rich formatted box
            # With Rich prettify, no header should be printed as the Rich panel already includes it
            should_print_header = True

            # Determine if we should print a header based on formatting options
            if not args.plaintext:
                # Don't print header for stream-prettify
                should_print_header = False
            else:
                should_print_header = True
            
            # Print the header if needed
            if should_print_header:
                with TERMINAL_RENDER_LOCK:
                    if not args.plaintext:
                        print(f"\n{ngpt_header()}: {COLORS['reset']}", end="", flush=True)
                    else:
                        print(f"\n{ngpt_header()}: {COLORS['reset']}", flush=True)
            
            # Determine streaming behavior
            should_stream = not args.plaintext
            
            # Setup for stream-prettify
            stream_callback = None
            live_display = None
            stop_spinner_func = None
            stop_spinner_event = None
            first_content_received = False
            
            # Set up spinner for plaintext mode
            plaintext_spinner_thread = None
            plaintext_stop_event = None
            
            if args.plaintext:
                # Use spinner for plaintext mode
                plaintext_spinner_thread, plaintext_stop_event = setup_plaintext_spinner("Waiting for response...", COLORS['green'])
            
            if not args.plaintext and should_stream:
                # Set up streaming markdown (same as other modes)
                live_display, stream_callback, setup_spinner = prettify_streaming_markdown()
                
                if not live_display:
                    # Fallback to plain text if live display setup failed
                    should_stream = False
                    print(f"{COLORS['yellow']}Falling back to plain text mode.{COLORS['reset']}")
                else:
                    # Set up the spinner if we have a live display and stream-prettify is enabled
                    stop_spinner_event = threading.Event()
                    stop_spinner_func = setup_spinner(stop_spinner_event, "Waiting for response...", color=COLORS['green'])
                    
                    # Create a wrapper for the stream callback that handles spinner
                    if stream_callback:
                        original_callback = stream_callback
                        first_content_received_ref = [first_content_received]
                        stream_callback = create_spinner_handling_callback(original_callback, stop_spinner_func, first_content_received_ref)

            # Get AI response with conversation history
            response = client.chat(
                prompt=enhanced_prompt,
                messages=conversation,
                stream=should_stream,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                markdown_format=not args.plaintext,
                stream_callback=stream_callback
            )
            
            # Stop plaintext spinner if it was started
            cleanup_plaintext_spinner(plaintext_spinner_thread, plaintext_stop_event)
            
            # Ensure spinner is stopped if no content was received
            if stop_spinner_event and not first_content_received_ref[0]:
                stop_spinner_event.set()
            
            # Stop live display if using stream-prettify
            if not args.plaintext and live_display and first_content_received_ref[0]:
                # Before stopping the live display, update with complete=True to show final formatted content
                if stream_callback and response:
                    stream_callback(response, complete=True)
            
            # Add AI response to conversation history
            if response:
                assistant_message = {"role": "assistant", "content": response}
                conversation.append(assistant_message)
                
                # Print response if not streamed (plaintext mode)
                if args.plaintext:
                    with TERMINAL_RENDER_LOCK:
                        print(response)
                
                # Log AI response if logging is enabled
                if logger:
                    logger.log("assistant", response)
            
            # Auto-save conversation after each exchange
            current_session_id, current_session_filepath, current_session_name = auto_save_session(
                conversation=conversation,
                session_id=current_session_id,
                session_filepath=current_session_filepath,
                session_name=current_session_name,
                first_user_prompt=first_user_prompt,
                logger=logger
            )
        
            # Print separator between exchanges
            print_separator()
            
            # Add a small delay to ensure terminal stability
            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\n\n{COLORS['yellow']}Chat session interrupted by user.{COLORS['reset']}")
    except Exception as e:
        print(f"\n{COLORS['yellow']}Error in chat session: {str(e)}{COLORS['reset']}")
        if os.environ.get("NGPT_DEBUG"):
            traceback.print_exc() 