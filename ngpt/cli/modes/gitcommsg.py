import os
import re
import sys
import tempfile
import time
import subprocess
from datetime import datetime
import logging
from ..formatters import COLORS
from ...utils.log import create_gitcommsg_logger

def get_diff_content(diff_file=None):
    """Get git diff content from file or git staged changes.
    
    Args:
        diff_file: Path to a diff file to use instead of git staged changes
        
    Returns:
        str: Content of the diff, or None if no diff is available
    """
    if diff_file:
        try:
            with open(diff_file, 'r') as f:
                content = f.read()
                return content
        except Exception as e:
            print(f"{COLORS['yellow']}Error reading diff file: {str(e)}{COLORS['reset']}")
            return None
            
    # No diff file specified, get staged changes from git
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
            
        # Check if there are staged changes
        if not result.stdout.strip():
            print(f"{COLORS['yellow']}No staged changes found. Stage changes with 'git add' first.{COLORS['reset']}")
            return None
            
        return result.stdout
    except Exception as e:
        print(f"{COLORS['yellow']}Error getting git diff: {str(e)}{COLORS['reset']}")
        return None

def split_into_chunks(content, chunk_size=200):
    """Split content into chunks of specified size.
    
    Args:
        content: The content to split into chunks
        chunk_size: Maximum number of lines per chunk
        
    Returns:
        list: List of content chunks
    """
    lines = content.splitlines()
    chunks = []
    
    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i+chunk_size]
        chunks.append("\n".join(chunk))
        
    return chunks

def process_context(context):
    """Process context string to extract directives and filters.
    
    Args:
        context: The context string provided with -m/--message-context
        
    Returns:
        dict: Extracted context data
    """
    context_data = {
        "file_type_filter": None,
        "commit_type": None,
        "focus": None,
        "exclusions": [],
        "raw_context": context
    }
    
    if not context:
        return context_data
    
    # Extract commit type directive (e.g., "type:feat")
    if "type:" in context:
        match = re.search(r"type:(\w+)", context)
        if match:
            context_data["commit_type"] = match.group(1)
    
    # Extract file type filters
    file_type_keywords = ["html", "css", "javascript", "python", "js", "py", "ui", "api", "config"]
    for keyword in file_type_keywords:
        if keyword in context.lower():
            context_data["file_type_filter"] = keyword
            break
    
    # Process focus/exclusion directives
    if "focus on" in context.lower() or "only mention" in context.lower():
        focus_match = re.search(r"focus(?:\s+on)?\s+(\w+)", context.lower())
        if focus_match:
            context_data["focus"] = focus_match.group(1)
    
    if any(x in context.lower() for x in ["ignore", "don't include", "exclude"]):
        exclusion_matches = re.findall(r"(?:ignore|don't include|exclude)\s+(\w+)", context.lower())
        context_data["exclusions"] = exclusion_matches
    
    return context_data

