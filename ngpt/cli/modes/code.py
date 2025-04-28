from ..formatters import COLORS
from ..renderers import prettify_markdown, prettify_streaming_markdown, has_markdown_renderer, show_available_renderers
from ..ui import spinner
import sys
import threading

def code_mode(client, args, logger=None):
    """Handle the code generation mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    if args.prompt is None:
        try:
            print("Enter code description: ", end='')
            prompt = input()
        except KeyboardInterrupt:
            print("\nInput cancelled by user. Exiting gracefully.")
            sys.exit(130)
    else:
        prompt = args.prompt
    
    # Log the user prompt if logging is enabled
    if logger:
        logger.log("user", prompt)

    # Setup for streaming and prettify logic
    stream_callback = None
    live_display = None
    stop_spinner_func = None
    should_stream = True # Default to streaming
    use_stream_prettify = False
    use_regular_prettify = False

    # Determine final behavior based on flag priority
    if args.stream_prettify:
        # Highest priority: stream-prettify
        if has_markdown_renderer('rich'):
            should_stream = True
            use_stream_prettify = True
            live_display, stream_callback, setup_spinner = prettify_streaming_markdown(args.renderer)
            if not live_display:
                # Fallback if live display fails
                use_stream_prettify = False
                use_regular_prettify = True
                should_stream = False 
                print(f"{COLORS['yellow']}Live display setup failed. Falling back to regular prettify mode.{COLORS['reset']}")
        else:
            # Rich not available for stream-prettify
            print(f"{COLORS['yellow']}Warning: Rich is not available for --stream-prettify. Install with: pip install \"ngpt[full]\".{COLORS['reset']}")
            print(f"{COLORS['yellow']}Falling back to default streaming without prettify.{COLORS['reset']}")
            should_stream = True
            use_stream_prettify = False
    elif args.no_stream:
        # Second priority: no-stream
        should_stream = False
        use_regular_prettify = False # No prettify if no streaming
    elif args.prettify:
        # Third priority: prettify (requires disabling stream)
        if has_markdown_renderer(args.renderer):
            should_stream = False
            use_regular_prettify = True
            print(f"{COLORS['yellow']}Note: Streaming disabled to enable regular markdown rendering (--prettify).{COLORS['reset']}")
        else:
            # Renderer not available for prettify
            print(f"{COLORS['yellow']}Warning: Renderer '{args.renderer}' not available for --prettify.{COLORS['reset']}")
            show_available_renderers()
            print(f"{COLORS['yellow']}Falling back to default streaming without prettify.{COLORS['reset']}")
            should_stream = True 
            use_regular_prettify = False
    # else: Default is should_stream = True
    
    print("\nGenerating code...")
    
    # Show a static message if no live_display is available
    if use_stream_prettify and not live_display:
        print("Waiting for AI response...")
    
    # Set up the spinner if we have a live display
    stop_spinner_event = None
    if use_stream_prettify and live_display:
        stop_spinner_event = threading.Event()
        stop_spinner_func = setup_spinner(stop_spinner_event, color=COLORS['cyan'])
    
    # Create a wrapper for the stream callback that will stop the spinner on first content
    original_callback = stream_callback
    first_content_received = False
    
    def spinner_handling_callback(content):
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
            original_callback(content)
    
    # Use our wrapper callback
    if use_stream_prettify and live_display:
        stream_callback = spinner_handling_callback
        
    generated_code = client.generate_code(
        prompt=prompt, 
        language=args.language, 
        web_search=args.web_search,
        temperature=args.temperature, 
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        # Request markdown from API if any prettify option is active
        markdown_format=use_regular_prettify or use_stream_prettify,
        stream=should_stream,
        stream_callback=stream_callback
    )
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if use_stream_prettify and live_display:
        live_display.stop()
    
    # Log the generated code if logging is enabled
    if logger and generated_code:
        logger.log("assistant", generated_code)
        
    # Print non-streamed output if needed
    if generated_code and not should_stream:
        if use_regular_prettify:
            print("\nGenerated code:")
            prettify_markdown(generated_code, args.renderer)
        else:
            # Should only happen if --no-stream was used without prettify
            print(f"\nGenerated code:\n{generated_code}") 