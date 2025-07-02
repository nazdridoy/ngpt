from ngpt.ui.colors import COLORS
from ngpt.ui.renderers import prettify_streaming_markdown, TERMINAL_RENDER_LOCK, setup_plaintext_spinner, cleanup_plaintext_spinner, create_spinner_handling_callback
from ngpt.ui.tui import spinner, copy_to_clipboard, get_terminal_input
from ngpt.utils.web_search import enhance_prompt_with_web_search
from ngpt.ui.pipe import process_piped_input
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

*** SHELL TYPE: {shell_name} ***
*** OS: {operating_system} ***

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

*** SHELL TYPE: {shell_name} ***
*** OS: {operating_system} ***

Your role: Provide only plain text without Markdown formatting. Do not show any warnings or information regarding your capabilities. Do not provide any description. If you need to store any data, assume it will be stored in the chat. Provide only {shell_name} command for {operating_system} without any description. If there is a lack of details, provide most logical solution. Ensure the output is a valid shell command. If multiple steps required try to combine them together.

Command:"""

def detect_os():
    """Detect the current operating system with detailed information.
    
    Returns:
        tuple: (os_type, operating_system) - the basic OS type and detailed OS description
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
        
    return os_type, operating_system, is_wsl


def detect_gitbash_shell(operating_system):
    """Detect if we're running in a Git Bash / MINGW environment.
    
    Args:
        operating_system: The detected operating system string
        
    Returns:
        tuple or None: (shell_name, highlight_language, operating_system) if Git Bash detected,
                       None otherwise
    """
    # Check for Git Bash / MINGW environments 
    if any(env_var in os.environ for env_var in ["MSYSTEM", "MINGW_PREFIX"]):
        # We're definitely in a MINGW environment (Git Bash)
        return "bash", "bash", operating_system
        
    if "MSYSTEM" in os.environ and any(msys_type in os.environ.get("MSYSTEM", "") 
                                      for msys_type in ["MINGW", "MSYS"]):
        return "bash", "bash", operating_system
        
    # Check command PATH for mingw
    if os.environ.get("PATH") and any(
            mingw_pattern in path.lower() 
            for mingw_pattern in ["/mingw/", "\\mingw\\", "/usr/bin", "\\usr\\bin"] 
            for path in os.environ.get("PATH", "").split(os.pathsep)
    ):
        return "bash", "bash", operating_system
        
    return None


