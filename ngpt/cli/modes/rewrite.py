import sys
import platform
import threading
import time
from ..formatters import COLORS
from ..renderers import prettify_markdown, prettify_streaming_markdown
from ..ui import get_multiline_input, spinner
from ...utils import enhance_prompt_with_web_search

# System prompt for rewriting text
REWRITE_SYSTEM_PROMPT = """You are an expert text editor and rewriter. Your task is to rewrite the user's text to improve readability and flow while carefully preserving the original meaning, tone, and style.

PRIMARY GOAL:
Improve the quality and clarity of writing without changing the author's voice or intent.

PRESERVATION RULES (HIGHEST PRIORITY):
1. Preserve the exact meaning and information content
2. Maintain the original tone (formal/casual/technical/friendly/serious/rude)
3. Keep the author's perspective and point of view
4. Respect the style of expression when intentional
5. Retain technical terminology, jargon, and domain-specific language
6. Keep all facts, data points, quotes, and references exactly as provided
7. Preserve all @ mentions (like @username) exactly as written

FORMAT PRESERVATION:
1. Maintain all paragraph breaks and section structures
2. Preserve formatting of lists, bullet points, and numbering
3. Keep code blocks (```) exactly as they appear with no changes to code
4. Respect all markdown formatting (bold, italic, headers, etc.)
5. Preserve URLs, email addresses, file paths, variables, and @ mentions exactly
6. Maintain the structure of tables and other special formats

IMPROVEMENT FOCUS:
1. Fix grammar, spelling, and punctuation errors
2. Improve sentence structure and flow
3. Enhance clarity and readability
4. Make language more concise and precise
5. Replace awkward phrasings with more natural alternatives
6. Break up sentences longer than 25 words
7. Convert passive voice to active when appropriate
8. Remove redundancies, filler words, and unnecessary repetition

CONTENT-SPECIFIC GUIDANCE:
- For technical content: Prioritize precision and clarity over stylistic changes
- For casual text: Maintain conversational flow and personality
- For formal writing: Preserve professionalism while improving structure
- For emotional content: Carefully maintain the emotional resonance and intensity

STRICTLY AVOID:
1. Adding new information not present in the original
2. Removing key points or substantive content
3. Significantly changing the formality level
4. Inserting your own opinions or commentary
5. Explaining what you changed (just provide the improved text)
6. Altering the meaning of any sentence, even slightly
7. Changing domain-specific terminology or jargon to general terms
8. Modifying or removing @ mentions, hashtags, or issue references (like #123)

OUTPUT INSTRUCTION:
Provide ONLY the rewritten text with no explanations, comments, or meta-text.

EXAMPLES:

ORIGINAL: "The implementation of the feature, which was delayed due to unforeseen technical complications, is now scheduled for next week's release."
BETTER: "We delayed the feature implementation due to unforeseen technical complications. It's now scheduled for next week's release."

ORIGINAL: "We was hoping you could help with this issue what we are having with the server."
BETTER: "We were hoping you could help with this issue we're having with the server."

ORIGINAL: "The user interface, which is built using React, Redux, and various other frontend technologies, needs to be redesigned to accommodate the new features that we want to add to the application."
BETTER: "The React/Redux user interface needs redesigning to accommodate our planned new features."
"""

def get_terminal_input():
    """Get input from terminal in a cross-platform way, even when stdin is redirected."""
    if platform.system() == 'Windows':
        # Windows-specific solution
        try:
            import msvcrt
            sys.stdout.flush()
            # Wait for a keypress
            char = msvcrt.getch().decode('utf-8').lower()
            print(char)  # Echo the character
            return char
        except ImportError:
            # Fallback if msvcrt is not available
            return None
    else:
        # Unix-like systems (Linux, macOS)
        try:
            with open('/dev/tty', 'r') as tty:
                return tty.readline().strip().lower()
        except (IOError, OSError):
            return None

