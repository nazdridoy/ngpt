from ..formatters import COLORS
from ..renderers import prettify_markdown, prettify_streaming_markdown
from ..ui import spinner
from ...utils import enhance_prompt_with_web_search
import sys
import threading

def chat_mode(client, args, logger=None):
    """Handle the standard chat mode with a single prompt.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    # Handle pipe mode
    if args.pipe:
        # Read input from stdin
        stdin_content = sys.stdin.read().strip()
        
        # Get the prompt - either use provided one or ask user
        if args.prompt is None:
            try:
                print("Enter your prompt (use {} as placeholder for stdin): ", end='')
                prompt = input()
            except KeyboardInterrupt:
                print("\nInput cancelled by user. Exiting gracefully.")
                sys.exit(130)
        else:
            prompt = args.prompt
        
        # Replace the placeholder in the prompt with stdin content
        placeholder = "{}"
        
        # Check if the placeholder exists in the prompt
        if placeholder not in prompt:
            print(f"{COLORS['yellow']}Warning: Placeholder '{placeholder}' not found in prompt. Appending stdin content to the end.{COLORS['reset']}")
            prompt = f"{prompt} {stdin_content}"
        else:
            prompt = prompt.replace(placeholder, stdin_content)
    # Handle regular chat mode
    else:
        # Get the prompt
        if args.prompt is None:
            try:
                print("Enter your prompt: ", end='')
                prompt = input()
            except KeyboardInterrupt:
                print("\nInput cancelled by user. Exiting gracefully.")
                sys.exit(130)
        else:
            prompt = args.prompt
    
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
        
    # Create messages array with system prompt
    default_system_prompt = "You are a helpful assistant."
    if args.prettify or args.stream_prettify:
        default_system_prompt += " You can use markdown formatting in your responses where appropriate."
    
    system_prompt = args.preprompt if args.preprompt else default_system_prompt
    
    # Log the system message if logging is enabled
    if logger:
        logger.log("system", system_prompt)
        
    messages = [
        {"role": "system", "content": system_prompt},
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