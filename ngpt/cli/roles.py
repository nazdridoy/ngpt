import os
import json
import sys
from pathlib import Path
from .formatters import COLORS
from .ui import get_multiline_input

# Role directory within config
ROLE_DIR_NAME = "ngpt_roles"

def get_role_directory():
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

def create_role(role_name):
    """Create a new role with the given name.
    
    Args:
        role_name: The name of the role to create.
        
    Returns:
        bool: True if the role was created successfully, False otherwise.
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role already exists
    if role_file.exists():
        print(f"{COLORS['yellow']}Role '{role_name}' already exists. Use --role-config edit {role_name} to modify it.{COLORS['reset']}")
        return False
    
    print(f"Creating new role '{role_name}'. Enter system prompt below (Ctrl+D to finish):")
    
    # Get multiline input for the system prompt
    system_prompt = get_multiline_input()
    if not system_prompt:
        print(f"{COLORS['yellow']}Role creation cancelled.{COLORS['reset']}")
        return False
    
    # Create role data
    role_data = {
        "name": role_name,
        "system_prompt": system_prompt
    }
    
    # Save role to file
    try:
        with open(role_file, 'w') as f:
            json.dump(role_data, f, indent=2)
        print(f"{COLORS['green']}Role '{role_name}' created successfully.{COLORS['reset']}")
        return True
    except Exception as e:
        print(f"{COLORS['red']}Error creating role: {str(e)}{COLORS['reset']}")
        return False

def edit_role(role_name):
    """Edit an existing role with the given name.
    
    Args:
        role_name: The name of the role to edit.
        
    Returns:
        bool: True if the role was edited successfully, False otherwise.
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role exists
    if not role_file.exists():
        print(f"{COLORS['yellow']}Role '{role_name}' does not exist.{COLORS['reset']}")
        return False
    
    # Load existing role data
    try:
        with open(role_file, 'r') as f:
            role_data = json.load(f)
        
        print(f"Editing role '{role_name}'. Current system prompt will be loaded in the editor.")
        
        # Get multiline input for the new system prompt with the current one pre-loaded
        system_prompt = get_multiline_input(initial_text=role_data['system_prompt'])
        if not system_prompt:
            print(f"{COLORS['yellow']}Role edit cancelled.{COLORS['reset']}")
            return False
        
        # Update role data
        role_data['system_prompt'] = system_prompt
        
        # Save updated role to file
        with open(role_file, 'w') as f:
            json.dump(role_data, f, indent=2)
        
        print(f"{COLORS['green']}Role '{role_name}' updated successfully.{COLORS['reset']}")
        return True
    except Exception as e:
        print(f"{COLORS['red']}Error editing role: {str(e)}{COLORS['reset']}")
        return False

def show_role(role_name):
    """Show details of a role with the given name.
    
    Args:
        role_name: The name of the role to show.
        
    Returns:
        bool: True if the role was found and displayed, False otherwise.
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role exists
    if not role_file.exists():
        print(f"{COLORS['yellow']}Role '{role_name}' does not exist.{COLORS['reset']}")
        return False
    
    # Load role data
    try:
        with open(role_file, 'r') as f:
            role_data = json.load(f)
        
        print(f"\n{COLORS['bold']}Role: {COLORS['cyan']}{role_name}{COLORS['reset']}")
        print(f"\n{COLORS['bold']}System Prompt:{COLORS['reset']}")
        print(f"{COLORS['cyan']}{role_data['system_prompt']}{COLORS['reset']}")
        
        return True
    except Exception as e:
        print(f"{COLORS['red']}Error showing role: {str(e)}{COLORS['reset']}")
        return False

def list_roles():
    """List all available roles.
    
    Returns:
        bool: True if roles were listed successfully, False otherwise.
    """
    role_dir = get_role_directory()
    
    # Get all JSON files in the role directory
    try:
        role_files = list(role_dir.glob("*.json"))
        
        if not role_files:
            print(f"{COLORS['yellow']}No roles found. Use --role-config create <role_name> to create a new role.{COLORS['reset']}")
            return True
        
        print(f"\n{COLORS['bold']}Available Roles:{COLORS['reset']}")
        for role_file in sorted(role_files):
            role_name = role_file.stem
            print(f" • {COLORS['cyan']}{role_name}{COLORS['reset']}")
        
        return True
    except Exception as e:
        print(f"{COLORS['red']}Error listing roles: {str(e)}{COLORS['reset']}")
        return False

def remove_role(role_name):
    """Remove a role with the given name.
    
    Args:
        role_name: The name of the role to remove.
        
    Returns:
        bool: True if the role was removed successfully, False otherwise.
    """
    role_dir = get_role_directory()
    role_file = role_dir / f"{role_name}.json"
    
    # Check if role exists
    if not role_file.exists():
        print(f"{COLORS['yellow']}Role '{role_name}' does not exist.{COLORS['reset']}")
        return False
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to remove the role '{role_name}'? (y/N): ")
    if confirm.lower() not in ["y", "yes"]:
        print(f"{COLORS['yellow']}Role removal cancelled.{COLORS['reset']}")
        return False
    
    # Remove role file
    try:
        os.remove(role_file)
        print(f"{COLORS['green']}Role '{role_name}' removed successfully.{COLORS['reset']}")
        return True
    except Exception as e:
        print(f"{COLORS['red']}Error removing role: {str(e)}{COLORS['reset']}")
        return False

def get_role_prompt(role_name):
    """Get the system prompt for a role with the given name.
    
    Args:
        role_name: The name of the role.
        
    Returns:
        str or None: The system prompt for the role, or None if the role does not exist.
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

def show_help():
    """Show help information for role configuration."""
    print(f"\n{COLORS['bold']}Role Configuration Help:{COLORS['reset']}")
    print(f"  {COLORS['cyan']}--role-config help{COLORS['reset']} - Show this help information")
    print(f"  {COLORS['cyan']}--role-config create <role_name>{COLORS['reset']} - Create a new role")
    print(f"  {COLORS['cyan']}--role-config show <role_name>{COLORS['reset']} - Show details of a role")
    print(f"  {COLORS['cyan']}--role-config edit <role_name>{COLORS['reset']} - Edit an existing role")
    print(f"  {COLORS['cyan']}--role-config list{COLORS['reset']} - List all available roles")
    print(f"  {COLORS['cyan']}--role-config remove <role_name>{COLORS['reset']} - Remove a role")
    print(f"\n{COLORS['bold']}Usage Examples:{COLORS['reset']}")
    print(f"  {COLORS['cyan']}ngpt --role-config create json_generator{COLORS['reset']} - Create a new role for generating JSON")
    print(f"  {COLORS['cyan']}ngpt --role json_generator \"generate random user data\"{COLORS['reset']} - Use the json_generator role")

def handle_role_config(action, role_name):
    """Handle role configuration based on the action and role name.
    
    Args:
        action: The action to perform (help, create, show, edit, list, remove).
        role_name: The name of the role (or None for actions like list and help).
        
    Returns:
        bool: True if the action was handled successfully, False otherwise.
    """
    if action == "help":
        show_help()
        return True
    elif action == "create":
        return create_role(role_name)
    elif action == "show":
        return show_role(role_name)
    elif action == "edit":
        return edit_role(role_name)
    elif action == "list":
        return list_roles()
    elif action == "remove":
        return remove_role(role_name)
    else:
        # This shouldn't happen due to prior validation
        print(f"{COLORS['yellow']}Unknown action: {action}{COLORS['reset']}")
        show_help()
        return False