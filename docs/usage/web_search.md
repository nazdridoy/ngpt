---
layout: default
title: Web Search
parent: Usage
nav_order: 4
permalink: /usage/web_search/
---

# Web Search Feature

nGPT includes a powerful web search capability that enhances your prompts with real-time information from the web. This feature is particularly useful for:

- Getting up-to-date information that may not be in the model's training data
- Researching specific topics with authoritative sources
- Providing context for questions about current events
- Fact-checking and verification

## Using Web Search

To enable web search in nGPT, use the `--web-search` or `--web` flag:

```bash
# Basic web search query
ngpt --web-search "What are the latest developments in quantum computing?"

# Interactive mode with web search enabled
ngpt -i --web-search

# With code generation
ngpt --code --web-search "Create a function to calculate Bitcoin's current price"
```

## How It Works

When you enable web search:

1. nGPT uses DuckDuckGo to search for relevant information
2. The search results (typically 5 sources) are processed to extract the most relevant content
3. This information is added to your prompt before sending it to the AI model
4. The model can then reference this information in its response

By default, the model will include numbered citations to reference the sources it used.

## Advanced Content Extraction

nGPT uses a sophisticated content extraction algorithm that:

1. **Analyzes content density** to identify the main content of web pages
2. **Filters out boilerplate content** like navigation menus, ads, and sidebars
3. **Prioritizes semantic content blocks** based on:
   - Text-to-HTML ratio
   - Link density (lower is better)
   - Paragraph density and structure
   - Content indicators in HTML attributes

Our extraction technology uses Python's standard library and BeautifulSoup with the built-in html.parser, ensuring:

- High-quality content extraction
- Fast performance
- Minimal dependencies
- Accurate identification of main content versus navigation/boilerplate
- Special handling for popular sites like Wikipedia and major news outlets

## Configuration Options

You can set web search as your default:

```bash
# Enable web search by default
ngpt --cli-config set web-search true
```

## Example Output

When using web search, the model will typically include citations:

```
According to recent studies, quantum computing has seen several breakthroughs in 2024 [1]. 
IBM announced a new 1,000-qubit processor in March [2], while Google has demonstrated 
quantum advantage in a practical application for the first time [3].

References:
> [1] https://example.com/quantum-computing-advances-2024
>
> [2] https://research.ibm.com/blog/1000-qubit-processor
>
> [3] https://ai.googleblog.com/2024/quantum-advantage-practical
```

## Code Generation with Web Search

When combined with code generation, web search can be especially powerful:

```bash
# Generate code for a current API with web search
ngpt --code --web-search "Create a function to query the latest Hacker News API"
```

The model will be able to reference up-to-date API documentation and provide more accurate code samples.

## Limitations

- Web search results depend on the quality of the search engine results
- The extraction process may occasionally miss content from websites with unusual structures
- The feature requires internet connectivity
- Results may vary based on region and search availability

## Performance Considerations

The web search feature adds a small amount of latency to requests as it needs to:
1. Perform the search query
2. Download and process the top results
3. Extract relevant content
4. Format the information for the model

However, the benefits of having up-to-date information typically outweigh this slight increase in response time. 