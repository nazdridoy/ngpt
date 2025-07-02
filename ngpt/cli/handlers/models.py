"""
Models handler module.
"""
from typing import Dict, Any

from ngpt.api.client import NGPTClient

def list_models(client: NGPTClient, active_config: Dict[str, Any]) -> None:
    """List available models from the API.
    
    Args:
        client: Initialized NGPTClient
        active_config: Active configuration dictionary
    """
    print("Retrieving available models...")
    models = client.list_models()
    if models:
        print(f"\nAvailable models for {active_config.get('provider', 'API')}:")
        print("-" * 50)
        for model in models:
            if "id" in model:
                owned_by = f" ({model.get('owned_by', 'Unknown')})" if "owned_by" in model else ""
                current = " [active]" if model["id"] == active_config["model"] else ""
                print(f"- {model['id']}{owned_by}{current}")
        print("\nUse --model MODEL_NAME to select a specific model")
    else:
        print("No models available or could not retrieve models.") 