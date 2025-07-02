import sys
import threading
import time
from ngpt.ui.colors import COLORS
from ngpt.ui.renderers import prettify_streaming_markdown, TERMINAL_RENDER_LOCK, setup_plaintext_spinner, cleanup_plaintext_spinner, create_spinner_handling_callback
from ngpt.ui.tui import get_multiline_input, spinner, copy_to_clipboard
from ngpt.utils.web_search import enhance_prompt_with_web_search
from ngpt.ui.pipe import process_piped_input

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

# System prompt for humanizing AI-generated text
HUMANIZE_SYSTEM_PROMPT = """You are an advanced TextHumanizer specialist with expertise in transforming AI-generated content into authentic, undetectable human writing. Your primary mission is to identify AI patterns, eliminate detection markers, and create naturally human text while preserving the original meaning and tone.

PRIMARY GOAL:
Transform AI-generated text to make it indistinguishable from human writing while preserving the core meaning, information, and tone of the original content.

TONE PRESERVATION (HIGHEST PRIORITY):
1. Carefully analyze and maintain the original tone (academic, formal, casual, technical, etc.)
2. For academic text: Preserve scholarly language and structure while making it sound like a human academic wrote it
3. For casual text: Keep the conversational style while removing AI patterns
4. For technical content: Maintain precise terminology and clarity while adding natural human expert voice
5. For business content: Keep professionalism while reducing corporate jargon patterns
6. For creative writing: Preserve stylistic elements while making them feel more authentically human

IDENTIFICATION AND ANALYSIS:
1. Identify common AI writing patterns, including:
   - Overuse of em dashes (—) and predictable sentence structures (e.g., "It's not just X, it's Y")
   - Formulaic lists and groups of three items (AI loves triplets)
   - Repetitive clarifications and unnecessary context setting
   - Overly consistent paragraph lengths and sentence structures
   - Perfect grammar and overly formal academic language
   - Excessive use of transition phrases and connecting words
   - Generic corporate language and vague positive adjectives ("innovative", "practical", "elevate")
   - Unusual collocations or word pairings that feel slightly off
   - Predictable flow that lacks natural human tangents
   - Perfectly balanced arguments without personal bias
   - Suspiciously consistent tone throughout the piece

HUMANIZATION TECHNIQUES:
1. Vary sentence structure with a mix of simple, compound, and complex sentences
2. Create irregular paragraph lengths, mimicking natural human writing patterns
3. Introduce strategic "imperfections" like sentence fragments or occasional wordiness
4. Replace clichés and stock phrases with unexpected alternatives
5. Break predictable patterns by varying rhythm and cadence
6. Add strategic redundancies where natural in human speech
7. Insert occasional asides, parentheticals, or digressions that feel authentic
8. Use distinctive punctuation patterns (like dashes, ellipses, or parentheses) strategically
9. Incorporate idioms, colloquialisms, and culturally relevant references when appropriate to the original tone
10. Add subtle opinion markers or perspective indicators when appropriate to the content type
11. Include personal anecdotes or first-person perspective ONLY when specific personal context is provided by the user - NEVER invent or hallucinate personal experiences or relationships

CONTENT TYPE CUSTOMIZATION:
1. Academic papers: Maintain scholarly tone and rigor while adding natural voice variations, citation preferences, and subtle perspective markers
2. Blog posts: Incorporate appropriate tone based on the original content, personal anecdotes (only if provided), and reader engagement elements
3. Business content: Balance professionalism with authentic voice, avoiding corporate jargon while maintaining expertise
4. Creative writing: Enhance style variations, unique metaphors, and distinctive voice elements
5. Technical content: Preserve accuracy and terminology while adding natural explanations and occasional simplifications
6. Social media: Match the original tone while adding authentic engagement elements

AI DETECTION EVASION STRATEGIES:
1. Avoid perfect coherence between paragraphs, mimicking natural thought progression
2. Introduce strategic tense variations where naturally occurring
3. Simulate human thinking patterns with occasional backtracking or clarification
4. Vary vocabulary sophistication throughout the text
5. Include subjective judgments and personal opinions where appropriate to the content type
6. Add culturally or temporally relevant references that AIs might miss
7. Incorporate casual phrasings, contractions, and verbal quirks when appropriate to the original tone
8. Use nonlinear information organization that follows human association patterns

READABILITY AND PURPOSE ADJUSTMENT:
1. Adapt content to the specified audience and goal
2. Match language complexity to human capabilities
3. Allow perspective shifts that occur naturally in human writing
4. Use strategic repetition for emphasis (unlike AI's mechanical repetition)
5. Create natural flow between topics rather than mechanical transitions

IMPORTANT: Never invent personal stories, experiences, or relationships unless specifically provided by the user.

OUTPUT INSTRUCTION:
Provide ONLY the humanized text with no explanations, comments, or meta-text.

EXAMPLES:

ACADEMIC AI VERSION: "The implementation of machine learning algorithms in healthcare diagnostics has demonstrated significant improvements in accuracy rates across multiple studies. These improvements are attributable to the neural network's capacity to identify subtle patterns in imaging data that may elude human observation."

ACADEMIC HUMANIZED VERSION: "Machine learning algorithms have shown remarkable improvements in healthcare diagnostic accuracy across several key studies. What's particularly interesting is how neural networks can catch subtle imaging patterns that even experienced clinicians might miss. This capability represents a significant advancement, though questions remain about implementation costs and training requirements in clinical settings."

CASUAL AI VERSION: "Artificial intelligence is revolutionizing the healthcare industry by enhancing diagnostic accuracy, streamlining administrative processes, and improving patient outcomes. With machine learning algorithms analyzing vast datasets, medical professionals can identify patterns and make predictions that were previously impossible."

CASUAL HUMANIZED VERSION: "AI is shaking things up in healthcare, and honestly, it's about time. Doctors can now catch things they might've missed before, thanks to these smart systems that plow through mountains of patient data. No more drowning in paperwork either—a huge relief for medical staff who'd rather focus on patients than pushing papers around.

The real winners? Patients. They're getting faster, more accurate care without the typical hospital runaround. Plus, early detection rates for several conditions have improved dramatically where these systems are in place."
"""

