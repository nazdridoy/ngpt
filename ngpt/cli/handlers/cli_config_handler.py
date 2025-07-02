"""
CLI configuration handler module.
Handles CLI config options stored in ngpt-cli.conf
"""
import sys
from typing import Tuple, Optional, Dict, Any

from ngpt.ui.colors import COLORS
from ngpt.core.cli_config import (
    set_cli_config_option, 
    get_cli_config_option, 
    unset_cli_config_option,
    list_cli_config_options,
    CLI_CONFIG_OPTIONS
)

def show_cli_config_help() -> str:
    """Display help information about CLI configuration.
    
    Returns:
        str: Formatted help text
    """
    help_text = [
        f"\n{COLORS['green']}{COLORS['bold']}CLI Configuration Help:{COLORS['reset']}",
        f"  {COLORS['cyan']}Command syntax:{COLORS['reset']}",
        f"    {COLORS['yellow']}ngpt --cli-config help{COLORS['reset']}                - Show this help message",
        f"    {COLORS['yellow']}ngpt --cli-config set OPTION VALUE{COLORS['reset']}    - Set a default value for OPTION",
        f"    {COLORS['yellow']}ngpt --cli-config get OPTION{COLORS['reset']}          - Get the current value of OPTION",
        f"    {COLORS['yellow']}ngpt --cli-config get{COLORS['reset']}                 - Show all CLI configuration settings",
        f"    {COLORS['yellow']}ngpt --cli-config unset OPTION{COLORS['reset']}        - Remove OPTION from configuration",
        f"    {COLORS['yellow']}ngpt --cli-config list{COLORS['reset']}                - List all available options with types and defaults"
    ]
    
    # Group options by context
    context_groups = {
        "all": [],
        "code": [],
        "interactive": [],
        "text": [],
        "shell": [],
        "gitcommsg": []
    }
    
    # Get option details from list_cli_config_options instead of CLI_CONFIG_OPTIONS
    for option_details in list_cli_config_options():
        option = option_details["name"]
        for context in option_details["context"]:
            if context in context_groups:
                if context == "all":
                    context_groups[context].append(option)
                    break
                else:
                    context_groups[context].append(option)
    
    # Print general options (available in all contexts)
    help_text.append(f"\n  {COLORS['cyan']}Available options:{COLORS['reset']}")
    help_text.append(f"    {COLORS['yellow']}General options (all modes):{COLORS['reset']}")
    for option in sorted(context_groups["all"]):
        # Get option details
        option_detail = next((o for o in list_cli_config_options() if o["name"] == option), None)
        if option_detail:
            option_type = option_detail["type"]
            default = option_detail["default"]
            default_str = f"(default: {default})" if default is not None else "(default: None)"
            help_text.append(f"      {option} - {COLORS['cyan']}Type: {option_type}{COLORS['reset']} {default_str}")
        else:
            help_text.append(f"      {option}")
    
    # Print code options
    if context_groups["code"]:
        help_text.append(f"\n    {COLORS['yellow']}Code mode options (-c/--code):{COLORS['reset']}")
        for option in sorted(context_groups["code"]):
            # Get option details
            option_detail = next((o for o in list_cli_config_options() if o["name"] == option), None)
            if option_detail:
                option_type = option_detail["type"]
                default = option_detail["default"]
                default_str = f"(default: {default})" if default is not None else "(default: None)"
                help_text.append(f"      {option} - {COLORS['cyan']}Type: {option_type}{COLORS['reset']} {default_str}")
            else:
                help_text.append(f"      {option}")
    
    # Print interactive mode options
    if context_groups["interactive"]:
        help_text.append(f"\n    {COLORS['yellow']}Interactive mode options (-i/--interactive):{COLORS['reset']}")
        for option in sorted(context_groups["interactive"]):
            # Get option details
            option_detail = next((o for o in list_cli_config_options() if o["name"] == option), None)
            if option_detail:
                option_type = option_detail["type"]
                default = option_detail["default"]
                default_str = f"(default: {default})" if default is not None else "(default: None)"
                help_text.append(f"      {option} - {COLORS['cyan']}Type: {option_type}{COLORS['reset']} {default_str}")
            else:
                help_text.append(f"      {option}")
    
    # Print gitcommsg options
    if context_groups["gitcommsg"]:
        help_text.append(f"\n    {COLORS['yellow']}Git commit message options (-g/--gitcommsg):{COLORS['reset']}")
        for option in sorted(context_groups["gitcommsg"]):
            # Get option details
            option_detail = next((o for o in list_cli_config_options() if o["name"] == option), None)
            if option_detail:
                option_type = option_detail["type"]
                default = option_detail["default"]
                default_str = f"(default: {default})" if default is not None else "(default: None)"
                help_text.append(f"      {option} - {COLORS['cyan']}Type: {option_type}{COLORS['reset']} {default_str}")
            else:
                help_text.append(f"      {option}")
    
    help_text.append(f"\n  {COLORS['cyan']}Example usage:{COLORS['reset']}")
    help_text.append(f"    {COLORS['yellow']}ngpt --cli-config set language java{COLORS['reset']}        - Set default language to java for code generation")
    help_text.append(f"    {COLORS['yellow']}ngpt --cli-config set temperature 0.9{COLORS['reset']}      - Set default temperature to 0.9")
    help_text.append(f"    {COLORS['yellow']}ngpt --cli-config set recursive-chunk true{COLORS['reset']} - Enable recursive chunking for git commit messages")
    help_text.append(f"    {COLORS['yellow']}ngpt --cli-config set diff /path/to/file.diff{COLORS['reset']} - Set default diff file for git commit messages")
    help_text.append(f"    {COLORS['yellow']}ngpt --cli-config get temperature{COLORS['reset']}          - Check the current temperature setting")
    help_text.append(f"    {COLORS['yellow']}ngpt --cli-config get{COLORS['reset']}                      - Show all current CLI settings")
    help_text.append(f"    {COLORS['yellow']}ngpt --cli-config unset language{COLORS['reset']}           - Remove language setting")
    
    help_text.append(f"\n  {COLORS['cyan']}Notes:{COLORS['reset']}")
    help_text.append(f"    - CLI configuration is stored in:")
    help_text.append(f"      • Linux: {COLORS['yellow']}~/.config/ngpt/ngpt-cli.conf{COLORS['reset']}")
    help_text.append(f"      • macOS: {COLORS['yellow']}~/Library/Application Support/ngpt/ngpt-cli.conf{COLORS['reset']}")
    help_text.append(f"      • Windows: {COLORS['yellow']}%APPDATA%\\ngpt\\ngpt-cli.conf{COLORS['reset']}")
    help_text.append(f"    - Settings are applied based on context (e.g., language only applies to code generation mode)")
    help_text.append(f"    - Command-line arguments always override CLI configuration")
    help_text.append(f"    - Some options are mutually exclusive and will not be applied together")
    
    return "\n".join(help_text)

