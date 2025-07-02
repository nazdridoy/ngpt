import sys
from ngpt.ui.colors import COLORS

def process_piped_input(prompt, logger=None):
    """Process piped input to be used with a prompt.
    
    Args:
        prompt: The prompt string which may contain a {} placeholder
        logger: Optional logger instance
    
    Returns:
        str: The processed prompt with piped input inserted at placeholder, or appended
    """
    
    # Only process if stdin is not a TTY (i.e., if we're receiving piped input)
    if not sys.stdin.isatty():
        # Read input from stdin
        stdin_content = sys.stdin.read().strip()
        
        # If we have stdin content and prompt is provided
        if stdin_content and prompt:
            placeholder = "{}"
            
            # Check if the placeholder exists in the prompt
            if placeholder not in prompt:
                print(f"{COLORS['yellow']}Warning: Placeholder '{placeholder}' not found in prompt. Appending stdin content to the end.{COLORS['reset']}")
                processed_prompt = f"{prompt}\n\n{stdin_content}"
            else:
                # Replace the placeholder in the prompt with stdin content
                processed_prompt = prompt.replace(placeholder, stdin_content)
                
            # Log if a logger is provided
            if logger:
                logger.log("info", f"Processed piped input: Combined prompt with stdin content")
                
            return processed_prompt
        
        # If we have stdin content but no prompt, just use the stdin content
        elif stdin_content:
            return stdin_content
        elif prompt:
            # We have prompt but stdin is empty
            print(f"{COLORS['yellow']}Warning: No stdin content received. Using only the provided prompt.{COLORS['reset']}")
            return prompt
        else:
            # No stdin content and no prompt
            print(f"{COLORS['yellow']}Error: No stdin content and no prompt provided.{COLORS['reset']}")
            return ""
    
    # If no stdin or no content in stdin, just return the original prompt
    return prompt 