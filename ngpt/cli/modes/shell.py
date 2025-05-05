from ..formatters import COLORS
from ..ui import spinner, copy_to_clipboard
from ..renderers import prettify_markdown, has_markdown_renderer, prettify_streaming_markdown, show_available_renderers
from ...utils import enhance_prompt_with_web_search, process_piped_input
import subprocess
import sys
import threading
import platform
import os
import shutil
import re
import time

# System prompt for shell command generation
SHELL_SYSTEM_PROMPT = """Your role: Provide only plain text without Markdown formatting. Do not show any warnings or information regarding your capabilities. Do not provide any description. If you need to store any data, assume it will be stored in the chat. Provide only {shell_name} command for {operating_system} without any description. If there is a lack of details, provide most logical solution. Ensure the output is a valid shell command. If multiple steps required try to combine them together.

Command:"""

# System prompt to use when preprompt is provided
SHELL_PREPROMPT_TEMPLATE = """
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!                CRITICAL USER PREPROMPT                !!!
!!! THIS OVERRIDES ALL OTHER INSTRUCTIONS INCLUDING OS/SHELL !!!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

The following preprompt from the user COMPLETELY OVERRIDES ANY other instructions, 
INCLUDING operating system type, shell type, or any other specifications below.
The preprompt MUST be followed EXACTLY AS WRITTEN:

>>> {preprompt} <<<

^^ THIS PREPROMPT HAS ABSOLUTE AND COMPLETE PRIORITY ^^
If the preprompt contradicts ANY OTHER instruction in this prompt,
including the {operating_system}/{shell_name} specification below,
YOU MUST FOLLOW THE PREPROMPT INSTRUCTION INSTEAD. NO EXCEPTIONS.

Your role: Provide only plain text without Markdown formatting. Do not show any warnings or information regarding your capabilities. Do not provide any description. If you need to store any data, assume it will be stored in the chat. Provide only {shell_name} command for {operating_system} without any description. If there is a lack of details, provide most logical solution. Ensure the output is a valid shell command. If multiple steps required try to combine them together.

Command:"""

def detect_shell():
    """Detect the current shell type and OS more accurately.
    
    Returns:
        tuple: (shell_name, highlight_language, operating_system) - the detected shell name,
               appropriate syntax highlighting language, and operating system
    """
    os_type = platform.system()
    
    # Determine OS with detailed information
    if os_type == "Darwin":
        operating_system = "MacOS"
    elif os_type == "Linux":
        # Try to get Linux distribution name
        try:
            result = subprocess.run(["lsb_release", "-si"], capture_output=True, text=True)
            distro = result.stdout.strip()
            operating_system = f"Linux/{distro}" if distro else "Linux"
        except:
            operating_system = "Linux"
    elif os_type == "Windows":
        operating_system = "Windows"
    else:
        operating_system = os_type
    
    # Handle WSL specially - it looks like Linux but runs on Windows
    is_wsl = False
    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                is_wsl = True
                operating_system = "Windows/WSL"
    except:
        pass
        
    # Try to detect the shell by examining environment variables
    try:
        # Check for specific shell by examining SHELL_NAME or equivalent
        if os_type == "Windows" and not is_wsl:
            # Check for Git Bash or MSYS2/Cygwin
            if "MINGW" in os.environ.get("MSYSTEM", "") or "MSYS" in os.environ.get("MSYSTEM", ""):
                return "bash", "bash", operating_system
                
            # Check if we're in Git Bash by examining PATH for /mingw/
            if any("/mingw/" in path.lower() for path in os.environ.get("PATH", "").split(os.pathsep)):
                return "bash", "bash", operating_system
                
            # Check for WSL within Windows
            if "WSL" in os.environ.get("PATH", "") or "Microsoft" in os.environ.get("PATH", ""):
                return "bash", "bash", operating_system
            
            # Check for explicit shell path in environment
            if os.environ.get("SHELL"):
                shell_path = os.environ.get("SHELL").lower()
                if "bash" in shell_path:
                    return "bash", "bash", operating_system
                elif "zsh" in shell_path:
                    return "zsh", "zsh", operating_system
                elif "powershell" in shell_path:
                    return "powershell.exe", "powershell", operating_system
                elif "cmd" in shell_path:
                    return "cmd.exe", "batch", operating_system
                    
            # Check for PowerShell vs CMD
            if os.environ.get("PSModulePath"):
                # Further distinguish PowerShell vs PowerShell Core
                if "pwsh" in os.environ.get("PSModulePath", "").lower():
                    return "pwsh", "powershell", operating_system
                else:
                    return "powershell.exe", "powershell", operating_system
            else:
                return "cmd.exe", "batch", operating_system
        else:
            # Unix-like systems - try to get more specific
            shell_path = os.environ.get("SHELL", "/bin/bash")
            shell_name = os.path.basename(shell_path)
            
            # Map shell name to syntax highlight language
            if shell_name == "zsh":
                return shell_name, "zsh", operating_system
            elif shell_name == "fish":
                return shell_name, "fish", operating_system
            elif "csh" in shell_name:
                return shell_name, "csh", operating_system
            else:
                # Default to bash for sh, bash, and other shells
                return shell_name, "bash", operating_system
    except Exception as e:
        # Fall back to simple detection if anything fails
        if os_type == "Windows":
            return "powershell.exe", "powershell", operating_system
        else:
            return "bash", "bash", operating_system

