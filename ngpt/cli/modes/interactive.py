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
        print(f"  {COLORS['yellow']}/clear{COLORS['reset']}   : Reset conversation")
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
    
    # Function to clear conversation history
    def clear_history():
        nonlocal conversation, current_session_id, current_session_filepath, current_session_name
        conversation = [{"role": "system", "content": system_prompt}]
        current_session_id = None
        current_session_filepath = None
        current_session_name = None
        with TERMINAL_RENDER_LOCK:
            print(f"\n{COLORS['yellow']}Conversation history cleared. A new session will be created on next exchange.{COLORS['reset']}")
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
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Check if session already exists in index
        session_exists = False
        for session in index["sessions"]:
            if session["id"] == session_id:
                session["name"] = session_name
                session["last_modified"] = now_str
                session_exists = True
                break
        # If session doesn't exist and we're not just updating, add it
        if not session_exists and not update_existing:
            index["sessions"].append({
                "id": session_id,
                "name": session_name,
                "created_at": now_str,
                "last_modified": now_str
            })
        save_session_index(index)

    def save_session(session_name=None, silent=False):
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
            if not silent:
                print(f"{COLORS['green']}Session: {current_session_name}{COLORS['reset']}")
        else:
            # Always update last_modified, and optionally name
            if session_name:
                current_session_name = session_name
                if not silent:
                    print(f"{COLORS['green']}Session renamed: {current_session_name}{COLORS['reset']}")
            update_session_in_index(current_session_id, current_session_name, update_existing=True)
        with open(current_session_filepath, "w") as f:
            json.dump(conversation, f, indent=2)

    def list_sessions():
        """Interactive session manager with enhanced visuals for the /sessions command."""
        index = get_session_index()
        if not index["sessions"]:
            print(f"\n{COLORS['yellow']}No saved sessions found.{COLORS['reset']}")
            return
        
        # Create command history for session manager
        session_command_history = InMemoryHistory() if HAS_PROMPT_TOOLKIT else None
        
        def get_last_modified(session):
            return session.get("last_modified") or session.get("created_at") or ""
        
        # Sort sessions by last modified time (oldest first)
        sorted_sessions = sorted(index["sessions"], key=get_last_modified, reverse=False)
        
        # Format dates nicely and calculate session sizes
        for session in sorted_sessions:
            # Format the date
            last = session.get('last_modified') or session.get('created_at', 'N/A')
            try:
                last_fmt = datetime.strptime(last, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %I:%M %p')
                session['last_modified_fmt'] = last_fmt
            except Exception:
                session['last_modified_fmt'] = last
            
            # Calculate session size
            history_dir = get_history_dir()
            session_file = history_dir / f"session_{session['id']}.json"
            size_indicator = "•"
            size_color = COLORS['green']
            if session_file.exists():
                size = os.path.getsize(session_file)
                if size < 10000:  # Small session
                    size_indicator = "•"
                    size_color = COLORS['green']
                elif size < 50000:  # Medium session
                    size_indicator = "••"
                    size_color = COLORS['yellow']
                else:  # Large session
                    size_indicator = "•••"
                    size_color = COLORS['red']
            session['size_indicator'] = size_indicator
            session['size_color'] = size_color
        
        # Define modes
        MODES = {
            'list': 'List Sessions',
            'preview': 'Preview Session',
            'help': 'Help'
        }
        
        current_mode = 'list'
        # Initialize to the last index (newest session) rather than the first
        current_session_idx = len(sorted_sessions) - 1 if sorted_sessions else -1
        preview_mode = 'tail'
        preview_count = 5
        filtered_sessions = sorted_sessions.copy()
        search_query = ""
        
        # Terminal width for better formatting
        try:
            term_width = shutil.get_terminal_size().columns
        except:
            term_width = 80
        
        # Separator for visual separation
        separator = f"{COLORS['gray']}{'─' * min(term_width - 4, 50)}{COLORS['reset']}"
        
        def print_header():
            """Print a nice header with current mode."""
            mode_name = MODES.get(current_mode, 'Sessions')
            print(f"\n{COLORS['cyan']}{COLORS['bold']}🤖 nGPT Session Manager - {mode_name} 🤖{COLORS['reset']}")
            print(separator)
        
        def print_help():
            """Print help information."""
            nonlocal current_mode
            
            current_mode = 'help'
            print_header()
            print(f"\n{COLORS['cyan']}{COLORS['bold']}Available Commands:{COLORS['reset']}")
            print(f"  {COLORS['yellow']}list{COLORS['reset']}                 Show session list")
            print(f"  {COLORS['yellow']}preview <idx>{COLORS['reset']}        Show preview of session messages")
            print(f"  {COLORS['yellow']}load <idx>{COLORS['reset']}           Load a session")
            print(f"  {COLORS['yellow']}rename <idx> <name>{COLORS['reset']}  Rename a session")
            print(f"  {COLORS['yellow']}delete <idx>{COLORS['reset']}         Delete a session")
            print(f"  {COLORS['yellow']}search <query>{COLORS['reset']}       Search sessions by name")
            print(f"  {COLORS['yellow']}help{COLORS['reset']}                 Show this help")
            print(f"  {COLORS['yellow']}exit{COLORS['reset']}                 Exit session manager")
            
            print(f"\n{COLORS['cyan']}{COLORS['bold']}Preview Commands:{COLORS['reset']}")
            print(f"  {COLORS['yellow']}head <idx> [count]{COLORS['reset']}   Show first messages in session")
            print(f"  {COLORS['yellow']}tail <idx> [count]{COLORS['reset']}   Show last messages in session")
            
            print(f"\n{COLORS['cyan']}{COLORS['bold']}Navigation:{COLORS['reset']}")
            print(f"  {COLORS['yellow']}↑/↓{COLORS['reset']}                  Browse command history")
            
            print(f"\n{COLORS['cyan']}{COLORS['bold']}Session Size Legend:{COLORS['reset']}")
            print(f"  {COLORS['green']}•{COLORS['reset']}    Small session")
            print(f"  {COLORS['yellow']}••{COLORS['reset']}   Medium session")
            print(f"  {COLORS['red']}•••{COLORS['reset']}  Large session")
            print(separator)
        
        def print_session_list():
            """Print session list with enhancements."""
            nonlocal filtered_sessions, current_mode
            
            current_mode = 'list'
            
            # Apply search filter if needed
            if search_query:
                filtered_sessions = [s for s in sorted_sessions if search_query.lower() in s['name'].lower()]
            else:
                filtered_sessions = sorted_sessions.copy()
            
            print_header()
            
            # Show search status if filtering
            if search_query:
                print(f"{COLORS['yellow']}Filtered by: \"{search_query}\" ({len(filtered_sessions)} results){COLORS['reset']}")
            
            # Header row
            print(f"\n  {COLORS['cyan']}#{COLORS['reset']}  {COLORS['cyan']}Size{COLORS['reset']}  {COLORS['cyan']}Session Name{COLORS['reset']}                        {COLORS['cyan']}Last Modified{COLORS['reset']}")
            print(f"  {COLORS['gray']}─{COLORS['reset']}  {COLORS['gray']}────{COLORS['reset']}  {COLORS['gray']}────────────────────────────────────{COLORS['reset']}  {COLORS['gray']}─────────────────{COLORS['reset']}")
            
            # Session rows
            if not filtered_sessions:
                print(f"\n  {COLORS['yellow']}No sessions found.{COLORS['reset']}")
            else:
                for i, session in enumerate(filtered_sessions):
                    name = session['name']
                    last_fmt = session.get('last_modified_fmt', 'Unknown')
                    size_indicator = session.get('size_indicator', '•')
                    size_color = session.get('size_color', COLORS['green'])
                    
                    # Truncate name if too long
                    if len(name) > 30:
                        name = name[:27] + "..."
                    
                    # Display sessions with consistent formatting
                    if i == current_session_idx and current_mode == 'list':
                        print(f"  {COLORS['cyan']}{COLORS['bold']}{i:<2}{COLORS['reset']} {size_color}{size_indicator:<4}{COLORS['reset']} {COLORS['white']}{COLORS['bold']}{name:<35}{COLORS['reset']} {COLORS['white']}{last_fmt}{COLORS['reset']}")
                    else:
                        print(f"  {COLORS['yellow']}{i:<2}{COLORS['reset']} {size_color}{size_indicator:<4}{COLORS['reset']} {COLORS['white']}{name:<35}{COLORS['reset']} {COLORS['gray']}{last_fmt}{COLORS['reset']}")
            
            print(separator)
            print(f"{COLORS['green']}Enter command: {COLORS['reset']}(Type 'help' for available commands)")
        
        def show_session_preview(idx, mode='tail', count=5):
            """Show preview of session content."""
            nonlocal filtered_sessions, current_mode
            
            if not filtered_sessions:
                print(f"{COLORS['red']}No sessions available.{COLORS['reset']}")
                return
                
            if idx < 0 or idx >= len(filtered_sessions):
                print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                return
            
            current_mode = 'preview'
            session = filtered_sessions[idx]
            history_dir = get_history_dir()
            session_file = history_dir / f"session_{session['id']}.json"
            
            if not session_file.exists():
                print(f"{COLORS['red']}Session file not found.{COLORS['reset']}")
                return
            
            try:
                with open(session_file, "r") as f:
                    loaded_conversation = json.load(f)
                    
                # Extract user/assistant pairs
                pairs = []
                current_pair = []
                for msg in loaded_conversation:
                    if msg['role'] == 'user':
                        if current_pair:
                            pairs.append(current_pair)
                        current_pair = [msg]
                    elif msg['role'] == 'assistant' and current_pair:
                        current_pair.append(msg)
                if current_pair:
                    pairs.append(current_pair)
                    
                # Get preview based on mode
                if mode == 'tail':
                    to_show = pairs[-count:]
                    mode_desc = f"last {len(to_show)}"
                else:  # head
                    to_show = pairs[:count]
                    mode_desc = f"first {len(to_show)}"
                    
                print_header()
                print(f"\n{COLORS['cyan']}{COLORS['bold']}Preview of {mode_desc} messages from:{COLORS['reset']} {COLORS['white']}{session['name']}{COLORS['reset']}")
                print(separator)
                
                if not to_show:
                    print(f"\n{COLORS['yellow']}No messages found in this session.{COLORS['reset']}")
                
                # Show pairs with nice formatting
                for i, pair in enumerate(to_show):
                    # User message
                    print(f"\n{COLORS['cyan']}{COLORS['bold']}╭─ 👤 User {i+1}{COLORS['reset']}")
                    
                    # Truncate if very long
                    user_content = pair[0]['content']
                    if len(user_content) > 500:
                        user_content = user_content[:497] + "..."
                        
                    print(f"{COLORS['cyan']}│{COLORS['reset']} {user_content}")
                    
                    # Assistant message if available
                    if len(pair) > 1:
                        print(f"\n{COLORS['green']}{COLORS['bold']}╭─ 🤖 AI{COLORS['reset']}")
                        
                        # Truncate if very long
                        ai_content = pair[1]['content']
                        if len(ai_content) > 500:
                            ai_content = ai_content[:497] + "..."
                            
                        print(f"{COLORS['green']}│{COLORS['reset']} {ai_content}")
                
                print(separator)
                print(f"{COLORS['green']}Enter command: {COLORS['reset']}(Type 'list' to return to session list)")
                
            except Exception as e:
                print(f"{COLORS['red']}Error reading session: {str(e)}{COLORS['reset']}")
        
        def process_command(command):
            """Process a command entered by the user."""
            nonlocal current_mode, current_session_idx, preview_mode, preview_count, search_query
            nonlocal filtered_sessions, sorted_sessions, conversation, current_session_id, current_session_filepath, current_session_name
            
            if not command.strip():
                return True
            
            parts = command.strip().split()
            cmd = parts[0].lower()
            
            # Check if the command has a slash prefix but is not a valid command
            if cmd.startswith('/'):
                print(f"{COLORS['red']}Unknown command: {cmd}. Commands in the session manager don't use slash prefix.{COLORS['reset']}")
                return True
            
            # Exit commands
            if cmd in ('exit', 'quit', 'q'):
                print(f"{COLORS['green']}Exiting session manager.{COLORS['reset']}")
                return False
            
            # Help command
            if cmd == 'help':
                print_help()
                return True
            
            # List command
            if cmd == 'list':
                current_mode = 'list'
                search_query = ""  # Clear any search
                print_session_list()
                return True
            
            # Preview commands
            if cmd in ('head', 'tail'):
                if len(parts) < 2:
                    print(f"{COLORS['red']}Usage: {cmd} <idx> [count]{COLORS['reset']}")
                    return True
                
                try:
                    idx = int(parts[1])
                    count = int(parts[2]) if len(parts) > 2 else 5
                except ValueError:
                    print(f"{COLORS['red']}Invalid index or count.{COLORS['reset']}")
                    return True
                
                current_mode = 'preview'
                preview_mode = cmd
                preview_count = max(1, count)
                show_session_preview(idx, preview_mode, preview_count)
                return True
            
            # Preview shorthand
            if cmd == 'preview':
                if len(parts) < 2:
                    print(f"{COLORS['red']}Usage: preview <idx>{COLORS['reset']}")
                    return True
                
                try:
                    idx = int(parts[1])
                except ValueError:
                    print(f"{COLORS['red']}Invalid index.{COLORS['reset']}")
                    return True
                
                current_mode = 'preview'
                show_session_preview(idx, preview_mode, preview_count)
                return True
            
            # Search command
            if cmd == 'search':
                if len(parts) < 2:
                    search_query = ""  # Clear search
                    print(f"{COLORS['green']}Search cleared.{COLORS['reset']}")
                else:
                    search_query = ' '.join(parts[1:])
                    print(f"{COLORS['green']}Searching for: {search_query}{COLORS['reset']}")
                
                current_mode = 'list'
                print_session_list()
                return True
            
            # Load command
            if cmd == 'load':
                if len(parts) < 2:
                    print(f"{COLORS['red']}Usage: load <idx>{COLORS['reset']}")
                    return True
                
                try:
                    idx = int(parts[1])
                except ValueError:
                    print(f"{COLORS['red']}Invalid index.{COLORS['reset']}")
                    return True
                
                # Make sure we have filtered sessions
                if not filtered_sessions:
                    print_session_list()
                
                if idx < 0 or idx >= len(filtered_sessions):
                    print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                    return True
                
                session = filtered_sessions[idx]
                
                # Actually load session
                nonlocal conversation, current_session_id, current_session_filepath, current_session_name
                history_dir = get_history_dir()
                session_file = history_dir / f"session_{session['id']}.json"
                
                if not session_file.exists():
                    print(f"{COLORS['red']}Session file not found.{COLORS['reset']}")
                    return True
                
                try:
                    with open(session_file, "r") as f:
                        loaded_conversation = json.load(f)
                        
                    if isinstance(loaded_conversation, list) and all(isinstance(item, dict) for item in loaded_conversation):
                        conversation = loaded_conversation
                        current_session_filepath = session_file
                        current_session_id = session["id"]
                        current_session_name = session["name"]
                        print(f"\n{COLORS['green']}Session loaded: {current_session_name}{COLORS['reset']}")
                        return False  # Exit session manager and return to chat
                    else:
                        print(f"{COLORS['red']}Invalid session file format.{COLORS['reset']}")
                except Exception as e:
                    print(f"{COLORS['red']}Error loading session: {str(e)}{COLORS['reset']}")
                
                return True
            
            # Rename command
            if cmd == 'rename':
                if len(parts) < 3:
                    print(f"{COLORS['red']}Usage: rename <idx> <new name>{COLORS['reset']}")
                    return True
                
                try:
                    idx = int(parts[1])
                except ValueError:
                    print(f"{COLORS['red']}Invalid index.{COLORS['reset']}")
                    return True
                
                # Make sure we have filtered sessions
                if not filtered_sessions:
                    print_session_list()
                
                if idx < 0 or idx >= len(filtered_sessions):
                    print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                    return True
                
                new_name = ' '.join(parts[2:])
                session = filtered_sessions[idx]
                old_name = session['name']
                
                session['name'] = new_name
                save_session_index({'sessions': sorted_sessions})
                print(f"{COLORS['green']}Renamed session from '{old_name}' to '{new_name}'{COLORS['reset']}")
                
                current_mode = 'list'
                print_session_list()
                return True
            
            # Delete command
            if cmd == 'delete':
                if len(parts) < 2:
                    print(f"{COLORS['red']}Usage: delete <idx>{COLORS['reset']}")
                    return True
                
                try:
                    idx = int(parts[1])
                except ValueError:
                    print(f"{COLORS['red']}Invalid index.{COLORS['reset']}")
                    return True
                
                # Make sure we have filtered sessions
                if not filtered_sessions:
                    print_session_list()
                    
                if idx < 0 or idx >= len(filtered_sessions):
                    print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                    return True
                
                session = filtered_sessions[idx]
                confirm = input(f"Are you sure you want to delete session '{session['name']}'? (y/N): ")
                
                if confirm.strip().lower() == 'y':
                    # Remove from index and delete file
                    history_dir = get_history_dir()
                    session_file = history_dir / f"session_{session['id']}.json"
                    
                    try:
                        if session_file.exists():
                            os.remove(session_file)
                    except Exception as e:
                        print(f"{COLORS['red']}Error deleting file: {str(e)}{COLORS['reset']}")
                    
                    # Remove from main list
                    session_id = session['id']
                    for i, s in enumerate(sorted_sessions):
                        if s['id'] == session_id:
                            sorted_sessions.pop(i)
                            break
                    
                    save_session_index({'sessions': sorted_sessions})
                    print(f"{COLORS['green']}Deleted session: {session['name']}{COLORS['reset']}")
                    
                    # Reset filter
                    search_query = ""
                    filtered_sessions = sorted_sessions.copy()
                    if current_session_idx >= len(filtered_sessions):
                        current_session_idx = max(0, len(filtered_sessions) - 1)
                else:
                    print(f"{COLORS['yellow']}Delete cancelled.{COLORS['reset']}")
                
                current_mode = 'list'
                print_session_list()
                return True
            
            # Unknown command
            print(f"{COLORS['red']}Unknown command: {cmd}. Type 'help' for available commands.{COLORS['reset']}")
            return True
        
        # Start with the session list
        print_session_list()
        
        # Command loop
        while True:
            try:
                if HAS_PROMPT_TOOLKIT:
                    # Create key bindings for prompt_toolkit
                    kb = KeyBindings()
                    
                    # Add Ctrl+C handler
                    @kb.add('c-c')
                    def _(event):
                        event.app.exit(result=None)
                        raise KeyboardInterrupt()
                    
                    # Add Ctrl+E binding for multiline input
                    @kb.add('c-e')
                    def open_multiline_editor(event):
                        # Exit the prompt and return a special value that indicates we want multiline
                        event.app.exit(result="/ml")
                    
                    # Use HTML formatting for better styling
                    prompt_prefix = HTML(f"<ansigreen>command</ansigreen>: ")
                    
                    # Use prompt_toolkit with history and key bindings
                    command = pt_prompt(
                        prompt_prefix,
                        history=session_command_history,
                        key_bindings=kb
                    )
                else:
                    command = input(f"{COLORS['green']}command:{COLORS['reset']} ")
                    
                if not process_command(command):
                    break
            except KeyboardInterrupt:
                print(f"\n{COLORS['yellow']}Session manager interrupted.{COLORS['reset']}")
                break
            except Exception as e:
                print(f"{COLORS['red']}Error: {str(e)}{COLORS['reset']}")
                if os.environ.get("NGPT_DEBUG"):
                    traceback.print_exc()

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
                    # We don't print any message here as it will be handled in the main loop
                    event.app.exit(result="/ml")
                
                # Define reserved keywords
                reserved_commands = [
                    '/clear', '/sessions', '/help', '/ml',
                    '/exit', '/quit', '/bye'
                ]
                
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
            if user_input.lower() in ('/exit', '/quit', '/bye', 'exit', 'quit', 'bye'):
                print(f"\n{COLORS['green']}Ending chat session. Goodbye!{COLORS['reset']}")
                break
            
            # Define reserved slash commands
            reserved_commands = ['/clear', '/sessions', '/help', '/ml', '/exit', '/quit', '/bye']
            
            # Check if input starts with / but is not a reserved command
            if user_input.startswith('/') and not any(user_input.lower().startswith(cmd.lower()) for cmd in reserved_commands):
                print(f"{COLORS['red']}Unknown command: {user_input}{COLORS['reset']}")
                continue
            
            # Check for special commands (now require a '/' prefix)
            if user_input.lower() == '/clear':
                clear_history()
                continue
            
            if user_input.lower() == '/sessions':
                list_sessions()
                continue

            if user_input.lower() == '/help':
                show_help()
                continue
                
            # Handle multiline input from either /ml command or Ctrl+E shortcut
            if multiline_enabled and user_input == "/ml":
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
            if current_session_id is None:
                save_session(silent=True)  # This will create a new session on first exchange
            else:
                # Update existing session silently (without printing message)
                with open(current_session_filepath, "w") as f:
                    json.dump(conversation, f, indent=2)
                update_session_in_index(current_session_id, current_session_name, update_existing=True)
        
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