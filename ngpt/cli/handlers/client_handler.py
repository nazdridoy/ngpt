import sys
from ngpt.api.client import NGPTClient
from ngpt.core.config import load_config
from ngpt.ui.colors import COLORS

def process_config_selection(args, cli_config):
    """
    Process and select the appropriate configuration based on command line arguments and CLI config.
    
    Args:
        args: Command line arguments
        cli_config: CLI configuration
    
    Returns:
        tuple: (effective_provider, effective_config_index)
    """
    # Priority order for config selection:
    # 1. Command-line arguments (args.provider, args.config_index)
    # 2. CLI configuration (cli_config["provider"], cli_config["config-index"])
    # 3. Default values (None, 0)
    
    # Get provider/config-index from CLI config if not specified in args
    effective_provider = args.provider
    effective_config_index = args.config_index
    
    # Only apply CLI config for provider/config-index if not explicitly set on command line
    # If --config-index is explicitly provided, we should ignore provider from CLI config
    config_index_from_cli = '--config-index' in sys.argv
    provider_from_cli = '--provider' in sys.argv
    
    if not provider_from_cli and 'provider' in cli_config and not config_index_from_cli:
        effective_provider = cli_config['provider']
    
    if not config_index_from_cli and 'config-index' in cli_config and not provider_from_cli:
        effective_config_index = cli_config['config-index']
    
    # Check for mutual exclusivity between provider and config-index
    if effective_config_index != 0 and effective_provider:
        from_cli_config = not provider_from_cli and 'provider' in cli_config
        provider_source = "CLI config file (ngpt-cli.conf)" if from_cli_config else "command-line arguments"
        error_msg = f"--config-index and --provider cannot be used together. Provider from {provider_source}."
        print(f"{COLORS['bold']}{COLORS['yellow']}error: {COLORS['reset']}{error_msg}\n")
        sys.exit(2)
    
    return effective_provider, effective_config_index

def initialize_client(args, cli_config):
    """
    Initialize client with appropriate configuration.
    
    Args:
        args: Command line arguments
        cli_config: CLI configuration
    
    Returns:
        tuple: (client, active_config)
    """
    effective_provider, effective_config_index = process_config_selection(args, cli_config)
    
    # Load configuration using the effective provider/config-index
    active_config = load_config(args.config, effective_config_index, effective_provider)
    
    # Command-line arguments override config settings
    if args.api_key:
        active_config["api_key"] = args.api_key
    if args.base_url:
        active_config["base_url"] = args.base_url
    if args.model:
        active_config["model"] = args.model
    
    # Initialize client using the potentially overridden active_config
    client = NGPTClient(
        api_key=active_config.get("api_key", args.api_key),
        base_url=active_config.get("base_url", args.base_url),
        provider=active_config.get("provider"),
        model=active_config.get("model", args.model)
    )
    
    return client, active_config 