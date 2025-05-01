from ..formatters import COLORS
from ..ui import spinner
from ...utils import enhance_prompt_with_web_search
import subprocess
import sys
import threading

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
            prompt = enhance_prompt_with_web_search(prompt, logger=logger)
            print("Enhanced input with web search results.")
            
            # Log the enhanced prompt if logging is enabled
            if logger:
                # Use "web_search" role instead of "system" for clearer logs
                logger.log("web_search", prompt.replace(original_prompt, "").strip())
        except Exception as e:
            print(f"{COLORS['yellow']}Warning: Failed to enhance prompt with web search: {str(e)}{COLORS['reset']}")
            # Continue with the original prompt if web search fails
    
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
        command = client.generate_shell_command(prompt,
                                           temperature=args.temperature, top_p=args.top_p,
                                           max_tokens=args.max_tokens)
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
        
    print(f"\nGenerated command: {command}")
    
    try:
        print("Do you want to execute this command? [y/N] ", end='')
        response = input().lower()
    except KeyboardInterrupt:
        print("\nCommand execution cancelled by user.")
        return
        
    if response == 'y' or response == 'yes':
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