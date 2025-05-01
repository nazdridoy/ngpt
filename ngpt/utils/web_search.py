"""
Web search utilities for nGPT using duckduckgo-search and trafilatura.

This module provides functionality to search the web and extract
information from search results to enhance AI prompts.
"""

import re
from typing import List, Dict, Any, Optional
from duckduckgo_search import DDGS
from urllib.parse import urlparse
import requests
import sys

# Get actual logger from global context instead of using standard logging
from . import log

# Use a global variable to store the logger provided during runtime
_logger = None

def set_logger(logger):
    """Set the logger to use for this module."""
    global _logger
    _logger = logger

def get_logger():
    """Get the current logger or use a default."""
    if _logger is not None:
        return _logger
    else:
        # Default logging to stderr if no logger provided
        class DefaultLogger:
            def info(self, msg): print(f"INFO: {msg}", file=sys.stderr)
            def error(self, msg): print(f"ERROR: {msg}", file=sys.stderr)
            def warning(self, msg): print(f"WARNING: {msg}", file=sys.stderr)
            def debug(self, msg): pass
        return DefaultLogger()

def perform_web_search(query: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Search the web using DuckDuckGo and return relevant results.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing search results (title, url, snippet)
    """
    logger = get_logger()
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        logger.error(f"Error performing web search: {str(e)}")
        logger.info("Web search encountered an issue, but will continue with available results")
        return []

def extract_article_content(url: str, max_chars: int = 2000) -> Optional[str]:
    """
    Extract and clean content from a webpage URL.
    
    Args:
        url: The URL to extract content from
        max_chars: Maximum number of characters to extract
        
    Returns:
        Cleaned article text or None if extraction failed
    """
    logger = get_logger()
    try:
        # Skip non-http URLs or suspicious domains
        parsed_url = urlparse(url)
        if not parsed_url.scheme.startswith('http'):
            return None
        
        # Browser-like user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        logger.info(f"Fetching content from {url}")
        
        try:
            # Try using trafilatura
            import trafilatura
            
            # Download with correct parameters
            # trafilatura handles user-agent internally
            downloaded = trafilatura.fetch_url(url)
            
            if downloaded:
                # Extract main content
                content = trafilatura.extract(downloaded, include_comments=False, 
                                             include_tables=False, 
                                             no_fallback=False)
                
                if content:
                    # Clean up content if needed
                    content = content.strip()
                    
                    # Truncate if needed
                    if len(content) > max_chars:
                        content = content[:max_chars] + "..."
                        
                    return content
            
            # If trafilatura failed, try direct requests
            logger.info(f"Trafilatura extraction failed for {url}, trying fallback method")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Very basic HTML cleaning
                html_content = response.text
                # Remove HTML tags
                text = re.sub(r'<[^>]+>', ' ', html_content)
                # Remove excess whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                if text:
                    if len(text) > max_chars:
                        text = text[:max_chars] + "..."
                    return text
                
            else:
                logger.error(f"Request to {url} returned status code {response.status_code}")
                
        except ImportError:
            logger.error("Trafilatura not installed. Install with 'pip install trafilatura'")
            # Try direct requests only
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Very basic HTML cleaning
                    html_content = response.text
                    text = re.sub(r'<[^>]+>', ' ', html_content)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        if len(text) > max_chars:
                            text = text[:max_chars] + "..."
                        return text
            except Exception as req_error:
                logger.error(f"Direct request fallback failed: {str(req_error)}")
                
        except Exception as e:
            logger.error(f"Error extracting content with trafilatura: {str(e)}")
            # Try the requests fallback
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    html_content = response.text
                    text = re.sub(r'<[^>]+>', ' ', html_content)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        if len(text) > max_chars:
                            text = text[:max_chars] + "..."
                        return text
            except Exception as req_error:
                logger.error(f"Direct request fallback failed: {str(req_error)}")
            
        return None
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return None

def get_web_search_results(query: str, max_results: int = 3, max_chars_per_result: int = 2000) -> Dict[str, Any]:
    """
    Get formatted web search results ready to be included in AI prompts.
    
    Args:
        query: The search query
        max_results: Maximum number of results to include
        max_chars_per_result: Maximum characters to include per result
        
    Returns:
        Dictionary containing search results and metadata
    """
    logger = get_logger()
    search_results = perform_web_search(query, max_results)
    enhanced_results = []
    success_count = 0
    failure_count = 0
    
    for result in search_results:
        content = extract_article_content(result['href'], max_chars_per_result)
        
        enhanced_results.append({
            'title': result.get('title', ''),
            'url': result.get('href', ''),
            'snippet': result.get('body', ''),
            'content': content if content else result.get('body', '')
        })
        
        if content:
            success_count += 1
        else:
            failure_count += 1
    
    # Log a user-friendly summary
    if search_results:
        if failure_count > 0:
            logger.info(f"Retrieved content from {success_count} out of {len(search_results)} sources")
        else:
            logger.info(f"Successfully retrieved content from all {success_count} sources")
    else:
        logger.error("No search results were found")
            
    return {
        'query': query,
        'timestamp': 'current_time',  # Could replace with actual timestamp
        'results': enhanced_results
    }

def format_web_search_results_for_prompt(search_results: Dict[str, Any]) -> str:
    """
    Format web search results into a string to include in AI prompts.
    
    Args:
        search_results: Dictionary of search results from get_web_search_results()
        
    Returns:
        Formatted string to include in prompts
    """
    query = search_results['query']
    results = search_results['results']
    
    formatted_text = f"[Web Search Results for: {query}]\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_text += f"RESULT {i}: {result['title']}\n"
        formatted_text += f"URL: {result['url']}\n"
        formatted_text += f"CONTENT:\n{result['content']}\n\n"
    
    formatted_text += f"[End of Web Search Results]\n\n"
    formatted_text += "Consider the above information when answering the following question:\n\n"
    
    return formatted_text

def enhance_prompt_with_web_search(prompt: str, max_results: int = 3, logger=None) -> str:
    """
    Enhance a prompt with web search results.
    
    Args:
        prompt: The original user prompt
        max_results: Maximum number of search results to include
        logger: Optional logger to use
        
    Returns:
        Enhanced prompt with web search results prepended
    """
    # Set the logger for this module
    if logger is not None:
        set_logger(logger)
        
    logger = get_logger()
    search_results = get_web_search_results(prompt, max_results)
    formatted_results = format_web_search_results_for_prompt(search_results)
    
    # Combine results with original prompt
    enhanced_prompt = formatted_results + prompt
    
    logger.info("Enhanced input with web search results")
    return enhanced_prompt 