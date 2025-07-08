import shutil
from typing import Optional


def get_terminal_width() -> int:
    """Get terminal width for better formatting."""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


def get_table_config(is_help_table: bool = False) -> dict:
    """
    Get consistent styling configuration for tables.
    - Help tables get a fixed max width for readability.
    - Data tables (like session list) use available horizontal space.
    """
    term_width = get_terminal_width()
    max_width = 100 if is_help_table else term_width
    table_width = min(term_width - 4, max_width)

    # For 2-column help tables
    help_cmd_width = 36

    # For session list table (4 columns)
    session_list_idx_width = 6
    session_list_size_width = 8
    remaining_width = table_width - session_list_idx_width - session_list_size_width
    session_list_name_width = int(remaining_width * 0.6)
    session_list_date_width = remaining_width - session_list_name_width

    return {
        "table_width": table_width,
        "help_cmd_width": help_cmd_width,
        "session_list_widths": {
            "idx": session_list_idx_width,
            "size": session_list_size_width,
            "name": session_list_name_width,
            "date": session_list_date_width,
        },
    } 