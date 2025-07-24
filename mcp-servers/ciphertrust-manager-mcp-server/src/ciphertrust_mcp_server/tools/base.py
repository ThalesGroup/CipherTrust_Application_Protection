"""Base classes for CipherTrust MCP tools with comprehensive domain support and universal client compatibility."""

import json
from abc import ABC, abstractmethod
from typing import Any, TypeVar, Optional

from mcp.types import Tool
from pydantic import BaseModel

# Import the ksctl manager
try:
    from ..ksctl_cli_manager import KsctlManager, get_ksctl_manager
except ImportError:
    # If import fails, we'll handle it in __init__
    KsctlManager = None
    get_ksctl_manager = None

T = TypeVar("T", bound=BaseModel)


class BaseTool(ABC):
    """Base class for all CipherTrust MCP tools with domain support."""

    def __init__(self):
        if get_ksctl_manager:
            self.ksctl = get_ksctl_manager()  # type: ignore
        else:
            self.ksctl = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """Get the JSON schema for tool parameters."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given parameters."""
        pass

    def execute_with_domain(self, args: list[str], domain: Optional[str] = None, auth_domain: Optional[str] = None) -> dict[str, Any]:
        """Execute ksctl command with optional domain override.
        
        This method allows executing commands in a specific domain without changing
        global settings. It temporarily modifies the command arguments to include
        domain parameters.
        
        Args:
            args: Base command arguments (e.g., ["users", "list"])
            domain: Optional domain override for this operation
            auth_domain: Optional auth domain override for this operation
            
        Returns:
            Command execution result
        """
        # Clone args to avoid modifying the original
        domain_args = args.copy()
        
        # Add domain parameters if specified
        if domain:
            domain_args.extend(["--domain", domain])
        if auth_domain:
            domain_args.extend(["--auth-domain", auth_domain])
        
        return self.ksctl.execute(domain_args)
    
    def execute_with_global_domain_override(self, args: list[str], domain: Optional[str], auth_domain: Optional[str]) -> dict[str, Any]:
        """Execute command with temporary global domain settings override.
        
        This method temporarily changes the global domain settings, executes the command,
        then restores the original settings. Use this when the command doesn't support
        --domain flags directly.
        
        Args:
            args: Base command arguments
            domain: Optional domain override
            auth_domain: Optional auth domain override
            
        Returns:
            Command execution result
        """
        from ..config import settings
        
        # Store original settings
        original_domain = settings.ciphertrust_domain
        original_auth_domain = settings.ciphertrust_auth_domain
        
        try:
            # Temporarily override settings
            if domain:
                settings.ciphertrust_domain = domain
            if auth_domain:
                settings.ciphertrust_auth_domain = auth_domain
            
            # Execute with overridden settings
            return self.ksctl.execute(args)
        
        finally:
            # Restore original settings
            settings.ciphertrust_domain = original_domain
            settings.ciphertrust_auth_domain = original_auth_domain

    # New helper methods for connection management tools
    def get_domain_auth_params(self) -> dict[str, Any]:
        """Get standard domain and auth-domain parameters."""
        return {
            "domain": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "The CipherTrust Manager Domain that the command will operate in",
                "title": "Domain"
            },
            "auth_domain": {
                "anyOf": [{"type": "string"}, {"type": "null"}],
                "default": None,
                "description": "The CipherTrust Manager Domain where the user is created",
                "title": "Auth Domain"
            }
        }

    def add_domain_auth_params(self, cmd: list[str], kwargs: dict[str, Any]) -> None:
        """Add domain and auth-domain parameters to command if specified."""
        if kwargs.get("domain"):
            cmd.extend(["--domain", kwargs["domain"]])
        if kwargs.get("auth_domain"):
            cmd.extend(["--auth-domain", kwargs["auth_domain"]])

    def execute_command(self, cmd: list[str]) -> str:
        """Execute a ksctl command and return the result."""
        try:
            # Use the ksctl manager
            result = self.ksctl.execute(cmd)
            
            # Return the data or stdout
            if result.get("data"):
                if isinstance(result["data"], str):
                    return result["data"]
                else:
                    import json
                    return json.dumps(result["data"], indent=2)
            else:
                return result.get("stdout", "")
                
        except Exception as e:
            return f"Error executing command: {str(e)}"

    def _ensure_schema_compatibility(self, schema: dict[str, Any]) -> dict[str, Any]:
        """Ensure JSON schema compatibility across all MCP clients.
        
        This method fixes common JSON Schema issues that can cause problems
        with strict validators in various MCP clients (Claude Desktop, Cursor AI, 
        Gemini CLI, VS Code, etc.).
        
        Fixes:
        1. Removes conflicting 'type' when 'anyOf' or 'oneOf' is present
        2. Converts array types (["string", "null"]) to proper anyOf format
        3. Ensures consistent schema structure for all clients
        """
        # Create a deep copy to avoid modifying the original
        schema = json.loads(json.dumps(schema))
        
        def fix_node(node: Any) -> None:
            if not isinstance(node, dict):
                return
            
            # Fix 1: Remove 'type' when 'anyOf' or 'oneOf' is present (conflicting definitions)
            if ('anyOf' in node or 'oneOf' in node) and 'type' in node:
                del node['type']
            
            # Fix 2: Convert array types (["string", "null"]) to proper anyOf format
            if 'type' in node and isinstance(node['type'], list) and len(node['type']) > 1:
                node['anyOf'] = [{'type': t} for t in node['type']]
                del node['type']
            
            # Recursively fix nested schemas
            if 'properties' in node and isinstance(node['properties'], dict):
                for prop in node['properties'].values():
                    fix_node(prop)
            
            if 'items' in node:
                fix_node(node['items'])
            
            # Fix nested anyOf/oneOf/allOf schemas
            for key in ['anyOf', 'oneOf', 'allOf']:
                if key in node and isinstance(node[key], list):
                    for item in node[key]:
                        fix_node(item)
        
        fix_node(schema)
        return schema

    def to_mcp_tool(self) -> Tool:
        """Convert to MCP Tool definition with universal compatibility."""
        # Get the original schema
        schema = self.get_schema()
        
        # Ensure compatibility with all MCP clients
        compatible_schema = self._ensure_schema_compatibility(schema)
        
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=compatible_schema,
        )