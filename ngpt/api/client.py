from typing import Optional, Dict, List
import os
import json
import requests
import platform
import subprocess
import sys

class NGPTClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1/",
        provider: str = "OpenAI",
        model: str = "gpt-3.5-turbo"
    ):
        self.api_key = api_key
        # Ensure base_url ends with /
        self.base_url = base_url if base_url.endswith('/') else base_url + '/'
        self.model = model
        
        # Default headers
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def chat(
        self,
        prompt: str,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        messages: Optional[List[Dict[str, str]]] = None,
        markdown_format: bool = False,
        stream_callback: Optional[callable] = None,
        **kwargs
    ) -> str:
        """
        Send a chat message to the API and get a response.
        
        Args:
            prompt: The user's message
            stream: Whether to stream the response
            temperature: Controls randomness in the response
            max_tokens: Maximum number of tokens to generate
            top_p: Controls diversity via nucleus sampling
            messages: Optional list of message objects to override default behavior
            markdown_format: If True, allow markdown-formatted responses, otherwise plain text
            stream_callback: Optional callback function for streaming mode updates
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            The generated response as a string
        """
        # Allow blank API keys for local endpoints that don't require authentication
        # Only show error if api_key is None (not explicitly set) rather than empty string
        if self.api_key is None:
            print("Error: API key is not set. Please configure your API key in the config file or provide it with --api-key.")
            return ""
            
        if messages is None:
            if markdown_format:
                system_message = {"role": "system", "content": "You can use markdown formatting in your responses where appropriate."}
                messages = [system_message, {"role": "user", "content": prompt}]
            else:
                messages = [{"role": "user", "content": prompt}]
        
        # Prepare API parameters
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "top_p": top_p,
        }
        
        # Handle model-specific parameter constraints
        # Check if temperature was explicitly set by user
        temperature_explicitly_set = '--temperature' in sys.argv
        
        # Models that only support temperature=1.0 (no custom values)
        temp_restricted_models = ["gpt-5", "o1", "o3", "o4"]
        model_temp_restricted = any(self.model.startswith(prefix) for prefix in temp_restricted_models)
        
        if model_temp_restricted:
            # Models like GPT-5, o1, o3, o4 that only support temperature=1.0
            if temperature_explicitly_set and temperature != 1.0:
                # User explicitly set a non-1.0 temperature
                model_family = next(prefix for prefix in temp_restricted_models if self.model.startswith(prefix))
                print(f"\n\nError: {model_family.upper()} models only support temperature=1 (default).")
                print(f"You specified --temperature {temperature}, but {self.model} only accepts temperature=1.")
                print(f"\nSolution: Remove the --temperature flag or use a different model that supports custom temperature values.\n\n")
                sys.exit(1)
            elif temperature_explicitly_set and temperature == 1.0:
                # User explicitly set temperature=1, which is supported
                payload["temperature"] = temperature
            # If temperature not explicitly set, omit it (model will use default)
        else:
            # Other models support custom temperature values
            payload["temperature"] = temperature
        # Add max_tokens if provided
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
            
        # Add any additional parameters
        payload.update(kwargs)
        
        # Endpoint for chat completions
        endpoint = "chat/completions"
        url = f"{self.base_url}{endpoint}"
        
        try:
            if not stream:
                # Regular request
                try:
                    response = requests.post(url, headers=self.headers, json=payload)
                    response.raise_for_status()  # Raise exception for HTTP errors
                    result = response.json()
                    
                    # Extract content from response
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    return ""
                except KeyboardInterrupt:
                    print("\nRequest cancelled by user.")
                    return ""
            else:
                # Streaming request
                collected_content = ""
                with requests.post(url, headers=self.headers, json=payload, stream=True) as response:
                    # Check for specific error conditions before raising
                    if response.status_code == 400:
                        try:
                            error_data = response.json()
                            error_message = error_data.get('error', {}).get('message', '')
                            error_param = error_data.get('error', {}).get('param', '')
                            error_code = error_data.get('error', {}).get('code', '')
                            
                            # Handle organization verification error for streaming
                            if 'organization must be verified to stream' in error_message.lower() and error_param == 'stream':
                                print(f"\n\nError: {error_message}")
                                print(f"\nTo use {self.model} without organization verification, add the --plaintext flag:")
                                print(f"  ngpt --plaintext --provider OpenAI --model {self.model} \"your prompt\"\n\n")
                                sys.exit(1)
                        except (json.JSONDecodeError, KeyError):
                            pass  # Fall through to normal error handling
                    
                    response.raise_for_status()  # Raise exception for HTTP errors
                    
                    try:
                        for line in response.iter_lines():
                            if not line:
                                continue
                                
                            # Handle SSE format
                            line = line.decode('utf-8')
                            if line.startswith('data: '):
                                line = line[6:]  # Remove 'data: ' prefix
                                
                                # Skip keep-alive lines
                                if line == "[DONE]":
                                    break
                                    
                                try:
                                    chunk = json.loads(line)
                                    if "choices" in chunk and len(chunk["choices"]) > 0:
                                        delta = chunk["choices"][0].get("delta", {})
                                        content = delta.get("content", "")
                                        if content:
                                            if stream_callback:
                                                # If we have a callback, use it and don't print here
                                                collected_content += content
                                                stream_callback(collected_content)
                                            else:
                                                # Default behavior: print to console
                                                print(content, end="", flush=True)
                                                collected_content += content
                                except json.JSONDecodeError:
                                    pass  # Skip invalid JSON
                    except KeyboardInterrupt:
                        print("\nGeneration cancelled by user.")
                        return collected_content
                
                # Only print a newline if we're not using a callback
                if not stream_callback:
                    print()  # Add a final newline
                return collected_content
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("Error: Authentication failed. Please check your API key.")
            elif e.response.status_code == 404:
                print(f"Error: Endpoint not found at {url}")
            elif e.response.status_code == 429:
                print("Error: Rate limit exceeded. Please try again later.")
            elif e.response.status_code == 400:
                print(f"HTTP Error (400): {e.response.text}")
            else:
                print(f"HTTP Error: {e}")
            return ""
            
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to {self.base_url}. Please check your internet connection and base URL.")
            return ""
            
        except requests.exceptions.Timeout:
            print("Error: Request timed out. Please try again later.")
            return ""
            
        except requests.exceptions.RequestException as e:
            print(f"Error: An error occurred while making the request: {e}")
            return ""
            
        except Exception as e:
            print(f"Error: An unexpected error occurred: {e}")
            return ""

    def list_models(self) -> list:
        """
        Retrieve the list of available models from the API.
        
        Returns:
            List of available model objects or empty list if failed
        """
        # Allow blank API keys for local endpoints that don't require authentication
        # Only show error if api_key is None (not explicitly set) rather than empty string
        if self.api_key is None:
            print("Error: API key is not set. Please configure your API key in the config file or provide it with --api-key.")
            return []
            
        # Endpoint for models
        url = f"{self.base_url}models"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            result = response.json()
            
            if "data" in result:
                return result["data"]
            else:
                print("Error: Unexpected response format when retrieving models.")
                return []
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("Error: Authentication failed. Please check your API key.")
            elif e.response.status_code == 404:
                print(f"Error: Models endpoint not found at {url}")
            elif e.response.status_code == 429:
                print("Error: Rate limit exceeded. Please try again later.")
            else:
                print(f"HTTP Error: {e}")
            return []
            
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to {self.base_url}. Please check your internet connection and base URL.")
            return []
            
        except Exception as e:
            print(f"Error: An unexpected error occurred while retrieving models: {e}")
            return [] 