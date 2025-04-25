import sys
from .formatters import COLORS

def show_config_help():
    """Display help information about configuration."""
    print(f"\n{COLORS['green']}{COLORS['bold']}Configuration Help:{COLORS['reset']}")
    print(f"  1. {COLORS['cyan']}Create a config file at one of these locations:{COLORS['reset']}")
    if sys.platform == "win32":
        print(f"     - {COLORS['yellow']}%APPDATA%\\ngpt\\ngpt.conf{COLORS['reset']}")
    elif sys.platform == "darwin":
        print(f"     - {COLORS['yellow']}~/Library/Application Support/ngpt/ngpt.conf{COLORS['reset']}")
    else:
        print(f"     - {COLORS['yellow']}~/.config/ngpt/ngpt.conf{COLORS['reset']}")
    
    print(f"  2. {COLORS['cyan']}Format your config file as JSON:{COLORS['reset']}")
    print(f"""{COLORS['yellow']}     [
       {{
         "api_key": "your-api-key-here",
         "base_url": "https://api.openai.com/v1/",
         "provider": "OpenAI",
         "model": "gpt-3.5-turbo"
       }},
       {{
         "api_key": "your-second-api-key",
         "base_url": "http://localhost:1337/v1/",
         "provider": "Another Provider",
         "model": "different-model"
       }}
     ]{COLORS['reset']}""")
    
    print(f"  3. {COLORS['cyan']}Or set environment variables:{COLORS['reset']}")
    print(f"     - {COLORS['yellow']}OPENAI_API_KEY{COLORS['reset']}")
    print(f"     - {COLORS['yellow']}OPENAI_BASE_URL{COLORS['reset']}")
    print(f"     - {COLORS['yellow']}OPENAI_MODEL{COLORS['reset']}")
    
    print(f"  4. {COLORS['cyan']}Or provide command line arguments:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --api-key your-key --base-url https://api.example.com --model your-model \"Your prompt\"{COLORS['reset']}")
    
    print(f"  5. {COLORS['cyan']}Use --config-index to specify which configuration to use or edit:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config-index 1 \"Your prompt\"{COLORS['reset']}")
    
    print(f"  6. {COLORS['cyan']}Use --provider to specify which configuration to use by provider name:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --provider Gemini \"Your prompt\"{COLORS['reset']}")
    
    print(f"  7. {COLORS['cyan']}Use --config without arguments to add a new configuration:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config{COLORS['reset']}")
    print(f"     Or specify an index or provider to edit an existing configuration:")
    print(f"     {COLORS['yellow']}ngpt --config --config-index 1{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config --provider Gemini{COLORS['reset']}")

    print(f"  8. {COLORS['cyan']}Remove a configuration by index or provider:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config --remove --config-index 1{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --config --remove --provider Gemini{COLORS['reset']}")

    print(f"  9. {COLORS['cyan']}List available models for the current configuration:{COLORS['reset']}")
    print(f"     {COLORS['yellow']}ngpt --list-models{COLORS['reset']}")

def check_config(config):
    """Check config for common issues and provide guidance."""
    if not config.get("api_key"):
        print(f"{COLORS['yellow']}{COLORS['bold']}Error: API key is not set.{COLORS['reset']}")
        show_config_help()
        return False
        
    # Check for common URL mistakes
    base_url = config.get("base_url", "")
    if base_url and not (base_url.startswith("http://") or base_url.startswith("https://")):
        print(f"{COLORS['yellow']}Warning: Base URL '{base_url}' doesn't start with http:// or https://{COLORS['reset']}")
    
    return True 