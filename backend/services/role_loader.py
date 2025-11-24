"""
Role Loader Service

Loads and validates role configurations from roles.json.
Provides role selection and validation logic.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

from models.data_models import Role


class RoleLoaderError(Exception):
    """Exception raised for role loading errors."""
    pass


class RoleLoader:
    """Service for loading and managing interview role configurations."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the RoleLoader.
        
        Args:
            config_path: Path to roles.json file. If None, uses default location.
        """
        if config_path is None:
            # Default to backend/config/roles.json
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "roles.json"
        
        self.config_path = Path(config_path)
        self._roles: Dict[str, Role] = {}
        self._loaded = False
    
    def load_roles(self) -> Dict[str, Role]:
        """
        Load roles from the configuration file.
        
        Returns:
            Dictionary mapping role names to Role objects.
            
        Raises:
            RoleLoaderError: If the file cannot be loaded or is invalid.
        """
        if not self.config_path.exists():
            raise RoleLoaderError(f"Role configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise RoleLoaderError(f"Invalid JSON in role configuration: {e}")
        except Exception as e:
            raise RoleLoaderError(f"Error reading role configuration: {e}")
        
        # Validate structure
        if "roles" not in data:
            raise RoleLoaderError("Role configuration must contain 'roles' key")
        
        roles_data = data["roles"]
        if not isinstance(roles_data, dict):
            raise RoleLoaderError("'roles' must be a dictionary")
        
        # Parse and validate each role
        self._roles = {}
        for role_name, role_config in roles_data.items():
            try:
                role = self._parse_role(role_name, role_config)
                self._validate_role(role)
                self._roles[role_name] = role
            except Exception as e:
                raise RoleLoaderError(f"Error loading role '{role_name}': {e}")
        
        if not self._roles:
            raise RoleLoaderError("No valid roles found in configuration")
        
        self._loaded = True
        return self._roles
    
    def _parse_role(self, role_name: str, config: dict) -> Role:
        """
        Parse a role configuration into a Role object.
        
        Args:
            role_name: Name of the role
            config: Role configuration dictionary
            
        Returns:
            Role object
        """
        return Role(
            name=config.get("name", role_name),
            display_name=config.get("display_name", role_name.replace("_", " ").title()),
            questions=config.get("questions", []),
            evaluation_criteria=config.get("evaluation_criteria", {})
        )
    
    def _validate_role(self, role: Role) -> None:
        """
        Validate a role configuration.
        
        Args:
            role: Role object to validate
            
        Raises:
            ValueError: If the role configuration is invalid
        """
        # Validate role name
        if not role.name:
            raise ValueError("Role name cannot be empty")
        
        # Validate questions
        if not role.questions:
            raise ValueError(f"Role '{role.name}' must have at least one question")
        
        if len(role.questions) < 8:
            raise ValueError(f"Role '{role.name}' should have at least 8 questions (has {len(role.questions)})")
        
        for i, question in enumerate(role.questions):
            if not isinstance(question, str) or not question.strip():
                raise ValueError(f"Role '{role.name}' question {i+1} is invalid")
        
        # Validate evaluation criteria
        if not role.evaluation_criteria:
            raise ValueError(f"Role '{role.name}' must have evaluation criteria")
        
        required_criteria = {"communication", "technical_knowledge", "structure"}
        criteria_keys = set(role.evaluation_criteria.keys())
        
        if not required_criteria.issubset(criteria_keys):
            missing = required_criteria - criteria_keys
            raise ValueError(f"Role '{role.name}' missing required criteria: {missing}")
    
    def get_role(self, role_name: str) -> Optional[Role]:
        """
        Get a specific role by name.
        
        Args:
            role_name: Name of the role to retrieve
            
        Returns:
            Role object if found, None otherwise
        """
        if not self._loaded:
            self.load_roles()
        
        return self._roles.get(role_name)
    
    def get_all_roles(self) -> Dict[str, Role]:
        """
        Get all available roles.
        
        Returns:
            Dictionary mapping role names to Role objects
        """
        if not self._loaded:
            self.load_roles()
        
        return self._roles.copy()
    
    def get_role_names(self) -> List[str]:
        """
        Get list of all available role names.
        
        Returns:
            List of role names
        """
        if not self._loaded:
            self.load_roles()
        
        return list(self._roles.keys())
    
    def is_valid_role(self, role_name: str) -> bool:
        """
        Check if a role name is valid.
        
        Args:
            role_name: Name of the role to check
            
        Returns:
            True if the role exists, False otherwise
        """
        if not self._loaded:
            self.load_roles()
        
        return role_name in self._roles
    
    def get_role_display_name(self, role_name: str) -> Optional[str]:
        """
        Get the display name for a role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            Display name if role exists, None otherwise
        """
        role = self.get_role(role_name)
        return role.display_name if role else None
    
    def get_role_questions(self, role_name: str) -> List[str]:
        """
        Get all questions for a specific role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            List of questions for the role
            
        Raises:
            RoleLoaderError: If the role doesn't exist
        """
        role = self.get_role(role_name)
        if not role:
            raise RoleLoaderError(f"Role '{role_name}' not found")
        
        return role.questions.copy()


# Global instance for easy access
_role_loader_instance: Optional[RoleLoader] = None


def get_role_loader() -> RoleLoader:
    """
    Get the global RoleLoader instance.
    
    Returns:
        RoleLoader instance
    """
    global _role_loader_instance
    if _role_loader_instance is None:
        _role_loader_instance = RoleLoader()
    return _role_loader_instance


def load_roles() -> Dict[str, Role]:
    """
    Convenience function to load all roles.
    
    Returns:
        Dictionary mapping role names to Role objects
    """
    return get_role_loader().load_roles()


def get_role(role_name: str) -> Optional[Role]:
    """
    Convenience function to get a specific role.
    
    Args:
        role_name: Name of the role to retrieve
        
    Returns:
        Role object if found, None otherwise
    """
    return get_role_loader().get_role(role_name)


def is_valid_role(role_name: str) -> bool:
    """
    Convenience function to check if a role is valid.
    
    Args:
        role_name: Name of the role to check
        
    Returns:
        True if the role exists, False otherwise
    """
    return get_role_loader().is_valid_role(role_name)
