from ..formatters import COLORS
from ..renderers import prettify_markdown, prettify_streaming_markdown
from ..ui import get_multiline_input, spinner
from ...utils import enhance_prompt_with_web_search
import threading
import sys

def text_mode(client, args, logger=None):
    """Handle the multi-line text input mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    if args.prompt is not None:
        prompt = args.prompt
    else:
        prompt = get_multiline_input()
        if prompt is None:
            # Input was cancelled or empty
            print("Exiting.")
            return
    
    # Log the user message if logging is enabled
    if logger:
        logger.log("user", prompt)
    
    # Enhance prompt with web search if enabled
    if args.web_search:
        try:
            original_prompt = prompt
            prompt = enhance_prompt_with_web_search(prompt, logger=logger)
            print("Enhanced input with web search results.")
            
            # Log the enhanced prompt if logging is enabled
            if logger:
                # Use "web_search" role instead of "system" for clearer logs
                logger.log("web_search", prompt.replace(original_prompt, "").strip())
        except Exception as e:
            print(f"{COLORS['yellow']}Warning: Failed to enhance prompt with web search: {str(e)}{COLORS['reset']}")
            # Continue with the original prompt if web search fails
    
    # Create messages array with preprompt if available
    messages = None
    if args.preprompt:
        # Log the system message if logging is enabled
        if logger:
            logger.log("system", args.preprompt)
            
        messages = [
            {"role": "system", "content": args.preprompt},
            {"role": "user", "content": prompt}
        ]
    
    # Set default streaming behavior based on --no-stream and --prettify arguments
    should_stream = not args.no_stream and not args.prettify
    
    # If stream-prettify is enabled
    stream_callback = None
    live_display = None
    stop_spinner_func = None
    
    if args.stream_prettify:
        should_stream = True  # Enable streaming
        # This is the standard mode, not interactive
        live_display, stream_callback, setup_spinner = prettify_streaming_markdown(args.renderer)
        if not live_display:
            # Fallback to normal prettify if live display setup failed
            args.prettify = True
            args.stream_prettify = False
            should_stream = False
            print(f"{COLORS['yellow']}Falling back to regular prettify mode.{COLORS['reset']}")
    
    # If regular prettify is enabled with streaming, inform the user
    if args.prettify and not args.no_stream:
        print(f"{COLORS['yellow']}Note: Using standard markdown rendering (--prettify). For streaming markdown rendering, use --stream-prettify instead.{COLORS['reset']}")
    
    # Show a static message if live_display is not available
    if args.stream_prettify and not live_display:
        print("\nWaiting for AI response...")
    
    # Set up the spinner if we have a live display
    stop_spinner_event = None
    if args.stream_prettify and live_display:
        stop_spinner_event = threading.Event()
        stop_spinner_func = setup_spinner(stop_spinner_event, color=COLORS['cyan'])
    
    # Create a wrapper for the stream callback that will stop the spinner on first content
    original_callback = stream_callback
    first_content_received = False
    
    def spinner_handling_callback(content, **kwargs):
        nonlocal first_content_received
        
        # On first content, stop the spinner 
        if not first_content_received and stop_spinner_func:
            first_content_received = True
            # Stop the spinner
            stop_spinner_func()
            # Ensure spinner message is cleared with an extra blank line
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush()
        
        # Call the original callback to update the display
        if original_callback:
            original_callback(content, **kwargs)
    
    # Use our wrapper callback
    if args.stream_prettify and live_display:
        stream_callback = spinner_handling_callback
    
    response = client.chat(prompt, stream=should_stream,
                       temperature=args.temperature, top_p=args.top_p,
                       max_tokens=args.max_tokens, messages=messages,
                       markdown_format=args.prettify or args.stream_prettify,
                       stream_callback=stream_callback)
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if args.stream_prettify and live_display:
        # Before stopping the live display, update with complete=True to show final formatted content
        if stream_callback and response:
            stream_callback(response, complete=True)
        
    # Log the AI response if logging is enabled
    if logger and response:
        logger.log("assistant", response)
        
    # Handle non-stream response or regular prettify
    if (args.no_stream or args.prettify) and response:
        if args.prettify:
            prettify_markdown(response, args.renderer)
        else:
            print(response) 