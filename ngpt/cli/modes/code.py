from ..formatters import COLORS
from ..renderers import prettify_markdown, prettify_streaming_markdown, has_markdown_renderer, show_available_renderers
from ..ui import spinner
from ...utils import enhance_prompt_with_web_search
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
    
    # Log the user prompt if logging is enabled
    if logger:
        logger.log("user", prompt)
    
    # Enhance prompt with web search if enabled
    if args.web_search:
        try:
            original_prompt = prompt
            prompt = enhance_prompt_with_web_search(prompt, logger=logger, disable_citations=True)
            print("Enhanced input with web search results.")
            
            # Log the enhanced prompt if logging is enabled
            if logger:
                # Use "web_search" role instead of "system" for clearer logs
                logger.log("web_search", prompt.replace(original_prompt, "").strip())
        except Exception as e:
            print(f"{COLORS['yellow']}Warning: Failed to enhance prompt with web search: {str(e)}{COLORS['reset']}")
            # Continue with the original prompt if web search fails

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
            print(f"{COLORS['yellow']}Note: Using standard markdown rendering (--prettify). For streaming markdown rendering, use --stream-prettify instead.{COLORS['reset']}")
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
    if use_stream_prettify and live_display:
        stream_callback = spinner_handling_callback
    
    # Select the appropriate system prompt based on formatting and preprompt
    if args.preprompt:
        # Log the preprompt if logging is enabled
        if logger:
            logger.log("system", f"Preprompt: {args.preprompt}")
            
        # Use preprompt template with high-priority formatting
        if use_regular_prettify or use_stream_prettify:
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
        if use_regular_prettify or use_stream_prettify:
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
            stream_callback=stream_callback
        )
    except Exception as e:
        print(f"Error generating code: {e}")
        generated_code = ""
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if use_stream_prettify and live_display:
        # Before stopping the live display, update with complete=True to show final formatted content
        if stream_callback and generated_code:
            stream_callback(generated_code, complete=True)
    
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