def create_system_prompt(context_data=None):
    """Create system prompt based on context data.
    
    Args:
        context_data: The processed context data
        
    Returns:
        str: System prompt for the AI
    """
    base_prompt = """You are an expert Git commit message writer. Your task is to analyze the git diff and create a precise, factual commit message following the conventional commit format.

FORMAT:
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>

COMMIT TYPES:
- feat: New user-facing features
- fix: Bug fixes or error corrections
- refactor: Code restructuring (no behavior change)
- style: Formatting/whitespace changes only
- docs: Documentation only
- test: Test-related changes
- perf: Performance improvements
- build: Build system changes
- ci: CI/CD pipeline changes
- chore: Routine maintenance tasks
- revert: Reverting previous changes
- add: New files without user-facing features
- remove: Removing files/code
- update: Changes to existing functionality
- security: Security-related changes
- config: Configuration changes
- ui: User interface changes
- api: API-related changes

RULES:
1. BE 100% FACTUAL - Mention ONLY code explicitly shown in the diff
2. NEVER invent or assume changes not directly visible in the code
3. EVERY bullet point MUST reference specific files/functions/lines
4. Include ALL significant changes (do not skip any important modifications)
5. If unsure about a change's purpose, describe WHAT changed, not WHY
6. Keep summary line under 50 characters (mandatory)
7. Use appropriate type tags for each change (main summary and each bullet)
8. ONLY describe code that was actually changed
9. Focus on technical specifics, avoid general statements
10. Include proper technical details (method names, component identifiers, etc.)
11. When all changes are to the same file, mention it once in the summary"""

    if not context_data:
        return base_prompt
    
    # Add file type filtering instructions
    if context_data.get("file_type_filter"):
        file_type = context_data["file_type_filter"]
        file_type_prompt = f"""

CRITICAL FILE TYPE FILTERING:
You MUST INCLUDE ONLY changes to {file_type} files or files related to {file_type}.
You MUST EXCLUDE ALL other files completely from your output.
This is a strict filter - no exceptions allowed."""
        base_prompt += file_type_prompt
    
    # Add commit type directive
    if context_data.get("commit_type"):
        commit_type = context_data["commit_type"]
        commit_type_prompt = f"""

CRITICAL COMMIT TYPE DIRECTIVE:
You MUST use exactly "{commit_type}:" as the commit type prefix.
This takes highest priority over any other commit type you might determine.
Do not override this commit type based on your own analysis."""
        base_prompt += commit_type_prompt
    
    # Add focus/exclusion directives
    if context_data.get("focus"):
        focus = context_data["focus"]
        focus_prompt = f"""

FOCUS DIRECTIVE:
Focus exclusively on changes related to {focus}.
Exclude everything else from your analysis."""
        base_prompt += focus_prompt
    
    if context_data.get("exclusions"):
        exclusions = ", ".join(context_data["exclusions"])
        exclusion_prompt = f"""

EXCLUSION DIRECTIVE:
Completely ignore and exclude any mentions of: {exclusions}."""
        base_prompt += exclusion_prompt
    
    return base_prompt

def create_chunk_prompt(chunk):
    """Create prompt for processing a single diff chunk.
    
    Args:
        chunk: The diff chunk to process
        
    Returns:
        str: Prompt for the AI
    """
    return f"""Analyze this PARTIAL git diff and create a detailed technical summary with this EXACT format:

[FILES]: Comma-separated list of affected files with full paths

[CHANGES]: 
- Technical detail 1 (include specific function/method names and line numbers)
- Technical detail 2 (be precise about exactly what code was added/modified/removed)
- Additional technical details (include ALL significant changes in this chunk)

[IMPACT]: Brief technical description of what the changes accomplish

CRITICALLY IMPORTANT: Be extremely specific with technical details.
ALWAYS identify exact function names, method names, class names, and line numbers where possible.
Use format 'filename:function_name()' or 'filename:line_number' when referencing code locations.
Be precise and factual - only describe code that actually changed.

Diff chunk:

{chunk}"""

def create_rechunk_prompt(combined_analysis, depth):
    """Create prompt for re-chunking process.
    
    Args:
        combined_analysis: The combined analysis to re-chunk
        depth: Current recursion depth
        
    Returns:
        str: Prompt for the AI
    """
    return f"""IMPORTANT: You are analyzing SUMMARIES of git changes, not raw git diff.

You are in a re-chunking process (depth: {depth}) where the input is already summarized changes.
Create a TERSE summary of these summaries focusing ONLY ON TECHNICAL CHANGES:

[CHANGES]:
- Technical change 1 (specific file and function)
- Technical change 2 (specific file and function)
- Additional relevant changes

DO NOT ask for raw git diff. These summaries are all you need to work with.
Keep your response FACTUAL and SPECIFIC to what's in the summaries.

Section to summarize:

{combined_analysis}"""

