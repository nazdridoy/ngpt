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

    # For data tables, use available horizontal space.
    # The -4 is a safe margin for shell padding etc.
    table_width = term_width - 4 if not is_help_table else min(term_width - 4, 100)

    # For 2-column help tables
    help_cmd_width = 36

    # For session list table (6 columns)
    session_list_idx_width = 5
    session_list_id_width = 12
    session_list_size_width = 8
    session_list_date_width = 19

    # Sum of widths for fixed columns
    # Rich adds 1 char padding between columns. 5 gaps for 6 columns.
    fixed_width = (
        session_list_idx_width
        + session_list_id_width
        + session_list_size_width
        + session_list_date_width  # Created
        + session_list_date_width  # Modified
        + 5  # for column separators
    )

    # The name column gets the rest of the space
    session_list_name_width = table_width - fixed_width

    # Ensure name column has a minimum width, otherwise it can be negative
    if session_list_name_width < 15:
        session_list_name_width = 15

    return {
        "table_width": table_width,
        "help_cmd_width": help_cmd_width,
        "session_list_widths": {
            "idx": session_list_idx_width,
            "id": session_list_id_width,
            "size": session_list_size_width,
            "name": session_list_name_width,
            "created": session_list_date_width,
            "modified": session_list_date_width,
        },
    } 