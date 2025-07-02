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
        print(f"  {COLORS['yellow']}/history{COLORS['reset']} : Show conversation history")
        print(f"  {COLORS['yellow']}/clear{COLORS['reset']}   : Reset conversation")
        print(f"  {COLORS['yellow']}/exit{COLORS['reset']}    : End session")
        print(f"  {COLORS['yellow']}/save [name]{COLORS['reset']} : Save session (with optional custom name)")
        print(f"  {COLORS['yellow']}/load{COLORS['reset']}    : Load a previous session")
        print(f"  {COLORS['yellow']}/sessions{COLORS['reset']}: List saved sessions")
        print(f"  {COLORS['yellow']}/help{COLORS['reset']}    : Show this help message")
        
        if multiline_enabled:
            print(f"  {COLORS['yellow']}/ml{COLORS['reset']}      : Open multiline editor")
        
        print(f"\n{separator}\n")

    show_help()
    
    # Show logging info if logger is available
    if logger:
        print(f"{COLORS['green']}Logging conversation to: {logger.get_log_path()}{COLORS['reset']}")
    
    # Display a note about web search if enabled
    if web_search:
        print(f"{COLORS['green']}Web search capability is enabled.{COLORS['reset']}")
    
    # Display a note about markdown rendering only once at the beginning
    if args.plaintext:
        print(f"{COLORS['yellow']}Note: Using plain text mode (--plaintext). For markdown rendering, remove --plaintext flag.{COLORS['reset']}")
    
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
    
    # Function to display conversation history
    def display_history():
        with TERMINAL_RENDER_LOCK:
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
        nonlocal conversation, current_session_id, current_session_filepath, current_session_name
        conversation = [{"role": "system", "content": system_prompt}]
        current_session_id = None
        current_session_filepath = None
        current_session_name = None
        with TERMINAL_RENDER_LOCK:
            print(f"\n{COLORS['yellow']}Conversation history cleared. A new session will be created on next save.{COLORS['reset']}")
            print(separator)
    
    # --- Session Management Functions ---

    def get_history_dir():
        """Get the history directory, creating it if it doesn't exist."""
        history_dir = get_config_dir() / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        return history_dir
    
    def get_session_index():
        """Get the session index from session-index.json, or create if it doesn't exist."""
        history_dir = get_history_dir()
        index_path = history_dir / "session-index.json"
        
        if index_path.exists():
            try:
                with open(index_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # If index is corrupted, create a new one
                return {"sessions": []}
        else:
            return {"sessions": []}
    
    def save_session_index(index):
        """Save the session index to session-index.json."""
        history_dir = get_history_dir()
        index_path = history_dir / "session-index.json"
        
        with open(index_path, "w") as f:
            json.dump(index, f, indent=2)
    
    def generate_session_name(content):
        """Generate a session name from the first user prompt."""
        # Extract the first 30 characters, removing special characters
        if not content:
            return "Untitled Session"
        
        # Remove special characters and limit to 30 chars
        name = re.sub(r'[^\w\s]', '', content).strip()
        name = re.sub(r'\s+', ' ', name)  # Replace multiple spaces with a single space
        
        if len(name) > 30:
            name = name[:30].strip() + "..."
        
        return name or "Untitled Session"
    
    def update_session_in_index(session_id, session_name, update_existing=False):
        """Add or update a session in the index."""
        index = get_session_index()
        
        # Check if session already exists in index
        session_exists = False
        for session in index["sessions"]:
            if session["id"] == session_id:
                session["name"] = session_name
                session_exists = True
                break
        
        # If session doesn't exist and we're not just updating, add it
        if not session_exists and not update_existing:
            index["sessions"].append({
                "id": session_id,
                "name": session_name,
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        save_session_index(index)

    def save_session(session_name=None):
        """Save the current conversation to a JSON file, creating a new session or updating the current one."""
        nonlocal current_session_id, current_session_filepath, current_session_name, first_user_prompt
        history_dir = get_history_dir()

        if current_session_id is None:
            # Generate a new session ID if not already set (new session or cleared)
            current_session_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            current_session_filepath = history_dir / f"session_{current_session_id}.json"
            
            # Generate a session name if none provided
            if not session_name:
                # Use first user prompt to generate name
                if first_user_prompt:
                    current_session_name = generate_session_name(first_user_prompt)
                else:
                    current_session_name = "Untitled Session"
            else:
                current_session_name = session_name
                
            # Add to index
            update_session_in_index(current_session_id, current_session_name)
            
            print(f"\n{COLORS['green']}Starting new session: {current_session_name}{COLORS['reset']}")
        elif session_name:
            # Update existing session name
            current_session_name = session_name
            update_session_in_index(current_session_id, current_session_name, update_existing=True)
        
        with open(current_session_filepath, "w") as f:
            json.dump(conversation, f, indent=2)
        
        print(f"\n{COLORS['green']}Session saved as: {current_session_name}{COLORS['reset']}")

    def list_sessions():
        """List all saved sessions."""
        index = get_session_index()
        
        if not index["sessions"]:
            print(f"\n{COLORS['yellow']}No saved sessions found.{COLORS['reset']}")
            return
            
        print(f"\n{COLORS['cyan']}{COLORS['bold']}Saved Sessions:{COLORS['reset']}")
        for i, session in enumerate(index["sessions"]):
            print(f"  [{i}] {session['name']} (created: {session['created_at']})")

    def load_session():
        """Load a conversation from a saved session file."""
        nonlocal conversation, current_session_id, current_session_filepath, current_session_name
        index = get_session_index()

        if not index["sessions"]:
            print(f"\n{COLORS['yellow']}No saved sessions to load.{COLORS['reset']}")
            return

        list_sessions()
        
        try:
            choice = input("Enter the number of the session to load: ")
            choice_index = int(choice)
            
            if 0 <= choice_index < len(index["sessions"]):
                session = index["sessions"][choice_index]
                history_dir = get_history_dir()
                session_file = history_dir / f"session_{session['id']}.json"
                
                if not session_file.exists():
                    print(f"\n{COLORS['red']}Error: Session file not found. The index may be out of sync.{COLORS['reset']}")
                    return
                
                with open(session_file, "r") as f:
                    loaded_conversation = json.load(f)
                
                # Basic validation
                if isinstance(loaded_conversation, list) and all(isinstance(item, dict) for item in loaded_conversation):
                    conversation = loaded_conversation
                    current_session_filepath = session_file
                    current_session_id = session["id"]
                    current_session_name = session["name"]
                    print(f"\n{COLORS['green']}Session loaded: {current_session_name}{COLORS['reset']}")
                    display_history()
                else:
                    print(f"\n{COLORS['red']}Error: Invalid session file format.{COLORS['reset']}")
            else:
                print(f"\n{COLORS['red']}Error: Invalid selection.{COLORS['reset']}")
        except (ValueError, IndexError):
            print(f"\n{COLORS['red']}Error: Invalid input. Please enter a number from the list.{COLORS['reset']}")

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
                    history=prompt_history,
                    # Add completer for fuzzy suggestions
                    completer=WordCompleter([
                        '/history', '/clear', '/save', '/load', '/sessions', '/help', '/ml',
                        '/exit', '/quit', '/bye' # Include exit commands for completeness in suggestions
                    ], ignore_case=True, sentence=True)
                )
            else:
                user_input = input(f"{user_header()}: {COLORS['reset']}")
            
            # Check for exit commands (no prefix for these for convenience)
            if user_input.lower() in ('/exit', '/quit', '/bye', 'exit', 'quit', 'bye'):
                print(f"\n{COLORS['green']}Ending chat session. Goodbye!{COLORS['reset']}")
                break
            
            # Check for special commands (now require a '/' prefix)
            if user_input.lower() == '/history':
                display_history()
                continue
            
            if user_input.lower() == '/clear':
                clear_history()
                continue
            
            if user_input.lower().startswith('/save'):
                # Check if a session name was provided
                parts = user_input.strip().split(' ', 1)
                if len(parts) > 1 and parts[1].strip():
                    save_session(parts[1].strip())
                else:
                    save_session()
                continue

            if user_input.lower() == '/sessions':
                list_sessions()
                continue

            if user_input.lower() == '/load':
                load_session()
                continue

            if user_input.lower() == '/help':
                show_help()
                continue
                
            if multiline_enabled and user_input.lower() == '/ml':
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