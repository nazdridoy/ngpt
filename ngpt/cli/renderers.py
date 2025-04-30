import os
import shutil
import subprocess
import tempfile
import sys
from .formatters import COLORS

# Try to import markdown rendering libraries
try:
    import rich
    from rich.markdown import Markdown
    from rich.console import Console
    from rich.live import Live
    from rich.text import Text
    from rich.panel import Panel
    import rich.box
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

# Try to import the glow command if available
def has_glow_installed():
    """Check if glow is installed in the system."""
    return shutil.which("glow") is not None

HAS_GLOW = has_glow_installed()

def has_markdown_renderer(renderer='auto'):
    """Check if the specified markdown renderer is available.
    
    Args:
        renderer (str): Which renderer to check: 'auto', 'rich', or 'glow'
    
    Returns:
        bool: True if the renderer is available, False otherwise
    """
    if renderer == 'auto':
        return HAS_RICH or HAS_GLOW
    elif renderer == 'rich':
        return HAS_RICH
    elif renderer == 'glow':
        return HAS_GLOW
    else:
        return False

def show_available_renderers():
    """Show which markdown renderers are available and their status."""
    print(f"\n{COLORS['cyan']}{COLORS['bold']}Available Markdown Renderers:{COLORS['reset']}")
    
    if HAS_GLOW:
        print(f"  {COLORS['green']}✓ Glow{COLORS['reset']} - Terminal-based Markdown renderer")
    else:
        print(f"  {COLORS['yellow']}✗ Glow{COLORS['reset']} - Not installed (https://github.com/charmbracelet/glow)")
        
    if HAS_RICH:
        print(f"  {COLORS['green']}✓ Rich{COLORS['reset']} - Python library for terminal formatting (Recommended)")
    else:
        print(f"  {COLORS['yellow']}✗ Rich{COLORS['reset']} - Not installed (pip install \"ngpt[full]\" or pip install rich)")
        
    if not HAS_GLOW and not HAS_RICH:
        print(f"\n{COLORS['yellow']}To enable prettified markdown output, install one of the above renderers.{COLORS['reset']}")
        print(f"{COLORS['yellow']}For Rich: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
    else:
        renderers = []
        if HAS_RICH:
            renderers.append("rich")
        if HAS_GLOW:
            renderers.append("glow")
        print(f"\n{COLORS['green']}Usage examples:{COLORS['reset']}")
        print(f"  ngpt --prettify \"Your prompt here\"                {COLORS['gray']}# Beautify markdown responses{COLORS['reset']}")
        print(f"  ngpt -c --prettify \"Write a sort function\"        {COLORS['gray']}# Syntax highlight generated code{COLORS['reset']}")
        if renderers:
            renderer = renderers[0]
            print(f"  ngpt --prettify --renderer={renderer} \"Your prompt\"  {COLORS['gray']}# Specify renderer{COLORS['reset']}")
    
    print("")

def warn_if_no_markdown_renderer(renderer='auto'):
    """Warn the user if the specified markdown renderer is not available.
    
    Args:
        renderer (str): Which renderer to check: 'auto', 'rich', or 'glow'
    
    Returns:
        bool: True if the renderer is available, False otherwise
    """
    if has_markdown_renderer(renderer):
        return True
    
    if renderer == 'auto':
        print(f"{COLORS['yellow']}Warning: No markdown rendering library available.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\"{COLORS['reset']}")
        print(f"{COLORS['yellow']}Or install 'glow' from https://github.com/charmbracelet/glow{COLORS['reset']}")
    elif renderer == 'rich':
        print(f"{COLORS['yellow']}Warning: Rich is not available.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
    elif renderer == 'glow':
        print(f"{COLORS['yellow']}Warning: Glow is not available.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install from https://github.com/charmbracelet/glow{COLORS['reset']}")
    else:
        print(f"{COLORS['yellow']}Error: Invalid renderer '{renderer}'. Use 'auto', 'rich', or 'glow'.{COLORS['reset']}")
    
    return False

def prettify_markdown(text, renderer='auto'):
    """Render markdown text with beautiful formatting using either Rich or Glow.
    
    The function handles both general markdown and code blocks with syntax highlighting.
    For code generation mode, it automatically wraps the code in markdown code blocks.
    
    Args:
        text (str): Markdown text to render
        renderer (str): Which renderer to use: 'auto', 'rich', or 'glow'
        
    Returns:
        bool: True if rendering was successful, False otherwise
    """
    # For 'auto', prefer rich if available, otherwise use glow
    if renderer == 'auto':
        if HAS_RICH:
            return prettify_markdown(text, 'rich')
        elif HAS_GLOW:
            return prettify_markdown(text, 'glow')
        else:
            return False
    
    # Use glow for rendering
    elif renderer == 'glow':
        if not HAS_GLOW:
            print(f"{COLORS['yellow']}Warning: Glow is not available. Install from https://github.com/charmbracelet/glow{COLORS['reset']}")
            # Fall back to rich if available
            if HAS_RICH:
                print(f"{COLORS['yellow']}Falling back to Rich renderer.{COLORS['reset']}")
                return prettify_markdown(text, 'rich')
            return False
            
        # Use glow
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp:
            temp_filename = temp.name
            temp.write(text)
            
        try:
            # Execute glow on the temporary file
            subprocess.run(["glow", temp_filename], check=True)
            os.unlink(temp_filename)
            return True
        except Exception as e:
            print(f"{COLORS['yellow']}Error using glow: {str(e)}{COLORS['reset']}")
            os.unlink(temp_filename)
            
            # Fall back to rich if available
            if HAS_RICH:
                print(f"{COLORS['yellow']}Falling back to Rich renderer.{COLORS['reset']}")
                return prettify_markdown(text, 'rich')
            return False
    
    # Use rich for rendering
    elif renderer == 'rich':
        if not HAS_RICH:
            print(f"{COLORS['yellow']}Warning: Rich is not available.{COLORS['reset']}")
            print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
            # Fall back to glow if available
            if HAS_GLOW:
                print(f"{COLORS['yellow']}Falling back to Glow renderer.{COLORS['reset']}")
                return prettify_markdown(text, 'glow')
            return False
            
        # Use rich
        try:
            console = Console()
            
            # Create a panel around the markdown for consistency with stream_prettify
            from rich.panel import Panel
            import rich.box
            from rich.text import Text
            
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
    
    # Invalid renderer specified
    else:
        print(f"{COLORS['yellow']}Error: Invalid renderer '{renderer}'. Use 'auto', 'rich', or 'glow'.{COLORS['reset']}")
        return False

def prettify_streaming_markdown(renderer='rich', is_interactive=False, header_text=None):
    """Set up streaming markdown rendering.
    
    This function creates a live display context for rendering markdown
    that can be updated in real-time as streaming content arrives.
    
    Args:
        renderer (str): Which renderer to use (currently only 'rich' is supported for streaming)
        is_interactive (bool): Whether this is being used in interactive mode
        header_text (str): Header text to include at the top (for interactive mode)
        
    Returns:
        tuple: (live_display, update_function, stop_spinner_func) if successful, (None, None, None) otherwise
              stop_spinner_func is a function that should be called when first content is received
    """
    # Only warn if explicitly specifying a renderer other than 'rich' or 'auto'
    if renderer != 'rich' and renderer != 'auto':
        print(f"{COLORS['yellow']}Warning: Streaming prettify only supports 'rich' renderer currently.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Falling back to Rich renderer.{COLORS['reset']}")
    
    # Always use rich for streaming prettify
    renderer = 'rich'
    
    if not HAS_RICH:
        print(f"{COLORS['yellow']}Warning: Rich is not available for streaming prettify.{COLORS['reset']}")
        print(f"{COLORS['yellow']}Install with: pip install \"ngpt[full]\" or pip install rich{COLORS['reset']}")
        return None, None, None
        
    try:
        from rich.live import Live
        from rich.markdown import Markdown
        from rich.console import Console
        from rich.text import Text
        from rich.panel import Panel
        import rich.box
        
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