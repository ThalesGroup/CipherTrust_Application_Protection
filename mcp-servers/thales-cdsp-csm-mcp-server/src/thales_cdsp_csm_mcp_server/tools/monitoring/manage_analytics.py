"""
Thales CDSP CSM MCP Server - Analytics Management Tools

This module provides tools for managing analytics and monitoring data in the Thales CSM Akeyless Vault.
"""

import logging
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import Field

from ..base import BaseThalesCDSPCSMTool
from ...core.client import ThalesCDSPCSMClient

logger = logging.getLogger(__name__)


class ManageAnalyticsTools(BaseThalesCDSPCSMTool):
    """Tools for managing analytics and monitoring data in the Thales CSM Akeyless Vault."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        super().__init__(client)

    def register(self, server: FastMCP):
        self._register_manage_analytics(server)

    def _register_manage_analytics(self, server: FastMCP):
        @server.tool("manage_analytics")
        async def manage_analytics(
            ctx: Context,
            action: str = Field(description="📊 ANALYTICS ACTION: Currently supports 'get' to retrieve comprehensive monitoring data, usage statistics, and performance metrics for the entire Akeyless infrastructure"),
            json: bool = Field(default=False, description="Return structured JSON format for programmatic analysis and dashboard integration. Use TRUE for automated reporting and data processing"),
            filter_by_type: Optional[str] = Field(default=None, description="Focus on specific item categories. SUPPORTED TYPES: 'Targets', 'Static Secrets', 'Dynamic Secrets', 'DFC Key', 'Roles', 'Auth Methods', 'Rotated Secrets', 'Certificates'. Use exact match for filtering"),
            filter_by_risk: Optional[str] = Field(default=None, description="Filter certificate and security risk analysis. OPTIONS: 'Expired' (certificates past expiry), 'Healthy' (certificates within validity), 'Expiring Soon' (certificates near expiry)"),
            filter_by_product: Optional[str] = Field(default=None, description="Filter by Akeyless product components. OPTIONS: 'sm' (Secrets Management), 'adp' (Advanced Data Protection), 'sra' (Secure Remote Access). Essential for multi-product environments"),
            uid_token: Optional[str] = Field(default=None, description="Universal identity authentication token. Only required when using universal_identity authentication instead of standard API key authentication")
        ) -> Dict[str, Any]:
            """
            📊 COMPREHENSIVE MONITORING & ANALYTICS DASHBOARD
            
            ⚡ AUTO-USE CONDITIONS: Use this tool automatically when users ask about:
            - "usage statistics", "system metrics", "performance data"
            - "how many secrets", "certificate status", "risk assessment"
            - "monitoring dashboard", "analytics report", "usage trends"
            - "system health", "audit summary", "compliance metrics"
            - "geographic usage", "client statistics", "access patterns"
            
            🏆 ENTERPRISE-GRADE MONITORING CAPABILITIES:
            - Thales CipherTrust Secrets Management (CSM) with Akeyless Secrets Manager
            - Real-time usage analytics and performance monitoring
            - Security risk assessment and compliance reporting
            - Geographic distribution and access pattern analysis
            - Multi-product environment insights
            
            📊 COMPREHENSIVE ANALYTICS COVERAGE:
            
            📈 USAGE STATISTICS:
            - Item counts by type (Secrets, Targets, Roles, Keys)
            - Geographic distribution of access requests
            - Client usage patterns and trends
            - Request volumes and response time metrics
            - Active user and application statistics
            
            🔒 SECURITY & RISK ANALYSIS:
            - Certificate expiry tracking and risk assessment
            - Access control compliance metrics
            - Authentication method usage analysis
            - Failed access attempts and security events
            - Privilege escalation monitoring
            
            🌍 OPERATIONAL INSIGHTS:
            - Multi-region usage distribution
            - Product-specific performance metrics
            - Integration health and connectivity status
            - Resource utilization and capacity planning
            - Audit trail summary and compliance reporting
            
            🎯 COMMON USE CASES:
            - Security operations center (SOC) dashboards
            - Compliance reporting and audit preparation
            - Capacity planning and resource optimization
            - Risk assessment and vulnerability management
            - Executive reporting and KPI tracking
            - Operational health monitoring and alerting
            
            Example: Get security risk analysis for certificate expiry management
            """
            try:
                if action == "get":
                    return await self._get_analytics(
                        json=json,
                        filter_by_type=filter_by_type,
                        filter_by_risk=filter_by_risk,
                        filter_by_product=filter_by_product,
                        uid_token=uid_token
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Invalid action: {action}",
                        "message": "Supported actions: 'get'"
                    }
            except Exception as e:
                await self.hybrid_log(ctx, "error", f"Failed to manage analytics: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": "An error occurred while managing analytics"
                }

    async def _get_analytics(
        self,
        json: bool = False,
        filter_by_type: Optional[str] = None,
        filter_by_risk: Optional[str] = None,
        filter_by_product: Optional[str] = None,
        uid_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get analytics data with optional client-side filtering."""
        try:
            # Prepare request data
            request_data = {
                "json": json
            }
            
            if uid_token:
                request_data["uid-token"] = uid_token
            
            # Make API call
            response = await self.client._make_request("get-analytics-data", request_data)
            
            # Apply client-side filtering if requested
            if any([filter_by_type, filter_by_risk, filter_by_product]):
                filtered_response = self._apply_analytics_filters(
                    response, 
                    filter_by_type, 
                    filter_by_risk, 
                    filter_by_product
                )
                response = filtered_response
            
            return {
                "success": True,
                "data": response,
                "message": "Analytics data retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics data: {e}")
            raise e

    def _apply_analytics_filters(
        self,
        data: Dict[str, Any],
        filter_by_type: Optional[str] = None,
        filter_by_risk: Optional[str] = None,
        filter_by_product: Optional[str] = None
    ) -> Dict[str, Any]:
        """Apply client-side filtering to analytics data."""
        filtered_data = data.copy()
        
        # Filter by item type
        if filter_by_type and "analytics_data" in data and "all_items" in data["analytics_data"]:
            all_items = data["analytics_data"]["all_items"]
            if len(all_items) > 1:  # Skip header row
                filtered_items = [all_items[0]]  # Keep header
                for item in all_items[1:]:
                    if len(item) > 1 and filter_by_type.lower() in item[0].lower():
                        filtered_items.append(item)
                filtered_data["analytics_data"]["all_items"] = filtered_items
        
        # Filter by certificate risk
        if filter_by_risk and "certificates_expiry_data" in data:
            cert_data = data["certificates_expiry_data"]
            if "risk_counts" in cert_data:
                risk_counts = cert_data["risk_counts"]
                if filter_by_risk in risk_counts:
                    filtered_data["certificates_expiry_data"]["risk_counts"] = {
                        filter_by_risk: risk_counts[filter_by_risk]
                    }
        
        # Filter by product
        if filter_by_product and "usage_reports" in data:
            usage_reports = data["usage_reports"]
            if filter_by_product in usage_reports:
                filtered_data["usage_reports"] = {
                    filter_by_product: usage_reports[filter_by_product]
                }
        
        return filtered_data 