import os
import sys
import datetime
import logging
import tempfile
from pathlib import Path
from typing import Optional, TextIO, Dict, Any, Union

# Define colors locally to avoid circular imports
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "cyan": "\033[36m",
    "green": "\033[32m", 
    "yellow": "\033[33m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "gray": "\033[90m",
    "bg_blue": "\033[44m",
    "bg_cyan": "\033[46m"
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

    # Add standard logging methods to be compatible with gitcommsg mode
    def info(self, message: str):
        """Log an info message."""
        self.log("INFO", message)
    
    def debug(self, message: str):
        """Log a debug message."""
        self.log("DEBUG", message)
    
    def warning(self, message: str):
        """Log a warning message."""
        self.log("WARNING", message)
    
    def error(self, message: str, exc_info=False):
        """Log an error message."""
        if exc_info:
            import traceback
            message += "\n" + traceback.format_exc()
        self.log("ERROR", message)


class GitCommsgLogger:
    """Specialized logger for gitcommsg mode with standard logging methods."""
    
    def __init__(self, log_path: Optional[str] = None):
        """
        Initialize the gitcommsg logger.
        
        Args:
            log_path: Optional path to the log file. If None, a temporary file will be created.
        """
        self.log_path = log_path
        self.logger = None
        self.is_temp = False
        self.command_args = sys.argv
        
        # Create a temporary log file if no path provided
        if self.log_path is True or self.log_path is None:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            if sys.platform == "win32":
                temp_dir = os.environ.get("TEMP", "")
                self.log_path = os.path.join(temp_dir, f"ngpt_gitcommsg_{timestamp}.log")
            else:
                self.log_path = f"/tmp/ngpt_gitcommsg_{timestamp}.log"
            self.is_temp = True

    def setup(self):
        """Set up the logger."""
        # Set up Python's standard logging module
        self.logger = logging.getLogger("gitcommsg")
        self.logger.setLevel(logging.DEBUG)
        
        # Clear any existing handlers
        if self.logger.handlers:
            for handler in self.logger.handlers:
                self.logger.removeHandler(handler)
        
        # Create file handler
        try:
            # Ensure the directory exists
            log_dir = os.path.dirname(self.log_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(self.log_path)
            file_handler.setLevel(logging.DEBUG)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(file_handler)
            
            print(f"{COLORS['green']}Logging enabled. Log file: {self.log_path}{COLORS['reset']}")
            self.logger.info("GitCommitMsg mode started")
            self.logger.info(f"Command: {' '.join(self.command_args)}")
            
            return True
        except Exception as e:
            print(f"{COLORS['yellow']}Error setting up logger: {str(e)}{COLORS['reset']}")
            return False

    def info(self, message: str):
        """Log an info message."""
        if self.logger:
            self.logger.info(message)
    
    def debug(self, message: str):
        """Log a debug message."""
        if self.logger:
            self.logger.debug(message)
    
    def warning(self, message: str):
        """Log a warning message."""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message: str, exc_info=False):
        """Log an error message."""
        if self.logger:
            self.logger.error(message, exc_info=exc_info)

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
        
    def log_file_contents(self, level: str, description: str, filepath: str):
        """
        Log the contents of a file.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            description: Description of the file contents
            filepath: Path to the file
        """
        if not self.logger or not os.path.isfile(filepath):
            return
            
        try:
            # Start marker with description
            self.logger.log(
                getattr(logging, level.upper()),
                f"===== BEGIN {description}: {filepath} ====="
            )
            
            # Read and log file contents
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                for line in content.split('\n'):
                    self.logger.log(
                        getattr(logging, level.upper()),
                        line
                    )
            
            # End marker
            self.logger.log(
                getattr(logging, level.upper()),
                f"===== END {description}: {filepath} ====="
            )
        except Exception as e:
            self.logger.error(f"Error logging file contents: {str(e)}")
            
    def log_content(self, level: str, description: str, content: str):
        """
        Log the provided content.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            description: Description of the content
            content: The content to log
        """
        if not self.logger:
            return
            
        try:
            # Create a temporary file for the content
            fd, temp_path = tempfile.mkstemp(prefix="ngpt_log_", suffix=".txt")
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Log the content from the file
            self.log_file_contents(level, description, temp_path)
            
            # Clean up the temporary file
            try:
                os.unlink(temp_path)
            except Exception:
                pass
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error logging content: {str(e)}")
                
    def log_prompt(self, level: str, system_prompt: Optional[str], user_prompt: str):
        """
        Log AI prompt information with detailed content.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            system_prompt: Optional system prompt
            user_prompt: User prompt
        """
        if not self.logger:
            return
            
        # Log summary
        self.logger.log(
            getattr(logging, level.upper()),
            "AI Request:"
        )
        
        # Log system prompt if provided
        if system_prompt:
            self.log_content(level, "SYSTEM_PROMPT", system_prompt)
        
        # Log user prompt
        self.log_content(level, "USER_PROMPT", user_prompt)
        
    def log_response(self, level: str, response: str):
        """
        Log AI response with full content.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            response: The AI response
        """
        if not self.logger:
            return
            
        # Log response
        self.log_content(level, "AI_RESPONSE", response)
        
    def log_diff(self, level: str, diff_content: str):
        """
        Log git diff content.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            diff_content: The git diff content
        """
        if not self.logger:
            return
            
        # Log diff content
        self.log_content(level, "GIT_DIFF", diff_content)
        
    def log_chunks(self, level: str, chunk_number: int, total_chunks: int, chunk_content: str):
        """
        Log chunk content for processing.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            chunk_number: Current chunk number
            total_chunks: Total number of chunks
            chunk_content: Content of the chunk
        """
        if not self.logger:
            return
            
        # Log chunk content
        self.log_content(
            level, 
            f"CHUNK_{chunk_number}_OF_{total_chunks}", 
            chunk_content
        )
        
    def log_template(self, level: str, template_type: str, template: str):
        """
        Log prompt template.
        
        Args:
            level: Log level (DEBUG, INFO, etc.)
            template_type: Type of template (INITIAL, CHUNK, COMBINE, etc.)
            template: Template content
        """
        if not self.logger:
            return
            
        # Log template
        self.log_content(level, f"{template_type}_TEMPLATE", template)


def create_logger(log_path: Optional[str] = None) -> Logger:
    """
    Create a logger instance.
    
    Args:
        log_path: Optional path to the log file
        
    Returns:
        Logger: Logger instance
    """
    return Logger(log_path)


def create_gitcommsg_logger(log_path: Optional[str] = None) -> GitCommsgLogger:
    """
    Create a gitcommsg logger instance.
    
    Args:
        log_path: Optional path to the log file
        
    Returns:
        GitCommsgLogger: GitCommsgLogger instance
    """
    logger = GitCommsgLogger(log_path)
    logger.setup()
    return logger 