import shutil
from .colors import COLORS
from .tables import get_table_config

# Import Rich components
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich import box
from rich.align import Align

console = Console()


class InteractiveUI:
    def __init__(self, client, args, logger=None):
        self.client = client
        self.args = args
        self.logger = logger
        self.table_config = get_table_config(is_help_table=True)
        self.table_width = self.table_config["table_width"]
        self.separator_length = self.table_config["table_width"]
        self.separator = f"{COLORS['gray']}{'─' * self.separator_length}{COLORS['reset']}"

    def show_help(self):
        """Displays the help menu using Rich components."""
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

        # Section headers
        section_style = "cyan bold"

        # Session Commands section
        help_table.add_row(
            Text("Session Commands (prefix with '/'):", style=section_style), ""
        )

        # Sort commands alphabetically
        commands = [
            ("/editor", "Open multiline editor"),
            ("/exit", "End session"),
            ("/help", "Show this help message"),
            ("/reset", "Reset Session"),
            ("/sessions", "Manage saved sessions"),
            ("/transcript", "Show recent conversation exchanges"),
        ]
        commands.sort(key=lambda x: x[0])

        # Add command rows
        for cmd, desc in commands:
            help_table.add_row(cmd, desc)

        # Keyboard Shortcuts section
        help_table.add_row("", "")  # Empty row as spacer
        help_table.add_row(Text("Keyboard Shortcuts:", style=section_style), "")
        help_table.add_row("Ctrl+E", "Open multiline editor")
        help_table.add_row("Ctrl+C", "Interrupt/exit session")

        # Navigation section
        help_table.add_row("", "")  # Empty row as spacer
        help_table.add_row(Text("Navigation:", style=section_style), "")
        help_table.add_row("↑/↓", "Browse input history")

        # Print the help table
        console.print(help_table)

        # Print a separator line at the end
        console.print(Text("─" * self.separator_length, style="dim"))

    def show_welcome(self):
        """Shows a welcome screen with enhanced Rich formatting."""
        from ngpt.version import __version__

        # Set a fixed width for the logo panel
        panel_width = min(self.table_width, 100)
        console.print("\n")

        version_info = f"v{__version__}"

        # Detect model
        model_name = None
        if hasattr(self.client, "model"):
            model_name = self.client.model
        elif hasattr(self.client, "config") and hasattr(self.client.config, "model"):
            model_name = self.client.config.model
        elif hasattr(self.args, "model") and self.args.model:
            model_name = self.args.model

        # Truncate model name if it's too long
        if model_name and len(model_name) > 40:
            model_name = model_name[:37] + "..."

        model_info = f"Model: {model_name}" if model_name else "Default model"
        status_line = (
            f"Temperature: {self.args.temperature} | {model_info}"
        )


        # Manually center the content
        logo_lines = [
            "███╗   ██╗ ██████╗ ██████╗ ████████╗",
            "████╗  ██║██╔════╝ ██╔══██╗╚══██╔══╝",
            "██╔██╗ ██║██║  ███╗██████╔╝   ██║   ",
            "██║╚██╗██║██║   ██║██╔═══╝    ██║   ",
            "██║ ╚████║╚██████╔╝██║        ██║   ",
            "╚═╝  ╚═══╝ ╚═════╝ ╚═╝        ╚═╝   ",
        ]

        content_width = panel_width - 4  # Inner width of the panel

        # Build the final text block with manual centering and styling
        final_text = Text()
        final_text.append("\n")
        for line in logo_lines:
            final_text.append(line.center(content_width) + "\n", style="green")

        final_text.append("\n")
        final_text.append(version_info.center(content_width) + "\n", style="yellow")
        final_text.append("\n")
        final_text.append(status_line.center(content_width) + "\n", style="dim")

        # Create a welcome panel with the manually centered text
        welcome_panel = Panel(
            final_text,
            box=box.ROUNDED,
            border_style="cyan",
            width=panel_width,
            title="nGPT",
            title_align="center",
        )

        # Print the welcome panel with proper centering
        console.print(Align.center(welcome_panel))
        console.print("\n")

        # Show help info after the welcome panel
        console.print(
            Text("Type '/help' to see a list of commands.", style="dim"),
            justify="center",
        )
        console.print("")

        # Show logging info if logger is available
        if self.logger:
            console.print(
                Text(
                    f"Logging conversation to: {self.logger.get_log_path()}",
                    style="green",
                )
            )

        # Display a note about web search if enabled
        if self.args.web_search:
            console.print(Text("Web search capability is enabled.", style="green"))

    def show_conversation_preview(self, conversation):
        """Shows a preview of the current conversation history."""
        # Extract user/assistant pairs from conversation
        pairs = []
        current_pair = []
        count = 5  # Fixed count of exchanges to show

        # Skip the system message
        for msg in conversation[1:]:
            if msg["role"] == "user":
                if current_pair:
                    pairs.append(current_pair)
                current_pair = [msg]
            elif msg["role"] == "assistant" and current_pair:
                current_pair.append(msg)

        # Add the last pair if it exists
        if current_pair:
            pairs.append(current_pair)

        # Get the last N pairs
        pairs_to_show = pairs[-count:] if count < len(pairs) else pairs

        # Create a title with emoji and styling
        title = Text()
        title.append("🤖 ", style="")
        title.append("Conversation Transcript", style="cyan bold")
        title.append(" 🤖", style="")

        # Print the header with proper centering
        console.print("\n")
        console.print(title, justify="center")

        # Create a subtitle with exchange count
        subtitle = Text(
            f"Showing the last {len(pairs_to_show)} of {len(pairs)} exchanges",
            style="dim",
        )
        console.print(subtitle, justify="center")

        # Print separator
        separator_width = min(self.table_width, 50)
        console.print(Text("─" * separator_width, style="dim"), justify="center")
        console.print("")

        if not pairs_to_show:
            console.print(
                Text("No conversation history yet.", style="yellow"), justify="center"
            )
            console.print(Text("─" * separator_width, style="dim"), justify="center")
            return

        # Show pairs with nice formatting
        for i, pair in enumerate(pairs_to_show):
            # User message
            user_content = pair[0]["content"]
            if len(user_content) > 500:
                user_content = user_content[:497] + "..."

            user_panel = Panel(
                Text(user_content, style="white"),
                title=f"👤 You {i + 1}",
                title_align="left",
                border_style="cyan",
                box=box.ROUNDED,
            )
            console.print(user_panel)

            # Assistant message if available
            if len(pair) > 1:
                ai_content = pair[1]["content"]
                if len(ai_content) > 500:
                    ai_content = ai_content[:497] + "..."

                ai_panel = Panel(
                    Text(ai_content, style="white"),
                    title="🤖 nGPT",
                    title_align="left",
                    border_style="green",
                    box=box.ROUNDED,
                )
                console.print(ai_panel)
        
        console.print(Text("─" * separator_width, style="dim"), justify="center") 