def create_combine_prompt(partial_analyses):
    """Create prompt for combining partial analyses.
    
    Args:
        partial_analyses: List of partial analyses to combine
        
    Returns:
        str: Prompt for the AI
    """
    all_analyses = "\n\n".join(partial_analyses)
    
    return f"""===CRITICAL INSTRUCTION===
You are working with ANALYZED SUMMARIES of git changes, NOT raw git diff.
The raw git diff has ALREADY been processed into these summaries.
DO NOT ask for or expect to see the original git diff.

TASK: Synthesize these partial analyses into a complete conventional commit message:

{all_analyses}

Create a CONVENTIONAL COMMIT MESSAGE with:
1. First line: "type[(scope)]: brief summary" (50 chars max)
   - Include scope ONLY if you are 100% confident about the affected area
   - Omit scope if changes affect multiple areas or scope is unclear
2. ⚠️ ONE BLANK LINE IS MANDATORY - NEVER SKIP THIS STEP ⚠️
   - This blank line MUST be present in EVERY commit message
   - The blank line separates the summary from the detailed changes
   - Without this blank line, the commit message format is invalid
3. Bullet points with specific changes, each with appropriate [type] tag
4. Reference files in EACH bullet point with function names or line numbers

FILENAME & FUNCTION HANDLING RULES:
- Include SPECIFIC function names, method names, or line numbers when available
- Format as filename:function() or filename:line_number
- Use short relative paths for files
- Group related changes to the same file when appropriate
- Avoid breaking long filenames across lines

STRICTLY follow this format with NO EXPLANATION or additional commentary.
DO NOT mention insufficient information or ask for the original diff."""

def create_final_prompt(diff_content):
    """Create prompt for direct processing without chunking.
    
    Args:
        diff_content: The full diff content
        
    Returns:
        str: Prompt for the AI
    """
    return f"""Analyze ONLY the exact changes in this git diff and create a precise, factual commit message.

FORMAT:
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>

RULES FOR FILENAMES:
1. Use short relative paths when possible
2. For multiple changes to the same file, consider grouping them
3. Abbreviate long paths when they're repeated (e.g., 'commit.zsh' instead of full path)
4. Avoid breaking filenames across lines
5. Only include function names when they add clarity

COMMIT TYPES:
- feat: New user-facing features
- fix: Bug fixes or error corrections
- refactor: Code restructuring (no behavior change)
- style: Formatting/whitespace changes only
- docs: Documentation only
- test: Test-related changes
- perf: Performance improvements
- build: Build system changes
- ci: CI/CD pipeline changes
- chore: Routine maintenance tasks
- revert: Reverting previous changes
- add: New files without user-facing features
- remove: Removing files/code
- update: Changes to existing functionality
- security: Security-related changes
- config: Configuration changes
- ui: User interface changes
- api: API-related changes

RULES:
1. BE 100% FACTUAL - Mention ONLY code explicitly shown in the diff
2. NEVER invent or assume changes not directly visible in the code
3. EVERY bullet point MUST reference specific files/functions/lines
4. Include ALL significant changes (do not skip any important modifications)
5. If unsure about a change's purpose, describe WHAT changed, not WHY
6. Keep summary line under 50 characters (mandatory)
7. Use appropriate type tags for each change (main summary and each bullet)
8. ONLY describe code that was actually changed
9. Focus on technical specifics, avoid general statements
10. Include proper technical details (method names, component identifiers, etc.)
11. When all changes are to the same file, mention it once in the summary

Git diff to process:

{diff_content}"""

