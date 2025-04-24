from ..formatters import COLORS
import subprocess
import sys

def shell_mode(client, args):
    """Handle the shell command generation mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command-line arguments
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
        
    command = client.generate_shell_command(prompt, web_search=args.web_search, 
                                         temperature=args.temperature, top_p=args.top_p,
                                         max_tokens=args.max_tokens)
    if not command:
        return  # Error already printed by client
        
    print(f"\nGenerated command: {command}")
    
    try:
        print("Do you want to execute this command? [y/N] ", end='')
        response = input().lower()
    except KeyboardInterrupt:
        print("\nCommand execution cancelled by user.")
        return
        
    if response == 'y' or response == 'yes':
        try:
            try:
                print("\nExecuting command... (Press Ctrl+C to cancel)")
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
                print(f"\nOutput:\n{result.stdout}")
            except KeyboardInterrupt:
                print("\nCommand execution cancelled by user.")
        except subprocess.CalledProcessError as e:
            print(f"\nError:\n{e.stderr}") 