from ngpt.ui.colors import COLORS
from ngpt.ui.renderers import prettify_streaming_markdown, TERMINAL_RENDER_LOCK, setup_plaintext_spinner, cleanup_plaintext_spinner, create_spinner_handling_callback
from ngpt.ui.tui import spinner
from ngpt.utils.web_search import enhance_prompt_with_web_search
from ngpt.ui.pipe import process_piped_input
import sys
import threading

def chat_mode(client, args, logger=None):
    """Handle the standard chat mode with a single prompt.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
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
    
    # Handle pipe mode
    if args.pipe:
        prompt = process_piped_input(prompt, logger=logger)
    
    # Log the user message if logging is enabled
    if logger:
        logger.log("user", prompt)
    
    # Enhance prompt with web search if enabled
    if args.web_search:
        try:
            original_prompt = prompt
            
            # Start spinner for web search
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(
                target=spinner, 
                args=("Searching the web for information...",), 
                kwargs={"stop_event": stop_spinner, "color": COLORS['cyan']}
            )
            spinner_thread.daemon = True
            spinner_thread.start()
            
            try:
                prompt = enhance_prompt_with_web_search(prompt, logger=logger)
                # Stop the spinner
                stop_spinner.set()
                spinner_thread.join()
                # Clear the spinner line completely
                with TERMINAL_RENDER_LOCK:
                    sys.stdout.write("\r" + " " * 100 + "\r")
                    sys.stdout.flush()
                    print("Enhanced input with web search results.")
            except Exception as e:
                # Stop the spinner before re-raising
                stop_spinner.set()
                spinner_thread.join()
                raise e
            
            # Log the enhanced prompt if logging is enabled
            if logger:
                # Use "web_search" role instead of "system" for clearer logs
                logger.log("web_search", prompt.replace(original_prompt, "").strip())
        except Exception as e:
            print(f"{COLORS['yellow']}Warning: Failed to enhance prompt with web search: {str(e)}{COLORS['reset']}")
            # Continue with the original prompt if web search fails
        
    # Create messages array with system prompt
    default_system_prompt = "You are a helpful assistant."
    if not args.plaintext:
        default_system_prompt += " You can use markdown formatting in your responses where appropriate."
    
    system_prompt = args.preprompt if args.preprompt else default_system_prompt
    
    # Log the system message if logging is enabled
    if logger:
        logger.log("system", system_prompt)
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Set up display mode based on args
    should_stream = True  # Default behavior (stream-prettify)
    stream_callback = None
    live_display = None
    stop_spinner_func = None
    stop_spinner_event = None
    first_content_received = False
    
    # Spinner for plaintext mode
    plaintext_spinner_thread = None
    plaintext_stop_event = None
    
    # Handle display mode based on parameters
    if args.plaintext:
        # Plain text mode - no streaming, no markdown rendering
        should_stream = False
        plaintext_spinner_thread, plaintext_stop_event = setup_plaintext_spinner("Waiting for response...", COLORS['cyan'])
    else:
        # Default stream-prettify mode - stream with live markdown rendering
        live_display, stream_callback, setup_spinner = prettify_streaming_markdown()
        if not live_display:
            # Fallback if display creation fails
            print(f"{COLORS['yellow']}Warning: Live display setup failed. Falling back to plain streaming.{COLORS['reset']}")
    
    # Show a static message if streaming without prettify
    if should_stream and not live_display and not args.plaintext:
        print("\nWaiting for AI response...")
    
    # Set up the spinner if we have a live display and stream-prettify is enabled
    if should_stream and not args.plaintext and live_display:
        stop_spinner_event = threading.Event()
        stop_spinner_func = setup_spinner(stop_spinner_event, color=COLORS['cyan'])
    
    # Create a wrapper for the stream callback that handles spinner
    if stream_callback:
        original_callback = stream_callback
        first_content_received_ref = [first_content_received]
        stream_callback = create_spinner_handling_callback(original_callback, stop_spinner_func, first_content_received_ref)
    
    response = client.chat(prompt, stream=should_stream,
                       temperature=args.temperature, top_p=args.top_p,
                       max_tokens=args.max_tokens, messages=messages,
                       markdown_format=not args.plaintext,
                       stream_callback=stream_callback)
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received_ref[0]:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if not args.plaintext and live_display:
        # Before stopping the live display, update with complete=True to show final formatted content
        if stream_callback and response:
            stream_callback(response, complete=True)
    
    # Stop plaintext spinner if it was started
    cleanup_plaintext_spinner(plaintext_spinner_thread, plaintext_stop_event)
    
    # Log the AI response if logging is enabled
    if logger and response:
        logger.log("assistant", response)
        
    # Handle plain text response
    if args.plaintext and response:
        with TERMINAL_RENDER_LOCK:
            print(response) 