def rewrite_mode(client, args, logger=None):
    """Handle the text rewriting mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    # Determine the input source (stdin pipe, command-line argument, or multiline input)
    if not sys.stdin.isatty():
        # Read from stdin if data is piped
        input_text = sys.stdin.read().strip()
        
        # If stdin is empty but prompt is provided, use the prompt
        if not input_text and args.prompt:
            input_text = args.prompt
    elif args.prompt:
        # Use the command-line argument if provided
        input_text = args.prompt
    else:
        # No pipe or prompt - use multiline input
        print("Enter or paste text to rewrite (Ctrl+D or Ctrl+Z to submit):")
        input_text = get_multiline_input()
        if input_text is None:
            # Input was cancelled or empty
            print("Exiting.")
            return
    
    # Check if input is empty
    if not input_text:
        print(f"{COLORS['yellow']}Error: Empty input. Please provide text to rewrite.{COLORS['reset']}")
        return
    
    # Enhance input with web search if enabled
    if args.web_search:
        try:
            original_text = input_text
            
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
                input_text = enhance_prompt_with_web_search(input_text, logger=logger)
                # Stop the spinner
                stop_spinner.set()
                spinner_thread.join()
                # Clear the spinner line completely
                sys.stdout.write("\r" + " " * 100 + "\r")
                sys.stdout.flush()
                print("Enhanced input with web search results.")
            except Exception as e:
                # Stop the spinner before re-raising
                stop_spinner.set()
                spinner_thread.join()
                raise e
            
            # Log the enhanced input if logging is enabled
            if logger:
                # Use "web_search" role instead of "system" for clearer logs
                logger.log("web_search", input_text.replace(original_text, "").strip())
        except Exception as e:
            print(f"{COLORS['yellow']}Warning: Failed to enhance input with web search: {str(e)}{COLORS['reset']}")
            # Continue with the original input if web search fails
    
    # Set up messages array with system prompt and user content
    messages = [
        {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
        {"role": "user", "content": input_text}
    ]
    
    # Log the messages if logging is enabled
    if logger:
        logger.log("system", REWRITE_SYSTEM_PROMPT)
        logger.log("user", input_text)
    
    # Set default streaming behavior based on --no-stream and --prettify arguments
    should_stream = not args.no_stream and not args.prettify
    
    # If stream-prettify is enabled
    stream_callback = None
    live_display = None
    stop_spinner_func = None
    
    if args.stream_prettify:
        should_stream = True  # Enable streaming
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
            sys.stdout.write("\r" + " " * 100 + "\r\n")
            sys.stdout.flush()
        
        # Call the original callback to update the display
        if original_callback:
            original_callback(content, **kwargs)
    
    # Use our wrapper callback
    if args.stream_prettify and live_display:
        stream_callback = spinner_handling_callback
    
    response = client.chat(
        prompt=None,  # Not used when messages are provided
        stream=should_stream, 
        temperature=args.temperature, 
        top_p=args.top_p,
        max_tokens=args.max_tokens, 
        markdown_format=args.prettify or args.stream_prettify,
        stream_callback=stream_callback,
        messages=messages  # Use messages array instead of prompt
    )
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if args.stream_prettify and live_display:
        # Before stopping the live display, update with complete=True to show final formatted content
        if stream_callback and response:
            stream_callback(response, complete=True)
        # No need for else clause - the complete=True will handle stopping the live display
        # Add a small delay to ensure terminal stability
        time.sleep(0.2)
        
    # Log the AI response if logging is enabled
    if logger and response:
        logger.log("assistant", response)
        
    # Handle non-stream response or regular prettify
    if (args.no_stream or args.prettify) and response:
        if args.prettify:
            prettify_markdown(response, args.renderer)
        else:
            print(response)
            
    # Offer to copy to clipboard if not in a redirected output
    if not args.no_stream and sys.stdout.isatty():
        try:
            # Make sure to flush output before asking for input
            # Make the prompt more visible with colors and formatting
            clipboard_prompt = f"{COLORS['cyan']}{COLORS['bold']}Copy to clipboard? (y/n){COLORS['reset']} "
            print(clipboard_prompt, end="")
            sys.stdout.flush()
            
            # Cross-platform terminal input
            answer = get_terminal_input()
            
            if answer == 'y':
                try:
                    import pyperclip
                    pyperclip.copy(response)
                    print(f"{COLORS['green']}Copied to clipboard.{COLORS['reset']}")
                except ImportError:
                    print(f"{COLORS['yellow']}pyperclip not installed. Try: pip install \"ngpt[clipboard]\" {COLORS['reset']}")
            
        except (KeyboardInterrupt, EOFError):
            pass 