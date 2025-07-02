"""
Role configuration handler module.
"""
import os
import json
import sys
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from ngpt.ui.colors import COLORS
from ngpt.ui.tui import get_multiline_input

# Role directory within config
ROLE_DIR_NAME = "ngpt_roles"

def get_role_directory() -> Path:
    """Get the path to the role directory, creating it if it doesn't exist."""
    # Use OS-specific paths
    if sys.platform == "win32":
        # Windows
        config_dir = Path(os.environ.get("APPDATA", "")) / "ngpt"
    elif sys.platform == "darwin":
        # macOS
        config_dir = Path.home() / "Library" / "Application Support" / "ngpt"
    else:
        # Linux and other Unix-like systems
        xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config_home:
            config_dir = Path(xdg_config_home) / "ngpt"
        else:
            config_dir = Path.home() / ".config" / "ngpt"
    
    # Create role directory if it doesn't exist
    role_dir = config_dir / ROLE_DIR_NAME
    role_dir.mkdir(parents=True, exist_ok=True)
    
    return role_dir

def _create_role(role_name: str) -> Tuple[bool, str]:
    """Create a new role with the given name.
    
    Args:
        role_name: The name of the role to create.
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role already exists
    if role_file.exists():
        return False, f"Role '{role_name}' already exists. Use --role-config edit {role_name} to modify it."
    
    print(f"Creating new role '{role_name}'. Enter system prompt below (Ctrl+D to finish):")
    
    # Get multiline input for the system prompt
    system_prompt = get_multiline_input()
    if not system_prompt:
        return False, "Role creation cancelled."
    
    # Create role data
    role_data = {
        "name": role_name,
        "system_prompt": system_prompt
    }
    
    # Save role to file
    try:
        with open(role_file, 'w') as f:
            json.dump(role_data, f, indent=2)
        return True, f"Role '{role_name}' created successfully."
    except Exception as e:
        return False, f"Error creating role: {str(e)}"

def _edit_role(role_name: str) -> Tuple[bool, str]:
    """Edit an existing role with the given name.
    
    Args:
        role_name: The name of the role to edit.
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role exists
    if not role_file.exists():
        return False, f"Role '{role_name}' does not exist."
    
    # Load existing role data
    try:
        with open(role_file, 'r') as f:
            role_data = json.load(f)
        
        print(f"Editing role '{role_name}'. Current system prompt will be loaded in the editor.")
        
        # Get multiline input for the new system prompt with the current one pre-loaded
        system_prompt = get_multiline_input(initial_text=role_data['system_prompt'])
        if not system_prompt:
            return False, "Role edit cancelled."
        
        # Update role data
        role_data['system_prompt'] = system_prompt
        
        # Save updated role to file
        with open(role_file, 'w') as f:
            json.dump(role_data, f, indent=2)
        
        return True, f"Role '{role_name}' updated successfully."
    except Exception as e:
        return False, f"Error editing role: {str(e)}"

def _show_role(role_name: str) -> Tuple[bool, str]:
    """Show details of a role with the given name.
    
    Args:
        role_name: The name of the role to show.
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role exists
    if not role_file.exists():
        return False, f"Role '{role_name}' does not exist."
    
    # Load role data
    try:
        with open(role_file, 'r') as f:
            role_data = json.load(f)
        
        output = [
            f"\n{COLORS['bold']}Role: {COLORS['cyan']}{role_name}{COLORS['reset']}",
            f"\n{COLORS['bold']}System Prompt:{COLORS['reset']}",
            f"{COLORS['cyan']}{role_data['system_prompt']}{COLORS['reset']}"
        ]
        
        return True, "\n".join(output)
    except Exception as e:
        return False, f"Error showing role: {str(e)}"

def _list_roles() -> Tuple[bool, str]:
    """List all available roles.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    role_dir = get_role_directory()
    
    # Get all JSON files in the role directory
    try:
        role_files = list(role_dir.glob("*.json"))
        
        if not role_files:
            return True, f"{COLORS['yellow']}No roles found. Use --role-config create <role_name> to create a new role.{COLORS['reset']}"
        
        output = [f"\n{COLORS['bold']}Available Roles:{COLORS['reset']}"]
        for role_file in sorted(role_files):
            role_name = role_file.stem
            output.append(f" • {COLORS['cyan']}{role_name}{COLORS['reset']}")
        
        return True, "\n".join(output)
    except Exception as e:
        return False, f"Error listing roles: {str(e)}"