def detect_unix_shell(operating_system):
    """Detect shell type on Unix-like systems (Linux, macOS, BSD).
    
    Args:
        operating_system: The detected operating system string
        
    Returns:
        tuple: (shell_name, highlight_language, operating_system) - the detected shell information
    """
    # Try multiple methods to detect the shell
    
    # Method 1: Check shell-specific environment variables
    # These are very reliable indicators of the actual shell
    if "BASH_VERSION" in os.environ:
        return "bash", "bash", operating_system
        
    if "ZSH_VERSION" in os.environ:
        return "zsh", "zsh", operating_system
        
    if "FISH_VERSION" in os.environ:
        return "fish", "fish", operating_system
    
    # Method 2: Try to get shell from process information
    try:
        # Try to get parent process name using ps command
        current_pid = os.getpid()
        parent_pid = os.getppid()
        
        # Method 2a: Try to get the parent process command line from /proc
        try:
            with open(f'/proc/{parent_pid}/cmdline', 'r') as f:
                cmdline = f.read().split('\0')
                if cmdline and cmdline[0]:
                    cmd = os.path.basename(cmdline[0])
                    if "zsh" in cmd:
                        return "zsh", "zsh", operating_system
                    elif "bash" in cmd:
                        return "bash", "bash", operating_system
                    elif "fish" in cmd:
                        return "fish", "fish", operating_system
        except:
            pass
        
        # Method 2b: Try using ps command with different formats
        for fmt in ["comm=", "command=", "args="]:
            try:
                ps_cmd = ["ps", "-p", str(parent_pid), "-o", fmt]
                result = subprocess.run(ps_cmd, capture_output=True, text=True)
                process_info = result.stdout.strip()
                
                if process_info:
                    if "zsh" in process_info.lower():
                        return "zsh", "zsh", operating_system
                    elif "bash" in process_info.lower():
                        return "bash", "bash", operating_system
                    elif "fish" in process_info.lower():
                        return "fish", "fish", operating_system
                    elif any(sh in process_info.lower() for sh in ["csh", "tcsh"]):
                        shell_name = "csh" if "csh" in process_info.lower() else "tcsh"
                        return shell_name, "csh", operating_system
                    elif "ksh" in process_info.lower():
                        return "ksh", "ksh", operating_system
            except:
                continue
        
        # Method 2c: Try to find parent shell by traversing process hierarchy
        # This handles Python wrappers, uv run, etc.
        for _ in range(5):  # Check up to 5 levels up the process tree
            try:
                # Try to get process command
                ps_cmd = ["ps", "-p", str(parent_pid), "-o", "comm="]
                result = subprocess.run(ps_cmd, capture_output=True, text=True)
                process_name = result.stdout.strip()
                
                # If it's a known shell, return it
                if process_name:
                    process_basename = os.path.basename(process_name)
                    if "bash" in process_basename:
                        return "bash", "bash", operating_system
                    elif "zsh" in process_basename:
                        return "zsh", "zsh", operating_system
                    elif "fish" in process_basename:
                        return "fish", "fish", operating_system
                    elif any(sh in process_basename for sh in ["csh", "tcsh"]):
                        return process_basename, "csh", operating_system
                    elif "ksh" in process_basename:
                        return process_basename, "ksh", operating_system
                
                # Check if we've reached init/systemd (PID 1)
                if parent_pid <= 1:
                    break
                    
                # Move up to next parent
                try:
                    # Get the parent of our current parent
                    with open(f'/proc/{parent_pid}/status', 'r') as f:
                        for line in f:
                            if line.startswith('PPid:'):
                                parent_pid = int(line.split()[1])
                                break
                except:
                    break  # Can't determine next parent, stop here
            except:
                break
    except:
        # Process detection failed, continue with other methods
        pass
        
    # Method 3: Try running a command that prints info about the parent shell
    try:
        # Get parent's process ID and use it to get more info
        cmd = f"ps -p $PPID -o cmd="
        result = subprocess.run(['bash', '-c', cmd], capture_output=True, text=True, timeout=1)
        parent_cmd = result.stdout.strip()
        
        if "zsh" in parent_cmd.lower():
            return "zsh", "zsh", operating_system
        elif "bash" in parent_cmd.lower():
            return "bash", "bash", operating_system
        elif "fish" in parent_cmd.lower():
            return "fish", "fish", operating_system
    except:
        pass
    
    # Method 4: Check for shell-specific environment variables beyond the basic ones
    try:
        for env_var in os.environ:
            if env_var.startswith("BASH_"):
                return "bash", "bash", operating_system
            elif env_var.startswith("ZSH_"):
                return "zsh", "zsh", operating_system
            elif env_var.startswith("FISH_"):
                return "fish", "fish", operating_system
    except:
        pass
    
    # Method 5: Check SHELL environment variable 
    if os.environ.get("SHELL"):
        shell_path = os.environ.get("SHELL")
        shell_name = os.path.basename(shell_path)
        
        # Match against known shell types - use exact matches first
        if shell_name == "zsh":
            return "zsh", "zsh", operating_system
        elif shell_name == "bash":
            return "bash", "bash", operating_system
        elif shell_name == "fish":
            return "fish", "fish", operating_system
        elif shell_name in ["csh", "tcsh"]:
            return shell_name, "csh", operating_system
        elif shell_name == "ksh":
            return shell_name, "ksh", operating_system
            
        # If no exact match, try substring
        if "zsh" in shell_name:
            return "zsh", "zsh", operating_system
        elif "bash" in shell_name:
            return "bash", "bash", operating_system
        elif "fish" in shell_name:
            return "fish", "fish", operating_system
        elif any(sh in shell_name for sh in ["csh", "tcsh"]):
            return shell_name, "csh", operating_system
        elif "ksh" in shell_name:
            return shell_name, "ksh", operating_system
    
    # Fallback: default to bash for Unix-like systems if all else fails
    return "bash", "bash", operating_system


def detect_windows_shell(operating_system):
    """Detect shell type on Windows systems.
    
    Args:
        operating_system: The detected operating system string
        
    Returns:
        tuple: (shell_name, highlight_language, operating_system) - the detected shell information
    """
    # Check for WSL within Windows first
    if any(("wsl" in path.lower() or "microsoft" in path.lower()) for path in os.environ.get("PATH", "").split(os.pathsep)):
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
    
    # Check environment variables that strongly indicate shell type
    if "PROMPT" in os.environ and "$P$G" in os.environ.get("PROMPT", ""):
        # CMD.exe uses $P$G as default prompt
        return "cmd.exe", "batch", operating_system
    
    if os.environ.get("PSModulePath"):
        # PowerShell has this environment variable
        if "pwsh" in os.environ.get("PSModulePath", "").lower():
            return "pwsh", "powershell", operating_system
        else:
            return "powershell.exe", "powershell", operating_system
    
    # Check ComSpec environment variable
    if "ComSpec" in os.environ:
        comspec = os.environ.get("ComSpec", "").lower()
        if "powershell" in comspec:
            return "powershell.exe", "powershell", operating_system
        elif "cmd.exe" in comspec:
            return "cmd.exe", "batch", operating_system
    
    # Last resort fallback to PowerShell (most common modern Windows shell)
    return "powershell.exe", "powershell", operating_system