def handle_api_call(client, prompt, system_prompt=None, logger=None, max_retries=3):
    """Handle API call with retries and error handling.
    
    Args:
        client: The NGPTClient instance
        prompt: The prompt to send to the API
        system_prompt: Optional system prompt
        logger: Optional logger instance
        max_retries: Maximum number of retries on error
        
    Returns:
        str: Response from the API
    """
    if logger:
        # Enhanced logging of full prompt and system prompt
        logger.log_prompt("DEBUG", system_prompt, prompt)
    
    retry_count = 0
    wait_seconds = 5
    
    while True:
        try:
            # Create messages array with system prompt if available
            messages = None
            if system_prompt:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            else:
                messages = [
                    {"role": "user", "content": prompt}
                ]
            
            response = client.chat(
                prompt=prompt,
                stream=False,
                markdown_format=False,
                messages=messages
            )
            
            if logger:
                # Log full response
                logger.log_response("DEBUG", response)
                
            return response
            
        except Exception as e:
            retry_count += 1
            error_msg = f"Error (attempt {retry_count}/{max_retries}): {str(e)}"
            
            if logger:
                logger.error(error_msg)
                
            if retry_count >= max_retries:
                raise Exception(f"Failed after {max_retries} retries: {str(e)}")
                
            print(f"{COLORS['yellow']}{error_msg}{COLORS['reset']}")
            print(f"{COLORS['yellow']}Retrying in {wait_seconds} seconds...{COLORS['reset']}")
            
            # Create a spinner effect for waiting
            spinner = "⣾⣽⣻⢿⡿⣟⣯⣷"
            for _ in range(wait_seconds * 5):
                for char in spinner:
                    sys.stdout.write(f"\r{COLORS['yellow']}Waiting... {char}{COLORS['reset']}")
                    sys.stdout.flush()
                    time.sleep(0.2)
            
            print("\r" + " " * 20 + "\r", end="")
            
            # Exponential backoff
            wait_seconds *= 2

def process_with_chunking(client, diff_content, context_data, chunk_size=200, recursive=False, max_depth=3, logger=None):
    """Process diff with chunking to handle large diffs.
    
    Args:
        client: The NGPTClient instance
        diff_content: The diff content to process
        context_data: The processed context data
        chunk_size: Maximum number of lines per chunk
        recursive: Whether to use recursive chunking
        max_depth: Maximum recursion depth
        logger: Optional logger instance
        
    Returns:
        str: Generated commit message
    """
    # Create system prompt
    system_prompt = create_system_prompt(context_data)
    
    # Log initial diff content
    if logger:
        logger.log_diff("DEBUG", diff_content)
    
    # Split diff into chunks
    chunks = split_into_chunks(diff_content, chunk_size)
    chunk_count = len(chunks)
    
    if logger:
        logger.info(f"Processing {chunk_count} chunks of {chunk_size} lines each")
    
    print(f"{COLORS['green']}Processing diff in {chunk_count} chunks...{COLORS['reset']}")
    
    # Process each chunk
    partial_analyses = []
    for i, chunk in enumerate(chunks):
        print(f"\n{COLORS['cyan']}[Chunk {i+1}/{chunk_count}]{COLORS['reset']}")
        
        # Log chunk content
        if logger:
            logger.log_chunks("DEBUG", i+1, chunk_count, chunk)
        
        # Create chunk prompt
        chunk_prompt = create_chunk_prompt(chunk)
        
        # Log chunk template
        if logger:
            logger.log_template("DEBUG", "CHUNK", chunk_prompt)
        
        # Process chunk
        print(f"{COLORS['yellow']}Analyzing changes...{COLORS['reset']}")
        try:
            result = handle_api_call(client, chunk_prompt, system_prompt, logger)
            partial_analyses.append(result)
            print(f"{COLORS['green']}✓ Chunk {i+1} processed{COLORS['reset']}")
        except Exception as e:
            print(f"{COLORS['red']}Error processing chunk {i+1}: {str(e)}{COLORS['reset']}")
            if logger:
                logger.error(f"Error processing chunk {i+1}: {str(e)}")
            return None
        
        # Rate limit protection between chunks
        if i < chunk_count - 1:
            print(f"{COLORS['yellow']}Waiting to avoid rate limits...{COLORS['reset']}")
            time.sleep(5)
    
    # Combine partial analyses
    print(f"\n{COLORS['cyan']}Combining analyses from {len(partial_analyses)} chunks...{COLORS['reset']}")
    
    # Log partial analyses
    if logger:
        combined_analyses = "\n\n".join(partial_analyses)
        logger.log_content("DEBUG", "PARTIAL_ANALYSES", combined_analyses)
    
    # Check if we need to use recursive chunking
    combined_analyses = "\n\n".join(partial_analyses)
    combined_line_count = len(combined_analyses.splitlines())
    
    if recursive and combined_line_count > 50 and max_depth > 0:
        # Use recursive chunking
        return recursive_process(client, combined_analyses, context_data, max_depth, logger)
    else:
        # Use direct combination
        combine_prompt = create_combine_prompt(partial_analyses)
        
        # Log combine template
        if logger:
            logger.log_template("DEBUG", "COMBINE", combine_prompt)
        
        try:
            result = handle_api_call(client, combine_prompt, system_prompt, logger)
            return result
        except Exception as e:
            print(f"{COLORS['red']}Error combining analyses: {str(e)}{COLORS['reset']}")
            if logger:
                logger.error(f"Error combining analyses: {str(e)}")
            return None