def _remove_role(role_name: str) -> Tuple[bool, str]:
    """Remove a role with the given name.
    
    Args:
        role_name: The name of the role to remove.
        
    Returns:
        Tuple[bool, str]: (success, message)
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role exists
    if not role_file.exists():
        return False, f"Role '{role_name}' does not exist."
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to remove the role '{role_name}'? (y/N): ")
    if confirm.lower() not in ["y", "yes"]:
        return False, "Role removal cancelled."
    
    # Remove role file
    try:
        os.remove(role_file)
        return True, f"Role '{role_name}' removed successfully."
    except Exception as e:
        return False, f"Error removing role: {str(e)}"

def get_role_prompt(role_name: str) -> Optional[str]:
    """Get the system prompt for a role with the given name.
    
    Args:
        role_name: The name of the role.
        
    Returns:
        Optional[str]: The system prompt for the role, or None if the role does not exist.
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role exists
    if not role_file.exists():
        print(f"{COLORS['yellow']}Role '{role_name}' does not exist.{COLORS['reset']}")
        return None
    
    # Load role data
    try:
        with open(role_file, 'r') as f:
            role_data = json.load(f)
        
        return role_data.get('system_prompt')
    except Exception as e:
        print(f"{COLORS['red']}Error loading role: {str(e)}{COLORS['reset']}")
        return None

def show_help() -> str:
    """Show help information for role configuration.
    
    Returns:
        str: The help text
    """
    help_text = [
        f"\n{COLORS['bold']}Role Configuration Help:{COLORS['reset']}",
        f"  {COLORS['cyan']}--role-config help{COLORS['reset']} - Show this help information",
        f"  {COLORS['cyan']}--role-config create <role_name>{COLORS['reset']} - Create a new role",
        f"  {COLORS['cyan']}--role-config show <role_name>{COLORS['reset']} - Show details of a role",
        f"  {COLORS['cyan']}--role-config edit <role_name>{COLORS['reset']} - Edit an existing role",
        f"  {COLORS['cyan']}--role-config list{COLORS['reset']} - List all available roles",
        f"  {COLORS['cyan']}--role-config remove <role_name>{COLORS['reset']} - Remove a role",
        f"\n{COLORS['bold']}Usage Examples:{COLORS['reset']}",
        f"  {COLORS['cyan']}ngpt --role-config create json_generator{COLORS['reset']} - Create a new role for generating JSON",
        f"  {COLORS['cyan']}ngpt --role json_generator \"generate random user data\"{COLORS['reset']} - Use the json_generator role"
    ]
    return "\n".join(help_text)

def handle_role_config(action: str, role_name: Optional[str] = None) -> bool:
    """Handle role configuration based on the action and role name.
    
    Args:
        action: The action to perform (help, create, show, edit, list, remove).
        role_name: The name of the role (or None for actions like list and help).
        
    Returns:
        bool: True if the action was handled successfully, False otherwise.
    """
    if action == "help":
        print(show_help())
        return True
    
    handlers = {
        "create": _create_role,
        "show": _show_role,
        "edit": _edit_role,
        "list": _list_roles,
        "remove": _remove_role
    }
    
    if action not in handlers:
        print(f"{COLORS['yellow']}Unknown action: {action}{COLORS['reset']}")
        print(show_help())
        return False
    
    # List doesn't need a role name
    if action == "list":
        success, message = handlers[action]()
    else:
        if not role_name:
            print(f"{COLORS['yellow']}Error: Role name is required for '{action}' action.{COLORS['reset']}")
            return False
        success, message = handlers[action](role_name)
    
    # Print the result with appropriate color
    color = COLORS['green'] if success else COLORS['yellow']
    print(f"{color}{message}{COLORS['reset']}")
    
    return success 