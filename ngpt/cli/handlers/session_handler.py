"""
Session management handler for nGPT interactive mode.
"""

import os
import json
import uuid
import re
import shutil
import traceback
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# Optional imports for enhanced UI
try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.completion import WordCompleter
    HAS_PROMPT_TOOLKIT = True
except ImportError:
    HAS_PROMPT_TOOLKIT = False

from ngpt.core.config import get_config_dir
from ngpt.ui.colors import COLORS


class SessionManager:
    """Manages chat session persistence and retrieval."""
    
    def __init__(self):
        self.history_dir = self._get_history_dir()
        self.index_path = self.history_dir / "session-index.json"
    
    def _get_history_dir(self) -> Path:
        """Get the history directory, creating it if it doesn't exist."""
        history_dir = get_config_dir() / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        return history_dir
    
    def get_session_index(self) -> Dict[str, List[Dict[str, str]]]:
        """Get the session index from session-index.json, or create if it doesn't exist."""
        if self.index_path.exists():
            try:
                with open(self.index_path, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # If index is corrupted, create a new one
                return {"sessions": []}
        else:
            return {"sessions": []}
    
    def validate_session_index(self, logger=None) -> int:
        """
        Validates the session index against actual files and repairs any discrepancies.
        
        Args:
            logger: Optional logger instance for logging errors
            
        Returns:
            int: Number of fixes made
        """
        index = self.get_session_index()
        fixes = 0
        
        # 1. Remove index entries for missing files
        valid_sessions = []
        for session in index["sessions"]:
            session_file = self.history_dir / f"session_{session['id']}.json"
            if session_file.exists():
                valid_sessions.append(session)
            else:
                # Record removing the invalid session
                error_msg = f"Removing invalid session from index: {session['name']} (file not found)"
                print(f"{COLORS['yellow']}{error_msg}{COLORS['reset']}")
                if logger:
                    logger.log("session_index", error_msg)
                fixes += 1
        
        # 2. Add entries for files not in the index
        existing_ids = {s["id"] for s in valid_sessions}
        for file_path in self.history_dir.glob("session_*.json"):
            try:
                # Skip the index file itself
                if file_path.name == "session-index.json":
                    continue
                
                # Extract session_id from filename
                session_id = file_path.stem.replace("session_", "")
                if session_id and session_id not in existing_ids:
                    # Default name in case we can't extract one from file
                    name = "Recovered Session"
                    
                    # Always try to extract a meaningful name from the file content
                    try:
                        with open(file_path, "r") as f:
                            conversation = json.load(f)
                            # Find the first user message to use as a title
                            for msg in conversation:
                                if msg.get("role") == "user":
                                    name = self.generate_session_name(msg.get("content", ""))
                                    break
                    except Exception as e:
                        error_msg = f"Could not read content from {file_path.name}: {str(e)}"
                        print(f"{COLORS['yellow']}{error_msg}{COLORS['reset']}")
                        if logger:
                            logger.log("session_index", error_msg)
                    
                    # Create metadata for the orphaned file
                    valid_sessions.append({
                        "id": session_id,
                        "name": name,
                        "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    # Record adding the orphaned session
                    add_msg = f"Added orphaned session to index: {name}"
                    print(f"{COLORS['green']}{add_msg}{COLORS['reset']}")
                    if logger:
                        logger.log("session_index", add_msg)
                    
                    fixes += 1
            except Exception as e:
                error_msg = f"Error processing file {file_path}: {str(e)}"
                print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
                if logger:
                    logger.log("session_index", error_msg)
                continue
        
        # Update the index if fixes were made
        if fixes > 0:
            try:
                index["sessions"] = valid_sessions
                self.save_session_index(index, logger)
                msg = f"Session index repaired. {fixes} {'issue' if fixes == 1 else 'issues'} fixed."
                print(f"{COLORS['green']}{msg}{COLORS['reset']}")
                if logger:
                    logger.log("session_index", msg)
            except Exception as e:
                error_msg = f"Error saving session index: {str(e)}"
                print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
                if logger:
                    logger.log("session_index", error_msg)
        
        return fixes
    
    def save_session_index(self, index: Dict[str, List[Dict[str, str]]], logger=None) -> None:
        """Save the session index to session-index.json."""
        # Clean the index to only include core session data
        clean_index = {"sessions": []}
        for session in index["sessions"]:
            clean_session = {
                "id": session["id"],
                "name": session["name"],
                "created_at": session.get("created_at", ""),
                "last_modified": session.get("last_modified", "")
            }
            clean_index["sessions"].append(clean_session)
        
        try:
            with open(self.index_path, "w") as f:
                json.dump(clean_index, f, indent=2)
                
            if logger:
                logger.log("session_index", f"Saved session index with {len(clean_index['sessions'])} sessions")
        except Exception as e:
            error_msg = f"Failed to save session index: {str(e)}"
            print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
            if logger:
                logger.log("session_index", error_msg)
    
    def generate_session_name(self, content: str) -> str:
        """Generate a session name from the first user prompt."""
        if not content:
            return "Untitled Session"
        
        # Remove special characters and limit to 30 chars
        name = re.sub(r'[^\w\s]', '', content).strip()
        name = re.sub(r'\s+', ' ', name)  # Replace multiple spaces with a single space
        
        if len(name) > 30:
            name = name[:30].strip() + "..."
        
        return name or "Untitled Session"
    
    def update_session_in_index(self, session_id: str, session_name: str, update_existing: bool = False, logger=None) -> None:
        """Add or update a session in the index."""
        index = self.get_session_index()
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
        
        self.save_session_index(index, logger)
    
    def save_session(self, conversation: List[Dict[str, str]], session_id: Optional[str] = None, 
                    session_name: Optional[str] = None, first_user_prompt: Optional[str] = None,
                    verbose: bool = False, logger=None) -> Tuple[str, Path, str]:
        """Save the current conversation to a JSON file, creating a new session or updating the current one."""
        if session_id is None:
            # Generate a new session ID if not already set (new session or cleared)
            session_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
            session_filepath = self.history_dir / f"session_{session_id}.json"
            
            # Generate a session name if none provided
            if not session_name:
                if first_user_prompt:
                    session_name = self.generate_session_name(first_user_prompt)
                else:
                    session_name = "Untitled Session"
            
            # Add to index
            self.update_session_in_index(session_id, session_name, logger=logger)
            if verbose:
                print(f"{COLORS['green']}Session: {session_name}{COLORS['reset']}")
            
            if logger:
                logger.log("session_manager", f"Created new session: {session_name} (ID: {session_id})")
        else:
            session_filepath = self.history_dir / f"session_{session_id}.json"
            # Always update last_modified, and optionally name
            if session_name:
                if verbose:
                    print(f"{COLORS['green']}Session renamed: {session_name}{COLORS['reset']}")
                if logger:
                    logger.log("session_manager", f"Renamed session to: {session_name} (ID: {session_id})")
            self.update_session_in_index(session_id, session_name or "Untitled Session", update_existing=True, logger=logger)
        
        try:
            with open(session_filepath, "w") as f:
                json.dump(conversation, f, indent=2)
            
            if logger:
                msg_count = sum(1 for msg in conversation if msg.get("role") in ["user", "assistant"])
                logger.log("session_manager", f"Saved session {session_id} with {msg_count} messages")
        except Exception as e:
            error_msg = f"Error saving session {session_id}: {str(e)}"
            print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
            if logger:
                logger.log("session_manager", error_msg)
        
        return session_id, session_filepath, session_name or "Untitled Session"
    
    def load_session(self, session_id: str, logger=None) -> Optional[List[Dict[str, str]]]:
        """Load a session by ID."""
        session_file = self.history_dir / f"session_{session_id}.json"
        
        if not session_file.exists():
            error_msg = f"Session file for {session_id} not found"
            print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
            if logger:
                logger.log("session_manager", error_msg)
            return None
        
        try:
            with open(session_file, "r") as f:
                conversation = json.load(f)
                
            if isinstance(conversation, list) and all(isinstance(item, dict) for item in conversation):
                if logger:
                    msg_count = sum(1 for msg in conversation if msg.get("role") in ["user", "assistant"])
                    logger.log("session_manager", f"Loaded session {session_id} with {msg_count} messages")
                return conversation
            else:
                error_msg = f"Invalid session format in {session_id}"
                print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
                if logger:
                    logger.log("session_manager", error_msg)
                return None
        except Exception as e:
            error_msg = f"Error loading session {session_id}: {str(e)}"
            print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
            if logger:
                logger.log("session_manager", error_msg)
            return None
    
    def delete_session(self, session_id: str, logger=None) -> bool:
        """Delete a session by ID."""
        session_file = self.history_dir / f"session_{session_id}.json"
        
        try:
            if session_file.exists():
                os.remove(session_file)
                if logger:
                    logger.log("session_manager", f"Deleted session file for {session_id}")
            
            # Remove from index
            index = self.get_session_index()
            # Find session name before deleting for logging purposes
            session_name = "Unknown"
            for session in index["sessions"]:
                if session["id"] == session_id:
                    session_name = session["name"]
                    break
                    
            index["sessions"] = [s for s in index["sessions"] if s["id"] != session_id]
            self.save_session_index(index, logger)
            
            if logger:
                logger.log("session_manager", f"Removed session '{session_name}' (ID: {session_id}) from index")
            
            return True
        except Exception as e:
            error_msg = f"Error deleting session {session_id}: {str(e)}"
            print(f"{COLORS['red']}{error_msg}{COLORS['reset']}")
            if logger:
                logger.log("session_manager", error_msg)
            return False
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information including size and metadata."""
        session_file = self.history_dir / f"session_{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            size = os.path.getsize(session_file)
            size_indicator = "•"
            size_color = COLORS['green']
            
            if size < 10000:  # Small session
                size_indicator = "•"
                size_color = COLORS['green']
            elif size < 50000:  # Medium session
                size_indicator = "••"
                size_color = COLORS['yellow']
            else:  # Large session
                size_indicator = "•••"
                size_color = COLORS['red']
            
            return {
                "size": size,
                "size_indicator": size_indicator,
                "size_color": size_color
            }
        except Exception:
            return None


class SessionUI:
    """Handles the interactive session management UI."""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.term_width = self._get_terminal_width()
        self.separator = f"{COLORS['gray']}{'─' * min(self.term_width - 4, 50)}{COLORS['reset']}"
    
    def _get_terminal_width(self) -> int:
        """Get terminal width for better formatting."""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    def print_header(self, mode_name: str = "Sessions") -> None:
        """Print a nice header with current mode."""
        print(f"\n{COLORS['cyan']}{COLORS['bold']}🤖 nGPT Session Manager - {mode_name} 🤖{COLORS['reset']}")
        print(self.separator)
    
    def print_help(self) -> None:
        """Print help information."""
        self.print_header("Help")
        print(f"\n{COLORS['cyan']}{COLORS['bold']}Available Commands:{COLORS['reset']}")
        print(f"  {COLORS['yellow']}list{COLORS['reset']}                 Show session list")
        print(f"  {COLORS['yellow']}preview <idx>{COLORS['reset']}        Show preview of session messages")
        print(f"  {COLORS['yellow']}load <idx>{COLORS['reset']}           Load a session")
        print(f"  {COLORS['yellow']}rename <idx> <name>{COLORS['reset']}  Rename a session")
        print(f"  {COLORS['yellow']}delete <idx>{COLORS['reset']}         Delete a single session")
        print(f"  {COLORS['yellow']}delete <idx1>,<idx2>{COLORS['reset']} Delete multiple sessions")
        print(f"  {COLORS['yellow']}delete <idx1>-<idx5>{COLORS['reset']} Delete a range of sessions")
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
        print(self.separator)
    
    def format_sessions_for_display(self, sessions: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Format sessions with display metadata."""
        def get_last_modified(session):
            return session.get("last_modified") or session.get("created_at") or ""
        
        # Sort sessions by last modified time (oldest first)
        sorted_sessions = sorted(sessions, key=get_last_modified, reverse=False)
        
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
            session_info = self.session_manager.get_session_info(session['id'])
            if session_info:
                session['size_indicator'] = session_info['size_indicator']
                session['size_color'] = session_info['size_color']
            else:
                session['size_indicator'] = "•"
                session['size_color'] = COLORS['green']
        
        return sorted_sessions
    
    def print_session_list(self, sessions: List[Dict[str, Any]], 
                          filtered_sessions: List[Dict[str, Any]], 
                          current_session_idx: int, search_query: str = "") -> None:
        """Print session list with enhancements."""
        self.print_header("List Sessions")
        
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
                if i == current_session_idx:
                    print(f"  {COLORS['cyan']}{COLORS['bold']}{i:<2}{COLORS['reset']} {size_color}{size_indicator:<4}{COLORS['reset']} {COLORS['white']}{COLORS['bold']}{name:<35}{COLORS['reset']} {COLORS['white']}{last_fmt}{COLORS['reset']}")
                else:
                    print(f"  {COLORS['yellow']}{i:<2}{COLORS['reset']} {size_color}{size_indicator:<4}{COLORS['reset']} {COLORS['white']}{name:<35}{COLORS['reset']} {COLORS['gray']}{last_fmt}{COLORS['reset']}")
        
        print(self.separator)
        print(f"{COLORS['green']}Enter command: {COLORS['reset']}(Type 'help' for available commands)")
    
    def show_session_preview(self, session: Dict[str, Any], mode: str = 'tail', count: int = 5) -> None:
        """Show preview of session content."""
        session_file = self.session_manager.history_dir / f"session_{session['id']}.json"
        
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
                
            self.print_header("Preview Session")
            print(f"\n{COLORS['cyan']}{COLORS['bold']}Preview of {mode_desc} messages from:{COLORS['reset']} {COLORS['white']}{session['name']}{COLORS['reset']}")
            print(self.separator)
            
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
            
            print(self.separator)
            print(f"{COLORS['green']}Enter command: {COLORS['reset']}(Type 'list' to return to session list)")
            
        except Exception as e:
            print(f"{COLORS['red']}Error reading session: {str(e)}{COLORS['reset']}")


def handle_session_management(logger=None) -> Optional[Tuple[str, Path, str, List[Dict[str, str]]]]:
    """
    Handle the interactive session management.
    
    Args:
        logger: Optional logger instance for logging operations
        
    Returns:
        Optional[Tuple[str, Path, str, List[Dict[str, str]]]]: 
        (session_id, session_filepath, session_name, conversation) if a session was loaded,
        None if the user exited without loading a session
    """
    session_manager = SessionManager()
    session_ui = SessionUI(session_manager)
    
    # Get sessions and validate index first to avoid missing files
    fixes = session_manager.validate_session_index(logger=logger)
    
    index = session_manager.get_session_index()
    if not index["sessions"]:
        print(f"\n{COLORS['yellow']}No saved sessions found.{COLORS['reset']}")
        return None
    
    # Create command history for session manager
    session_command_history = InMemoryHistory() if HAS_PROMPT_TOOLKIT else None
    
    # Format sessions for display
    sorted_sessions = session_ui.format_sessions_for_display(index["sessions"])
    
    # Initialize state
    current_mode = 'list'
    current_session_idx = len(sorted_sessions) - 1 if sorted_sessions else -1
    preview_mode = 'tail'
    preview_count = 5
    filtered_sessions = sorted_sessions.copy()
    search_query = ""
    
    # Show subtle notification if fixes were made
    if fixes > 0:
        if fixes == 1:
            print(f"\n{COLORS['gray']}Note: 1 session index inconsistency was automatically repaired.{COLORS['reset']}")
        else:
            print(f"\n{COLORS['gray']}Note: {fixes} session index inconsistencies were automatically repaired.{COLORS['reset']}")
    
    # Flag to track if we've already validated the index in this session
    index_validated = True  # We just validated it above
    
    def process_command(command: str) -> bool:
        """Process a command entered by the user."""
        nonlocal current_mode, current_session_idx, preview_mode, preview_count, search_query
        nonlocal filtered_sessions, sorted_sessions
        
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
            session_ui.print_help()
            if logger:
                logger.log("session_manager", "Displayed help information")
            return True
        
        # List command
        if cmd == 'list':
            current_mode = 'list'
            search_query = ""  # Clear any search
            filtered_sessions = sorted_sessions.copy()  # Reset filtered sessions to show all
            current_session_idx = len(sorted_sessions) - 1 if sorted_sessions else -1  # Reset to last session
            session_ui.print_session_list(sorted_sessions, filtered_sessions, current_session_idx, search_query)
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
            
            if idx < 0 or idx >= len(filtered_sessions):
                print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                return True
            
            session = filtered_sessions[idx]
            
            # Log preview operation
            if logger:
                logger.log("session_manager", f"Previewing {cmd} of session: {session['name']} (ID: {session['id']}, count: {preview_count})")
                
            session_ui.show_session_preview(filtered_sessions[idx], preview_mode, preview_count)
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
            
            if idx < 0 or idx >= len(filtered_sessions):
                print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                return True
            
            session = filtered_sessions[idx]
            
            # Log preview operation
            if logger:
                logger.log("session_manager", f"Previewing session: {session['name']} (ID: {session['id']}, mode: {preview_mode}, count: {preview_count})")
                
            session_ui.show_session_preview(filtered_sessions[idx], preview_mode, preview_count)
            return True
        
        # Search command
        if cmd == 'search':
            if len(parts) < 2:
                search_query = ""  # Clear search
                print(f"{COLORS['green']}Search cleared.{COLORS['reset']}")
                filtered_sessions = sorted_sessions.copy()  # Reset to all sessions
                
                if logger:
                    logger.log("session_manager", "Search filter cleared")
            else:
                search_query = ' '.join(parts[1:])
                print(f"{COLORS['green']}Searching for: {search_query}{COLORS['reset']}")
                
                # Actually filter the sessions by name (case-insensitive)
                filtered_sessions = [s for s in sorted_sessions if search_query.lower() in s['name'].lower()]
                
                # Reset current session index to last item in filtered list
                if filtered_sessions:
                    current_session_idx = len(filtered_sessions) - 1
                else:
                    current_session_idx = -1
                
                # Log search operation
                if logger:
                    logger.log("session_manager", f"Searching sessions for: '{search_query}' (found {len(filtered_sessions)} results)")
                
            current_mode = 'list'
            session_ui.print_session_list(sorted_sessions, filtered_sessions, current_session_idx, search_query)
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
            
            if idx < 0 or idx >= len(filtered_sessions):
                print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                return True
            
            session = filtered_sessions[idx]
            conversation = session_manager.load_session(session['id'], logger)
            
            if conversation is None:
                print(f"{COLORS['red']}Error loading session.{COLORS['reset']}")
                return True
            
            # Log explicit load command
            if logger:
                logger.log("session_manager", f"User explicitly loaded session: {session['name']} (ID: {session['id']})")
                
            session_filepath = session_manager.history_dir / f"session_{session['id']}.json"
            print(f"\n{COLORS['green']}Session loaded: {session['name']}{COLORS['reset']}")
            return False  # Exit session manager and return to chat
        
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
            
            if idx < 0 or idx >= len(filtered_sessions):
                print(f"{COLORS['red']}Invalid session index.{COLORS['reset']}")
                return True
            
            new_name = ' '.join(parts[2:])
            session = filtered_sessions[idx]
            old_name = session['name']
            
            session['name'] = new_name
            session_manager.update_session_in_index(session['id'], new_name, update_existing=True, logger=logger)
            print(f"{COLORS['green']}Renamed session from '{old_name}' to '{new_name}'{COLORS['reset']}")
            
            # Log the rename operation explicitly
            if logger:
                logger.log("session_manager", f"Renamed session from '{old_name}' to '{new_name}' (ID: {session['id']})")
            
            current_mode = 'list'
            session_ui.print_session_list(sorted_sessions, filtered_sessions, current_session_idx, search_query)
            return True
        
        # Delete command
        if cmd == 'delete':
            if len(parts) < 2:
                print(f"{COLORS['red']}Usage: delete <idx> or delete <idx1>,<idx2> or delete <idx1>-<idx5>{COLORS['reset']}")
                return True
            
            # Parse indices to delete - support multiple formats:
            # 1. Single index: "delete 3"
            # 2. Comma-separated indices: "delete 1,3,5"
            # 3. Range notation: "delete 1-5"
            # 4. Mixed format: "delete 1-3,5,7-9"
            indices_to_delete = []
            input_indices = ' '.join(parts[1:])
            invalid_segments = []
            
            # Split by commas first
            segments = [s.strip() for s in input_indices.split(',')]
            
            for segment in segments:
                try:
                    if '-' in segment:
                        # Handle range notation (e.g., "1-5")
                        start_str, end_str = segment.split('-')
                        start, end = int(start_str), int(end_str)
                        
                        # Handle reversed ranges (e.g., "5-2")
                        if start > end:
                            invalid_segments.append(f"{segment} (reversed range)")
                            continue
                            
                        indices_to_delete.extend(range(start, end + 1))
                    else:
                        # Handle single index
                        indices_to_delete.append(int(segment))
                except ValueError:
                    invalid_segments.append(segment)
            
            # Report invalid segments if any
            if invalid_segments:
                print(f"{COLORS['yellow']}Warning: Ignoring invalid segments: {', '.join(invalid_segments)}{COLORS['reset']}")
            
            if not indices_to_delete:
                print(f"{COLORS['red']}No valid indices provided.{COLORS['reset']}")
                return True
                
            # Validate all indices are in range
            valid_indices = []
            out_of_range_indices = []
            
            for idx in indices_to_delete:
                if 0 <= idx < len(filtered_sessions):
                    valid_indices.append(idx)
                else:
                    out_of_range_indices.append(idx)
            
            if out_of_range_indices:
                print(f"{COLORS['yellow']}Warning: Ignoring out-of-range indices: {out_of_range_indices}{COLORS['reset']}")
                
            if not valid_indices:
                print(f"{COLORS['red']}No valid indices to delete.{COLORS['reset']}")
                return True
                
            # Remove duplicates and sort for consistent deletion
            indices_to_delete = sorted(set(valid_indices))
            
            # Get session names for confirmation
            sessions_to_delete = [filtered_sessions[idx] for idx in indices_to_delete]
            session_names = [f"'{s['name']}'" for s in sessions_to_delete]
            
            # Format confirmation message based on number of sessions
            if len(sessions_to_delete) == 1:
                confirm_msg = f"Are you sure you want to delete session {session_names[0]}? (y/N): "
            else:
                confirm_msg = f"Are you sure you want to delete {len(sessions_to_delete)} sessions?\n"
                for i, name in enumerate(session_names[:5]):  # Show first 5 sessions
                    confirm_msg += f"  {i+1}. {name}\n"
                if len(session_names) > 5:
                    confirm_msg += f"  ... and {len(session_names) - 5} more\n"
                confirm_msg += "(y/N): "
            
            # Log delete attempt
            if logger:
                if len(sessions_to_delete) == 1:
                    logger.log("session_manager", f"Attempting to delete session: {sessions_to_delete[0]['name']} (ID: {sessions_to_delete[0]['id']})")
                else:
                    logger.log("session_manager", f"Attempting to delete {len(sessions_to_delete)} sessions")
                
            confirm = input(confirm_msg)
            
            if confirm.strip().lower() == 'y':
                success_count = 0
                for session in sessions_to_delete:
                    if session_manager.delete_session(session['id'], logger):
                        success_count += 1
                
                # Provide feedback based on deletion results
                if success_count == len(sessions_to_delete):
                    if len(sessions_to_delete) == 1:
                        print(f"{COLORS['green']}Deleted session: {sessions_to_delete[0]['name']}{COLORS['reset']}")
                    else:
                        print(f"{COLORS['green']}Successfully deleted {success_count} sessions.{COLORS['reset']}")
                else:
                    print(f"{COLORS['yellow']}Deleted {success_count} of {len(sessions_to_delete)} sessions.{COLORS['reset']}")
                    
                # Refresh sessions
                index = session_manager.get_session_index()
                sorted_sessions = session_ui.format_sessions_for_display(index["sessions"])
                filtered_sessions = sorted_sessions.copy()
                search_query = ""
                
                if current_session_idx >= len(filtered_sessions):
                    current_session_idx = max(0, len(filtered_sessions) - 1)
            else:
                print(f"{COLORS['yellow']}Delete cancelled.{COLORS['reset']}")
                if logger:
                    if len(sessions_to_delete) == 1:
                        logger.log("session_manager", f"Delete cancelled for session: {sessions_to_delete[0]['name']} (ID: {sessions_to_delete[0]['id']})")
                    else:
                        logger.log("session_manager", f"Delete cancelled for {len(sessions_to_delete)} sessions")
            
            current_mode = 'list'
            session_ui.print_session_list(sorted_sessions, filtered_sessions, current_session_idx, search_query)
            return True
        
        # Unknown command
        print(f"{COLORS['red']}Unknown command: {cmd}. Type 'help' for available commands.{COLORS['reset']}")
        return True
    
    # Start with the session list
    session_ui.print_session_list(sorted_sessions, filtered_sessions, current_session_idx, search_query)
    
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
                # Session was loaded, return the session data
                session = filtered_sessions[int(command.split()[1])]
                conversation = session_manager.load_session(session['id'])
                session_filepath = session_manager.history_dir / f"session_{session['id']}.json"
                return session['id'], session_filepath, session['name'], conversation
                
        except KeyboardInterrupt:
            print(f"\n{COLORS['yellow']}Session manager interrupted.{COLORS['reset']}")
            break
        except Exception as e:
            print(f"{COLORS['red']}Error: {str(e)}{COLORS['reset']}")
            if os.environ.get("NGPT_DEBUG"):
                traceback.print_exc()
    
    return None


def clear_conversation_history(conversation: List[Dict[str, str]], system_prompt: str) -> List[Dict[str, str]]:
    """Clear conversation history and return to initial state."""
    return [{"role": "system", "content": system_prompt}]


def auto_save_session(conversation: List[Dict[str, str]], session_id: Optional[str], 
                     session_filepath: Optional[Path], session_name: Optional[str],
                     first_user_prompt: Optional[str], logger=None) -> Tuple[str, Path, str]:
    """Auto-save conversation after each exchange."""
    session_manager = SessionManager()
    
    if session_id is None:
        # Create new session
        return session_manager.save_session(
            conversation=conversation,
            first_user_prompt=first_user_prompt,
            verbose=False,
            logger=logger
        )
    else:
        # Update existing session
        session_manager.save_session(
            conversation=conversation,
            session_id=session_id,
            session_name=session_name,
            verbose=False,
            logger=logger
        )
        return session_id, session_filepath, session_name or "Untitled Session" 