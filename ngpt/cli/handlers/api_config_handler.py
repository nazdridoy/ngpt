"""
API Configuration management handler module.
Handles API configurations stored in config.json
"""
import os
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List, Union

from ngpt.ui.colors import COLORS
from ngpt.core.config import load_config, get_config_path, load_configs, add_config_entry, remove_config_entry, check_config
from ngpt.core.cli_config import load_cli_config

def handle_config_command(config_file: Union[str, bool, None], config_index: int, provider: Optional[str], remove: bool = False) -> None:
    """Handle the --config command.
    
    Args:
        config_file: Path to config file or None, or boolean True when --config is used without a path
        config_index: Index of the config to edit/show
        provider: Provider name to use
        remove: Whether to remove the config
    """
    # Convert bool to None to handle --config flag without value
    if isinstance(config_file, bool):
        config_file = None
        
    config_path = get_config_path(config_file)
    
    # Handle configuration removal if --remove flag is present
    if remove:
        # Show config details before asking for confirmation
        configs = load_configs(str(config_path))
        
        # Determine the config index to remove
        config_idx = config_index
        if provider:
            # Find config index by provider name
            matching_configs = [i for i, cfg in enumerate(configs) if cfg.get('provider', '').lower() == provider.lower()]
            if not matching_configs:
                print(f"Error: No configuration found for provider '{provider}'")
                return
            elif len(matching_configs) > 1:
                print(f"Multiple configurations found for provider '{provider}':")
                for i, idx in enumerate(matching_configs):
                    print(f"  Choice [{i+1}] → Config #{idx}: {configs[idx].get('model', 'Unknown model')}")
                
                try:
                    choice = input("Choose a configuration to remove (or press Enter to cancel): ")
                    if choice and choice.isdigit() and 1 <= int(choice) <= len(matching_configs):
                        config_idx = matching_configs[int(choice)-1]
                    else:
                        print("Configuration removal cancelled.")
                        return
                except (ValueError, IndexError, KeyboardInterrupt):
                    print("\nConfiguration removal cancelled.")
                    return
            else:
                config_idx = matching_configs[0]
        
        # Check if index is valid
        if config_idx < 0 or config_idx >= len(configs):
            print(f"Error: Configuration index {config_idx} is out of range. Valid range: 0-{len(configs)-1}")
            return
        
        # Show the configuration that will be removed
        config = configs[config_idx]
        print(f"Configuration to remove (index {config_idx}):")
        print(f"  Provider: {config.get('provider', 'N/A')}")
        print(f"  Model: {config.get('model', 'N/A')}")
        print(f"  Base URL: {config.get('base_url', 'N/A')}")
        print(f"  API Key: {'[Set]' if config.get('api_key') else '[Not Set]'}")
        
        # Ask for confirmation
        try:
            print("\nAre you sure you want to remove this configuration? [y/N] ", end='')
            response = input().lower()
            if response in ('y', 'yes'):
                remove_config_entry(config_path, config_idx)
            else:
                print("Configuration removal cancelled.")
        except KeyboardInterrupt:
            print("\nConfiguration removal cancelled by user.")
        
        return
    
    # Check if --config-index was explicitly specified in command line args
    config_index_explicit = '--config-index' in sys.argv
    provider_explicit = '--provider' in sys.argv
    
    # When only --config is used (without explicit --config-index or --provider),
    # always create a new configuration regardless of CLI config settings
    if not config_index_explicit and not provider_explicit:
        # Always create a new config when just --config is used
        configs = load_configs(str(config_path))
        print(f"Creating new configuration at index {len(configs)}")
        add_config_entry(config_path, None)
        return
    
    # If explicitly specified indexes or provider, continue with editing behavior
    config_idx = None
    
    # Determine if we're editing an existing config or creating a new one
    if provider:
        # Find config by provider name
        configs = load_configs(str(config_path))
        matching_configs = [i for i, cfg in enumerate(configs) if cfg.get('provider', '').lower() == provider.lower()]
        
        if not matching_configs:
            print(f"No configuration found for provider '{provider}'. Creating a new configuration.")
        elif len(matching_configs) > 1:
            print(f"Multiple configurations found for provider '{provider}':")
            for i, idx in enumerate(matching_configs):
                print(f"  [{i}] Index {idx}: {configs[idx].get('model', 'Unknown model')}")
            
            try:
                choice = input("Choose a configuration to edit (or press Enter for the first one): ")
                if choice and choice.isdigit() and 0 <= int(choice) < len(matching_configs):
                    config_idx = matching_configs[int(choice)]
                else:
                    config_idx = matching_configs[0]
            except (ValueError, IndexError, KeyboardInterrupt):
                config_idx = matching_configs[0]
        else:
            config_idx = matching_configs[0]
            
        print(f"Editing existing configuration at index {config_idx}")
    elif config_index != 0 or config_index_explicit:
        # Check if the index is valid
        configs = load_configs(str(config_path))
        if config_index >= 0 and config_index < len(configs):
            config_idx = config_index
            print(f"Editing existing configuration at index {config_idx}")
        else:
            print(f"Configuration index {config_index} is out of range. Creating a new configuration.")
    else:
        # Creating a new config
        configs = load_configs(str(config_path))
        print(f"Creating new configuration at index {len(configs)}")
    
    add_config_entry(config_path, config_idx)

