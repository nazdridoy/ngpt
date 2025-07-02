# ngpt utils module

from .web_search import (
    enhance_prompt_with_web_search,
    get_web_search_results,
    format_web_search_results_for_prompt
)
from .pipe import process_piped_input

__all__ = [
    # Web search utilities
    "enhance_prompt_with_web_search", "get_web_search_results", "format_web_search_results_for_prompt",
    # Input processing utilities
    "process_piped_input"
]