def recursive_process(client, combined_analysis, context_data, max_depth, logger=None, current_depth=1):
    """Process large analysis results recursively.
    
    Args:
        client: The NGPTClient instance
        combined_analysis: The combined analysis to process
        context_data: The processed context data
        max_depth: Maximum recursion depth
        logger: Optional logger instance
        current_depth: Current recursion depth
        
    Returns:
        str: Generated commit message
    """
    system_prompt = create_system_prompt(context_data)
    
    print(f"\n{COLORS['cyan']}Recursive chunking level {current_depth}/{max_depth}...{COLORS['reset']}")
    
    if logger:
        logger.info(f"Starting recursive chunking at depth {current_depth}/{max_depth}")
        logger.debug(f"Combined analysis size: {len(combined_analysis.splitlines())} lines")
        logger.log_content("DEBUG", f"COMBINED_ANALYSIS_DEPTH_{current_depth}", combined_analysis)
    
    # Create rechunk prompt
    rechunk_prompt = create_rechunk_prompt(combined_analysis, current_depth)
    
    # Log rechunk template
    if logger:
        logger.log_template("DEBUG", f"RECHUNK_DEPTH_{current_depth}", rechunk_prompt)
    
    # Process rechunk
    try:
        result = handle_api_call(client, rechunk_prompt, system_prompt, logger)
        
        # Check if further recursive chunking is needed
        result_line_count = len(result.splitlines())
        
        if result_line_count > 50 and current_depth < max_depth:
            # Need another level of chunking
            print(f"{COLORS['yellow']}Result still too large ({result_line_count} lines), continuing recursion...{COLORS['reset']}")
            if logger:
                logger.info(f"Result still too large ({result_line_count} lines), depth {current_depth}/{max_depth}")
            
            return recursive_process(client, result, context_data, max_depth, logger, current_depth + 1)
        else:
            # Final processing
            print(f"{COLORS['green']}Recursion complete, generating final commit message...{COLORS['reset']}")
            
            # Create final combine prompt
            final_prompt = f"""Create a CONVENTIONAL COMMIT MESSAGE based on these analyzed git changes:

{result}

FORMAT:
type[(scope)]: <concise summary> (max 50 chars)

- [type] <specific change 1> (filename:function/method/line)
- [type] <specific change 2> (filename:function/method/line)
- [type] <additional changes...>

RULES:
1. First line must be under 50 characters
2. Include a blank line after the first line
3. Each bullet must include specific file references
4. BE SPECIFIC - mention technical details and function names

DO NOT include any explanation or commentary outside the commit message format."""
            
            # Log final template
            if logger:
                logger.log_template("DEBUG", "FINAL", final_prompt)
            
            return handle_api_call(client, final_prompt, system_prompt, logger)
    except Exception as e:
        print(f"{COLORS['red']}Error in recursive processing: {str(e)}{COLORS['reset']}")
        if logger:
            logger.error(f"Error in recursive processing at depth {current_depth}: {str(e)}")
        return None