def show_config(config_file: Union[str, bool, None], config_index: int, provider: Optional[str]) -> None:
    """Show configuration information.
    
    Args:
        config_file: Path to config file, None, or boolean True when --config is used without a path
        config_index: Index of the config to show
        provider: Provider name to use
    """
    # Convert bool to None to handle --config flag without value
    if isinstance(config_file, bool):
        config_file = None
        
    config_path = get_config_path(config_file)
    configs = load_configs(config_file)
    
    # Check CLI configuration for provider preference if not overridden by command line
    cli_config = load_cli_config()
    cli_provider = None
    if not provider and not ('--config-index' in sys.argv):
        cli_provider = cli_config.get('provider')
    
    # Show minimal config file info
    print(f"Configuration file: {config_path}")
    
    # Determine active configuration index based on priorities
    active_index = config_index
    if provider:
        # Find by explicit provider flag
        matching_configs = [i for i, cfg in enumerate(configs) if cfg.get('provider', '').lower() == provider.lower()]
        if matching_configs:
            active_index = matching_configs[0]
    elif cli_provider:
        # Find by CLI config provider
        matching_configs = [i for i, cfg in enumerate(configs) if cfg.get('provider', '').lower() == cli_provider.lower()]
        if matching_configs:
            active_index = matching_configs[0]
    
    # Check for environment variable overrides
    env_overrides = {}
    if os.environ.get("OPENAI_API_KEY"):
        env_overrides["api_key"] = "[Set via environment]"
    if os.environ.get("OPENAI_BASE_URL"):
        env_overrides["base_url"] = os.environ.get("OPENAI_BASE_URL")
    if os.environ.get("OPENAI_MODEL"):
        env_overrides["model"] = os.environ.get("OPENAI_MODEL")
    
    # Get base configuration details
    active_config = configs[active_index]
    
    # Check for duplicate provider names for warning
    provider_counts = {}
    for cfg in configs:
        cfg_provider = cfg.get('provider', 'N/A').lower()
        provider_counts[cfg_provider] = provider_counts.get(cfg_provider, 0) + 1
    
    # Show list of available configurations
    print(f"\n{COLORS['bold']}Available configurations:{COLORS['reset']} {len(configs)} total")
    for i, cfg in enumerate(configs):
        cfg_provider = cfg.get('provider', 'N/A')
        provider_display = cfg_provider
        
        # Add warning for duplicate providers
        if provider_counts.get(cfg_provider.lower(), 0) > 1:
            provider_display = f"{cfg_provider} {COLORS['yellow']}(duplicate){COLORS['reset']}"
        
        # Determine if this config is active
        active_marker = "*" if (
            (provider and cfg_provider.lower() == provider.lower()) or 
            (cli_provider and not provider and cfg_provider.lower() == cli_provider.lower()) or
            (not provider and not cli_provider and i == active_index)
        ) else " "
        
        # Display config summary with model
        print(f"[{i}]{active_marker} {COLORS['green']}{provider_display}{COLORS['reset']} - {cfg.get('model', 'N/A')} ({'[API Key Set]' if cfg.get('api_key') else '[Not Set]'})")
    
    # Display active configuration with clear separation
    print("\n" + "-" * 50)
    print(f"\n{COLORS['green']}{COLORS['bold']}Active Configuration:{COLORS['reset']}")
    
    # Display each config value with override indication
    provider_value = active_config.get('provider', 'N/A')
    print(f"  Provider: {COLORS['green']}{provider_value}{COLORS['reset']}")
    
    # API Key - only show if set
    api_key_value = "[Set]" if active_config.get('api_key') or "api_key" in env_overrides else "[Not Set]"
    if "api_key" in env_overrides:
        print(f"  API Key: {COLORS['yellow']}{api_key_value}{COLORS['reset']} {COLORS['gray']}(from environment){COLORS['reset']}")
    else:
        print(f"  API Key: {api_key_value}")
    
    # Base URL with override if present
    if "base_url" in env_overrides:
        print(f"  Base URL: {COLORS['yellow']}{env_overrides['base_url']}{COLORS['reset']} {COLORS['gray']}(from environment){COLORS['reset']}")
    else:
        print(f"  Base URL: {active_config.get('base_url', 'N/A')}")
    
    # Model with override if present
    if "model" in env_overrides:
        print(f"  Model: {COLORS['yellow']}{env_overrides['model']}{COLORS['reset']} {COLORS['gray']}(from environment){COLORS['reset']}")
    else:
        print(f"  Model: {active_config.get('model', 'N/A')}")
    
    # Display source if from CLI config
    if cli_provider and not provider and active_config.get('provider', '').lower() == cli_provider.lower():
        print(f"  {COLORS['gray']}(Selected via CLI config: provider = {cli_provider}){COLORS['reset']}")
    
    # Display environment override info if needed
    if env_overrides:
        print(f"\n{COLORS['yellow']}Note: Environment variables are overriding some configuration values.{COLORS['reset']}")
    
    # Interactive provider selection
    try:
        print(f"\n{COLORS['cyan']}Enter index number to view details or press Enter to exit:{COLORS['reset']} ", end='')
        choice = input().strip()
        
        # Skip if user just pressed Enter
        if not choice:
            return
        
        # Determine which configuration to show
        selected_index = active_index
        if choice and choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(configs):
                selected_index = idx
            else:
                print(f"{COLORS['red']}Invalid index. Showing active configuration.{COLORS['reset']}")
        
        # Get the configuration to display
        selected_config = configs[selected_index]
        selected_provider = selected_config.get('provider', 'N/A')
        is_active = (
            (selected_index == active_index) or
            (provider and selected_provider.lower() == provider.lower()) or
            (cli_provider and not provider and selected_provider.lower() == cli_provider.lower())
        )
        
        # Clear a few lines and show the selected configuration details
        print("\n" + "-" * 50)
        if is_active:
            print(f"\n{COLORS['green']}{COLORS['bold']}Active Configuration Details:{COLORS['reset']}")
        else:
            print(f"\n{COLORS['cyan']}{COLORS['bold']}Configuration Details (Index {selected_index}):{COLORS['reset']}")
        
        print(f"  Provider: {COLORS['green']}{selected_config.get('provider', 'N/A')}{COLORS['reset']}")
        print(f"  API Key: {'[Set]' if selected_config.get('api_key') else '[Not Set]'}")
        print(f"  Base URL: {selected_config.get('base_url', 'N/A')}")
        print(f"  Model: {selected_config.get('model', 'N/A')}")
        
        # If not the active configuration, show how to use it
        if not is_active:
            print(f"\n{COLORS['yellow']}To use this configuration:{COLORS['reset']}")
            print(f"  {COLORS['green']}ngpt --provider {selected_config.get('provider')} \"Your prompt\"{COLORS['reset']}  {COLORS['gray']}or{COLORS['reset']}")
            print(f"  {COLORS['green']}ngpt --config-index {selected_index} \"Your prompt\"{COLORS['reset']}")
            
    except KeyboardInterrupt:
        print("\nInteractive selection cancelled.")
    
    # Show instruction for using --provider
    print(f"\nTip: Use {COLORS['yellow']}--provider NAME{COLORS['reset']} to select a configuration by provider name.") 