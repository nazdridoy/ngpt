from ..formatters import COLORS
import subprocess
import sys

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
        
    command = client.generate_shell_command(prompt, web_search=args.web_search, 
                                         temperature=args.temperature, top_p=args.top_p,
                                         max_tokens=args.max_tokens)
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