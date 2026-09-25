"""
Thales CDSP CSM MCP Server - Common Authentication Method Operations

This module provides common operations that work across all authentication method types.
"""

from typing import List, Dict, Any, Optional

from ...core.client import ThalesCDSPCSMClient


class CommonAuthOperations:
    """Common operations for all authentication method types."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        self.client = client
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging for common operations."""
        import logging
        self.logger = logging.getLogger("thales_csm_mcp.tools.common_operations")
    
    def log(self, level: str, message: str, data: dict = None):
        """Log message with structured data."""
        # Convert MCP level to Python logging level
        level_mapping = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'notice': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL,
            'alert': logging.CRITICAL,
            'emergency': logging.CRITICAL
        }
        
        python_level = level_mapping.get(level.lower(), logging.INFO)
        
        # Format message with data
        formatted_message = message
        if data:
            formatted_message = f"{message} | Data: {data}"
        
        # Log to common operations logger
        self.logger.log(python_level, formatted_message)
    
    async def delete(self, name: str, json: bool = False) -> Dict[str, Any]:
        """Delete a specific authentication method."""
        try:
            data = {
                "name": name,
                "json": json
            }
            
            result = await self.client.delete_auth_method(data)
            
            return {
                "success": True,
                "message": f"Authentication method '{name}' deleted successfully",
                "data": result
            }
            
        except Exception as e:
            self.log("error", f"Failed to delete authentication method '{name}'", {"error": str(e), "name": name})
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete authentication method '{name}'"
            }
    
    async def delete_auth_methods(self, path: str, json: bool = False) -> Dict[str, Any]:
        """Delete all authentication methods within a specific path."""
        try:
            data = {
                "path": path,
                "json": json
            }
            
            result = await self.client.delete_auth_methods(data)
            
            return {
                "success": True,
                "message": f"All authentication methods within path '{path}' deleted successfully",
                "data": result
            }
            
        except Exception as e:
            self.log("error", f"Failed to delete authentication methods within path '{path}'", {"error": str(e), "path": path})
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete authentication methods within path '{path}'"
            }
    
    async def list(self, filter: Optional[str] = None, json: bool = False,
                   pagination_token: Optional[str] = None, type: List[str] = None) -> Dict[str, Any]:
        """List all authentication methods."""
        try:
            data = {"json": json}
            
            # Add optional parameters if provided
            if filter:
                data["filter"] = filter
            if pagination_token:
                data["pagination-token"] = pagination_token
            if type:
                data["type"] = type
            
            result = await self.client.list_auth_methods(data)
            
            return {
                "success": True,
                "message": f"Authentication methods listed successfully",
                "data": result
            }
            
        except Exception as e:
            self.log("error", f"Failed to list authentication methods", {"error": str(e)})
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list authentication methods"
            }
    
    async def get(self, name: str, json: bool = False) -> Dict[str, Any]:
        """Get authentication method details."""
        try:
            data = {
                "name": name,
                "json": json
            }
            
            result = await self.client.get_auth_method(data)
            
            return {
                "success": True,
                "message": f"Authentication method '{name}' retrieved successfully",
                "data": result
            }
            
        except Exception as e:
            self.log("error", f"Failed to get authentication method '{name}'", {"error": str(e), "name": name})
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get authentication method '{name}'"
            } 