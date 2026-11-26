"""
Thales CDSP CSM MCP Server - Targets Management Tools

This module provides tools for managing targets in the Thales CSM Akeyless Vault.
"""

import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import Field

from ..base import BaseThalesCDSPCSMTool
from ...core.client import ThalesCDSPCSMClient

logger = logging.getLogger(__name__)


class ManageTargetsTools(BaseThalesCDSPCSMTool):
    """Tools for managing targets in the Thales CSM Akeyless Vault."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        super().__init__(client)

    def register(self, server: FastMCP):
        self._register_manage_targets(server)

    def _register_manage_targets(self, server: FastMCP):
        @server.tool("manage_targets")
        async def manage_targets(
            ctx: Context,
            action: str = Field(description="🎯 TARGET MANAGEMENT ACTION: 'list' to discover all configured targets with filtering, 'get' to retrieve detailed target configuration including credentials, connections, and version history"),
            name: Optional[str] = Field(default=None, description="Exact target name or identifier (REQUIRED for 'get' action). Examples: 'prod-mysql-db', 'aws-production', 'k8s-cluster-west'"),
            filter: Optional[str] = Field(default=None, description="Pattern to filter target names (for 'list' action). Supports wildcards. Examples: 'prod-*', '*database*', 'aws-*'"),
            json: bool = Field(default=False, description="Return structured JSON output for programmatic processing. Use TRUE when integrating with automation scripts or other tools"),
            pagination_token: Optional[str] = Field(default=None, description="Continuation token for large result sets. Automatically provided in previous response metadata when more results are available"),
            target_types: Optional[List[str]] = Field(default=None, description="Filter by specific target types. SUPPORTED: ['mysql', 'postgres', 'mongodb', 'aws', 'azure', 'gcp', 'k8s', 'ssh', 'ldap', 'github', 'dockerhub', 'artifactory', 'salesforce', 'snowflake', 'redshift', 'mssql', 'cassandra', 'hanadb', 'rabbitmq', 'venafi', 'chef', 'web', 'gke', 'eks', 'oracle']. Use multiple types as array."),
            show_versions: bool = Field(default=False, description="Include complete version history and configuration changes for the target (for 'get' action). Essential for audit trails and rollback scenarios"),
            target_version: Optional[int] = Field(default=None, description="Retrieve specific target version configuration. Use 0 for latest, positive integers for specific versions, or omit for current active version"),
            uid_token: Optional[str] = Field(default=None, description="Universal identity authentication token. Only required when using universal_identity authentication instead of standard API key authentication")
        ) -> Dict[str, Any]:
            """
            🎯 TARGET SYSTEM INTEGRATION & CONNECTION MANAGEMENT
            
            ⚡ AUTO-USE CONDITIONS: Use this tool automatically when users ask about:
            - "what systems are connected", "list databases", "show integrations"
            - "target configuration", "connection details", "system endpoints"
            - "database connections", "cloud integrations", "service targets"
            - "check target", "target health", "connection status"
            - "rotate credentials", "update target", "target versions"
            
            🏆 ENTERPRISE-GRADE TARGET MANAGEMENT:
            - Thales CipherTrust Secrets Management (CSM) with Akeyless Secrets Manager
            - Secure connection management for external systems
            - Automated credential rotation and lifecycle management
            - Multi-cloud and hybrid infrastructure support
            - Version control and audit trails for all configurations
            
            📋 COMPREHENSIVE OPERATIONS:
            - 'list': Discover all configured targets with advanced filtering
            - 'get': Retrieve detailed target information including:
              • Connection parameters and endpoints
              • Authentication configuration
              • Credential rotation settings
              • Health status and last connection
              • Version history and change tracking
              • Associated policies and permissions
            
            🎯 SUPPORTED INTEGRATION TYPES:
            
            🗄️ DATABASES: mysql, postgres, mongodb, mssql, oracle, cassandra, hanadb, snowflake, redshift
            ☁️ CLOUD PROVIDERS: aws, azure, gcp, gke, eks  
            🔧 DEVOPS/INFRA: k8s, ssh, github, dockerhub, artifactory, chef
            🏢 ENTERPRISE: ldap, salesforce, rabbitmq, venafi, web
            
            🎯 COMMON USE CASES:
            - Database connection management and rotation
            - Cloud service authentication setup
            - DevOps pipeline integrations
            - Enterprise system connections
            - Compliance and audit reporting
            - Multi-environment target management
            - Automated credential lifecycle management
            
            Example: Find all database targets and check their connection status
            """
            try:
                if action == "list":
                    return await self._list_targets(
                        filter=filter,
                        json=json,
                        pagination_token=pagination_token,
                        target_types=target_types,
                        uid_token=uid_token
                    )
                elif action == "get":
                    if not name:
                        return {
                            "success": False,
                            "error": "Target name is required for get action",
                            "message": "Please provide a name for the target"
                        }
                    return await self._get_target(
                        name=name,
                        json=json,
                        show_versions=show_versions,
                        target_version=target_version,
                        uid_token=uid_token
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Invalid action: {action}",
                        "message": "Supported actions: 'list', 'get'"
                    }
            except Exception as e:
                await self.hybrid_log(ctx, "error", f"Failed to manage targets: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": "An error occurred while managing targets"
                }

    async def _list_targets(
        self,
        filter: Optional[str] = None,
        json: bool = False,
        pagination_token: Optional[str] = None,
        target_types: Optional[List[str]] = None,
        uid_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """List targets in the Thales CSM Akeyless Secrets Manager."""
        try:
            # Prepare request data
            request_data = {
                "json": json
            }
            
            if filter:
                request_data["filter"] = filter
            if pagination_token:
                request_data["pagination-token"] = pagination_token
            if target_types:
                request_data["type"] = target_types
            if uid_token:
                request_data["uid-token"] = uid_token
            
            # Make API call
            response = await self.client._make_request("target-list", request_data)
            
            return {
                "success": True,
                "data": response,
                "message": "Targets retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to list targets: {e}")
            raise e

    async def _get_target(
        self,
        name: str,
        json: bool = False,
        show_versions: bool = False,
        target_version: Optional[int] = None,
        uid_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get details of a specific target."""
        try:
            # Prepare request data
            request_data = {
                "name": name,
                "json": json,
                "show-versions": show_versions
            }
            
            if target_version is not None:
                request_data["target-version"] = target_version
            
            if uid_token:
                request_data["uid-token"] = uid_token
            
            # Make API call - use target-get-details for more comprehensive information
            response = await self.client._make_request("target-get-details", request_data)
            
            return {
                "success": True,
                "data": response,
                "message": f"Target '{name}' retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get target '{name}': {e}")
            raise e 