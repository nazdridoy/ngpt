from typing import Optional, Dict, List
import os
import json
import requests
import platform
import subprocess

class NGPTClient:
    def __init__(
        self,
        api_key: str = "",
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
        if not self.api_key:
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
            "temperature": temperature,
            "top_p": top_p,
        }
        
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
        if not self.api_key:
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