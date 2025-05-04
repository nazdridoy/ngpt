from ..formatters import COLORS
from ..ui import spinner, copy_to_clipboard
from ..renderers import prettify_markdown, has_markdown_renderer
from ...utils import enhance_prompt_with_web_search
import subprocess
import sys
import threading
import platform
import os
import shutil
import re

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

def shell_mode(client, args, logger=None):
    """Handle the shell command generation mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
        logger: Optional logger instance
    """
    if args.prompt is None:
        try:
            print("Enter shell command description: ", end='')
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
    
    # Start spinner while waiting for command generation
    stop_spinner = threading.Event()
    spinner_thread = threading.Thread(
        target=spinner, 
        args=("Generating command...",), 
        kwargs={"stop_event": stop_spinner, "color": COLORS['cyan']}
    )
    spinner_thread.daemon = True
    spinner_thread.start()
    
    try:
        command = client.chat(
            prompt=prompt,
            stream=False,
            messages=messages,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens
        )
    except Exception as e:
        print(f"Error generating shell command: {e}")
        command = ""
    finally:
        # Stop the spinner
        stop_spinner.set()
        spinner_thread.join()
        
        # Clear the spinner line completely
        sys.stdout.write("\r" + " " * 100 + "\r")
        sys.stdout.flush()
    
    if not command:
        return  # Error already printed by client
    
    # Log the generated command if logging is enabled
    if logger:
        logger.log("assistant", command)
    
    # Get the most up-to-date shell type at command generation time
    _, highlight_lang, _ = detect_shell()
    
    # Create a markdown-formatted display of the command with appropriate syntax highlighting
    formatted_command = f"### Generated Command\n\n```{highlight_lang}\n{command}\n```"
    
    # Check if we can use rich rendering
    if has_markdown_renderer('rich'):
        # Use rich renderer for pretty output
        prettify_markdown(formatted_command, 'rich')
    else:
        # Fallback to simpler formatting
        term_width = shutil.get_terminal_size().columns
        box_width = min(term_width - 4, len(command) + 8)
        horizontal_line = "─" * box_width
        
        print(f"\n┌{horizontal_line}┐")
        print(f"│ {COLORS['bold']}Generated Command:{COLORS['reset']}  {' ' * (box_width - 20)}│")
        print(f"│ {COLORS['green']}{command}{COLORS['reset']}{' ' * (box_width - len(command) - 2)}│")
        print(f"└{horizontal_line}┘\n")
    
    # Display options with better formatting
    print(f"{COLORS['bold']}Options:{COLORS['reset']}")
    print(f"  {COLORS['cyan']}c{COLORS['reset']} - Copy to clipboard")
    print(f"  {COLORS['cyan']}e{COLORS['reset']} - Execute command")
    print(f"  {COLORS['cyan']}n{COLORS['reset']} - Cancel (default)")
    print(f"\nWhat would you like to do? [{COLORS['cyan']}c{COLORS['reset']}/{COLORS['cyan']}e{COLORS['reset']}/N] ", end='')
    
    try:
        response = input().lower()
    except KeyboardInterrupt:
        print("\nCommand execution cancelled by user.")
        return
        
    if response == 'e' or response == 'execute':
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
    elif response == 'c' or response == 'copy':
        # Copy command to clipboard without confirmation prompt
        copied = copy_to_clipboard(command, skip_confirmation=True)
        if not copied:
            print(f"{COLORS['yellow']}Failed to copy to clipboard. Command: {COLORS['green']}{command}{COLORS['reset']}")
        
        # Log the copy if logging is enabled
        if logger:
            logger.log("system", "Command copied to clipboard") 