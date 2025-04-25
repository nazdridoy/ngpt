import os
import sys
import datetime
from pathlib import Path
from typing import Optional, TextIO, Dict, Any

# Simple color definitions for fallback message
COLORS = {
    "green": "\033[32m",
    "yellow": "\033[33m",
    "reset": "\033[0m"
}

class Logger:
    """Handles logging functionality for ngpt"""
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize the logger.
        
        Args:
            log_path: Optional path to the log file. If None, a temporary file will be created.
        """
        self.log_path = log_path
        self.log_file: Optional[TextIO] = None
        self.is_temp = False
        self.command_args = sys.argv
        
        if self.log_path is None:
            # Create a temporary log file with date-time in the name
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            
            # Use OS-specific temp directory
            if sys.platform == "win32":
                # Windows
                temp_dir = os.environ.get("TEMP", "")
                self.log_path = os.path.join(temp_dir, f"ngpt-{timestamp}.log")
            else:
                # Linux/MacOS
                self.log_path = f"/tmp/ngpt-{timestamp}.log"
            
            self.is_temp = True
    
    def __enter__(self):
        """Context manager entry"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
    
    def open(self) -> bool:
        """
        Open the log file for writing.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Expand ~ to home directory if present
            if self.log_path.startswith('~'):
                self.log_path = os.path.expanduser(self.log_path)
                
            # Make sure the directory exists
            log_dir = os.path.dirname(self.log_path)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                except (PermissionError, OSError) as e:
                    print(f"Warning: Could not create log directory: {str(e)}", file=sys.stderr)
                    # Fall back to temp directory
                    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
                    if sys.platform == "win32":
                        temp_dir = os.environ.get("TEMP", "")
                        self.log_path = os.path.join(temp_dir, f"ngpt-{timestamp}.log")
                    else:
                        self.log_path = f"/tmp/ngpt-{timestamp}.log"
                    self.is_temp = True
                
            self.log_file = open(self.log_path, 'a', encoding='utf-8')
            
            # Write header information
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_file.write(f"\n--- nGPT Session Log ---\n")
            self.log_file.write(f"Started at: {timestamp}\n")
            self.log_file.write(f"Command: {' '.join(self.command_args)}\n")
            self.log_file.write(f"Log file: {self.log_path}\n\n")
            self.log_file.flush()
            
            return True
        except Exception as e:
            print(f"Warning: Could not open log file: {str(e)}", file=sys.stderr)
            
            # Fall back to temp file
            timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
            if sys.platform == "win32":
                temp_dir = os.environ.get("TEMP", "")
                self.log_path = os.path.join(temp_dir, f"ngpt-{timestamp}.log")
            else:
                self.log_path = f"/tmp/ngpt-{timestamp}.log"
            self.is_temp = True
            
            # Try again with temp file
            try:
                self.log_file = open(self.log_path, 'a', encoding='utf-8')
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.log_file.write(f"\n--- nGPT Session Log ---\n")
                self.log_file.write(f"Started at: {timestamp}\n")
                self.log_file.write(f"Command: {' '.join(self.command_args)}\n")
                self.log_file.write(f"Log file: {self.log_path}\n\n")
                self.log_file.flush()
                print(f"{COLORS['green']}Falling back to temporary log file: {self.log_path}{COLORS['reset']}", file=sys.stderr)
                return True
            except Exception as e2:
                print(f"Warning: Could not open temporary log file: {str(e2)}", file=sys.stderr)
                self.log_file = None
                return False
    
    def close(self):
        """Close the log file if it's open."""
        if self.log_file:
            try:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.log_file.write(f"\n--- Session ended at {timestamp} ---\n")
                self.log_file.close()
            except Exception:
                pass
            self.log_file = None
    
    def log(self, role: str, content: str):
        """
        Log a message.
        
        Args:
            role: Role of the message (e.g., 'system', 'user', 'assistant')
            content: Content of the message
        """
        if not self.log_file:
            return
            
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.log_file.write(f"{timestamp}: {role}: {content}\n")
            self.log_file.flush()
        except Exception:
            # Silently fail if logging fails
            pass

    def get_log_path(self) -> str:
        """
        Get the path to the log file.
        
        Returns:
            str: Path to the log file
        """
        return self.log_path

    def is_temporary(self) -> bool:
        """
        Check if the log file is temporary.
        
        Returns:
            bool: True if the log file is temporary
        """
        return self.is_temp


def create_logger(log_path: Optional[str] = None) -> Logger:
    """
    Create a logger instance.
    
    Args:
        log_path: Optional path to the log file
        
    Returns:
        Logger: Logger instance
    """
    return Logger(log_path) 