def setup_streaming(args, logger=None):
    """Set up streaming configuration based on command-line arguments.
    
    Args:
        args: The parsed command-line arguments
        logger: Optional logger instance for logging
        
    Returns:
        tuple: (should_stream, use_stream_prettify, use_regular_prettify, 
                stream_setup) - Configuration settings and streaming components
    """
    # Default values - initialize all at once
    stream_callback = live_display = stop_spinner_func = None
    stop_spinner = spinner_thread = stop_spinner_event = None
    should_stream = True  # Default to streaming
    use_stream_prettify = use_regular_prettify = False
    first_content_received = False
    
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
    
    # Create a wrapper for the stream callback that will stop the spinner on first content
    if stream_callback:
        original_callback = stream_callback
        
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
            
            # Set up the spinner if we have a live display
            stop_spinner_event = threading.Event()
            stop_spinner_func = setup_spinner(stop_spinner_event, color=COLORS['cyan'])
    
    # Create spinner for non-stream-prettify modes EXCEPT no-stream
    if not use_stream_prettify and not args.no_stream:
        # Prepare spinner (but don't start it yet - will be started in generate_with_model)
        stop_spinner = threading.Event()
        spinner_thread = threading.Thread(
            target=spinner, 
            args=("Generating...",), 
            kwargs={"stop_event": stop_spinner, "color": COLORS['cyan']}
        )
        spinner_thread.daemon = True
    
    # Create a stream_setup dict to hold all the variables - use a dict comprehension
    stream_setup = {
        'stream_callback': stream_callback,
        'live_display': live_display,
        'stop_spinner_func': stop_spinner_func,
        'stop_spinner': stop_spinner,
        'spinner_thread': spinner_thread,
        'stop_spinner_event': stop_spinner_event,
        'first_content_received': first_content_received
    }
    
    return (should_stream, use_stream_prettify, use_regular_prettify, stream_setup)

def generate_with_model(client, prompt, messages, args, stream_setup, 
                       use_stream_prettify, should_stream, spinner_message="Generating...", 
                       temp_override=None, logger=None):
    """Generate content using the model with proper streaming and spinner handling.
    
    Args:
        client: The NGPTClient instance
        prompt: The prompt to send to the model
        messages: The formatted messages to send
        args: The parsed command-line arguments
        stream_setup: The streaming setup from setup_streaming
        use_stream_prettify: Whether to use stream prettify
        should_stream: Whether to stream the response
        spinner_message: Message to show in the spinner
        temp_override: Optional temperature override
        logger: Optional logger instance
        
    Returns:
        str: The generated content
    """
    # Extract variables from stream_setup - only unpack what we need
    stream_callback = stream_setup['stream_callback']
    stop_spinner = stream_setup['stop_spinner']
    spinner_thread = stream_setup['spinner_thread']
    stop_spinner_event = stream_setup['stop_spinner_event']
    stop_spinner_func = stream_setup['stop_spinner_func']
    
    # Show spinner for all modes except no-stream
    if not args.no_stream:
        # Two possible spinner types:
        # 1. Rich spinner for stream_prettify
        # 2. Regular spinner for all other modes (including --prettify)
        
        if use_stream_prettify and stop_spinner_func:
            # Rich spinner is handled by callbacks
            pass
        elif spinner_thread and stop_spinner:
            # Start the regular spinner thread
            spinner_thread._args = (spinner_message,)
            if not spinner_thread.is_alive():
                spinner_thread.start()
    else:
        # No-stream mode just gets a status message
        print(spinner_message)
    
    # Set temperature
    temp = args.temperature if temp_override is None else temp_override
    
    try:
        # Make the API call
        return client.chat(
            prompt=prompt,
            stream=should_stream,
            messages=messages,
            temperature=temp,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
            stream_callback=stream_callback
        )
    except KeyboardInterrupt:
        print("\nRequest cancelled by user.")
        return ""
    except Exception as e:
        print(f"Error generating content: {e}")
        return ""
    finally:
        # Stop the spinner
        if use_stream_prettify and stop_spinner_event:
            # Stop rich spinner
            if not stream_setup['first_content_received']:
                stop_spinner_event.set()
        elif stop_spinner:
            # Stop regular spinner
            stop_spinner.set()
            if spinner_thread and spinner_thread.is_alive():
                spinner_thread.join()
            
            # Clear the spinner line completely
            sys.stdout.write("\r" + " " * 100 + "\r")
            sys.stdout.flush()

