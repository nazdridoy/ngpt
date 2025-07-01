import os
import shutil
import subprocess
import tempfile
import sys
import threading
from .formatters import COLORS

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

def prettify_markdown(text):
    """Render markdown text with beautiful formatting using Rich.
    
    The function handles both general markdown and code blocks with syntax highlighting.
    For code generation mode, it automatically wraps the code in markdown code blocks.
    
    Args:
        text (str): Markdown text to render
        
    Returns:
        bool: True if rendering was successful, False otherwise
    """
    try:
        console = Console()
        
        # Create a panel around the markdown for consistency with stream_prettify
        # Get terminal dimensions
        term_width = shutil.get_terminal_size().columns
        
        # Create panel with similar styling to stream_prettify
        clean_header = "🤖 nGPT"
        panel_title = Text(clean_header, style="cyan bold")
        
        md = Markdown(text)
        panel = Panel(
            md,
            title=panel_title,
            title_align="left",
            border_style="cyan",
            padding=(1, 1),
            width=console.width - 4,  # Make panel slightly narrower than console
            box=rich.box.ROUNDED
        )
        
        console.print(panel)
        return True
    except Exception as e:
        print(f"{COLORS['yellow']}Error using rich for markdown: {str(e)}{COLORS['reset']}")
        return False

def prettify_streaming_markdown(is_interactive=False, header_text=None):
    """Set up streaming markdown rendering.
    
    This function creates a live display context for rendering markdown
    that can be updated in real-time as streaming content arrives.
    
    Args:
        is_interactive (bool): Whether this is being used in interactive mode
        header_text (str): Header text to include at the top (for interactive mode)
        
    Returns:
        tuple: (live_display, update_function, stop_spinner_func) if successful, (None, None, None) otherwise
              stop_spinner_func is a function that should be called when first content is received
    """
    try:
        console = Console()
        
        # Create an empty markdown object to start with
        if is_interactive and header_text:
            # For interactive mode, include header in a panel
            # Clean up the header text to avoid duplication - use just "🤖 nGPT" instead of "╭─ 🤖 nGPT"
            clean_header = "🤖 nGPT"
            panel_title = Text(clean_header, style="cyan bold")
            
            # Create a nicer, more compact panel
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
        else:
            # Always use a panel - even in non-interactive mode
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
                if is_interactive and header_text:
                    # Update the panel content - for streaming, only show the last portion that fits in display_height
                    if not is_complete:
                        # Calculate approximate lines needed (rough estimation)
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
                else:
                    # Same logic for non-interactive mode
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
            from .ui import spinner
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