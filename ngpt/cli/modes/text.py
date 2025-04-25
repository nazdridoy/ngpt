from ..formatters import COLORS
from ..renderers import prettify_markdown, prettify_streaming_markdown
from ..ui import get_multiline_input

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
    
    print("\nSubmission successful. Waiting for response...")
    
    # Log the user message if logging is enabled
    if logger:
        logger.log("user", prompt)
    
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
    
    if args.stream_prettify:
        should_stream = True  # Enable streaming
        # This is the standard mode, not interactive
        live_display, stream_callback = prettify_streaming_markdown(args.renderer)
        if not live_display:
            # Fallback to normal prettify if live display setup failed
            args.prettify = True
            args.stream_prettify = False
            should_stream = False
            print(f"{COLORS['yellow']}Falling back to regular prettify mode.{COLORS['reset']}")
    
    # If regular prettify is enabled with streaming, inform the user
    if args.prettify and not args.no_stream:
        print(f"{COLORS['yellow']}Note: Streaming disabled to enable markdown rendering.{COLORS['reset']}")
    
    # Start live display if using stream-prettify
    if args.stream_prettify and live_display:
        live_display.start()
    
    response = client.chat(prompt, stream=should_stream, web_search=args.web_search,
                       temperature=args.temperature, top_p=args.top_p,
                       max_tokens=args.max_tokens, messages=messages,
                       markdown_format=args.prettify or args.stream_prettify,
                       stream_callback=stream_callback)
    
    # Stop live display if using stream-prettify
    if args.stream_prettify and live_display:
        live_display.stop()
        
    # Log the AI response if logging is enabled
    if logger and response:
        logger.log("assistant", response)
        
    # Handle non-stream response or regular prettify
    if (args.no_stream or args.prettify) and response:
        if args.prettify:
            prettify_markdown(response, args.renderer)
        else:
            print(response) 