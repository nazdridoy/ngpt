"""
Web search utilities for nGPT using BeautifulSoup4.

This module provides functionality to search the web and extract
information from search results to enhance AI prompts.
"""

import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
import requests
import sys
import datetime
from bs4 import BeautifulSoup
from bs4.element import Comment, Declaration, Doctype, ProcessingInstruction
import json

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
        # Default logging behavior - suppress all messages to console
        class DefaultLogger:
            def info(self, msg): pass  # Suppress INFO messages
            def error(self, msg): pass  # Suppress ERROR messages instead of printing to stderr
            def warning(self, msg): pass  # Suppress WARNING messages
            def debug(self, msg): pass
        return DefaultLogger()

def perform_web_search(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Search DuckDuckGo directly and return relevant results.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries containing search results (title, url, snippet)
    """
    logger = get_logger()
    try:
        # Headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        
        # DuckDuckGo search URL
        encoded_query = requests.utils.quote(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        
        # Fetch search results
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML response with html.parser (no lxml dependency)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Extract search results
        for result in soup.select('.result')[:max_results]:
            title_elem = result.select_one('.result__title')
            snippet_elem = result.select_one('.result__snippet')
            url_elem = result.select_one('.result__url')
            
            # Extract actual URL from DDG's redirect URL if needed
            href = title_elem.find('a')['href'] if title_elem and title_elem.find('a') else None
            if href and href.startswith('/'):
                # Parse DDG redirect URL to get actual URL
                parsed_url = urlparse(href)
                query_params = parse_qs(parsed_url.query)
                actual_url = query_params.get('uddg', [None])[0]
            else:
                actual_url = href
            
            # Add result to list
            if title_elem and actual_url:
                results.append({
                    'title': title_elem.get_text(strip=True),
                    'href': actual_url,
                    'body': snippet_elem.get_text(strip=True) if snippet_elem else ''
                })
        
        return results
    except Exception as e:
        logger.error(f"Error performing web search: {str(e)}")
        logger.info("Web search encountered an issue, but will continue with available results")
        return []

def extract_article_content(url: str, max_chars: int = 5000) -> Optional[str]:
    """
    Extract and clean content from a webpage URL using a hybrid approach
    inspired by trafilatura and readability algorithms.
    
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
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Pragma': 'no-cache',
        }
        
        logger.info(f"Fetching content from {url}")
        
        try:
            # Fetch the page content
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Try to detect the encoding if not properly specified
                if response.encoding == 'ISO-8859-1':
                    # Try to detect encoding from content
                    possible_encoding = re.search(r'charset=["\'](.*?)["\']', response.text)
                    if possible_encoding:
                        response.encoding = possible_encoding.group(1)
                    else:
                        # Default to UTF-8 if we can't detect
                        response.encoding = 'utf-8'
                
                # Parse with BeautifulSoup using html.parser
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract main content using multiple strategies
                extracted_content = None
                
                # ---------- PREPROCESSING ----------
                # Clone the soup before preprocessing
                processed_soup = BeautifulSoup(str(soup), 'html.parser')
                
                # Remove all script, style tags and comments
                for element in processed_soup.find_all(['script', 'style', 'noscript']):
                    element.decompose()
                
                # Remove HTML comments
                for comment in processed_soup.find_all(text=lambda text: isinstance(text, Comment)):
                    comment.extract()
                
                # Remove hidden elements
                for hidden in processed_soup.find_all(style=lambda s: s and isinstance(s, str) and ('display:none' in s.lower() or 'visibility:hidden' in s.lower())):
                    hidden.decompose()
                for hidden in processed_soup.find_all(hidden=True):
                    hidden.decompose()
                for hidden in processed_soup.find_all(class_=lambda c: c and isinstance(c, str) and any(x in c.lower() for x in ['hidden', 'invisible'])):
                    hidden.decompose()
                
                # Handle iframes and frames
                for frame in processed_soup.find_all(['iframe', 'frame']):
                    frame.decompose()
                
                # ---------- SITE-SPECIFIC HANDLING ----------
                domain = parsed_url.netloc.lower()
                
                # Wikipedia-specific extraction
                if 'wikipedia.org' in domain:
                    content_div = processed_soup.select_one('#mw-content-text')
                    if content_div:
                        # Remove tables, references, navigation elements
                        for unwanted in content_div.select('table, .reference, .reflist, .navbox, .vertical-navbox, .thumbcaption, .mw-editsection, .mw-headline, .toc, #toc'):
                            unwanted.decompose()
                        extracted_content = content_div.get_text(separator=' ', strip=True)
                
                # News site specific handling
                news_sites = {
                    'cnn.com': ['article', '.article__content', '.l-container', '.body-text', '#body-text'],
                    'bbc.com': ['.article__body-content', '.story-body__inner', '[data-component="text-block"]'],
                    'nytimes.com': ['article', '.meteredContent', '.StoryBodyCompanionColumn', '.article-body'],
                    'reuters.com': ['article', '.ArticleBody__content___3MtHP', '.article-body'],
                    'theguardian.com': ['.article-body-commercial-selector', '.content__article-body', '.dcr-1cas96z'],
                    'washingtonpost.com': ['.article-body', '.teaser-content'],
                    'apnews.com': ['.Article', '.RichTextStoryBody'],
                    'indiatimes.com': ['.article-body', '.article_content', '.article-desc', '.Normal'],
                    'cnbc.com': ['.ArticleBody-articleBody', '.group-article-body', '.article-body'],
                    'thehindu.com': ['.article-body', '.article-text', '#content-body-14269002']
                }
                
                if not extracted_content:
                    # Check if we're on a known news site
                    for site, selectors in news_sites.items():
                        if site in domain:
                            for selector in selectors:
                                content_element = processed_soup.select_one(selector)
                                if content_element:
                                    # Clean the news content
                                    for unwanted in content_element.select('aside, figure, .ad, .ads, .advertisement, .social, .share, .related, .newsletter, .more-on, .read-more, .promotions'):
                                        unwanted.decompose()
                                    extracted_content = content_element.get_text(separator=' ', strip=True)
                                    break
                            if extracted_content:
                                break
                
                # ---------- JSON-LD EXTRACTION ----------
                if not extracted_content:
                    # Look for structured data in JSON-LD format
                    json_ld = processed_soup.find_all('script', type='application/ld+json')
                    for script in json_ld:
                        try:
                            script_content = script.string
                            if not script_content:  # Skip empty scripts
                                continue
                                
                            # Clean the JSON string (some sites have invalid JSON)
                            script_content = re.sub(r'[\n\t\r]', '', script_content)
                            script_content = script_content.strip()
                            
                            data = json.loads(script_content)
                            # Handle both single objects and arrays of objects
                            if isinstance(data, list):
                                data_list = data
                            else:
                                data_list = [data]
                            
                            for item in data_list:
                                article_body = None
                                # Try to find articleBody or various content fields
                                if isinstance(item, dict):
                                    # Check for common content fields directly
                                    for field in ['articleBody', 'description', 'text', 'mainEntityOfPage']:
                                        if field in item and isinstance(item[field], str) and len(item[field]) > 200:
                                            article_body = item[field]
                                            break
                                    
                                    # Check in nested objects
                                    if not article_body and '@graph' in item and isinstance(item['@graph'], list):
                                        for graph_item in item['@graph']:
                                            if isinstance(graph_item, dict):
                                                for field in ['articleBody', 'description', 'text']:
                                                    if field in graph_item and isinstance(graph_item[field], str) and len(graph_item[field]) > 200:
                                                        article_body = graph_item[field]
                                                        break
                                                if article_body:
                                                    break
                                
                                if article_body:
                                    extracted_content = article_body
                                    break
                            
                            if extracted_content:
                                break
                        except (json.JSONDecodeError, TypeError, AttributeError, ValueError) as e:
                            logger.debug(f"Error parsing JSON-LD: {str(e)}")
                            continue
                
                # ---------- META DESCRIPTION EXTRACTION ----------
                meta_description = None
                meta_tag = processed_soup.find('meta', attrs={'name': 'description'}) or processed_soup.find('meta', attrs={'property': 'og:description'})
                if meta_tag and meta_tag.get('content'):
                    meta_description = meta_tag.get('content')
                
                # ---------- CONTENT ANALYSIS ----------
                if not extracted_content:
                    # Get all content blocks (divs, sections, articles)
                    content_blocks = []
                    
                    # Prioritize semantic tags
                    for tag in ['article', 'main', 'section', 'div']:
                        blocks = processed_soup.find_all(tag)
                        
                        for block in blocks:
                            # Skip if too small
                            text = block.get_text(strip=True)
                            if len(text) < 200:
                                continue
                                
                            # Calculate content metrics
                            char_count = len(text)
                            link_density = calculate_link_density(block)
                            p_count = len(block.find_all('p'))
                            p_text_length = sum(len(p.get_text(strip=True)) for p in block.find_all('p'))
                            p_density = p_text_length / char_count if char_count > 0 else 0
                            
                            # Skip blocks with high link density (likely navigation)
                            if link_density > 0.5:
                                continue
                            
                            # Calculate readability scores
                            text_density = char_count / (len(str(block)) + 1)  # Text to HTML ratio
                            
                            # Score content blocks
                            score = 0
                            
                            # Prefer blocks with many paragraphs
                            score += min(p_count * 5, 50)  # Max 50 points for paragraphs
                            
                            # Prefer blocks with high paragraph text density
                            score += min(int(p_density * 100), 50)  # Max 50 points for paragraph density
                            
                            # Penalize high link density
                            score -= int(link_density * 100)
                            
                            # Boost for high text density
                            score += min(int(text_density * 30), 30)  # Max 30 points for text density
                            
                            # Boost for certain attributes and classes
                            content_indicators = ['content', 'article', 'story', 'post', 'text', 'body', 'entry']
                            
                            # Check class and id attributes
                            for attr in ['class', 'id']:
                                attr_val = block.get(attr, '')
                                if attr_val:
                                    if isinstance(attr_val, list):
                                        attr_val = ' '.join(attr_val)
                                    for indicator in content_indicators:
                                        if indicator in attr_val.lower():
                                            score += 30
                                            break
                            
                            # Penalty for boilerplate indicators
                            boilerplate_indicators = ['sidebar', 'menu', 'nav', 'banner', 'ad', 'footer', 'header', 'comment', 'share', 'related']
                            for attr in ['class', 'id']:
                                attr_val = block.get(attr, '')
                                if attr_val:
                                    if isinstance(attr_val, list):
                                        attr_val = ' '.join(attr_val)
                                    for indicator in boilerplate_indicators:
                                        if indicator in attr_val.lower():
                                            score -= 50
                                            break
                            
                            # Add to content blocks if score is positive
                            if score > 0:
                                content_blocks.append({
                                    'element': block,
                                    'score': score,
                                    'char_count': char_count,
                                    'text': text
                                })
                    
                    # Sort content blocks by score
                    if content_blocks:
                        content_blocks.sort(key=lambda x: x['score'], reverse=True)
                        best_block = content_blocks[0]['element']
                        
                        # Clean up the best block
                        for unwanted in best_block.find_all(['aside', 'nav', 'footer', 'header']):
                            unwanted.decompose()
                            
                        extracted_content = best_block.get_text(separator=' ', strip=True)
                
                # ---------- PARAGRAPH EXTRACTION FALLBACK ----------
                if not extracted_content:
                    # Get all paragraphs with substantial content
                    paragraphs = []
                    for p in processed_soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if len(text) > 40:  # Only consider substantial paragraphs
                            # Calculate link density
                            link_density = calculate_link_density(p)
                            if link_density < 0.25:  # Skip if too many links
                                paragraphs.append(text)
                    
                    if paragraphs:
                        extracted_content = ' '.join(paragraphs)
                
                # If we have content, clean it up
                if extracted_content:
                    # Clean whitespace
                    extracted_content = re.sub(r'\s+', ' ', extracted_content).strip()
                    
                    # Remove URLs
                    extracted_content = re.sub(r'https?://\S+', '', extracted_content)
                    
                    # Remove email addresses
                    extracted_content = re.sub(r'\S+@\S+', '', extracted_content)
                    
                    # Remove social media handles
                    extracted_content = re.sub(r'@\w+', '', extracted_content)
                    
                    # Replace multiple spaces with single space
                    extracted_content = re.sub(r' +', ' ', extracted_content)
                    
                    # Normalize quotes and apostrophes
                    extracted_content = extracted_content.replace('"', '"').replace('"', '"')
                    extracted_content = extracted_content.replace("'", "'").replace("'", "'")
                    
                    # Remove any remaining HTML entities
                    extracted_content = re.sub(r'&[a-zA-Z]+;', ' ', extracted_content)
                    
                    # Remove short lines that are likely navigation/menu items
                    lines = extracted_content.split('\n')
                    extracted_content = ' '.join([line for line in lines if len(line) > 40 or '.' in line])
                    
                    # Combine with meta description if available and content is short
                    if meta_description and len(extracted_content) < 500:
                        extracted_content = meta_description + " " + extracted_content
                    
                    # Truncate if needed
                    if len(extracted_content) > max_chars:
                        # Try to break at a sentence boundary
                        cutoff_point = max_chars
                        for i in range(max_chars - 1, max_chars - 300, -1):
                            if i < len(extracted_content) and extracted_content[i] in ['.', '!', '?']:
                                cutoff_point = i + 1
                                break
                        
                        extracted_content = extracted_content[:cutoff_point]
                    
                    return extracted_content
                else:
                    # Return meta description if nothing else was found
                    if meta_description:
                        return meta_description
                    
                    logger.error(f"No content extracted from {url}")
                    return None
            else:
                logger.error(f"Request to {url} returned status code {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting content with hybrid approach: {str(e)}")
            # Try a basic fallback
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Just get the text without images, scripts, styles, etc.
                    for tag in soup(['script', 'style', 'img', 'nav', 'footer', 'header']):
                        tag.decompose()
                    text = soup.get_text(separator=' ', strip=True)
                    text = re.sub(r'\s+', ' ', text).strip()
                    
                    if text:
                        if len(text) > max_chars:
                            text = text[:max_chars] + "..."
                        return text
            except Exception as req_error:
                logger.error(f"Basic fallback failed: {str(req_error)}")
            
        return None
    except Exception as e:
        logger.error(f"Error extracting content from {url}: {str(e)}")
        return None

