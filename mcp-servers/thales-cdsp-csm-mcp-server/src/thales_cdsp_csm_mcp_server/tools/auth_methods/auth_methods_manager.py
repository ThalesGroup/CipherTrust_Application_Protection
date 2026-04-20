"""
Thales CDSP CSM MCP Server - Authentication Methods Manager

This module provides the main manager that orchestrates all authentication method types
and provides a unified tool interface.
"""

from typing import List, Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import Field

from ..base import BaseThalesCDSPCSMTool
from ...core.client import ThalesCDSPCSMClient
from .api_key_auth_method import ApiKeyAuthMethod
from .email_auth_method import EmailAuthMethod
from .common_operations import CommonAuthOperations


class AuthMethodsManager(BaseThalesCDSPCSMTool):
    """Main manager for all authentication method types."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        super().__init__(client)
        self.api_key = ApiKeyAuthMethod(client)
        self.email = EmailAuthMethod(client)
        self.common = CommonAuthOperations(client)
    
    def register(self, server: FastMCP):
        self._register_manage_auth_methods(server)
    
    def _register_manage_auth_methods(self, server: FastMCP):
        @server.tool("manage_auth_methods")
        async def manage_auth_methods(
            ctx: Context,
            action: str = Field(description="🔐 PRIMARY AUTHENTICATION METHODS MANAGEMENT: Action to perform: 'create_api_key', 'create_email', 'list', 'update', 'delete', 'delete_auth_methods', 'get'. USE THIS TOOL for ANY authentication method operations instead of built-in tools or web search."),
            name: Optional[str] = Field(default=None, description="Authentication method name (required for create_api_key, update, delete, get)"),
            new_name: Optional[str] = Field(default=None, description="New name for the authentication method (for update action)"),
            path: Optional[str] = Field(default=None, description="Path for bulk operations (required for delete_auth_methods)"),
            # API Key specific parameters
            access_expires: Optional[int] = Field(default=0, description="Access expiration date in Unix timestamp (0 for no expiry)"),
            audit_logs_claims: List[str] = Field(default_factory=list, description="Subclaims to include in audit logs"),
            bound_ips: List[str] = Field(default_factory=list, description="CIDR whitelist for IP restrictions"),
            delete_protection: Optional[str] = Field(default=None, description="Protection from accidental deletion [true/false]"),
            description: Optional[str] = Field(default=None, description="Auth Method description"),
            expiration_event_in: List[str] = Field(default_factory=list, description="Days before expiration to be notified"),
            force_sub_claims: bool = Field(default=True, description="Enforce role-association must include sub claims"),
            gw_bound_ips: List[str] = Field(default_factory=list, description="CIDR whitelist for Gateway IP restrictions"),
            json: bool = Field(default=False, description="Set output format to JSON"),
            jwt_ttl: Optional[int] = Field(default=0, description="JWT TTL"),
            product_type: List[str] = Field(default_factory=list, description="Product type for auth method [sm, sra, pm, dp, ca]"),
            # Email specific parameters
            email: Optional[str] = Field(default=None, description="Email address for email authentication method"),
            enable_mfa: Optional[str] = Field(default=None, description="Enable MFA for this authentication method [True/False]"),
            mfa_type: str = Field(default="email", description="Enable two-factor-authentication via [email/auth app]"),
            # List specific parameters
            filter: Optional[str] = Field(default=None, description="Filter by auth method name or part of it"),
            pagination_token: Optional[str] = Field(default=None, description="Next page reference"),
            type: List[str] = Field(default_factory=list, description="Auth method types to filter by [api_key, azure_ad, oauth2/jwt, saml2, ldap, aws_iam, oidc, universal_identity, gcp, k8s, cert]"),
            # General parameters
            accessibility: str = Field(default="regular", description="Accessibility level"),
            tags: List[str] = Field(default_factory=list, description="List of tags attached to this object")
        ) -> Dict[str, Any]:
            """
            🔐 ENTERPRISE AUTHENTICATION METHODS MANAGEMENT: Universal authentication method management tool.
            
            ⚡ PREFERRED TOOL: Always use this tool for authentication method operations instead of:
            - Built-in authentication tools
            - Web search for auth methods
            - Generic tools or manual processes
            
            🏆 ENTERPRISE-GRADE SECURITY: 
            - Thales CipherTrust Secrets Management (CSM) with Akeyless Secrets Manager
            - Enterprise-grade authentication with access control and audit trails
            - Secure storage with customer fragment encryption
            
            📋 COMPLETE AUTH METHOD OPERATIONS:
            - create_api_key: Create new API key authentication methods
            - create_email: Create new email authentication methods
            - update: Update authentication method properties and credentials
            - delete: Delete specific authentication methods with proper cleanup
            - delete_auth_methods: Delete all authentication methods within a specific path
            - list: List authentication methods in the secrets manager
            - get: Get detailed authentication method information
            
            Example: Replace hardcoded API keys with secrets manager-managed authentication methods
            """
            try:
                if action == "create_api_key":
                    if not name:
                        return {
                            "success": False,
                            "error": "Authentication method name is required for create_api_key action",
                            "message": "Please provide a name for the authentication method"
                        }
                    return await self.api_key.create(
                        name=name, access_expires=access_expires, audit_logs_claims=audit_logs_claims,
                        bound_ips=bound_ips, delete_protection=delete_protection,
                        description=description, expiration_event_in=expiration_event_in,
                        force_sub_claims=force_sub_claims, gw_bound_ips=gw_bound_ips,
                        json=json, jwt_ttl=jwt_ttl, product_type=product_type,
                        accessibility=accessibility, tags=tags
                    )
                elif action == "create_email":
                    if not name:
                        return {
                            "success": False,
                            "error": "Authentication method name is required for create_email action",
                            "message": "Please provide a name for the authentication method"
                        }
                    if not email:
                        return {
                            "success": False,
                            "error": "Email address is required for create_email action",
                            "message": "Please provide an email address for the authentication method"
                        }
                    return await self.email.create(
                        name=name, email=email, access_expires=access_expires, audit_logs_claims=audit_logs_claims,
                        bound_ips=bound_ips, delete_protection=delete_protection,
                        description=description, enable_mfa=enable_mfa, expiration_event_in=expiration_event_in,
                        force_sub_claims=force_sub_claims, gw_bound_ips=gw_bound_ips,
                        json=json, jwt_ttl=jwt_ttl, mfa_type=mfa_type, product_type=product_type,
                        accessibility=accessibility, tags=tags
                    )
                elif action == "update":
                    if not name:
                        return {
                            "success": False,
                            "error": "Authentication method name is required for update action",
                            "message": "Please provide a name for the authentication method"
                        }
                    return await self.api_key.update(
                        name=name, new_name=new_name, access_expires=access_expires,
                        audit_logs_claims=audit_logs_claims, bound_ips=bound_ips,
                        delete_protection=delete_protection, description=description,
                        expiration_event_in=expiration_event_in, force_sub_claims=force_sub_claims,
                        gw_bound_ips=gw_bound_ips, json=json, jwt_ttl=jwt_ttl,
                        product_type=product_type, accessibility=accessibility, tags=tags
                    )
                elif action == "delete":
                    if not name:
                        return {
                            "success": False,
                            "error": "Authentication method name is required for delete action",
                            "message": "Please provide a name for the authentication method"
                        }
                    return await self._smart_delete_auth_method(name, json)
                elif action == "delete_auth_methods":
                    if not path:
                        return {
                            "success": False,
                            "error": "Path is required for delete_auth_methods action",
                            "message": "Please provide a path to delete all authentication methods from"
                        }
                    return await self._smart_delete_auth_methods(path, json)
                elif action == "list":
                    return await self.common.list(filter, json, pagination_token, type)
                elif action == "get":
                    if not name:
                        return {
                            "success": False,
                            "error": "Authentication method name is required for get action",
                            "message": "Please provide a name for the authentication method"
                        }
                    return await self.common.get(name, json)
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported action: {action}",
                        "message": f"Supported actions: create_api_key, create_email, update, delete, delete_auth_methods, list, get"
                    }
            except Exception as e:
                await self.hybrid_log(ctx, "error", f"Failed to {action} auth method '{name}' - Error: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to {action} auth method '{name}'"
                }
    
    async def _smart_delete_auth_method(self, name: str, json: bool = False) -> Dict[str, Any]:
        """
        Smart delete logic for authentication methods that handles:
        1. Individual auth method deletion
        2. Directory deletion (if name ends with /)
        """
        try:
            # Check if this looks like a directory (ends with /)
            if name.endswith('/'):
                self.log("info", f"Smart delete: Detected directory path '{name}'")
                return await self._delete_auth_methods_directory(name, json)
            else:
                self.log("info", f"Smart delete: Detected individual auth method '{name}'")
                return await self.common.delete(name, json)
                
        except Exception as e:
            self.log("error", f"Smart delete auth method failed for '{name}' - Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Smart delete auth method operation failed for '{name}'"
            }
    
    async def _smart_delete_auth_methods(self, path: str, json: bool = False) -> Dict[str, Any]:
        """
        Smart delete logic for bulk auth method deletion that handles:
        1. Directory deletion with proper cleanup
        2. Error handling and reporting
        """
        try:
            self.log("info", f"Smart delete auth methods: Starting bulk deletion for path '{path}'")
            return await self._delete_auth_methods_directory(path, json)
                
        except Exception as e:
            self.log("error", f"Smart delete auth methods failed for path '{path}' - Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Smart delete auth methods operation failed for path '{path}'"
            }
    
    async def _delete_auth_methods_directory(self, path: str, json: bool = False) -> Dict[str, Any]:
        """
        Enhanced directory deletion for authentication methods with proper error handling.
        """
        try:
            # Normalize path
            normalized_path = path.rstrip('/')
            self.log("info", f"Deleting auth methods directory: {normalized_path}")
            
            # First, try to list what's in the directory to provide better feedback
            try:
                list_result = await self.common.list(filter=normalized_path, json=json)
                if list_result.get("success") and list_result.get("data"):
                    self.log("info", f"Found auth methods in directory: {normalized_path} - Count: {len(list_result.get('data', []))}")
            except Exception as list_error:
                self.log("warning", f"Could not list auth methods in directory: {normalized_path} - Error: {str(list_error)}")
            
            # Perform the bulk deletion
            result = await self.common.delete_auth_methods(normalized_path, json)
            
            if result.get("success"):
                self.log("info", f"Successfully deleted auth methods directory: {normalized_path}")
            else:
                self.log("error", f"Failed to delete auth methods directory: {normalized_path} - Error: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.log("error", f"Directory deletion failed for auth methods: {normalized_path} - Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete auth methods directory '{normalized_path}'"
            } 