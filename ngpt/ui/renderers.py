import os
import shutil
import subprocess
import tempfile
import sys
import threading
from ngpt.ui.colors import COLORS

# Global lock for terminal rendering to prevent race conditions
TERMINAL_RENDER_LOCK = threading.Lock()

# Import rich libraries
import rich
from rich.markdown import Markdown
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
import rich.box

def create_spinner_handling_callback(original_callback, stop_spinner_func, first_content_received_ref):
    """Create a spinner handling callback function to eliminate code repetition.
    
    This function creates a wrapper callback that handles stopping the spinner
    on first content received and then delegates to the original callback.
    
    Args:
        original_callback: The original stream callback function
        stop_spinner_func: Function to stop the spinner
        first_content_received_ref: Reference to the first_content_received variable (list with single element)
        
    Returns:
        function: The wrapped callback function
    """
    def spinner_handling_callback(content, **kwargs):
        # On first content, stop the spinner 
        if not first_content_received_ref[0] and stop_spinner_func:
            first_content_received_ref[0] = True
            
            # Use lock to prevent terminal rendering conflicts
            with TERMINAL_RENDER_LOCK:
                # Stop the spinner
                stop_spinner_func()
                # Ensure spinner message is cleared with an extra blank line
                sys.stdout.write("\r" + " " * 100 + "\r")
                sys.stdout.flush()
        
        # Call the original callback to update the display
        if original_callback:
            original_callback(content, **kwargs)
    
    return spinner_handling_callback

def prettify_streaming_markdown():
    """Set up streaming markdown rendering.
    
    This function creates a live display context for rendering markdown
    that can be updated in real-time as streaming content arrives.
    
    Returns:
        tuple: (live_display, update_function, stop_spinner_func) if successful, (None, None, None) otherwise
              stop_spinner_func is a function that should be called when first content is received
    """
    try:
        console = Console()
        
        # Create an empty markdown object to start with
        clean_header = "🤖 nGPT"
        panel_title = Text(clean_header, style="cyan bold")
        
        padding = (1, 1)  # Less horizontal padding (left, right)
        md_obj = Panel(
            Markdown(""),
            title=panel_title,
            title_align="left",
            border_style="cyan",
            padding=padding,
            width=console.width - 4,  # Make panel slightly narrower than console
            box=rich.box.ROUNDED
        )
        
        # Get terminal dimensions for better display
        term_width = shutil.get_terminal_size().columns
        term_height = shutil.get_terminal_size().lines
        
        # Use 2/3 of terminal height for content display (min 10 lines, max 30 lines)
        display_height = max(10, min(30, int(term_height * 2/3)))
        
        # Initialize the Live display (without height parameter)
        live = Live(
            md_obj, 
            console=console, 
            refresh_per_second=10, 
            auto_refresh=False
        )
        
        # Track if this is the first content update
        first_update = True
        stop_spinner_event = None
        spinner_thread = None
        
        # Store the full content for final display
        full_content = ""
        
        # Define an update function that will be called with new content
        def update_content(content, **kwargs):
            nonlocal md_obj, first_update, full_content, live, display_height
            
            # Store the full content for final display
            full_content = content
            
            # Check if this is the final update (complete flag)
            is_complete = kwargs.get('complete', False)
            
            # Use lock to prevent terminal rendering conflicts
            with TERMINAL_RENDER_LOCK:
                # Start live display on first content
                if first_update:
                    first_update = False
                    # Let the spinner's clean_exit handle the cleanup
                    # No additional cleanup needed here
                    live.start()
                
                # Update content in live display
                if not is_complete:
                    # Calculate approximate lines needed
                    content_lines = content.count('\n') + 1
                    available_height = display_height - 4  # Account for panel borders and padding
                    
                    if content_lines > available_height:
                        # If content is too big, show only the last part that fits
                        lines = content.split('\n')
                        truncated_content = '\n'.join(lines[-available_height:])
                        md_obj.renderable = Markdown(truncated_content)
                    else:
                        md_obj.renderable = Markdown(content)
                else:
                    md_obj.renderable = Markdown(content)
                    
                live.update(md_obj)
                    
                # Ensure the display refreshes with new content
                live.refresh()
                
                # If streaming is complete, stop the live display
                if is_complete:
                    try:
                        # Just stop the live display when complete - no need to redisplay content
                        live.stop()
                    except Exception as e:
                        # Fallback if something goes wrong
                        sys.stderr.write(f"\nError stopping live display: {str(e)}\n")
                        sys.stderr.flush()
        
        # Define a function to set up and start the spinner
        def setup_spinner(stop_event, message="Waiting for AI response...", color=COLORS['cyan']):
            nonlocal stop_spinner_event, spinner_thread
            from ngpt.ui.tui import spinner
            import threading
            
            # Store the event so the update function can access it
            stop_spinner_event = stop_event
            
            # Create and start spinner thread
            spinner_thread = threading.Thread(
                target=spinner,
                args=(message,),
                kwargs={"stop_event": stop_event, "color": color, "clean_exit": True}
            )
            spinner_thread.daemon = True
            spinner_thread.start()
            
            # Return a function that can be used to stop the spinner
            return lambda: stop_event.set() if stop_event else None
                
        # Return the necessary components for streaming to work
        return live, update_content, setup_spinner
    except Exception as e:
        print(f"{COLORS['yellow']}Error setting up Rich streaming display: {str(e)}{COLORS['reset']}")
        return None, None, None 

def setup_plaintext_spinner(message="Waiting for response...", color=COLORS['cyan']):
    """Set up a spinner for plaintext mode.
    
    This function creates a spinner thread that will be shown during AI response generation
    in plaintext mode, but only if output is a terminal (not redirected).
    
    Args:
        message (str): Message to display in the spinner
        color (str): Color for the spinner (from COLORS dict)
        
    Returns:
        tuple: (spinner_thread, stop_event) if terminal output, (None, None) if redirected
    """
    import threading
    import sys
    from ngpt.ui.tui import spinner
    
    # Only show spinner if output is a terminal (not redirected)
    if not sys.stdout.isatty():
        return None, None
    
    # Create spinner thread and stop event
    stop_event = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner,
        args=(message,),
        kwargs={"stop_event": stop_event, "color": color}
    )
    spinner_thread.daemon = True
    spinner_thread.start()
    
    return spinner_thread, stop_event

def cleanup_plaintext_spinner(spinner_thread, stop_event):
    """Clean up a plaintext spinner.
    
    This function stops the spinner thread and clears the terminal line.
    
    Args:
        spinner_thread: The spinner thread to stop
        stop_event: The stop event to signal
    """
    import sys
    import threading
    
    if stop_event and spinner_thread:
        stop_event.set()
        if spinner_thread.is_alive():
            spinner_thread.join()
        
        # Clear the spinner line completely
        with TERMINAL_RENDER_LOCK:
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush() 