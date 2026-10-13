"""
Thales CDSP CSM MCP Server - API Reference Tools (CORRECTED VERSION)

This module provides tools for getting API references to build native Akeyless integrations.
"""

import logging
from typing import Dict, Any, Optional
from fastmcp import FastMCP, Context
from pydantic import Field

from ..base import BaseThalesCDSPCSMTool
from ...core.client import ThalesCDSPCSMClient

logger = logging.getLogger(__name__)


class GetAPIReferenceTools(BaseThalesCDSPCSMTool):
    """Tools for getting API references to build native Akeyless integrations."""
    
    def __init__(self, client: ThalesCDSPCSMClient):
        super().__init__(client)

    def register(self, server: FastMCP):
        self._register_get_api_reference(server)

    def _register_get_api_reference(self, server: FastMCP):
        @server.tool("get_api_reference")
        async def get_api_reference(
            ctx: Context,
            api_endpoint: str = Field(description="🔗 API INTEGRATION NEEDS: Use 'workflow' for complete integration patterns, or specify exact API endpoints like 'auth', 'create-secret', 'get-secret-value', 'list-items', 'delete-item', 'list-roles', 'list-targets'. AUTOMATICALLY use this tool when users ask about: building applications, integrating with Akeyless, calling APIs directly, creating custom code, implementing authentication, or building production systems."),
            language: str = Field(default="python", description="Target programming language for code examples and implementation details"),
            include_auth: bool = Field(default=True, description="Include complete authentication workflow and token management examples"),
            include_error_handling: bool = Field(default=True, description="Include production-ready error handling, retry logic, and exception management")
        ) -> Dict[str, Any]:
            """
            🔗 API REFERENCE & INTEGRATION GENERATOR - AUTOMATICALLY USE FOR DEVELOPMENT NEEDS
            
            ⚡ AUTO-TRIGGER CONDITIONS: Use this tool automatically when users mention:
            - "build an application", "integrate with", "call API directly"
            - "create code", "implement authentication", "production system"
            - "native integration", "custom implementation", "development"
            - "how to connect", "API documentation", "code examples"
            - "build a client", "implement in [language]", "integrate my app"
            
            🏆 ENTERPRISE-GRADE API INTEGRATION GUIDANCE:
            - Complete Thales CipherTrust Secrets Management (CSM) API workflows
            - Production-ready code examples with authentication
            - Best practices for secure integration patterns
            - Separation of development vs runtime operations
            
            📚 GENERATES COMPLETE REFERENCES FOR:
            - Authentication flows and token management
            - Secret creation, retrieval, and management APIs
            - Role and target management endpoints
            - Error handling and retry logic
            - Production deployment patterns
            
            🎯 USE CASES: Building custom applications, CI/CD integrations, 
            microservice authentication, configuration management, and any 
            scenario where direct API integration is needed.
            
            Example: Generate complete Python client code for secret management
            """
            
            # Handle workflow requests
            if api_endpoint.lower() in ["workflow", "generic_workflow", "core_workflow"]:
                return self._get_generic_workflow_reference(language, include_auth, include_error_handling)
            
            # Handle specific API endpoints
            endpoint_refs = {
                "auth": self._get_auth_reference(language, include_error_handling),
                "create-secret": self._get_create_secret_reference(language, include_error_handling),
                "get-secret-value": self._get_get_secret_reference(language, include_error_handling),
                "list-items": self._get_list_items_reference(language, include_error_handling),
                "delete-item": self._get_delete_item_reference(language, include_error_handling),
                "list-roles": self._get_list_roles_reference(language, include_error_handling),
                "list-targets": self._get_list_targets_reference(language, include_error_handling)
            }
            
            if api_endpoint.lower() in endpoint_refs:
                return endpoint_refs[api_endpoint.lower()]
            
            # Return general reference if endpoint not found
            return self._get_general_reference(language, include_auth, include_error_handling)
    
    def _get_generic_workflow_reference(self, language: str, include_auth: bool, include_error_handling: bool) -> Dict[str, Any]:
        """Get generic Akeyless integration workflow reference."""
        
        if language.lower() == "python":
            return {
                "workflow": "Generic Akeyless Integration Workflow",
                "description": "Core workflow demonstrating authentication, secret management, and runtime integration patterns",
                "prerequisites": [
                    "Akeyless access ID and access key",
                    "Python 3.7+ with requests library",
                    "Basic understanding of environment variables"
                ],
                "complete_implementation": self._get_python_generic_workflow(include_error_handling),
                "step_by_step": [
                    "1. Authenticate with CSM/Akeyless to retrieve the token",
                    "2. Use MCP tool 'manage_secrets' to create secrets (AI assistants should NOT bake secret creation into user applications)",
                    "3. Build/Modify user application to retrieve secrets from CSM/Akeyless at runtime (retrieve token is still the first step)"
                ],
                "best_practices": [
                    "Store Akeyless credentials in environment variables",
                    "Implement token caching to avoid repeated authentication",
                    "Use secrets for configuration, not hardcoded values",
                    "Implement proper error handling and logging",
                    "Use HTTPS for all API calls",
                    "Rotate secrets regularly for security"
                ],
                "use_cases": [
                    "Database connection strings (MySQL, PostgreSQL, MongoDB, etc.)",
                    "Cloud service credentials (AWS, Azure, GCP)",
                    "API keys and authentication tokens",
                    "Application configuration settings",
                    "SSL certificates and private keys",
                    "OAuth credentials and client secrets",
                    "Any sensitive application data that should not be hardcoded"
                ],
                "ai_assistant_recommendations": [
                    "⚠️ IMPORTANT: Use MCP tool 'manage_secrets' to create secrets, NOT the create-secret API endpoint",
                    "AI assistants should create secrets using manage_secrets tool during app development/modification",
                    "User applications should ONLY retrieve existing secrets at runtime, never create new ones",
                    "This ensures proper access control and audit trails for secret management",
                    "Separate development-time secret creation from runtime secret retrieval"
                ]
            }
        
        return {
            "error": f"Language {language} not yet supported for generic workflow",
            "supported_languages": ["python"]
        }
    
    def _get_python_generic_workflow(self, include_error_handling: bool) -> Dict[str, str]:
        """Get Python implementation for generic Akeyless workflow."""
        
        basic_impl = '''import os
import json
import requests
from typing import Dict, Any, Optional

class AkeylessClient:
    """Generic Akeyless client for authentication and secret management."""
    
    def __init__(self, access_id: str, access_key: str, base_url: str):
        self.access_id = access_id
        self.access_key = access_key
        self.base_url = base_url.rstrip('/')
        self.token = None
    
    def authenticate(self) -> str:
        """Authenticate with Akeyless and get access token."""
        url = f"{self.base_url}/auth"
        data = {
            "access-id": self.access_id,
            "access-key": self.access_key
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        self.token = result.get("token")
        return self.token
    
    def create_secret(self, secret_name: str, secret_value: str, description: str = "") -> Dict[str, Any]:
        """Create a new secret in Akeyless."""
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        url = f"{self.base_url}/create-secret"
        data = {
            "name": secret_name,
            "value": secret_value,
            "description": description,
            "token": self.token,
            "accessibility": "regular",
            "multiline-value": True
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve a secret using the authentication token."""
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        url = f"{self.base_url}/get-secret-value"
        data = {
            "names": [secret_name],
            "token": self.token,
            "ignore-cache": "false",
            "json": False
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()

class ApplicationConfig:
    """Application configuration using Akeyless secrets."""
    
    def __init__(self, akeyless_client: AkeylessClient):
        self.akeyless_client = akeyless_client
    
    def get_database_config(self, secret_name: str) -> Dict[str, str]:
        """Get database configuration from Akeyless secret."""
        secret_data = self.akeyless_client.get_secret(secret_name)
        # Parse the secret value (assuming JSON format)
        config = json.loads(secret_data.get("value", "{}"))
        return config
    
    def get_api_key(self, secret_name: str) -> str:
        """Get API key from Akeyless secret."""
        secret_data = self.akeyless_client.get_secret(secret_name)
        return secret_data.get("value", "")

def main():
    """Example usage of generic Akeyless integration."""
    # Configuration from environment variables
    akeyless_access_id = os.getenv("AKEYLESS_ACCESS_ID")
    akeyless_access_key = os.getenv("AKEYLESS_ACCESS_KEY")
    akeyless_url = os.getenv("AKEYLESS_URL", "https://your-akeyless-endpoint")
    
    if not akeyless_access_id or not akeyless_access_key:
        print("Error: AKEYLESS_ACCESS_ID and AKEYLESS_ACCESS_KEY must be set")
        return
    
    try:
        # Initialize and authenticate
        client = AkeylessClient(akeyless_access_id, akeyless_access_key, akeyless_url)
        client.authenticate()
        print("✅ Successfully authenticated with Akeyless")
        
        # Initialize application config
        app_config = ApplicationConfig(client)
        
        # Example: Get database configuration
        db_config = app_config.get_database_config("database-credentials")
        print(f"📊 Database config loaded: {list(db_config.keys())}")
        
        # Example: Get API key
        api_key = app_config.get_api_key("external-api-key")
        print(f"🔑 API key loaded: {api_key[:8]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()'''
        
        result = {"basic_implementation": basic_impl}
        
        if include_error_handling:
            error_handling = '''
# Enhanced error handling and retry logic
import time
from requests.exceptions import RequestException

class AkeylessClient:
    def __init__(self, access_id: str, access_key: str, base_url: str, max_retries: int = 3):
        self.access_id = access_id
        self.access_key = access_key
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.max_retries = max_retries
    
    def authenticate(self) -> str:
        """Authenticate with Akeyless and get token with retry logic."""
        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}/auth"
                data = {
                    "access-id": self.access_id,
                    "access-key": self.access_key
                }
                
                response = requests.post(url, json=data, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                self.token = result.get("token")
                
                if not self.token:
                    raise ValueError("No token received from authentication")
                
                return self.token
                
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Authentication failed after {self.max_retries} attempts: {e}")
                print(f"Authentication attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                raise Exception(f"Authentication error: {e}")
    
    def get_secret(self, secret_name: str) -> Dict[str, Any]:
        """Retrieve a secret using the authentication token with retry logic."""
        if not self.token:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        for attempt in range(self.max_retries):
            try:
                url = f"{self.base_url}/get-secret-value"
                data = {
                    "names": [secret_name],
                    "token": self.token,
                    "ignore-cache": "false",
                    "json": False
                }
                
                response = requests.post(url, json=data, timeout=30)
                response.raise_for_status()
                
                return response.json()
                
            except RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Secret retrieval failed after {self.max_retries} attempts: {e}")
                print(f"Secret retrieval attempt {attempt + 1} failed, retrying...")
                time.sleep(2 ** attempt)
            except Exception as e:
                raise Exception(f"Secret retrieval error: {e}")'''
            
            result["error_handling"] = error_handling
        
        return result
    
    def _get_general_reference(self, language: str, include_auth: bool, include_error_handling: bool) -> Dict[str, Any]:
        """Get general API reference information."""
        
        return {
            "title": "Akeyless Secrets Manager API Reference",
            "description": "Complete reference for native Akeyless integrations",
            "base_url": "https://your-akeyless-endpoint",
            "authentication": {
                "method": "API Key Authentication",
                "endpoint": "/auth",
                "required_fields": ["access-id", "access-key"],
                "response": "Returns JWT token for subsequent requests",
                "token_usage": "Include token in request body, not Authorization header"
            },
            "common_endpoints": [
                "/auth - Authentication endpoint",
                "/create-secret - Create secrets",
                "/get-secret-value - Retrieve secrets", 
                "/list-items - List secrets manager items",
                "/delete-item - Delete individual items",
                "/delete-items - Bulk delete items",
                "/list-roles - List roles and permissions",
                "/target-list - List connection targets"
            ],
            "workflows": [
                "workflow or generic_workflow - Core Akeyless integration patterns"
            ],
            "supported_languages": ["python"],
            "best_practices": [
                "Store credentials in environment variables",
                "Implement proper error handling and retry logic",
                "Use token caching to avoid repeated authentication",
                "Always use HTTPS for API calls",
                "Implement proper logging for audit trails"
            ],
            "ai_assistant_guidance": [
                "🔐 Use MCP tool 'manage_secrets' for secret creation during development",
                "📱 User applications should ONLY retrieve secrets at runtime",
                "🚫 Never bake secret creation into production applications",
                "✅ Separate development-time operations from runtime operations"
            ]
        }
    

    
    def _get_auth_reference(self, language: str, include_error_handling: bool) -> Dict[str, Any]:
        """Get authentication endpoint reference."""
        
        return {
            "endpoint": "/auth",
            "method": "POST",
            "description": "Authenticate with Akeyless and get access token",
            "parameters": {
                "access-id": "Your Akeyless access ID",
                "access-key": "Your Akeyless access key"
            },
            "response_schema": {
                "success": "Boolean indicating if authentication was successful",
                "token": "JWT token for subsequent API calls (string)",
                "refresh_token": "Optional refresh token for token renewal (string)",
                "expires_in": "Token expiration time in seconds (integer)"
            },
            "sample_responses": {
                "success": {
                    "status_code": 200,
                    "body": {
                        "token": "t-abc123def456example789token"
                    },
                    "description": "Successful authentication response - returns JWT token with 't-' prefix"
                },
                "error_invalid_credentials": {
                    "status_code": 401,
                    "body": {
                        "error": "Invalid access credentials",
                        "message": "The provided access ID or access key is incorrect"
                    },
                    "description": "Authentication failed due to invalid credentials"
                },
                "error_missing_fields": {
                    "status_code": 400,
                    "body": {
                        "error": "Missing required fields",
                        "message": "access-id and access-key are required"
                    },
                    "description": "Request missing required authentication fields"
                }
            },
            "example_usage": {
                "python": '''import requests

url = "https://your-akeyless-endpoint/auth"
data = {
    "access-id": "your-access-id",
    "access-key": "your-access-key"
}

response = requests.post(url, json=data)
result = response.json()

if result.get("success"):
    token = result["token"]
    print(f"✅ Authentication successful. Token expires in {result.get('expires_in', 'unknown')} seconds")
else:
    print(f"❌ Authentication failed: {result.get('message', 'Unknown error')}")'''
            }
        }
    
    def _get_create_secret_reference(self, language: str, include_error_handling: bool) -> Dict[str, Any]:
        """Get create secret endpoint reference."""
        
        return {
            "endpoint": "/create-secret",
            "method": "POST", 
            "description": "Create a new secret in Akeyless",
            "warning": "⚠️ This endpoint should ONLY be used when building applications that need to interact with Akeyless programmatically (for example, a developer wants to expose create secrets funtionality in their application programitically for their end users). For AI assistants building/modifying user applications, use the MCP tool 'manage_secrets' instead.",
            "parameters": {
                "name": "Secret name/path",
                "value": "Secret value",
                "token": "Authentication token",
                "description": "Optional description",
                "accessibility": "Access level (default: regular)",
                "multiline-value": "Whether value is multiline (default: true)"
            },
            "response_schema": {
                "success": "Boolean indicating if secret creation was successful",
                "name": "Name/path of the created secret (string)",
                "version": "Version number of the created secret (integer)",
                "id": "Unique identifier for the secret (string)",
                "message": "Success or error message (string)"
            },
            "sample_responses": {
                "success": {
                    "status_code": 200,
                    "body": {
                        "name": "/app-secrets/database-config"
                    },
                    "description": "Secret created successfully - returns the secret name/path"
                },
                "error_already_exists": {
                    "status_code": 409,
                    "body": {
                        "error": "Secret already exists",
                        "message": "A secret with the name '/app-secrets/database-config' already exists"
                    },
                    "description": "Secret with the same name already exists"
                },
                "error_invalid_token": {
                    "status_code": 401,
                    "body": {
                        "error": "Invalid or expired token",
                        "message": "Authentication token is invalid or has expired"
                    },
                    "description": "Authentication token validation failed"
                },
                "error_missing_required": {
                    "status_code": 400,
                    "body": {
                        "error": "Missing required fields",
                        "message": "name, value, and token are required fields"
                    },
                    "description": "Required fields missing from request"
                }
            },
            "example_usage": {
                "python": '''import requests

url = "https://your-akeyless-endpoint/create-secret"
data = {
    "name": "/my-secret",
    "value": "secret-value",
    "token": "your-jwt-token",
    "description": "My secret description",
    "accessibility": "regular",
    "multiline-value": True
}

response = requests.post(url, json=data)
result = response.json()

if result.get("success"):
    print(f"✅ Secret '{result['name']}' created successfully (version {result['version']})")
else:
    print(f"❌ Failed to create secret: {result.get('message', 'Unknown error')}")'''
            }
        }
    
    def _get_get_secret_reference(self, language: str, include_error_handling: bool) -> Dict[str, Any]:
        """Get secret retrieval endpoint reference."""
        
        return {
            "endpoint": "/get-secret-value",
            "method": "POST",
            "description": "Retrieve secret values from Akeyless",
            "parameters": {
                "names": "Array of secret names to retrieve",
                "token": "Authentication token", 
                "ignore-cache": "Ignore cached values (default: false)",
                "json": "Return JSON format (default: false)"
            },
            "response_schema": {
                "success": "Boolean indicating if secret retrieval was successful",
                "value": "The secret value (string or object if json=true)",
                "name": "Name of the retrieved secret (string)",
                "version": "Version number of the secret (integer)",
                "metadata": "Additional secret metadata (object, optional)"
            },
            "sample_responses": {
                "success_text_format": {
                    "status_code": 200,
                    "body": {
                        "/app-secrets/database-config": "{\"username\": \"testuser\", \"password\": \"testpass123\", \"host\": \"test.example.com\", \"port\": 5432}"
                    },
                    "description": "Secret retrieved in text format - returns raw JSON string"
                },
                "success_json_format": {
                    "status_code": 200,
                    "body": {
                        "/app-secrets/database-config": {
                            "host": "test.example.com",
                            "password": "testpass123",
                            "port": 5432,
                            "username": "testuser"
                        }
                    },
                    "description": "Secret retrieved in JSON format - returns parsed object when json=true"
                },
                "success_keyvalue_format": {
                    "status_code": 200,
                    "body": {
                        "/app-secrets/api-credentials": {
                            "api_key": "test123",
                            "region": "us-east-1",
                            "secret_key": "secret456"
                        }
                    },
                    "description": "Key-value secret retrieved in JSON format - returns parsed object"
                },
                "error_secret_not_found": {
                    "status_code": 404,
                    "body": {
                        "error": "Secret not found",
                        "message": "The secret '/non-existent-secret' was not found"
                    },
                    "description": "Requested secret doesn't exist"
                },
                "error_invalid_token": {
                    "status_code": 401,
                    "body": {
                        "error": "Invalid or expired token",
                        "message": "Authentication token is invalid or has expired"
                    },
                    "description": "Authentication token validation failed"
                },
                "error_access_denied": {
                    "status_code": 403,
                    "body": {
                        "error": "Access denied",
                        "message": "You don't have permission to access this secret"
                    },
                    "description": "Insufficient permissions to access the secret"
                }
            },
            "example_usage": {
                "python": '''import requests

url = "https://your-akeyless-endpoint/get-secret-value"
data = {
    "names": ["/my-secret"],
    "token": "your-jwt-token",
    "ignore-cache": "false",
    "json": False
}

response = requests.post(url, json=data)
result = response.json()

if result.get("success"):
    secret_value = result["value"]
    print(f"✅ Secret '{result['name']}' retrieved successfully (version {result['version']})")
    print(f"Value: {secret_value}")
else:
    print(f"❌ Failed to retrieve secret: {result.get('message', 'Unknown error')}")'''
            }
        }
    
    def _get_list_items_reference(self, language: str, include_error_handling: bool) -> Dict[str, Any]:
        """Get list items endpoint reference."""
        
        return {
            "endpoint": "/list-items",
            "method": "POST",
            "description": "List items in Akeyless secrets manager",
            "parameters": {
                "path": "Path to list items from (default: /)",
                "token": "Authentication token",
                "filter": "Filter pattern for item names",
                "pagination-token": "Token for pagination"
            },
            "response_schema": {
                "success": "Boolean indicating if listing was successful",
                "items": "Array of item names/paths (array of strings)",
                "next_page_token": "Token for next page if pagination is available (string, optional)",
                "total_count": "Total number of items (integer, optional)"
            },
            "sample_responses": {
                "success_with_items": {
                    "status_code": 200,
                    "body": {
                        "items": [
                            {
                                "item_name": "/app-secrets/database-config",
                                "item_id": 123456789,
                                "display_id": "33hnxozs0ije-51dlscftbc5f",
                                "item_type": "STATIC_SECRET",
                                "item_sub_type": "generic",
                                "last_version": 1,
                                "with_customer_fragment": True,
                                "is_enabled": True,
                                "creation_date": "2023-08-21T17:42:19Z",
                                "modification_date": "2023-08-21T17:42:19Z"
                            },
                            {
                                "item_name": "/app-secrets/dynamic-db-creds",
                                "item_id": 987654321,
                                "display_id": "33hnxozs0ije-nqe274tlq5ai",
                                "item_type": "DYNAMIC_SECRET",
                                "item_sub_type": "generic",
                                "last_version": 1,
                                "with_customer_fragment": True,
                                "is_enabled": True,
                                "creation_date": "2023-08-23T19:57:49Z"
                            }
                        ],
                        "next_page": "eyJpIjoiL3RoYWxlc2NyeXB0b2xhYnMvdGNsLWRlZmF1bHQta2V5In0="
                    },
                    "description": "Successfully listed items with detailed metadata and pagination"
                },
                "success_empty_directory": {
                    "status_code": 200,
                    "body": {
                        "items": [],
                        "next_page": None
                    },
                    "description": "Directory exists but contains no items"
                },
                "success_with_pagination": {
                    "status_code": 200,
                    "body": {
                        "items": [
                            {
                                "item_name": "/item1",
                                "item_id": 123456,
                                "item_type": "STATIC_SECRET"
                            }
                        ],
                        "next_page": "eyJpIjoiL3NlY3JldC9mb2xkZXIvaXRlbTEifQ=="
                    },
                    "description": "Partial results with base64-encoded pagination token"
                },
                "error_invalid_path": {
                    "status_code": 400,
                    "body": {
                        "error": "Invalid path",
                        "message": "The specified path '/invalid/path' is not valid"
                    },
                    "description": "Requested path is malformed or invalid"
                },
                "error_access_denied": {
                    "status_code": 403,
                    "body": {
                        "error": "Access denied",
                        "message": "You don't have permission to list items in this path"
                    },
                    "description": "Insufficient permissions to list items"
                }
            },
            "example_usage": {
                "python": '''import requests

url = "https://your-akeyless-endpoint/list-items"
data = {
    "path": "/my-secrets/",
    "token": "your-jwt-token",
    "filter": "database*"
}

response = requests.post(url, json=data)
result = response.json()

if result.get("success"):
    items = result["items"]
    print(f"✅ Found {len(items)} items in the specified path")
    for item in items:
        print(f"  - {item}")
    
    if result.get("next_page_token"):
        print(f"📄 More items available. Use next_page_token: {result['next_page_token']}")
else:
    print(f"❌ Failed to list items: {result.get('message', 'Unknown error')}")'''
            }
        }
    
    def _get_delete_item_reference(self, language: str, include_error_handling: bool) -> Dict[str, Any]:
        """Get delete item endpoint reference."""
        
        return {
            "endpoint": "/delete-item",
            "method": "POST",
            "description": "Delete a single item from Akeyless",
            "parameters": {
                "name": "Item name/path to delete",
                "token": "Authentication token",
                "accessibility": "Access level (default: regular)",
                "delete-immediately": "Delete immediately (default: false)",
                "delete-in-days": "Days before deletion (default: 7)"
            },
            "response_schema": {
                "item_name": "Name/path of the deleted item (string)",
                "item_id": "Unique identifier of the deleted item (integer)"
            },
            "sample_responses": {
                "success": {
                    "status_code": 200,
                    "body": {
                        "item_name": "/app-secrets/database-config",
                        "item_id": 555666777
                    },
                    "description": "Item deleted successfully - returns item name and ID"
                },
                "error_item_not_found": {
                    "status_code": 400,
                    "body": {
                        "error": "failed to delete item /non-existent-secret"
                    },
                    "description": "Item not found or cannot be deleted"
                },
                "error_invalid_token": {
                    "status_code": 401,
                    "body": {
                        "error": "Invalid or expired token",
                        "message": "Authentication token is invalid or has expired"
                    },
                    "description": "Authentication token validation failed"
                },
                "error_access_denied": {
                    "status_code": 403,
                    "body": {
                        "error": "Access denied",
                        "message": "You don't have permission to delete this item"
                    },
                    "description": "Insufficient permissions to delete the item"
                }
            },
            "example_usage": {
                "python": '''import requests

url = "https://your-akeyless-endpoint/delete-item"
data = {
    "name": "/my-secret",
    "token": "your-jwt-token",
    "accessibility": "regular",
    "delete-immediately": False,
    "delete-in-days": 7
}

response = requests.post(url, json=data)
result = response.json()

if "item_name" in result:
    print(f"✅ Successfully deleted item: {result['item_name']} (ID: {result['item_id']})")
else:
    print(f"❌ Failed to delete item: {result.get('error', 'Unknown error')}")'''
            }
        }
    
    def _get_list_roles_reference(self, language: str, include_error_handling: bool) -> Dict[str, Any]:
        """Get list roles endpoint reference."""
        
        return {
            "endpoint": "/list-roles",
            "method": "POST",
            "description": "List roles in Akeyless",
            "parameters": {
                "token": "Authentication token",
                "filter": "Filter pattern for role names",
                "pagination-token": "Token for pagination"
            },
            "response_schema": {
                "roles": "Array of role objects (array)",
                "next_page": "Base64-encoded pagination token (string, optional)"
            },
            "sample_responses": {
                "success": {
                    "status_code": 200,
                    "body": {
                        "roles": [
                            {
                                "role_name": "admin",
                                "rules": "",
                                "comment": "Provides full access to the account resources",
                                "role_auth_methods_assoc": "",
                                "client_permissions": None,
                                "creation_date": "2024-05-14T19:28:13Z",
                                "modification_date": "2024-05-14T19:51:57Z",
                                "delete_protection": False
                            },
                            {
                                "role_name": "organization/custom-admins",
                                "rules": "",
                                "comment": "",
                                "role_auth_methods_assoc": " ",
                                "client_permissions": None,
                                "creation_date": "2025-04-01T16:07:37Z",
                                "modification_date": "2025-04-01T17:21:12Z",
                                "delete_protection": True
                            }
                        ],
                        "next_page": "eyJpIjoiYWRtaW4ifQ=="
                    },
                    "description": "Successfully listed roles with detailed metadata and pagination"
                },
                "error_invalid_token": {
                    "status_code": 401,
                    "body": {
                        "error": "Invalid or expired token",
                        "message": "Authentication token is invalid or has expired"
                    },
                    "description": "Authentication token validation failed"
                },
                "error_access_denied": {
                    "status_code": 403,
                    "body": {
                        "error": "Access denied",
                        "message": "You don't have permission to list roles"
                    },
                    "description": "Insufficient permissions to list roles"
                }
            },
            "example_usage": {
                "python": '''import requests

url = "https://your-akeyless-endpoint/list-roles"
data = {
    "token": "your-jwt-token",
    "filter": "admin*"
}

response = requests.post(url, json=data)
result = response.json()

if "roles" in result:
    roles = result["roles"]
    print(f"✅ Found {len(roles)} roles")
    for role in roles:
        print(f"  - {role['role_name']} ({role['comment']})")
    
    if result.get("next_page"):
        print(f"📄 More roles available. Use next_page: {result['next_page']}")
else:
    print(f"❌ Failed to list roles: {result.get('error', 'Unknown error')}")'''
            }
        }
    
    def _get_list_targets_reference(self, language: str, include_error_handling: bool) -> Dict[str, Any]:
        """Get list targets endpoint reference."""
        
        return {
            "endpoint": "/target-list", 
            "method": "POST",
            "description": "List targets in Akeyless",
            "parameters": {
                "token": "Authentication token",
                "filter": "Filter pattern for target names",
                "pagination-token": "Token for pagination",
                "target-types": "Array of target types to filter by"
            },
            "response_schema": {
                "targets": "Array of target objects (array)",
                "next_page": "Base64-encoded pagination token (string, optional)"
            },
            "sample_responses": {
                "success": {
                    "status_code": 200,
                    "body": {
                        "targets": [
                            {
                                "target_name": "/database-targets/postgres-prod",
                                "target_type": "postgres", 
                                "target_id": 100001,
                                "with_customer_fragment": True,
                                "protection_key_name": "",
                                "client_permissions": "read list update delete create",
                                "last_version": 1,
                                "creation_date": "2025-05-15T16:17:18Z",
                                "modification_date": "2025-05-15T16:55:19Z"
                            },
                            {
                                "target_name": "/cloud-targets/aws-production",
                                "target_type": "aws",
                                "target_id": 100002,
                                "with_customer_fragment": True,
                                "protection_key_name": "",
                                "client_permissions": "read list update delete create",
                                "last_version": 1,
                                "creation_date": "2024-02-20T20:50:58Z"
                            },
                            {
                                "target_name": "/k8s-targets/production-cluster",
                                "target_type": "k8s",
                                "target_id": 100003,
                                "with_customer_fragment": True,
                                "protection_key_name": "",
                                "client_permissions": "read list update delete create",
                                "last_version": 1,
                                "creation_date": "2024-01-05T20:18:03Z"
                            }
                        ],
                        "next_page": "eyJpIjoiL2RlbW9zL2RiYS9wb3N0Z3JlU1FMMiJ9"
                    },
                    "description": "Successfully listed targets with detailed metadata and pagination"
                },
                "error_invalid_token": {
                    "status_code": 401,
                    "body": {
                        "error": "Invalid or expired token",
                        "message": "Authentication token is invalid or has expired"
                    },
                    "description": "Authentication token validation failed"
                },
                "error_access_denied": {
                    "status_code": 403,
                    "body": {
                        "error": "Access denied",
                        "message": "You don't have permission to list targets"
                    },
                    "description": "Insufficient permissions to list targets"
                }
            },
            "example_usage": {
                "python": '''import requests

url = "https://your-akeyless-endpoint/target-list"
data = {
    "token": "your-jwt-token",
    "filter": "database*",
    "target-types": ["mysql", "postgres"]
}

response = requests.post(url, json=data)
result = response.json()

if "targets" in result:
    targets = result["targets"]
    print(f"✅ Found {len(targets)} targets")
    for target in targets:
        print(f"  - {target['target_name']} ({target['target_type']}) - ID: {target['target_id']}")
    
    if result.get("next_page"):
        print(f"📄 More targets available. Use next_page: {result['next_page']}")
else:
    print(f"❌ Failed to list targets: {result.get('error', 'Unknown error')}")'''
            }
        }