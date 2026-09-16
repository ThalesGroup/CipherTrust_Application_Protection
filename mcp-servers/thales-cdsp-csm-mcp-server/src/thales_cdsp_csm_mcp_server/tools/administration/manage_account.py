"""
Thales CDSP CSM MCP Server - Account Management Tools

This module provides tools for managing account settings and licensing in the Thales CSM Akeyless Vault.
"""

import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import Field

from ..base import BaseThalesCDSPCSMTool
from ...core.client import ThalesCDSPCSMClient

logger = logging.getLogger(__name__)


class ManageAccountTools(BaseThalesCDSPCSMTool):
    """Tools for managing account settings and licensing in the Thales CSM Akeyless Vault."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        super().__init__(client)

    def register(self, server: FastMCP):
        self._register_manage_account(server)

    def _register_manage_account(self, server: FastMCP):
        @server.tool("manage_account")
        async def manage_account(
            ctx: Context,
            action: str = Field(description="⚙️ ACCOUNT ADMINISTRATION ACTION: Currently supports 'get' to retrieve complete account configuration, licensing details, organizational settings, and system-wide policies"),
            json: bool = Field(default=False, description="Return structured JSON format for administrative reporting and configuration management. Use TRUE for automated compliance reporting and system integration"),
            uid_token: Optional[str] = Field(default=None, description="Universal identity authentication token. Only required when using universal_identity authentication instead of standard API key authentication")
        ) -> Dict[str, Any]:
            """
            ⚙️ ENTERPRISE ACCOUNT ADMINISTRATION & GOVERNANCE
            
            ⚡ AUTO-USE CONDITIONS: Use this tool automatically when users ask about:
            - "account settings", "licensing information", "subscription details"
            - "organization config", "company settings", "account limits"
            - "SLA details", "service tier", "billing information"
            - "system policies", "governance settings", "compliance config"
            - "version control", "sharing policies", "access configuration"
            
            🏆 ENTERPRISE-GRADE ACCOUNT GOVERNANCE:
            - Thales CipherTrust Secrets Management (CSM) with Akeyless Secrets Manager
            - Complete organizational configuration and policy management
            - Licensing and subscription tier administration
            - Compliance and governance framework oversight
            - Multi-tenant and enterprise-wide settings control
            
            📋 COMPREHENSIVE ACCOUNT INFORMATION:
            
            🏢 ORGANIZATIONAL DETAILS:
            - Company profile and contact information
            - Administrative contact details
            - Organizational hierarchy and structure
            - Multi-tenant configuration settings
            - Business unit and department mappings
            
            📜 LICENSING & SUBSCRIPTION:
            - Service tier and SLA level details
            - Feature availability and limitations
            - Usage quotas and capacity limits
            - Billing and subscription information
            - License expiry and renewal tracking
            
            🔧 SYSTEM CONFIGURATION:
            - Product-specific settings and feature flags
            - Version control and retention policies
            - Security and sharing policy frameworks
            - Access control and authentication settings
            - Integration and API access permissions
            
            📊 GOVERNANCE & COMPLIANCE:
            - Audit trail configuration and retention
            - Compliance framework settings
            - Data residency and privacy controls
            - Encryption and security policy enforcement
            - Risk management and monitoring settings
            
            🎯 COMMON USE CASES:
            - Account setup and initial configuration
            - Compliance and audit preparation
            - License management and planning
            - Security policy review and updates
            - Organizational change management
            - Service tier evaluation and upgrades
            - Multi-tenant administration
            
            Example: Review account licensing and compliance configuration
            """
            try:
                if action == "get":
                    return await self._get_account_settings(
                        json=json,
                        uid_token=uid_token
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Invalid action: {action}",
                        "message": "Supported actions: 'get'"
                    }
            except Exception as e:
                await self.hybrid_log(ctx, "error", f"Failed to manage account: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": "An error occurred while managing account"
                }

    async def _get_account_settings(
        self,
        json: bool = False,
        uid_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get account settings and licensing information."""
        try:
            # Prepare request data
            request_data = {
                "json": json
            }
            
            if uid_token:
                request_data["uid-token"] = uid_token
            
            # Make API call
            response = await self.client._make_request("get-account-settings", request_data)
            
            return {
                "success": True,
                "data": response,
                "message": "Account settings retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get account settings: {e}")
            raise e 