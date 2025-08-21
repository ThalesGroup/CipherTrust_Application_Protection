"""
Thales CDSP CSM MCP Server - API Key Authentication Method

This module provides the implementation for API Key authentication methods.
"""

from typing import List, Dict, Any, Optional

from .base_auth_method import BaseAuthMethod


class ApiKeyAuthMethod(BaseAuthMethod):
    """API Key authentication method implementation."""
    
    async def create(self, name: str, access_expires: Optional[int] = 0,
                    audit_logs_claims: List[str] = None, bound_ips: List[str] = None,
                    delete_protection: Optional[str] = None, description: Optional[str] = None,
                    expiration_event_in: List[str] = None, force_sub_claims: bool = True,
                    gw_bound_ips: List[str] = None, json: bool = False, 
                    jwt_ttl: Optional[int] = 0, product_type: List[str] = None,
                    accessibility: str = "regular", tags: List[str] = None) -> Dict[str, Any]:
        """Create a new API key authentication method."""
        try:
            # Prepare common data
            data = self._prepare_common_data(
                access_expires=access_expires, audit_logs_claims=audit_logs_claims or [],
                bound_ips=bound_ips or [], delete_protection=delete_protection,
                description=description, expiration_event_in=expiration_event_in or [],
                force_sub_claims=force_sub_claims, gw_bound_ips=gw_bound_ips or [],
                json=json, jwt_ttl=jwt_ttl, product_type=product_type or [],
                accessibility=accessibility, tags=tags or []
            )
            
            # Add API key specific fields
            data["name"] = name
            
            # Remove None values and set defaults
            data = self._remove_none_values(data)
            if "access-expires" not in data:
                data["access-expires"] = 0
            if "jwt-ttl" not in data:
                data["jwt-ttl"] = 0
            if "force-sub-claims" not in data:
                data["force-sub-claims"] = True
            
            result = await self.client.create_api_key_auth_method(data)
            
            return {
                "success": True,
                "message": f"API key authentication method '{name}' created successfully",
                "data": result
            }
            
        except Exception as e:
            self.log("error", f"Failed to create API key auth method '{name}'", {"error": str(e), "name": name})
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create API key auth method '{name}'"
            }
    
    async def update(self, name: str, new_name: Optional[str] = None,
                    access_expires: Optional[int] = None, audit_logs_claims: List[str] = None,
                    bound_ips: List[str] = None, delete_protection: Optional[str] = None,
                    description: Optional[str] = None, expiration_event_in: List[str] = None,
                    force_sub_claims: Optional[bool] = None, gw_bound_ips: List[str] = None,
                    json: bool = False, jwt_ttl: Optional[int] = None,
                    product_type: List[str] = None, accessibility: Optional[str] = None,
                    tags: List[str] = None) -> Dict[str, Any]:
        """Update an existing API key authentication method."""
        try:
            # Prepare common data
            data = self._prepare_common_data(
                access_expires=access_expires, audit_logs_claims=audit_logs_claims,
                bound_ips=bound_ips, delete_protection=delete_protection,
                description=description, expiration_event_in=expiration_event_in,
                force_sub_claims=force_sub_claims, gw_bound_ips=gw_bound_ips,
                json=json, jwt_ttl=jwt_ttl, product_type=product_type,
                accessibility=accessibility, tags=tags
            )
            
            # Add API key specific fields
            data["name"] = name
            if new_name:
                data["new-name"] = new_name
            
            # Remove None values
            data = self._remove_none_values(data)
            
            result = await self.client.update_api_key_auth_method(data)
            
            return {
                "success": True,
                "message": f"Authentication method '{name}' updated successfully",
                "data": result
            }
            
        except Exception as e:
            self.log("error", f"Failed to update authentication method '{name}'", {"error": str(e), "name": name})
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update authentication method '{name}'"
            } 