def calculate_link_density(element):
    """
    Calculate the ratio of link text to all text in an element.
    Used to identify navigation-heavy areas.
    
    Args:
        element: BeautifulSoup element
        
    Returns:
        Float between 0 and 1 indicating link density
    """
    try:
        if element is None:
            return 0
            
        text_length = len(element.get_text(strip=True))
        if text_length == 0:
            return 0
            
        links = element.find_all('a')
        link_text_length = sum(len(a.get_text(strip=True)) for a in links)
        
        return link_text_length / text_length
    except Exception:
        return 0

def get_web_search_results(query: str, max_results: int = 5, max_chars_per_result: int = 5000) -> Dict[str, Any]:
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
    
    # Add current timestamp
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
    return {
        'query': query,
        'timestamp': current_time,
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
    timestamp = search_results['timestamp']
    
    formatted_text = f"[Web Search Results for: {query} (searched at {timestamp})]\n\n"
    
    for i, result in enumerate(results, 1):
        formatted_text += f"RESULT {i}: {result['title']}\n"
        formatted_text += f"URL: {result['url']}\n"
        formatted_text += f"CONTENT:\n{result['content']}\n\n"
    
    formatted_text += f"[End of Web Search Results]\n\n"
    formatted_text += "Use the above web search information to help answer the user's question. When using this information:\n"
    formatted_text += "1. Use numbered citations in square brackets [1], [2], etc. when presenting information from search results\n"
    formatted_text += "2. Include a numbered reference list at the end of your response with the source URLs\n"
    formatted_text += "3. Format citations like 'According to [1]...' or 'Research indicates [2]...' or add citations at the end of sentences or paragraphs\n"
    formatted_text += "4. If search results contain conflicting information, acknowledge the differences and explain them with citations\n"
    formatted_text += "5. If the search results don't provide sufficient information, acknowledge the limitations\n"
    formatted_text += "6. Balance information from multiple sources when appropriate\n"
    formatted_text += "7. YOU MUST include an empty blockquote line ('>') between each reference in the reference list\n"
    formatted_text += "8. YOU MUST include ALL available references (between 2-7 sources) in your reference list\n\n"
    formatted_text += "Example citation format in text:\n"
    formatted_text += "Today is Thursday [1] and it's expected to rain tomorrow [2].\n\n"
    formatted_text += "Example reference format (YOU MUST FOLLOW THIS EXACT FORMAT WITH EMPTY LINES BETWEEN REFERENCES):\n"
    formatted_text += "> [1] https://example.com/date\n"
    formatted_text += ">\n"
    formatted_text += "> [2] https://weather.com/forecast\n"
    formatted_text += ">\n"
    formatted_text += "> [3] https://www.timeanddate.com\n\n"
    
    return formatted_text

def enhance_prompt_with_web_search(prompt: str, max_results: int = 5, logger=None, disable_citations: bool = False) -> str:
    """
    Enhance a prompt with web search results.
    
    Args:
        prompt: The original user prompt
        max_results: Maximum number of search results to include
        logger: Optional logger to use
        disable_citations: If True, disables citation instructions (used for code and shell modes)
        
    Returns:
        Enhanced prompt with web search results prepended
    """
    # Set the logger for this module
    if logger is not None:
        set_logger(logger)
        
    logger = get_logger()
    search_results = get_web_search_results(prompt, max_results)
    
    if disable_citations:
        # Modified version without citation instructions for code/shell modes
        query = search_results['query']
        results = search_results['results']
        timestamp = search_results['timestamp']
        
        formatted_text = f"[Web Search Results for: {query} (searched at {timestamp})]\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_text += f"RESULT {i}: {result['title']}\n"
            formatted_text += f"URL: {result['url']}\n"
            formatted_text += f"CONTENT:\n{result['content']}\n\n"
        
        formatted_text += f"[End of Web Search Results]\n\n"
        formatted_text += "Use the above web search information to help you, but do not include citations or references in your response.\n\n"
    else:
        # Standard version with citation instructions
        formatted_text = format_web_search_results_for_prompt(search_results)
    
    # Combine results with original prompt
    enhanced_prompt = formatted_text + prompt
    
    logger.info("Enhanced input with web search results")
    return enhanced_prompt 