def gitcommsg_mode(client, args, logger=None):
    """Handle the Git commit message generation mode.
    
    Args:
        client: The NGPTClient instance
        args: The parsed command line arguments
        logger: Optional logger instance
    """
    # Set up logging if requested
    custom_logger = None
    log_path = None
    
    if args.log:
        custom_logger = create_gitcommsg_logger(args.log)
    
    # Use both loggers if they exist
    active_logger = logger if logger else custom_logger
    
    if active_logger:
        active_logger.info("Starting gitcommsg mode")
        active_logger.debug(f"Args: {args}")
    
    try:
        # Get diff content
        diff_content = get_diff_content(args.diff)
        
        if not diff_content:
            print(f"{COLORS['red']}No diff content available. Exiting.{COLORS['reset']}")
            return
        
        # Log the diff content
        if active_logger:
            active_logger.log_diff("DEBUG", diff_content)
        
        # Process context if provided
        context_data = None
        if args.message_context:
            context_data = process_context(args.message_context)
            if active_logger:
                active_logger.debug(f"Processed context: {context_data}")
                active_logger.log_content("DEBUG", "CONTEXT_DATA", str(context_data))
        
        # Create system prompt
        system_prompt = create_system_prompt(context_data)
        
        # Log system prompt
        if active_logger:
            active_logger.log_template("DEBUG", "SYSTEM", system_prompt)
        
        print(f"\n{COLORS['green']}Generating commit message...{COLORS['reset']}")
        
        # Process based on chunking options
        result = None
        if args.chunk_size:
            chunk_size = args.chunk_size
            if active_logger:
                active_logger.info(f"Using chunk size: {chunk_size}")
        
        if args.recursive_chunk:
            # Use chunking with recursive processing
            if active_logger:
                active_logger.info(f"Using recursive chunking with max_depth: {args.max_depth}")
            
            result = process_with_chunking(
                client, 
                diff_content, 
                context_data, 
                chunk_size=args.chunk_size,
                recursive=True,
                max_depth=args.max_depth,
                logger=active_logger
            )
        else:
            # Direct processing without chunking
            if active_logger:
                active_logger.info("Processing without chunking")
            
            prompt = create_final_prompt(diff_content)
            
            # Log final template
            if active_logger:
                active_logger.log_template("DEBUG", "DIRECT_PROCESSING", prompt)
            
            result = handle_api_call(client, prompt, system_prompt, active_logger)
        
        if not result:
            print(f"{COLORS['red']}Failed to generate commit message.{COLORS['reset']}")
            return
        
        # Display the result
        print(f"\n{COLORS['green']}✨ Generated Commit Message:{COLORS['reset']}\n")
        print(result)
        
        # Log the result
        if active_logger:
            active_logger.info("Generated commit message successfully")
            active_logger.log_content("INFO", "FINAL_COMMIT_MESSAGE", result)
        
        # Try to copy to clipboard
        try:
            import pyperclip
            pyperclip.copy(result)
            print(f"\n{COLORS['green']}(Copied to clipboard){COLORS['reset']}")
            if active_logger:
                active_logger.info("Commit message copied to clipboard")
        except ImportError:
            if active_logger:
                active_logger.debug("pyperclip not available, couldn't copy to clipboard")
    
    except Exception as e:
        print(f"{COLORS['red']}Error: {str(e)}{COLORS['reset']}")
        if active_logger:
            active_logger.error(f"Error in gitcommsg mode: {str(e)}", exc_info=True) 