def handle_cli_config(action: str, option: Optional[str] = None, value: Optional[str] = None) -> None:
    """Handle CLI configuration commands.
    
    Args:
        action: The action to perform (help, get, set, unset, list)
        option: The option to operate on (for get, set, unset)
        value: The value to set (for set action)
    """
    if action == "help":
        print(show_cli_config_help())
        return
    
    if action == "list":
        # List all available options
        print(f"{COLORS['green']}{COLORS['bold']}Available CLI configuration options:{COLORS['reset']}")
        for option_details in list_cli_config_options():
            option = option_details["name"]
            option_type = option_details["type"]
            default = option_details["default"]
            contexts = option_details["context"]
            
            default_str = f"(default: {default})" if default is not None else "(default: None)"
            contexts_str = ', '.join(contexts)
            if "all" in contexts:
                contexts_str = "all modes"
            
            print(f"  {COLORS['cyan']}{option}{COLORS['reset']} - {COLORS['yellow']}Type: {option_type}{COLORS['reset']} {default_str} - Available in: {contexts_str}")
        return
    
    if action == "get":
        if option is None:
            # Get all options
            success, config = get_cli_config_option()
            if success and config:
                print(f"{COLORS['green']}{COLORS['bold']}Current CLI configuration:{COLORS['reset']}")
                for opt, val in config.items():
                    if opt in CLI_CONFIG_OPTIONS:
                        print(f"  {COLORS['cyan']}{opt}{COLORS['reset']} = {val}")
                    else:
                        print(f"  {COLORS['yellow']}{opt}{COLORS['reset']} = {val} (unknown option)")
            else:
                print(f"{COLORS['yellow']}No CLI configuration set. Use 'ngpt --cli-config set OPTION VALUE' to set options.{COLORS['reset']}")
        else:
            # Get specific option
            success, result = get_cli_config_option(option)
            if success:
                if result is None:
                    print(f"{COLORS['cyan']}{option}{COLORS['reset']} is not set (default: {CLI_CONFIG_OPTIONS.get(option, {}).get('default', 'N/A')})")
                else:
                    print(f"{COLORS['cyan']}{option}{COLORS['reset']} = {result}")
            else:
                print(f"{COLORS['yellow']}{result}{COLORS['reset']}")
        return
    
    if action == "set":
        if option is None or value is None:
            print(f"{COLORS['yellow']}Error: Both OPTION and VALUE are required for 'set' command.{COLORS['reset']}")
            print(f"Usage: ngpt --cli-config set OPTION VALUE")
            return
            
        success, message = set_cli_config_option(option, value)
        if success:
            print(f"{COLORS['green']}{message}{COLORS['reset']}")
        else:
            print(f"{COLORS['yellow']}{message}{COLORS['reset']}")
        return
    
    if action == "unset":
        if option is None:
            print(f"{COLORS['yellow']}Error: OPTION is required for 'unset' command.{COLORS['reset']}")
            print(f"Usage: ngpt --cli-config unset OPTION")
            return
            
        success, message = unset_cli_config_option(option)
        if success:
            print(f"{COLORS['green']}{message}{COLORS['reset']}")
        else:
            print(f"{COLORS['yellow']}{message}{COLORS['reset']}")
        return
    
    # If we get here, the action is not recognized
    print(f"{COLORS['yellow']}Error: Unknown action '{action}'. Use 'set', 'get', 'unset', or 'list'.{COLORS['reset']}")
    print(show_cli_config_help()) 