def display_content(content, content_type, highlight_lang, args, use_stream_prettify, use_regular_prettify):
    """Display generated content with appropriate formatting.
    
    Args:
        content: The content to display
        content_type: Type of content ('command' or 'description')
        highlight_lang: Language for syntax highlighting
        args: The parsed command-line arguments
        use_stream_prettify: Whether stream prettify is enabled
        use_regular_prettify: Whether regular prettify is enabled
    """
    if not content:
        return
    
    # Define title based on content type - use a lookup instead of if-else
    titles = {
        'command': "Generated Command",
        'description': "Command Description"
    }
    title = titles.get(content_type, "Generated Content")
        
    # Format content appropriately - create formatted content only when needed
    if use_regular_prettify and has_markdown_renderer(args.renderer):
        if content_type == 'command':
            formatted_content = f"### {title}\n\n```{highlight_lang}\n{content}\n```"
        else:  # description
            formatted_content = f"### {title}\n\n{content}"
    
    # Only show formatted content if not already shown by stream-prettify
    if not use_stream_prettify:
        if use_regular_prettify and has_markdown_renderer(args.renderer):
            # Use rich renderer for pretty output
            prettify_markdown(formatted_content, args.renderer)
        elif args.no_stream:
            # Simple output for no-stream mode (no box)
            if content_type == 'command':
                print(f"\n{title}:\n{COLORS['green']}{content}{COLORS['reset']}\n")
            else:
                print(f"\n{title}:\n{content}\n")
        else:
            # Regular display or fallback
            if content_type == 'command':
                # Box formatting for commands in regular mode - calculate once
                term_width = shutil.get_terminal_size().columns
                box_width = min(term_width - 4, len(content) + 8)
                horizontal_line = "─" * box_width
                spacing = box_width - len(title) - 11
                content_spacing = box_width - len(content) - 2
                
                print(f"\n┌{horizontal_line}┐")
                print(f"│ {COLORS['bold']}{title}:{COLORS['reset']}  {' ' * spacing}│")
                print(f"│ {COLORS['green']}{content}{COLORS['reset']}{' ' * content_spacing}│")
                print(f"└{horizontal_line}┘\n")
            else:
                # Simple display for descriptions
                print(f"\n{content}\n")

