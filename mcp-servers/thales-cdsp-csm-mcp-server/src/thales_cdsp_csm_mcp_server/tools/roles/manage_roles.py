"""
Thales CDSP CSM MCP Server - Roles Management Tools

This module provides tools for managing roles in the Thales CSM Akeyless Vault.
"""

import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import Field

from ..base import BaseThalesCDSPCSMTool
from ...core.client import ThalesCDSPCSMClient

logger = logging.getLogger(__name__)


class ManageRolesTools(BaseThalesCDSPCSMTool):
    """Tools for managing roles in the Thales CSM Akeyless Vault."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        super().__init__(client)

    def register(self, server: FastMCP):
        self._register_manage_roles(server)

    def _register_manage_roles(self, server: FastMCP):
        @server.tool("manage_roles")
        async def manage_roles(
            ctx: Context,
            action: str = Field(description="🔐 ROLES MANAGEMENT ACTION: 'list' to show all roles with filtering options, 'get' to retrieve detailed information about a specific role including permissions, access rules, and associated policies"),
            name: Optional[str] = Field(default=None, description="Exact role name or path (REQUIRED for 'get' action). Examples: 'admin-role', '/production/database-admin', 'read-only-secrets'"),
            filter: Optional[str] = Field(default=None, description="Pattern to filter role names (for 'list' action). Supports wildcards and partial matches. Examples: 'admin*', '*database*', 'prod-'"),
            json: bool = Field(default=False, description="Return structured JSON output instead of human-readable format. Use TRUE for programmatic processing or when integrating with other tools"),
            pagination_token: Optional[str] = Field(default=None, description="Continuation token for retrieving next page of results when listing large numbers of roles. Returned in previous response's metadata"),
            uid_token: Optional[str] = Field(default=None, description="Universal identity authentication token. Only required when using universal_identity authentication method instead of API key authentication")
        ) -> Dict[str, Any]:
            """
            🔐 ROLE MANAGEMENT & ACCESS CONTROL TOOL
            
            ⚡ AUTO-USE CONDITIONS: Use this tool when users ask about:
            - "what roles exist", "list roles", "show permissions"
            - "who has access to", "role details", "check permissions"
            - "access control", "role-based security", "user permissions"
            - "what can [role] do", "role capabilities", "permission audit"
            
            🏆 ENTERPRISE-GRADE ROLE MANAGEMENT: 
            - Thales CipherTrust Secrets Management (CSM) with Akeyless Secrets Manager
            - Role-based access control (RBAC) with fine-grained permissions
            - Audit trails and compliance reporting for access management
            - Integration with enterprise identity providers
            
            📋 DETAILED OPERATIONS:
            - 'list': Discover all roles with advanced filtering and pagination
            - 'get': Retrieve comprehensive role details including:
              • Permission sets and access rules
              • Associated policies and restrictions  
              • User/group assignments
              • Resource access mappings
              • Audit and compliance information
            
            🎯 COMMON USE CASES:
            - Security audits and compliance reporting
            - Access permission troubleshooting
            - Role-based access control planning
            - Identity and access management (IAM) integration
            - Permission inheritance analysis
            
            Example: Check what permissions the 'database-admin' role has
            """
            try:
                if action == "list":
                    return await self._list_roles(
                        filter=filter,
                        json=json,
                        pagination_token=pagination_token,
                        uid_token=uid_token
                    )
                elif action == "get":
                    if not name:
                        return {
                            "success": False,
                            "error": "Role name is required for get action",
                            "message": "Please provide a name for the role"
                        }
                    return await self._get_role(
                        name=name,
                        json=json,
                        uid_token=uid_token
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Invalid action: {action}",
                        "message": "Supported actions: 'list', 'get'"
                    }
            except Exception as e:
                await self.hybrid_log(ctx, "error", f"Failed to manage roles: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": "An error occurred while managing roles"
                }

    async def _list_roles(
        self,
        filter: Optional[str] = None,
        json: bool = False,
        pagination_token: Optional[str] = None,
        uid_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """List roles in the Thales CSM Akeyless Secrets Manager."""
        try:
            # Prepare request data
            request_data = {
                "json": json
            }
            
            if filter:
                request_data["filter"] = filter
            if pagination_token:
                request_data["pagination-token"] = pagination_token
            if uid_token:
                request_data["uid-token"] = uid_token
            
            # Make API call
            response = await self.client._make_request("list-roles", request_data)
            
            return {
                "success": True,
                "data": response,
                "message": "Roles retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to list roles: {e}")
            raise e

    async def _get_role(
        self,
        name: str,
        json: bool = False,
        uid_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get details of a specific role."""
        try:
            # Prepare request data
            request_data = {
                "name": name,
                "json": json
            }
            
            if uid_token:
                request_data["uid-token"] = uid_token
            
            # Make API call
            response = await self.client._make_request("get-role", request_data)
            
            return {
                "success": True,
                "data": response,
                "message": f"Role '{name}' retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get role '{name}': {e}")
            raise e 