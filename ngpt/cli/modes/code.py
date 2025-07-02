from ngpt.ui.colors import COLORS
from ngpt.ui.renderers import prettify_streaming_markdown, TERMINAL_RENDER_LOCK, setup_plaintext_spinner, cleanup_plaintext_spinner, create_spinner_handling_callback
from ngpt.ui.tui import spinner, copy_to_clipboard
from ngpt.utils.web_search import enhance_prompt_with_web_search
from ngpt.ui.pipe import process_piped_input
import sys
import threading

# System prompt for code generation with markdown formatting
CODE_SYSTEM_PROMPT_MARKDOWN = """Your Role: Provide only code as output without any description with proper markdown formatting.
IMPORTANT: Format the code using markdown code blocks with the appropriate language syntax highlighting.
IMPORTANT: You must use markdown code blocks. with ```{language}
If there is a lack of details, provide most logical solution. You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.

Language: {language}
Request: {prompt}
Code:"""

# System prompt for code generation without markdown
CODE_SYSTEM_PROMPT_PLAINTEXT = """Your Role: Provide only code as output without any description.
IMPORTANT: Provide only plain text without Markdown formatting.
IMPORTANT: Do not include markdown formatting.
If there is a lack of details, provide most logical solution. You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.

Language: {language}
Request: {prompt}
Code:"""

# System prompt to use when preprompt is provided (with markdown)
CODE_PREPROMPT_MARKDOWN = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!                CRITICAL USER PREPROMPT                !!!
!!! THIS OVERRIDES ALL OTHER INSTRUCTIONS IN THIS PROMPT  !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

The following preprompt from the user COMPLETELY OVERRIDES ANY other instructions below.
The preprompt MUST be followed EXACTLY AS WRITTEN:

>>> {preprompt} <<<

^^ THIS PREPROMPT HAS ABSOLUTE AND COMPLETE PRIORITY ^^
If the preprompt contradicts ANY OTHER instruction in this prompt,
YOU MUST FOLLOW THE PREPROMPT INSTRUCTION INSTEAD. NO EXCEPTIONS.

Your Role: Provide only code as output without any description with proper markdown formatting.
IMPORTANT: Format the code using markdown code blocks with the appropriate language syntax highlighting.
IMPORTANT: You must use markdown code blocks. with ```{language}
If there is a lack of details, provide most logical solution. You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.

Language: {language}
Request: {prompt}
Code:"""

# System prompt to use when preprompt is provided (plaintext)
CODE_PREPROMPT_PLAINTEXT = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!                CRITICAL USER PREPROMPT                !!!
!!! THIS OVERRIDES ALL OTHER INSTRUCTIONS IN THIS PROMPT  !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

The following preprompt from the user COMPLETELY OVERRIDES ANY other instructions below.
The preprompt MUST be followed EXACTLY AS WRITTEN:

>>> {preprompt} <<<

^^ THIS PREPROMPT HAS ABSOLUTE AND COMPLETE PRIORITY ^^
If the preprompt contradicts ANY OTHER instruction in this prompt,
YOU MUST FOLLOW THE PREPROMPT INSTRUCTION INSTEAD. NO EXCEPTIONS.

Your Role: Provide only code as output without any description.
IMPORTANT: Provide only plain text without Markdown formatting.
IMPORTANT: Do not include markdown formatting.
If there is a lack of details, provide most logical solution. You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.

Language: {language}
Request: {prompt}
Code:"""

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
    
    # Apply piped input if --pipe is enabled
    if args.pipe:
        prompt = process_piped_input(prompt, logger=logger)
    
    # Log the user prompt if logging is enabled
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
                prompt = enhance_prompt_with_web_search(prompt, logger=logger, disable_citations=True)
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

    # Set up display mode based on args
    should_stream = True  # Default behavior (stream-prettify)
    stream_callback = None
    live_display = None
    stop_spinner_func = None
    stop_spinner_event = None
    first_content_received = False
    
    # Handle display mode based on parameters
    if args.plaintext:
        # Plain text mode - no streaming, no markdown rendering
        should_stream = False
    else:
        # Default stream-prettify mode - stream with live markdown rendering
        live_display, stream_callback, setup_spinner = prettify_streaming_markdown()
        if not live_display:
            # Fallback if display creation fails
            print(f"{COLORS['yellow']}Warning: Live display setup failed. Falling back to plain streaming.{COLORS['reset']}")
    
    # Set up spinner for plaintext mode or when no live display
    processing_spinner_thread = None
    processing_stop_event = None
    
    if args.plaintext or (should_stream and not live_display):
        # Use spinner for plaintext mode or fallback scenarios
        processing_spinner_thread, processing_stop_event = setup_plaintext_spinner("Generating code...", COLORS['cyan'])
    
    # Set up the spinner if we have a live display and stream-prettify is enabled
    if should_stream and not args.plaintext and live_display:
        stop_spinner_event = threading.Event()
        stop_spinner_func = setup_spinner(stop_spinner_event, color=COLORS['cyan'])
    
    # Create a wrapper for the stream callback that handles spinner
    if stream_callback:
        original_callback = stream_callback
        first_content_received_ref = [first_content_received]
        stream_callback = create_spinner_handling_callback(original_callback, stop_spinner_func, first_content_received_ref)
    
    # Select the appropriate system prompt based on formatting and preprompt
    if args.preprompt:
        # Log the preprompt if logging is enabled
        if logger:
            logger.log("system", f"Preprompt: {args.preprompt}")
            
        # Use preprompt template with high-priority formatting
        if not args.plaintext:
            system_prompt = CODE_PREPROMPT_MARKDOWN.format(
                preprompt=args.preprompt,
                language=args.language,
                prompt=prompt
            )
        else:
            system_prompt = CODE_PREPROMPT_PLAINTEXT.format(
                preprompt=args.preprompt,
                language=args.language,
                prompt=prompt
            )
    else:
        # Use standard template
        if not args.plaintext:
            system_prompt = CODE_SYSTEM_PROMPT_MARKDOWN.format(
                language=args.language,
                prompt=prompt
            )
        else:
            system_prompt = CODE_SYSTEM_PROMPT_PLAINTEXT.format(
                language=args.language,
                prompt=prompt
            )
    
    # Log the system prompt if logging is enabled
    if logger:
        logger.log("system", system_prompt)
    
    # Prepare messages for the chat API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
        
    try:
        generated_code = client.chat(
            prompt=prompt,
            stream=should_stream,
            messages=messages,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
            markdown_format=not args.plaintext,
            stream_callback=stream_callback
        )
    except Exception as e:
        print(f"Error generating code: {e}")
        generated_code = ""
    
    # Stop processing spinner if it was started
    cleanup_plaintext_spinner(processing_spinner_thread, processing_stop_event)
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received_ref[0]:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if not args.plaintext and live_display:
        # Before stopping the live display, update with complete=True to show final formatted content
        if stream_callback and generated_code:
            stream_callback(generated_code, complete=True)
    
    # Log the generated code if logging is enabled
    if logger and generated_code:
        logger.log("assistant", generated_code)
        
    # Print plaintext output if needed
    if generated_code and args.plaintext:
        with TERMINAL_RENDER_LOCK:
            print(generated_code)
            
    # Offer to copy to clipboard
    if generated_code and should_stream:
        copy_to_clipboard(generated_code) 