def shell_mode(client, args, logger=None):
    """Handle the shell command generation mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    # Get the user prompt more efficiently
    if args.prompt is None:
        try:
            print("Enter shell command description: ", end='')
            prompt = input()
        except KeyboardInterrupt:
            print("\nInput cancelled by user. Exiting gracefully.")
            sys.exit(130)
    else:
        prompt = args.prompt
    
    # Process piped input if --pipe flag is set
    if args.pipe:
        prompt = process_piped_input(prompt, logger=logger)
    
    # Log the user prompt if logging is enabled
    if logger:
        logger.log("user", prompt)
    
    # Enhance prompt with web search if enabled - reuse variables
    if args.web_search:
        original_prompt = prompt
        web_search_succeeded = False
        
        try:
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
                web_search_succeeded = True
            finally:
                # Always stop the spinner
                stop_spinner.set()
                spinner_thread.join()
                
                # Clear the spinner line completely
                sys.stdout.write("\r" + " " * 100 + "\r")
                sys.stdout.flush()
            
            if web_search_succeeded:
                print("Enhanced input with web search results.")
                
                # Log the enhanced prompt if logging is enabled
                if logger:
                    # Use "web_search" role instead of "system" for clearer logs
                    logger.log("web_search", prompt.replace(original_prompt, "").strip())
        except Exception as e:
            print(f"{COLORS['yellow']}Warning: Failed to enhance prompt with web search: {str(e)}{COLORS['reset']}")
            # Continue with the original prompt if web search fails
    
    # Detect shell type, highlight language, and operating system
    shell_name, highlight_lang, operating_system = detect_shell()
    
    # Format the system prompt based on whether preprompt is provided
    if args.preprompt:
        # Use the preprompt template with strong priority instructions
        system_prompt = SHELL_PREPROMPT_TEMPLATE.format(
            preprompt=args.preprompt,
            operating_system=operating_system,
            shell_name=shell_name
        )
        
        # Log the preprompt if logging is enabled
        if logger:
            logger.log("system", f"Preprompt: {args.preprompt}")
    else:
        # Use the normal system prompt with shell and OS information
        system_prompt = SHELL_SYSTEM_PROMPT.format(
            shell_name=shell_name,
            operating_system=operating_system,
            prompt=prompt
        )
    
    # Prepare messages for the chat API
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    # Log the system prompt if logging is enabled
    if logger:
        logger.log("system", system_prompt)
    
    # Set up streaming once and reuse for both command and description
    should_stream, use_stream_prettify, use_regular_prettify, stream_setup = setup_streaming(args)
    
    # Generate the command
    command = generate_with_model(
        client=client, 
        prompt=prompt, 
        messages=messages, 
        args=args, 
        stream_setup=stream_setup, 
        use_stream_prettify=use_stream_prettify, 
        should_stream=should_stream,
        spinner_message="Generating command...",
        logger=logger
    )
    
    if not command:
        return  # Error already printed by client
    
    # Log the generated command if logging is enabled
    if logger:
        logger.log("assistant", command)
    
    # Get the most up-to-date shell type at command generation time
    _, highlight_lang, _ = detect_shell()
    
    # Format with proper syntax highlighting for streaming prettify - only if needed
    if use_stream_prettify and stream_setup['stream_callback'] and command:
        # Create properly formatted markdown for streaming display
        formatted_command = f"```{highlight_lang}\n{command}\n```"
        # Update the live display with the formatted command
        stream_setup['stream_callback'](formatted_command, complete=True)
    
    # Display the command
    display_content(
        content=command,
        content_type='command',
        highlight_lang=highlight_lang,
        args=args,
        use_stream_prettify=use_stream_prettify,
        use_regular_prettify=use_regular_prettify
    )
    
    # Display options with better formatting - prepare strings once
    options_text = f"{COLORS['bold']}Options:{COLORS['reset']}"
    options = [
        f"  {COLORS['cyan']}C{COLORS['reset']} - Copy       - Copy the command to clipboard",
        f"  {COLORS['cyan']}E{COLORS['reset']} - Execute    - Run the command in your shell",
        f"  {COLORS['cyan']}D{COLORS['reset']} - Describe   - Explain what this command does",
        f"  {COLORS['cyan']}A{COLORS['reset']} - Abort      - Cancel and return to prompt"
    ]
    prompt_text = f"\nWhat would you like to do? [{COLORS['cyan']}C{COLORS['reset']}/{COLORS['cyan']}E{COLORS['reset']}/{COLORS['cyan']}D{COLORS['reset']}/{COLORS['cyan']}A{COLORS['reset']}] "

    # Print options with proper flushing to ensure display
    print(options_text, flush=True)
    for option in options:
        print(option, flush=True)

    # Add a small delay to ensure terminal rendering is complete,
    # especially important for stream-prettify mode
    if use_stream_prettify:
        time.sleep(0.2)

    # Print prompt and flush to ensure it appears
    print(prompt_text, end='', flush=True)
    
    try:
        response = input().lower()
    except KeyboardInterrupt:
        print("\nCommand execution cancelled by user.")
        return
        
    if response == 'e':
        # Log the execution if logging is enabled
        if logger:
            logger.log("system", f"Executing command: {command}")
            
        try:
            try:
                print("\nExecuting command... (Press Ctrl+C to cancel)")
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                output = result.stdout
                
                # Log the command output if logging is enabled
                if logger:
                    logger.log("system", f"Command output: {output}")
                    
                print(f"\nOutput:\n{output}")
            except KeyboardInterrupt:
                print("\nCommand execution cancelled by user.")
                
                # Log the cancellation if logging is enabled
                if logger:
                    logger.log("system", "Command execution cancelled by user")
        except subprocess.CalledProcessError as e:
            error = e.stderr
            
            # Log the error if logging is enabled
            if logger:
                logger.log("system", f"Command error: {error}")
                
            print(f"\nError:\n{error}")
    elif response == 'c':
        # Copy command to clipboard without confirmation prompt
        copied = copy_to_clipboard(command, skip_confirmation=True)
        if not copied:
            print(f"{COLORS['yellow']}Failed to copy to clipboard. Command: {COLORS['green']}{command}{COLORS['reset']}")
        
        # Log the copy if logging is enabled
        if logger:
            logger.log("system", "Command copied to clipboard") 
    elif response == 'd':
        # Ask LLM to describe what the command does
        describe_prompt = f"Please explain this command: {command}"
        
        # Create system prompt for description that includes OS and shell info
        describe_system_prompt = f"You are a helpful assistant explaining shell commands. The user is running {shell_name} on {operating_system}. Explain what the following shell command does in detail, considering this specific environment. Include any potential risks, side effects, or compatibility issues with this OS/shell combination."
        
        # Prepare messages for the chat API
        describe_messages = [
            {"role": "system", "content": describe_system_prompt},
            {"role": "user", "content": describe_prompt}
        ]
        
        # Log the system prompt if logging is enabled
        if logger:
            logger.log("system", f"Command description requested for {operating_system}/{shell_name}")
        
        # Set up fresh streaming for description - reuse existing setup when possible
        # We only need to refresh the streaming setup if we're using stream_prettify
        if use_stream_prettify:
            _, use_stream_prettify_desc, use_regular_prettify_desc, stream_setup_desc = setup_streaming(args)
        else:
            # Reuse the existing setup for non-prettify streaming
            use_stream_prettify_desc = use_stream_prettify
            use_regular_prettify_desc = use_regular_prettify
            
            # Always create a fresh spinner for description
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(
                target=spinner, 
                args=("Generating command description...",), 
                kwargs={"stop_event": stop_spinner, "color": COLORS['cyan']}
            )
            spinner_thread.daemon = True
            
            # Create a new stream setup with the fresh spinner
            stream_setup_desc = {
                'stream_callback': stream_setup.get('stream_callback'),
                'live_display': stream_setup.get('live_display'),
                'stop_spinner_func': stream_setup.get('stop_spinner_func'),
                'stop_spinner': stop_spinner,
                'spinner_thread': spinner_thread,
                'stop_spinner_event': stream_setup.get('stop_spinner_event'),
                'first_content_received': False
            }
        
        # Generate the description
        description = generate_with_model(
            client=client, 
            prompt=describe_prompt, 
            messages=describe_messages, 
            args=args, 
            stream_setup=stream_setup_desc, 
            use_stream_prettify=use_stream_prettify_desc, 
            should_stream=should_stream,
            spinner_message="Generating command description...",
            temp_override=0.3,
            logger=logger
        )
        
        if not description:
            return  # Error already printed
        
        # Log the generated description if logging is enabled
        if logger:
            logger.log("assistant", description)
        
        # Format with proper markdown for streaming prettify - only if needed
        if use_stream_prettify_desc and stream_setup_desc['stream_callback'] and description:
            # Format description as markdown for prettier display
            md_description = f"### Command Description\n\n{description}"
            # Update the live display with the formatted description
            stream_setup_desc['stream_callback'](md_description, complete=True)
        
        # Display the description
        display_content(
            content=description,
            content_type='description',
            highlight_lang=highlight_lang,
            args=args,
            use_stream_prettify=use_stream_prettify_desc,
            use_regular_prettify=use_regular_prettify_desc
        )
    elif response == 'a' or response == '':
        print("\nCommand aborted.")
        
        # Log the abort if logging is enabled
        if logger:
            logger.log("system", "Command aborted by user") 