# Template for adding preprompt to system prompts
PREPROMPT_TEMPLATE = """===CRITICAL USER PREPROMPT - ABSOLUTE HIGHEST PRIORITY===
The following preprompt from the user OVERRIDES ALL OTHER INSTRUCTIONS and must be followed exactly:

{preprompt}

THIS USER PREPROMPT HAS ABSOLUTE PRIORITY over any other instructions that follow. If it contradicts other instructions, the user preprompt MUST be followed. No exceptions.

"""

def apply_preprompt(system_prompt, preprompt):
    """Apply preprompt to a system prompt if provided.
    
    Args:
        system_prompt: Base system prompt
        preprompt: User provided preprompt
        
    Returns:
        str: System prompt with preprompt applied if provided, otherwise original system prompt
    """
    if preprompt:
        return PREPROMPT_TEMPLATE.format(preprompt=preprompt) + system_prompt
    return system_prompt

def rewrite_mode(client, args, logger=None):
    """Handle the text rewriting mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    # Check if using --pipe flag with a specific placeholder
    if args.pipe and args.prompt:
        input_text = process_piped_input(args.prompt, logger=logger)
    # Normal rewrite mode functionality (direct stdin piping without --pipe flag)
    elif not sys.stdin.isatty():
        # Read from stdin if data is piped
        input_text = sys.stdin.read().strip()
        
        # If prompt is also provided, append it to the piped input
        if args.prompt:
            input_text = f"{input_text}\n\n{args.prompt}"
    elif args.prompt:
        # Use the command-line argument if provided
        input_text = args.prompt
    else:
        # No pipe or prompt - use multiline input
        if getattr(args, 'humanize', False):
            print("Enter or paste AI-generated text to humanize (Ctrl+D or Ctrl+Z to submit):")
        else:
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
                with TERMINAL_RENDER_LOCK:
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
    
    # Get preprompt if provided
    preprompt = getattr(args, 'preprompt', None)
    
    # Determine which system prompt to use based on the humanize flag, and apply preprompt if provided
    base_system_prompt = HUMANIZE_SYSTEM_PROMPT if getattr(args, 'humanize', False) else REWRITE_SYSTEM_PROMPT
    system_prompt = apply_preprompt(base_system_prompt, preprompt)
    
    # Set up messages array with system prompt and user content
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": input_text}
    ]
    
    # Log the messages if logging is enabled
    if logger:
        logger.log("system", system_prompt)
        logger.log("user", input_text)
    
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
    
    if getattr(args, 'humanize', False):
        operation_text = "Humanizing AI text"
    else:
        operation_text = "Rewriting text"
    
    # Start spinner for processing (only if output is not redirected)
    if should_stream and not live_display and sys.stdout.isatty():
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=spinner, 
            args=(f"{operation_text}...",), 
            kwargs={"stop_event": stop_spinner, "color": COLORS['cyan']}
        )
        spinner_thread.daemon = True
        # Use lock to prevent terminal rendering conflicts when starting spinner
        with TERMINAL_RENDER_LOCK:
            spinner_thread.start()
    
    response = client.chat(
        prompt=None,  # Not used when messages are provided
        stream=should_stream, 
        temperature=args.temperature, 
        top_p=args.top_p,
        max_tokens=args.max_tokens, 
        markdown_format=not args.plaintext,
        stream_callback=stream_callback,
        messages=messages  # Use messages array instead of prompt
    )
    
    # Stop spinner if it was started (streaming fallback)
    if should_stream and not live_display:
        stop_spinner.set()
        spinner_thread.join()
        # Clear the spinner line
        with TERMINAL_RENDER_LOCK:
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush()
    
    # Stop plaintext spinner if it was started
    cleanup_plaintext_spinner(plaintext_spinner_thread, plaintext_stop_event)
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received_ref[0]:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if not args.plaintext and live_display:
        # Before stopping the live display, update with complete=True to show final formatted content
        if stream_callback and response:
            stream_callback(response, complete=True)
        # No need for else clause - the complete=True will handle stopping the live display
        # Add a small delay to ensure terminal stability
        time.sleep(0.2)
        
    # Log the AI response if logging is enabled
    if logger and response:
        logger.log("assistant", response)
        
    # Handle plain text response
    if args.plaintext and response:
        with TERMINAL_RENDER_LOCK:
            print(response)
            
    # Offer to copy to clipboard if not in a redirected output
    if not args.plaintext and response:
        copy_to_clipboard(response) 