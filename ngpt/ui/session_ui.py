import os
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
from rich.panel import Panel

from .colors import COLORS
from .tables import get_table_config


console = Console()


class SessionUI:
    """Handles the interactive session management UI."""

    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.table_config = get_table_config(is_help_table=False)
        self.term_width = self.table_config["table_width"]
        self.separator = f"{COLORS['gray']}{'─' * min(self.term_width, 50)}{COLORS['reset']}"

    def print_header(self, mode_name: str = "Sessions") -> None:
        """Print a nice header with current mode using Rich."""
        # Create a title with emoji and styling
        title = Text()
        title.append("🤖 ", style="")
        title.append("nGPT Session Manager - ", style="cyan bold")
        title.append(mode_name, style="cyan bold")
        title.append(" 🤖", style="")

        # Print the header with proper centering
        console.print("\n")
        console.print(title, justify="center")

        # Print separator
        separator_width = min(self.term_width, 50)
        console.print(Text("─" * separator_width, style="dim"), justify="center")
        console.print("")  # Add a blank line

    def print_help(self) -> None:
        """Print help information using Rich formatting."""
        self.print_header("Help")

        # Create a table for command categories with fixed width
        help_table_config = get_table_config(is_help_table=True)
        table_width = help_table_config["table_width"]

        help_table = Table(
            show_header=False,
            box=None,
            padding=(0, 2),  # Add padding between columns
            width=table_width,
        )

        # Add columns for command and description with fixed width ratio
        cmd_width = help_table_config["help_cmd_width"]
        help_table.add_column("Command", style="yellow", width=cmd_width)
        help_table.add_column("Description", style="white")

        # Section headers and command rows
        section_style = "cyan bold"

        # Available Commands section
        help_table.add_row(Text("Available Commands:", style=section_style), "")
        help_table.add_row("list", "Show session list")
        help_table.add_row("preview \\[idx]", "Show preview of session messages (defaults to latest)")
        help_table.add_row("load \\[idx]", "Load a session (defaults to latest)")
        help_table.add_row("rename \\[idx] <name>", "Rename a session (defaults to latest)")
        help_table.add_row("delete \\[idx]", "Delete a single session (defaults to latest)")
        help_table.add_row("delete <idx1>,<idx2>", "Delete multiple sessions")
        help_table.add_row("delete <idx1>-<idx5>", "Delete a range of sessions")
        help_table.add_row("search <query>", "Search sessions by name")
        help_table.add_row("help", "Show this help")
        help_table.add_row("exit", "Exit session manager")

        # Preview Commands section
        help_table.add_row("", "")  # Empty row as spacer
        help_table.add_row(Text("Preview Commands:", style=section_style), "")
        help_table.add_row("head \\[idx] \\[count]", "Show first messages in session (defaults to latest)")
        help_table.add_row("tail \\[idx] \\[count]", "Show last messages in session (defaults to latest)")

        # Navigation section
        help_table.add_row("", "")  # Empty row as spacer
        help_table.add_row(Text("Navigation:", style=section_style), "")
        help_table.add_row("↑/↓", "Browse command history")

        # Session Size Legend section with colored bullets
        help_table.add_row("", "")  # Empty row as spacer
        help_table.add_row(Text("Session Size Legend:", style=section_style), "")

        # Create special rows for the bullets with correct colors
        bullet_small = Text("•", style="green")
        bullet_medium = Text("••", style="yellow")
        bullet_large = Text("•••", style="red")

        help_table.add_row(bullet_small, "Small session")
        help_table.add_row(bullet_medium, "Medium session")
        help_table.add_row(bullet_large, "Large session")

        # Print the help table
        console.print(help_table)

        # Print a separator line at the end
        console.print(Text("─" * min(self.term_width, 50), style="dim"))

    def format_sessions_for_display(
        self, sessions: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Format sessions with display metadata."""

        def get_last_modified(session):
            return session.get("last_modified") or session.get("created_at") or ""

        # Sort sessions by last modified time (oldest first)
        sorted_sessions = sorted(sessions, key=get_last_modified, reverse=False)

        # Format dates nicely and calculate session sizes
        for session in sorted_sessions:
            # Format the date
            last = session.get("last_modified") or session.get("created_at", "N/A")
            try:
                last_fmt = datetime.strptime(last, "%Y-%m-%d %H:%M:%S").strftime(
                    "%y-%m-%d %I:%M %p"
                )
                session["last_modified_fmt"] = last_fmt
            except Exception:
                session["last_modified_fmt"] = last

            # Format the created date
            created = session.get("created_at", "N/A")
            try:
                created_fmt = datetime.strptime(
                    created, "%Y-%m-%d %H:%M:%S"
                ).strftime("%y-%m-%d %I:%M %p")
                session["created_at_fmt"] = created_fmt
            except Exception:
                session["created_at_fmt"] = created

            # Calculate session size
            session_info = self.session_manager.get_session_info(session["id"])
            if session_info:
                session["size_indicator"] = session_info["size_indicator"]
                session["size_color"] = session_info["size_color"]
                session["color_name"] = session_info["color_name"]
            else:
                session["size_indicator"] = "•"
                session["size_color"] = COLORS["green"]
                session["color_name"] = "green"

        return sorted_sessions

    def print_session_list(
        self,
        sessions: List[Dict[str, Any]],
        filtered_sessions: List[Dict[str, Any]],
        current_session_idx: int,
        search_query: str = "",
    ) -> None:
        """Print session list with enhancements."""
        self.print_header("List Sessions")

        # Show search status if filtering
        if search_query:
            print(
                f"{COLORS['yellow']}Filtered by: \"{search_query}\" ({len(filtered_sessions)} results){COLORS['reset']}"
            )

        # Create a Rich table
        table = Table(
            box=box.SIMPLE,
            show_header=True,
            pad_edge=False,
            width=self.table_config["table_width"],
        )

        # Add columns
        col_widths = self.table_config["session_list_widths"]
        table.add_column(
            "idx",
            style="cyan",
            justify="left",
            width=col_widths["idx"],
        )
        table.add_column(
            "ID",
            style="cyan",
            justify="left",
            width=col_widths["id"],
        )
        table.add_column(
            "Size",
            style="cyan",
            justify="left",
            width=col_widths["size"],
        )
        table.add_column(
            "Session Name",
            style="cyan",
            justify="left",
            width=col_widths["name"],
            no_wrap=True,  # Prevent wrapping
        )
        table.add_column(
            "Created",
            style="cyan",
            justify="left",
            width=col_widths["created"],
            no_wrap=True,
        )
        table.add_column(
            "Last Modified",
            style="cyan",
            justify="left",
            width=col_widths["modified"],
            no_wrap=True,
        )

        # Add rows
        if not filtered_sessions:
            # Empty row with message
            table.add_row("", "", "", "No sessions found.", "", "", style="yellow")
        else:
            for i, session in enumerate(filtered_sessions):
                name = session["name"]
                session_id_short = (
                    session["id"].split("_")[-1] if "_" in session["id"] else session["id"]
                )
                created_fmt = session.get("created_at_fmt", "Unknown")
                last_fmt = session.get("last_modified_fmt", "Unknown")
                size_indicator = session.get("size_indicator", "•")

                # Row style based on selection
                row_style = "bold" if i == current_session_idx else None

                # Set colors for individual cells
                idx_text = Text(
                    str(i), style="cyan bold" if i == current_session_idx else "yellow"
                )
                id_text = Text(session_id_short, style="dim white")

                # Get size color directly from session
                size_style = session.get("color_name", "green")
                size_text = Text(size_indicator, style=size_style)

                # Set name and date styles
                name_style = "white bold" if i == current_session_idx else "white"
                date_style = "white" if i == current_session_idx else "dim white"

                name_text = Text(name, style=name_style)
                created_text = Text(created_fmt, style=date_style)
                modified_text = Text(last_fmt, style=date_style)

                # Add the row with all styled elements
                table.add_row(
                    idx_text,
                    id_text,
                    size_text,
                    name_text,
                    created_text,
                    modified_text,
                    end_section=(
                        i == len(filtered_sessions) - 1
                    ),  # Add separator after last row
                )

        # Print the table
        console.print(table)

        # Print command prompt
        print(self.separator)
        print(
            f"{COLORS['green']}Enter command: {COLORS['reset']}(Type 'help' for available commands)"
        )

    def show_session_preview(
        self, session: Dict[str, Any], mode: str = "tail", count: int = 5
    ) -> None:
        """Show preview of session content using Rich formatting."""
        session_file = self.session_manager.history_dir / f"session_{session['id']}.json"

        if not session_file.exists():
            console.print(Text("Session file not found.", style="red"))
            return

        try:
            with open(session_file, "r") as f:
                loaded_conversation = json.load(f)

            # Extract user/assistant pairs
            pairs = []
            current_pair = []
            for msg in loaded_conversation:
                if msg["role"] == "user":
                    if current_pair:
                        pairs.append(current_pair)
                    current_pair = [msg]
                elif msg["role"] == "assistant" and current_pair:
                    current_pair.append(msg)
            if current_pair:
                pairs.append(current_pair)

            # Get preview based on mode
            if mode == "tail":
                to_show = pairs[-count:]
                mode_desc = f"last {len(to_show)}"
            else:  # head
                to_show = pairs[:count]
                mode_desc = f"first {len(to_show)}"

            self.print_header("Preview Session")

            # Create a header with session name
            preview_header = Text()
            preview_header.append("Preview of ", style="cyan bold")
            preview_header.append(mode_desc, style="cyan bold")
            preview_header.append(" messages from: ", style="cyan bold")
            preview_header.append(session["name"], style="white")

            # Print the header
            console.print(preview_header)
            console.print(Text("─" * min(self.term_width, 50), style="dim"))

            if not to_show:
                console.print(Text("No messages found in this session.", style="yellow"))

            # Show pairs with nice Rich formatting
            for i, pair in enumerate(to_show):
                # Create user message panel
                user_content = pair[0]["content"]
                # Truncate if very long
                if len(user_content) > 500:
                    user_content = user_content[:497] + "..."

                user_panel = Panel(
                    Text(user_content),
                    title=f"👤 User {i+1}",
                    title_align="left",
                    border_style="cyan",
                    padding=(0, 1),
                    box=box.ROUNDED,
                )
                console.print(user_panel)

                # Assistant message if available
                if len(pair) > 1:
                    ai_content = pair[1]["content"]
                    # Truncate if very long
                    if len(ai_content) > 500:
                        ai_content = ai_content[:497] + "..."

                    ai_panel = Panel(
                        Text(ai_content),
                        title="🤖 AI",
                        title_align="left",
                        border_style="green",
                        padding=(0, 1),
                        box=box.ROUNDED,
                    )
                    console.print(ai_panel)

            # Print a separator and command prompt
            console.print(Text("─" * min(self.term_width, 50), style="dim"))
            console.print(
                Text(
                    "Enter command: (Type 'list' to return to session list)",
                    style="green",
                )
            )

        except Exception as e:
            console.print(Text(f"Error reading session: {str(e)}", style="red")) 