def detect_shell():
    """Detect the current shell type and OS more accurately.
    
    Returns:
        tuple: (shell_name, highlight_language, operating_system) - the detected shell name,
               appropriate syntax highlighting language, and operating system
    """
    try:
        # First detect the OS
        os_type, operating_system, is_wsl = detect_os()
        
        # Use the appropriate detection method based on OS
        if os_type in ["Linux", "Darwin", "FreeBSD"] or is_wsl:
            return detect_unix_shell(operating_system)
        elif os_type == "Windows":
            # On Windows, first check for Git Bash / MINGW environment
            gitbash_result = detect_gitbash_shell(operating_system)
            if gitbash_result:
                return gitbash_result
                
            # If not Git Bash, use regular Windows shell detection
            return detect_windows_shell(operating_system)
        else:
            # Fallback for unknown OS types
            if os_type == "Windows":
                return "powershell.exe", "powershell", operating_system
            else:
                return "bash", "bash", operating_system
    except Exception as e:
        # Fall back to simple detection if anything fails
        os_type = platform.system()
        operating_system = os_type
        if os_type == "Windows":
            return "powershell.exe", "powershell", operating_system
        else:
            return "bash", "bash", operating_system


def shell_mode(client, args, logger=None):
    """Handle the shell command generation mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    # Get the user prompt
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
    
    # Set up display mode based on args (unified pattern)
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
        plaintext_spinner_thread, plaintext_stop_event = setup_plaintext_spinner("Generating command...", COLORS['cyan'])
    else:
        # Default stream-prettify mode - stream with live markdown rendering
        live_display, stream_callback, setup_spinner = prettify_streaming_markdown()
        if not live_display:
            # Fallback if display creation fails
            print(f"{COLORS['yellow']}Warning: Live display setup failed. Falling back to plain streaming.{COLORS['reset']}")
    
    # Set up the spinner if we have a live display and stream-prettify is enabled
    if should_stream and not args.plaintext and live_display:
        stop_spinner_event = threading.Event()
        stop_spinner_func = setup_spinner(stop_spinner_event, color=COLORS['cyan'])
    
    # Create a wrapper for the stream callback that handles spinner
    if stream_callback:
        original_callback = stream_callback
        first_content_received_ref = [first_content_received]
        stream_callback = create_spinner_handling_callback(original_callback, stop_spinner_func, first_content_received_ref)
    
    # Generate the command
    try:
        command = client.chat(prompt, stream=should_stream,
                           temperature=args.temperature, top_p=args.top_p,
                           max_tokens=args.max_tokens, messages=messages,
                           markdown_format=not args.plaintext,
                           stream_callback=stream_callback)
    except KeyboardInterrupt:
        print("\nRequest cancelled by user.")
        return
    except Exception as e:
        print(f"Error generating content: {e}")
        return
    
    # Stop plaintext spinner if it was started
    cleanup_plaintext_spinner(plaintext_spinner_thread, plaintext_stop_event)
    
    # Ensure spinner is stopped if no content was received
    if stop_spinner_event and not first_content_received_ref[0]:
        stop_spinner_event.set()
    
    # Stop live display if using stream-prettify
    if not args.plaintext and live_display:
        # Before stopping the live display, update with complete=True to show final formatted content
        if stream_callback and command:
            # Format command with syntax highlighting for streaming display
            formatted_command = f"```{highlight_lang}\n{command}\n```"
            stream_callback(formatted_command, complete=True)
    
    # Log the generated command if logging is enabled
    if logger and command:
        logger.log("assistant", command)
    
    # Handle plain text response
    if args.plaintext and command:
        with TERMINAL_RENDER_LOCK:
            print(command)
    
    # Skip interactive options if output is redirected (not a terminal)
    if not sys.stdout.isatty():
        return
    
    # Display options with better formatting
    options_text = f"{COLORS['bold']}Options:{COLORS['reset']}"
    options = [
        f"  {COLORS['cyan']}C{COLORS['reset']} - Copy       - Copy the command to clipboard",
        f"  {COLORS['cyan']}E{COLORS['reset']} - Execute    - Run the command in your shell",
        f"  {COLORS['cyan']}D{COLORS['reset']} - Describe   - Explain what this command does",
        f"  {COLORS['cyan']}A{COLORS['reset']} - Abort      - Cancel and return to prompt"
    ]
    prompt_text = f"\nWhat would you like to do? [{COLORS['cyan']}C{COLORS['reset']}/{COLORS['cyan']}E{COLORS['reset']}/{COLORS['cyan']}D{COLORS['reset']}/{COLORS['cyan']}A{COLORS['reset']}] "

    # Make sure box rendering is complete before showing options
    with TERMINAL_RENDER_LOCK:
        # Add a small delay to ensure terminal rendering is complete,
        # especially important for stream-prettify mode
        if not args.plaintext:
            time.sleep(0.5)
            
        # Print options with proper flushing to ensure display
        print(options_text, flush=True)
        for option in options:
            print(option, flush=True)

        # Print prompt and flush to ensure it appears
        sys.stdout.write(prompt_text)
        sys.stdout.flush()
    
    try:
        # Use get_terminal_input which opens /dev/tty directly rather than using stdin
        # This allows user input even when stdin has been consumed by pipe
        response = get_terminal_input()
        if response:
            response = response.lower()
        else:
            # If get_terminal_input fails, default to abort
            print("\nFailed to get terminal input. Defaulting to abort option.")
            response = 'a'
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
                
                # Special handling for Windows PowerShell commands
                if shell_name in ["powershell.exe", "pwsh"] and platform.system() == "Windows":
                    # Execute PowerShell commands properly on Windows
                    result = subprocess.run(
                        ["powershell.exe", "-Command", command], 
                        shell=True, 
                        check=True, 
                        capture_output=True, 
                        text=True
                    )
                else:
                    # Regular command execution for other shells
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
        
        # Set up fresh display for description (unified pattern)
        desc_should_stream = True
        desc_stream_callback = None
        desc_live_display = None
        desc_stop_spinner_func = None
        desc_stop_spinner_event = None
        desc_first_content_received = False
        
        # Spinner for plaintext mode
        desc_plaintext_spinner_thread = None
        desc_plaintext_stop_event = None
        
        # Handle display mode based on parameters
        if args.plaintext:
            # Plain text mode - no streaming, no markdown rendering
            desc_should_stream = False
            desc_plaintext_spinner_thread, desc_plaintext_stop_event = setup_plaintext_spinner("Generating command description...", COLORS['cyan'])
        else:
            # Default stream-prettify mode - stream with live markdown rendering
            desc_live_display, desc_stream_callback, desc_setup_spinner = prettify_streaming_markdown()
            if not desc_live_display:
                # Fallback if display creation fails
                print(f"{COLORS['yellow']}Warning: Live display setup failed. Falling back to plain streaming.{COLORS['reset']}")
        
        # Set up the spinner if we have a live display and stream-prettify is enabled
        if desc_should_stream and not args.plaintext and desc_live_display:
            desc_stop_spinner_event = threading.Event()
            desc_stop_spinner_func = desc_setup_spinner(desc_stop_spinner_event, color=COLORS['cyan'])
        
        # Create a wrapper for the stream callback that handles spinner
        if desc_stream_callback:
            desc_original_callback = desc_stream_callback
            desc_first_content_received_ref = [desc_first_content_received]
            desc_stream_callback = create_spinner_handling_callback(desc_original_callback, desc_stop_spinner_func, desc_first_content_received_ref)
        
        # Generate the description
        try:
            description = client.chat(describe_prompt, stream=desc_should_stream,
                                   temperature=0.3, top_p=args.top_p,
                                   max_tokens=args.max_tokens, messages=describe_messages,
                                   markdown_format=not args.plaintext,
                                   stream_callback=desc_stream_callback)
        except KeyboardInterrupt:
            print("\nRequest cancelled by user.")
            return
        except Exception as e:
            print(f"Error generating description: {e}")
            return
        
        # Stop plaintext spinner if it was started
        cleanup_plaintext_spinner(desc_plaintext_spinner_thread, desc_plaintext_stop_event)
        
        # Ensure spinner is stopped if no content was received
        if desc_stop_spinner_event and not desc_first_content_received_ref[0]:
            desc_stop_spinner_event.set()
        
        # Stop live display if using stream-prettify
        if not args.plaintext and desc_live_display:
            # Before stopping the live display, update with complete=True to show final formatted content
            if desc_stream_callback and description:
                # Format description as markdown for prettier display
                md_description = f"### Command Description\n\n{description}"
                desc_stream_callback(md_description, complete=True)
        
        # Log the generated description if logging is enabled
        if logger and description:
            logger.log("assistant", description)
        
        # Handle plain text response
        if args.plaintext and description:
            with TERMINAL_RENDER_LOCK:
                print(description)
    elif response == 'a' or response == '':
        print("\nCommand aborted.")
        
        # Log the abort if logging is enabled
        if logger:
            logger.log("system", "Command aborted by user") 