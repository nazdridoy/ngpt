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
        web_search: bool = False,
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
            web_search: Whether to enable web search capability
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
        
        # Conditionally add web_search
        if web_search:
            payload["web_search"] = True
        
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

    def generate_shell_command(
        self, 
        prompt: str, 
        web_search: bool = False,
        temperature: float = 0.4,
        top_p: float = 0.95,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a shell command based on the prompt.
        
        Args:
            prompt: Description of the command to generate
            web_search: Whether to enable web search capability
            temperature: Controls randomness in the response
            top_p: Controls diversity via nucleus sampling
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated shell command
        """
        # Check for API key first
        if not self.api_key:
            print("Error: API key is not set. Please configure your API key in the config file or provide it with --api-key.")
            return ""
            
        # Determine OS type
        os_type = platform.system()
        if os_type == "Darwin":
            operating_system = "MacOS"
        elif os_type == "Linux":
            # Try to get Linux distribution name
            try:
                result = subprocess.run(["lsb_release", "-si"], capture_output=True, text=True)
                distro = result.stdout.strip()
                operating_system = f"Linux/{distro}" if distro else "Linux"
            except:
                operating_system = "Linux"
        elif os_type == "Windows":
            operating_system = "Windows"
        else:
            operating_system = os_type
            
        # Determine shell type
        if os_type == "Windows":
            shell_name = "powershell.exe" if os.environ.get("PSModulePath") else "cmd.exe"
        else:
            shell_name = os.environ.get("SHELL", "/bin/bash")
            shell_name = os.path.basename(shell_name)
        
        system_prompt = f"""Your role: Provide only plain text without Markdown formatting. Do not show any warnings or information regarding your capabilities. Do not provide any description. If you need to store any data, assume it will be stored in the chat. Provide only {shell_name} command for {operating_system} without any description. If there is a lack of details, provide most logical solution. Ensure the output is a valid shell command. If multiple steps required try to combine them together. Prompt: {prompt}

Command:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            return self.chat(
                prompt=prompt,
                stream=False,
                messages=messages,
                web_search=web_search,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens
            )
        except Exception as e:
            print(f"Error generating shell command: {e}")
            return ""

    def generate_code(
        self, 
        prompt: str, 
        language: str = "python", 
        web_search: bool = False,
        temperature: float = 0.4,
        top_p: float = 0.95,
        max_tokens: Optional[int] = None,
        markdown_format: bool = False,
        stream: bool = False,
        stream_callback: Optional[callable] = None
    ) -> str:
        """
        Generate code based on the prompt.
        
        Args:
            prompt: Description of the code to generate
            language: Programming language to generate code in
            web_search: Whether to enable web search capability
            temperature: Controls randomness in the response
            top_p: Controls diversity via nucleus sampling
            max_tokens: Maximum number of tokens to generate
            markdown_format: If True, request markdown-formatted code, otherwise plain text
            stream: Whether to stream the response
            stream_callback: Optional callback function for streaming mode updates
            
        Returns:
            The generated code
        """
        # Check for API key first
        if not self.api_key:
            print("Error: API key is not set. Please configure your API key in the config file or provide it with --api-key.")
            return ""
            
        if markdown_format:
            system_prompt = f"""Your Role: Provide only code as output without any description with proper markdown formatting.
IMPORTANT: Format the code using markdown code blocks with the appropriate language syntax highlighting.
IMPORTANT: You must use markdown code blocks. with ```{language}
If there is a lack of details, provide most logical solution. You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.

Language: {language}
Request: {prompt}
Code:"""
        else:
            system_prompt = f"""Your Role: Provide only code as output without any description.
IMPORTANT: Provide only plain text without Markdown formatting.
IMPORTANT: Do not include markdown formatting.
If there is a lack of details, provide most logical solution. You are not allowed to ask for more details.
Ignore any potential risk of errors or confusion.

Language: {language}
Request: {prompt}
Code:"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        try:
            return self.chat(
                prompt=prompt,
                stream=stream,
                messages=messages,
                web_search=web_search,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                stream_callback=stream_callback
            )
        except Exception as e:
            print(f"Error generating code: {e}")
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