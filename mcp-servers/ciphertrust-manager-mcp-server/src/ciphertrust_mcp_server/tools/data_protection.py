"""Data Protection tools for managing protection policies, clients and client groups.

This module provides a comprehensive interface to CipherTrust Manager's data protection
functionality through the ksctl CLI. It supports all major data protection operations
including:

Resource Types:
- access_policies: Manage access policies for data protection
- bdt_policies: Execute BDT (Business Data Transformation) policies
- character_sets: Manage character sets for data formatting
- client_profiles: Manage client profiles for data protection clients
- clients: Manage data protection clients
- containers: Manage data containers for protection operations
- data_sources: Manage data sources for protection operations
- dpg_policies: Execute DPG (Data Protection Gateway) policies
- masking_formats: Manage masking formats for data obfuscation
- protection_policies: Manage protection policies
- protection_profiles: Manage protection profiles
- user_sets: Manage user sets for access control

Actions:
- list: List resources with optional filtering
- get: Get details of a specific resource
- create: Create a new resource
- update/modify: Update an existing resource
- delete: Delete a resource
- count: Get count of resources (for clients and client profiles)
- clean: Clean error clients (for client profiles)
- add_user_set: Add user set to access policy
- remove_user_set: Remove user set from access policy
- update_user_set: Update user set in access policy
- error_replacement_value_null: Set error replacement value to null
- error_replacement_value_null_user_set: Set error replacement value to null for user set
- list_users: List users in a user set

Common Parameters:
- id: Resource ID for get/delete operations
- name: Resource name for create/update operations
- description: Description for the resource
- limit: Maximum number of results to return
- skip: Number of results to skip
- domain: Domain for the operation
- auth_domain: Authentication domain for the operation
- jsonfile: JSON file containing resource details

Usage Examples:
    # List all clients
    {"action": "list", "resource_type": "clients"}
    
    # Create a new access policy
    {"action": "create", "resource_type": "access_policies", 
     "params": {"name": "my_policy", "description": "My access policy"}}
    
    # Get a specific client
    {"action": "get", "resource_type": "clients", 
     "params": {"id": "client_id"}}
    
    # Create a protection policy
    {"action": "create", "resource_type": "protection_policies",
     "params": {"name": "my_protection", "algorithm": "AES", "key": "my_key"}}
"""

from typing import Any, Dict, List, Optional, Type

from .base import BaseTool

class DataProtectionTool(BaseTool):
    """Base class for Data Protection management tools.
    
    This tool provides a unified interface to all CipherTrust Manager data protection
    operations. It routes requests to appropriate handlers based on the resource type
    and action specified.
    
    The tool supports all major data protection resource types and operations as
    documented in the ksctl data-protection command documentation.
    
    Attributes:
        name (str): The tool name ("data_protection")
        description (str): Tool description for MCP clients
    """
    
    @property
    def name(self):
        return "data_protection"

    @property
    def description(self):
        return "Manage data protection policies, clients, profiles, and related resources. Supports access policies, BDT policies, character sets, client profiles, clients, containers, data sources, DPG policies, masking formats, protection policies, protection profiles, and user sets."

    def __init__(self) -> None:
        super().__init__()

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        # Common actions
                        "list", "get", "create", "update", "delete", "modify",
                        # Access Policies specific actions
                        "add_user_set", "remove_user_set", "update_user_set", 
                        "error_replacement_value_null", "error_replacement_value_null_user_set",
                        # Client Profiles specific actions
                        "count", "clean",
                        # User Sets specific actions
                        "list_users"
                    ],
                    "description": "The action to perform"
                },
                "resource_type": {
                    "type": "string",
                    "enum": [
                        "access_policies",
                        "bdt_policies",
                        "character_sets",
                        "client_profiles",
                        "clients",
                        "containers",
                        "data_sources",
                        "dpg_policies",
                        "masking_formats",
                        "protection_policies",
                        "protection_profiles",
                        "user_sets"
                    ],
                    "description": "The type of resource to manage"
                },
                "params": {
                    "type": "object",
                    "properties": {
                        # Common parameters
                        "id": {"type": "string", "description": "Resource ID for get/delete operations"},
                        "name": {"type": "string", "description": "Resource name for create/update operations"},
                        "description": {"type": "string", "description": "Description for the resource"},
                        "limit": {"type": "integer", "description": "Maximum number of results to return"},
                        "skip": {"type": "integer", "description": "Number of results to skip"},
                        "domain": {"type": "string", "description": "Domain for the operation"},
                        "auth_domain": {"type": "string", "description": "Authentication domain for the operation"},
                        "jsonfile": {"type": "string", "description": "JSON file containing resource details"},
                        
                        # Access Policies specific parameters
                        "default_masking_format_id": {"type": "string", "description": "Default masking format ID for access policies"},
                        "default_error_replacement_value": {"type": "string", "description": "Default error replacement value for access policies"},
                        "default_reveal_type": {"type": "string", "description": "Default reveal type for access policies (Error Replacement Value, Masked Value, Ciphertext, Plaintext)"},
                        "user_set_id": {"type": "string", "description": "User set ID for user set operations"},
                        "error_replacement_value": {"type": "string", "description": "Value to be revealed if the type is 'Error Replacement Value'"},
                        "masking_format_id": {"type": "string", "description": "Masking format used to reveal if the type is 'Masked Value'"},
                        "reveal_type": {"type": "string", "description": "Value using which data should be revealed"},
                        
                        # Clients specific parameters
                        "app_connector_type": {"type": "string", "description": "Connector type for client registration"},
                        "app_connector_version": {"type": "string", "description": "Version of the app connector"},
                        "client_host_name": {"type": "string", "description": "Client host name"},
                        "client_os_version": {"type": "string", "description": "Client operating system version"},
                        "registration_token": {"type": "string", "description": "Registration token for client registration"},
                        "client_profile_id": {"type": "string", "description": "Client profile ID"},
                        "connectivity_status": {"type": "string", "description": "Client connectivity status"},
                        
                        # Character Sets specific parameters
                        "range": {"type": "string", "description": "Character range for character sets"},
                        "encoding": {"type": "string", "description": "Encoding for character sets"},
                        
                        # Client Profiles specific parameters
                        "ca_id": {"type": "string", "description": "CA ID for client profiles"},
                        "cert_duration": {"type": "integer", "description": "Certificate duration for client profiles"},
                        "configurations": {"type": "string", "description": "Configurations for client profiles"},
                        "csr_parameters": {"type": "string", "description": "CSR parameters for client profiles"},
                        "enable_client_autorenewal": {"type": "boolean", "description": "Enable client auto-renewal"},
                        "groups": {"type": "array", "items": {"type": "string"}, "description": "Groups for client profiles"},
                        "heartbeat_threshold": {"type": "integer", "description": "Heartbeat threshold for client profiles"},
                        "jwt_verification_key": {"type": "string", "description": "JWT verification key for client profiles"},
                        "nae_iface_port": {"type": "integer", "description": "NAE interface port for client profiles"},
                        "policy_id": {"type": "string", "description": "Policy ID for client profiles"},
                        
                        # Containers specific parameters
                        "type": {"type": "string", "description": "Container type"},
                        "username": {"type": "string", "description": "Username for containers"},
                        "password": {"type": "string", "description": "Password for containers"},
                        "driverclass": {"type": "string", "description": "Driver class for containers"},
                        "connection_url": {"type": "string", "description": "Connection URL for containers"},
                        "column_count": {"type": "integer", "description": "Column count for containers"},
                        "column_position_info": {"type": "string", "description": "Column position info for containers"},
                        "delimiter": {"type": "string", "description": "Delimiter for containers"},
                        "filepath": {"type": "string", "description": "File path for containers"},
                        "has_header_row": {"type": "string", "description": "Has header row for containers"},
                        "line_separator": {"type": "string", "description": "Line separator for containers"},
                        "qualifier": {"type": "string", "description": "Qualifier for containers"},
                        "record_length": {"type": "integer", "description": "Record length for containers"},
                        "unescape_input": {"type": "string", "description": "Unescape input for containers"},
                        
                        # Masking Formats specific parameters
                        "ending_characters": {"type": "integer", "description": "Ending characters for masking formats"},
                        "mask_char": {"type": "string", "description": "Mask character for masking formats"},
                        "show": {"type": "boolean", "description": "Show for masking formats"},
                        "starting_characters": {"type": "integer", "description": "Starting characters for masking formats"},
                        "static": {"type": "boolean", "description": "Static for masking formats"},
                        
                        # Protection Policies specific parameters
                        "access_policy_name": {"type": "string", "description": "Access policy name for protection policies"},
                        "algorithm": {"type": "string", "description": "Algorithm for protection policies"},
                        "character_set_id": {"type": "string", "description": "Character set ID for protection policies"},
                        "data_format": {"type": "string", "description": "Data format for protection policies"},
                        "disable_versioning": {"type": "boolean", "description": "Disable versioning for protection policies"},
                        "iv": {"type": "string", "description": "IV for protection policies"},
                        "key": {"type": "string", "description": "Key for protection policies"},
                        "nonce": {"type": "string", "description": "Nonce for protection policies"},
                        "prefix": {"type": "string", "description": "Prefix for protection policies"},
                        "tweak": {"type": "string", "description": "Tweak for protection policies"},
                        "tweak_algorithm": {"type": "string", "description": "Tweak algorithm for protection policies"},
                        "use_external_versioning": {"type": "boolean", "description": "Use external versioning for protection policies"},
                        "aad": {"type": "string", "description": "Additional authenticated data"},
                        "allow_small_input": {"type": "boolean", "description": "Allow small input in protection policy"},
                        "random_nonce": {"type": "string", "description": "Random nonce string"},
                        "tag_length": {"type": "integer", "description": "Length of the tag"},
                        
                        # Protection Profiles specific parameters
                        "allow_single_char_input": {"type": "string", "description": "Allow single char input for protection profiles"},
                        "auth_tag_length": {"type": "string", "description": "Auth tag length for protection profiles"},
                        "ca_list": {"type": "string", "description": "CA list for protection profiles"},
                        "copy_runt_data": {"type": "string", "description": "Copy runt data for protection profiles"},
                        "format": {"type": "string", "description": "Format for protection profiles"},
                        "keep_left": {"type": "integer", "description": "Keep left for protection profiles"},
                        "keep_right": {"type": "integer", "description": "Keep right for protection profiles"},
                        "key_id": {"type": "string", "description": "Key ID for protection profiles"},
                        "luhn_check": {"type": "string", "description": "Luhn check for protection profiles"},
                        "md_name": {"type": "string", "description": "MD name for protection profiles"},
                        "mgf_name": {"type": "string", "description": "MGF name for protection profiles"},
                        "p_src": {"type": "string", "description": "P source for protection profiles"},
                        "salt_length": {"type": "integer", "description": "Salt length for protection profiles"},
                        "save_exceptions": {"type": "string", "description": "Save exceptions for protection profiles"},
                        "suffix": {"type": "string", "description": "Suffix for protection profiles"},
                        
                        # User Sets specific parameters
                        "user": {"type": "string", "description": "User to filter by in list_users operation"}
                    }
                }
            },
            "required": ["action", "resource_type"]
        }

    async def execute(self, **kwargs: Any) -> Any:
        """Execute data protection operations.
        
        This method routes requests to appropriate handlers based on the resource type
        and action specified. It validates required parameters and delegates to the
        appropriate resource-specific handler.
        
        Args:
            **kwargs: Keyword arguments containing:
                - action (str): The action to perform (list, get, create, update, delete, etc.)
                - resource_type (str): The type of resource to manage
                - params (dict): Parameters specific to the operation
                
        Returns:
            Any: The result of the operation, typically a dict or list
            
        Raises:
            ValueError: If required parameters are missing or resource type is unsupported
            
        Example:
            >>> await tool.execute(
            ...     action="list",
            ...     resource_type="clients",
            ...     params={"limit": 10}
            ... )
        """
        action = kwargs.get("action")
        resource_type = kwargs.get("resource_type")
        params = kwargs.get("params", {})

        if not action or not resource_type:
            raise ValueError("action and resource_type are required")

        # Route to appropriate resource handler
        handler = getattr(self, f"_handle_{resource_type}", None)
        if not handler:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        return await handler(action, params)

    async def _handle_clients(self, action: str, params: Dict[str, Any]) -> Any:
        """Handle client operations.
        
        Supports the following actions for data protection clients:
        - list: List all clients with optional filtering
        - get: Get details of a specific client by ID
        - create: Create a new client with registration token
        - update: Update an existing client
        - delete: Delete a client by ID
        - count: Get count of clients with different statuses
        
        Args:
            action (str): The action to perform
            params (dict): Parameters for the operation
            
        Returns:
            Any: Operation result
            
        Raises:
            ValueError: If action is not supported
        """
        if action == "list":
            return await self._list_clients(params)
        elif action == "get":
            return await self._get_client(params)
        elif action == "create":
            return await self._create_client(params)
        elif action == "update":
            return await self._update_client(params)
        elif action == "delete":
            return await self._delete_client(params)
        elif action == "count":
            return await self._count_clients(params)
        else:
            raise ValueError(f"Unsupported action for clients: {action}")

    async def _list_clients(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List clients with optional filtering"""
        cmd = ["data-protection", "clients", "list"]

        if "id" in params:
            cmd.extend(["--id", params["id"]])
        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "app_connector_type" in params:
            cmd.extend(["--app-connector-type", params["app_connector_type"]])
        if "client_profile_id" in params:
            cmd.extend(["--client-profile-id", params["client_profile_id"]])
        if "connectivity_status" in params:
            cmd.extend(["--connectivity-status", params["connectivity_status"]])
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _get_client(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific client"""
        if "id" not in params:
            raise ValueError("Client ID is required for get operation")

        cmd = ["data-protection", "clients", "get", "--id", params["id"]]

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _create_client(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client"""
        required_params = ["app_connector_type", "registration_token", "name"]
        for param in required_params:
            if param not in params:
                raise ValueError(f"{param} is required for create operation")

        cmd = ["data-protection", "clients", "create",
               "--app-connector-type", params["app_connector_type"],
               "--registration-token", params["registration_token"],
               "--name", params["name"]]

        if "app_connector_version" in params:
            cmd.extend(["--app-connector-version", params["app_connector_version"]])
        if "client_host_name" in params:
            cmd.extend(["--client-host-name", params["client_host_name"]])
        if "client_os_version" in params:
            cmd.extend(["--client-os-version", params["client_os_version"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _update_client(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing client"""
        if "id" not in params:
            raise ValueError("Client ID is required for update operation")

        cmd = ["data-protection", "clients", "update", "--id", params["id"]]

        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "app_connector_type" in params:
            cmd.extend(["--app-connector-type", params["app_connector_type"]])
        if "app_connector_version" in params:
            cmd.extend(["--app-connector-version", params["app_connector_version"]])
        if "client_host_name" in params:
            cmd.extend(["--client-host-name", params["client_host_name"]])
        if "client_os_version" in params:
            cmd.extend(["--client-os-version", params["client_os_version"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _delete_client(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a client"""
        if "id" not in params:
            raise ValueError("Client ID is required for delete operation")

        cmd = ["data-protection", "clients", "delete", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _count_clients(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get count of clients with different statuses"""
        cmd = ["data-protection", "clients", "count"]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _handle_access_policies(self, action: str, params: Dict[str, Any]) -> Any:
        """Handle access policy operations.
        
        Supports the following actions for access policies:
        - list: List all access policies with optional filtering
        - get: Get details of a specific access policy by ID
        - create: Create a new access policy
        - update: Update an existing access policy
        - delete: Delete an access policy by ID
        - add_user_set: Add a user set to an access policy
        - remove_user_set: Remove a user set from an access policy
        - update_user_set: Update a user set in an access policy
        - error_replacement_value_null: Set error replacement value to null for policy
        - error_replacement_value_null_user_set: Set error replacement value to null for user set
        
        Args:
            action (str): The action to perform
            params (dict): Parameters for the operation
            
        Returns:
            Any: Operation result
            
        Raises:
            ValueError: If action is not supported
        """
        if action == "list":
            return await self._list_access_policies(params)
        elif action == "get":
            return await self._get_access_policy(params)
        elif action == "create":
            return await self._create_access_policy(params)
        elif action == "update":
            return await self._update_access_policy(params)
        elif action == "delete":
            return await self._delete_access_policy(params)
        elif action == "add_user_set":
            return await self._add_user_set_to_policy(params)
        elif action == "remove_user_set":
            return await self._remove_user_set_from_policy(params)
        elif action == "update_user_set":
            return await self._update_user_set_in_policy(params)
        elif action == "error_replacement_value_null":
            return await self._set_error_replacement_value_null(params)
        elif action == "error_replacement_value_null_user_set":
            return await self._set_error_replacement_value_null_for_user_set(params)
        else:
            raise ValueError(f"Unsupported action for access policies: {action}")

    async def _list_access_policies(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List access policies with optional filtering"""
        cmd = ["data-protection", "access-policies", "list"]

        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _get_access_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for get operation")

        cmd = ["data-protection", "access-policies", "get", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _create_access_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new access policy"""
        if "name" not in params:
            raise ValueError("Name is required for create operation")

        cmd = ["data-protection", "access-policies", "create", "--name", params["name"]]
        
        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "default_masking_format_id" in params:
            cmd.extend(["--default-masking-format-id", params["default_masking_format_id"]])
        if "default_error_replacement_value" in params:
            cmd.extend(["--default-error-replacement-value", params["default_error_replacement_value"]])
        if "default_reveal_type" in params:
            cmd.extend(["--default-reveal-type", params["default_reveal_type"]])
        if "jsonfile" in params:
            cmd.extend(["--jsonfile", params["jsonfile"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _update_access_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for update operation")

        cmd = ["data-protection", "access-policies", "update", "--id", params["id"]]
        
        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "default_masking_format_id" in params:
            cmd.extend(["--default-masking-format-id", params["default_masking_format_id"]])
        if "default_error_replacement_value" in params:
            cmd.extend(["--default-error-replacement-value", params["default_error_replacement_value"]])
        if "default_reveal_type" in params:
            cmd.extend(["--default-reveal-type", params["default_reveal_type"]])
        if "jsonfile" in params:
            cmd.extend(["--jsonfile", params["jsonfile"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _delete_access_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for delete operation")

        cmd = ["data-protection", "access-policies", "delete", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _add_user_set_to_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add a user set to an access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for add_user_set operation")
        if "user_set_id" not in params:
            raise ValueError("User set ID is required for add_user_set operation")

        cmd = ["data-protection", "access-policies", "add-user-set", "--id", params["id"], "--user-set-id", params["user_set_id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _remove_user_set_from_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a user set from an access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for remove_user_set operation")
        if "user_set_id" not in params:
            raise ValueError("User set ID is required for remove_user_set operation")

        cmd = ["data-protection", "access-policies", "remove-user-set", "--id", params["id"], "--user-set-id", params["user_set_id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _update_user_set_in_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a user set in an access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for update_user_set operation")
        if "user_set_id" not in params:
            raise ValueError("User set ID is required for update_user_set operation")

        cmd = ["data-protection", "access-policies", "update-user-set", "--id", params["id"], "--user-set-id", params["user_set_id"]]
        if "jsonfile" in params:
            cmd.extend(["--jsonfile", params["jsonfile"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _set_error_replacement_value_null(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set error replacement value to null for an access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for error_replacement_value_null operation")

        cmd = ["data-protection", "access-policies", "error-replacement-value-null", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _set_error_replacement_value_null_for_user_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Set error replacement value to null for a user set in an access policy"""
        if "id" not in params:
            raise ValueError("Access policy ID is required for error_replacement_value_null_user_set operation")
        if "user_set_id" not in params:
            raise ValueError("User set ID is required for error_replacement_value_null_user_set operation")

        cmd = ["data-protection", "access-policies", "error-replacement-value-null-user-set", "--id", params["id"], "--user-set-id", params["user_set_id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _handle_bdt_policies(self, action: str, params: Dict[str, Any]) -> Any:
        """Handle BDT policy operations"""
        if action == "list":
            return await self._list_bdt_policies(params)
        elif action == "get":
            return await self._get_bdt_policy(params)
        elif action == "create":
            return await self._create_bdt_policy(params)
        elif action == "modify":
            return await self._modify_bdt_policy(params)
        elif action == "delete":
            return await self._delete_bdt_policy(params)
        else:
            raise ValueError(f"Unsupported action for BDT policies: {action}")

    async def _list_bdt_policies(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List BDT policies with optional filtering"""
        cmd = ["data-protection", "bdt-policies", "list"]

        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _get_bdt_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific BDT policy"""
        if "id" not in params:
            raise ValueError("BDT policy ID is required for get operation")

        cmd = ["data-protection", "bdt-policies", "get", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _create_bdt_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new BDT policy"""
        if "jsonfile" not in params:
            raise ValueError("JSON file is required for create operation")

        cmd = ["data-protection", "bdt-policies", "create", "--jsonfile", params["jsonfile"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _modify_bdt_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing BDT policy"""
        if "id" not in params:
            raise ValueError("BDT policy ID is required for modify operation")
        if "jsonfile" not in params:
            raise ValueError("JSON file is required for modify operation")

        cmd = ["data-protection", "bdt-policies", "modify", "--id", params["id"], "--jsonfile", params["jsonfile"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _delete_bdt_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a BDT policy"""
        if "id" not in params:
            raise ValueError("BDT policy ID is required for delete operation")

        cmd = ["data-protection", "bdt-policies", "delete", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _handle_character_sets(self, action: str, params: Dict[str, Any]) -> Any:
        """Handle character set operations"""
        if action == "list":
            return await self._list_character_sets(params)
        elif action == "get":
            return await self._get_character_set(params)
        elif action == "create":
            return await self._create_character_set(params)
        elif action == "update":
            return await self._update_character_set(params)
        elif action == "delete":
            return await self._delete_character_set(params)
        else:
            raise ValueError(f"Unsupported action for character sets: {action}")

    async def _list_character_sets(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List character sets with optional filtering"""
        cmd = ["data-protection", "character-sets", "list"]

        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _get_character_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific character set"""
        if "id" not in params:
            raise ValueError("Character set ID is required for get operation")

        cmd = ["data-protection", "character-sets", "get", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _create_character_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new character set"""
        required_params = ["name", "range", "encoding"]
        for param in required_params:
            if param not in params:
                raise ValueError(f"{param} is required for create operation")

        cmd = ["data-protection", "character-sets", "create",
               "--name", params["name"],
               "--range", params["range"],
               "--encoding", params["encoding"]]

        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _update_character_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing character set"""
        if "id" not in params:
            raise ValueError("Character set ID is required for update operation")

        cmd = ["data-protection", "character-sets", "update", "--id", params["id"]]

        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "range" in params:
            cmd.extend(["--range", params["range"]])
        if "encoding" in params:
            cmd.extend(["--encoding", params["encoding"]])
        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _delete_character_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a character set"""
        if "id" not in params:
            raise ValueError("Character set ID is required for delete operation")

        cmd = ["data-protection", "character-sets", "delete", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _handle_client_profiles(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle client profiles operations."""
        if action == "list":
            return await self._list_client_profiles(params)
        elif action == "get":
            return await self._get_client_profile(params)
        elif action == "create":
            return await self._create_client_profile(params)
        elif action == "update":
            return await self._update_client_profile(params)
        elif action == "delete":
            return await self._delete_client_profile(params)
        elif action == "count":
            return await self._count_client_profiles(params)
        elif action == "clean":
            return await self._clean_client_profile(params)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _list_client_profiles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List client profiles."""
        cmd = ["data-protection", "client-profiles", "list"]
        
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _get_client_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a client profile by ID."""
        if "id" not in params:
            raise ValueError("ID is required for get operation")

        cmd = ["data-protection", "client-profiles", "get", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _create_client_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new client profile."""
        if "name" not in params:
            raise ValueError("Name is required for create operation")

        cmd = ["data-protection", "client-profiles", "create", "--name", params["name"]]

        if "app_connector_type" in params:
            cmd.extend(["--app-connector-type", params["app_connector_type"]])
        if "ca_id" in params:
            cmd.extend(["--ca-id", params["ca_id"]])
        if "cert_duration" in params:
            cmd.extend(["--cert-duration", str(params["cert_duration"])])
        if "configurations" in params:
            cmd.extend(["--configurations", params["configurations"]])
        if "csr_parameters" in params:
            cmd.extend(["--csr-parameters", params["csr_parameters"]])
        if "enable_client_autorenewal" in params:
            cmd.extend(["--enable-client-autorenewal"])
        if "groups" in params:
            for group in params["groups"]:
                cmd.extend(["--groups", group])
        if "heartbeat_threshold" in params:
            cmd.extend(["--heartbeat-threshold", str(params["heartbeat_threshold"])])
        if "jwt_verification_key" in params:
            cmd.extend(["--jwt-verification-key", params["jwt_verification_key"]])
        if "nae_iface_port" in params:
            cmd.extend(["--nae-iface-port", str(params["nae_iface_port"])])
        if "policy_id" in params:
            cmd.extend(["--policy-id", params["policy_id"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _update_client_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a client profile."""
        if "id" not in params:
            raise ValueError("ID is required for update operation")

        cmd = ["data-protection", "client-profiles", "update", "--id", params["id"]]

        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "app_connector_type" in params:
            cmd.extend(["--app-connector-type", params["app_connector_type"]])
        if "ca_id" in params:
            cmd.extend(["--ca-id", params["ca_id"]])
        if "cert_duration" in params:
            cmd.extend(["--cert-duration", str(params["cert_duration"])])
        if "configurations" in params:
            cmd.extend(["--configurations", params["configurations"]])
        if "csr_parameters" in params:
            cmd.extend(["--csr-parameters", params["csr_parameters"]])
        if "enable_client_autorenewal" in params:
            cmd.extend(["--enable-client-autorenewal"])
        if "groups" in params:
            for group in params["groups"]:
                cmd.extend(["--groups", group])
        if "heartbeat_threshold" in params:
            cmd.extend(["--heartbeat-threshold", str(params["heartbeat_threshold"])])
        if "jwt_verification_key" in params:
            cmd.extend(["--jwt-verification-key", params["jwt_verification_key"]])
        if "nae_iface_port" in params:
            cmd.extend(["--nae-iface-port", str(params["nae_iface_port"])])
        if "policy_id" in params:
            cmd.extend(["--policy-id", params["policy_id"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _delete_client_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a client profile."""
        if "id" not in params:
            raise ValueError("ID is required for delete operation")

        cmd = ["data-protection", "client-profiles", "delete", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _count_client_profiles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get count of client profiles with different statuses."""
        cmd = ["data-protection", "client-profiles", "count"]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _clean_client_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clean all error clients associated with a client profile."""
        if "id" not in params:
            raise ValueError("ID is required for clean operation")

        cmd = ["data-protection", "client-profiles", "clean", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _handle_containers(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle container operations."""
        if action == "list":
            return await self._list_containers(params)
        elif action == "get":
            return await self._get_container(params)
        elif action == "create":
            return await self._create_container(params)
        elif action == "modify":
            return await self._modify_container(params)
        elif action == "delete":
            return await self._delete_container(params)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _list_containers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List containers."""
        cmd = ["data-protection", "containers", "list"]
        
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _get_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a container by ID."""
        if "id" not in params:
            raise ValueError("ID is required for get operation")

        cmd = ["data-protection", "containers", "get", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _create_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new container."""
        if "jsonfile" in params:
            cmd = ["data-protection", "containers", "create", "--jsonfile", params["jsonfile"]]
        else:
            if "name" not in params or "type" not in params:
                raise ValueError("Name and type are required for create operation when not using jsonfile")

            cmd = ["data-protection", "containers", "create", "--name", params["name"], "--type", params["type"]]

            if "username" in params:
                cmd.extend(["--username", params["username"]])
            if "password" in params:
                cmd.extend(["--password", params["password"]])
            if "driverclass" in params:
                cmd.extend(["--driverclass", params["driverclass"]])
            if "connection_url" in params:
                cmd.extend(["--connection-url", params["connection_url"]])
            if "column_count" in params:
                cmd.extend(["--column-count", str(params["column_count"])])
            if "column_position_info" in params:
                cmd.extend(["--column-position-info", params["column_position_info"]])
            if "delimiter" in params:
                cmd.extend(["--delimiter", params["delimiter"]])
            if "encoding" in params:
                cmd.extend(["--encoding", params["encoding"]])
            if "filepath" in params:
                cmd.extend(["--filepath", params["filepath"]])
            if "has_header_row" in params:
                cmd.extend(["--has-header-row", params["has_header_row"]])
            if "line_separator" in params:
                cmd.extend(["--line-separator", params["line_separator"]])
            if "qualifier" in params:
                cmd.extend(["--qualifier", params["qualifier"]])
            if "record_length" in params:
                cmd.extend(["--record-length", str(params["record_length"])])
            if "unescape_input" in params:
                cmd.extend(["--unescape-input", params["unescape_input"]])

        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _modify_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modify a container."""
        if "id" not in params:
            raise ValueError("ID is required for modify operation")

        if "jsonfile" in params:
            cmd = ["data-protection", "containers", "modify", "--id", params["id"], "--jsonfile", params["jsonfile"]]
        else:
            cmd = ["data-protection", "containers", "modify", "--id", params["id"]]

            if "name" in params:
                cmd.extend(["--name", params["name"]])
            if "type" in params:
                cmd.extend(["--type", params["type"]])
            if "username" in params:
                cmd.extend(["--username", params["username"]])
            if "password" in params:
                cmd.extend(["--password", params["password"]])
            if "driverclass" in params:
                cmd.extend(["--driverclass", params["driverclass"]])
            if "connection_url" in params:
                cmd.extend(["--connection-url", params["connection_url"]])
            if "column_count" in params:
                cmd.extend(["--column-count", str(params["column_count"])])
            if "column_position_info" in params:
                cmd.extend(["--column-position-info", params["column_position_info"]])
            if "delimiter" in params:
                cmd.extend(["--delimiter", params["delimiter"]])
            if "encoding" in params:
                cmd.extend(["--encoding", params["encoding"]])
            if "filepath" in params:
                cmd.extend(["--filepath", params["filepath"]])
            if "has_header_row" in params:
                cmd.extend(["--has-header-row", params["has_header_row"]])
            if "line_separator" in params:
                cmd.extend(["--line-separator", params["line_separator"]])
            if "qualifier" in params:
                cmd.extend(["--qualifier", params["qualifier"]])
            if "record_length" in params:
                cmd.extend(["--record-length", str(params["record_length"])])
            if "unescape_input" in params:
                cmd.extend(["--unescape-input", params["unescape_input"]])

        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _delete_container(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a container."""
        if "id" not in params:
            raise ValueError("ID is required for delete operation")

        cmd = ["data-protection", "containers", "delete", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _handle_dpg_policies(self, action: str, params: Dict[str, Any]) -> Any:
        """Handle DPG policy operations."""
        if action == "list":
            return await self._list_dpg_policies(params)
        elif action == "get":
            return await self._get_dpg_policy(params)
        elif action == "create":
            return await self._create_dpg_policy(params)
        elif action == "modify":
            return await self._modify_dpg_policy(params)
        elif action == "delete":
            return await self._delete_dpg_policy(params)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _list_dpg_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List DPG policies."""
        cmd = ["data-protection", "dpg-policies", "list"]
        
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _get_dpg_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a DPG policy by ID."""
        if "id" not in params:
            raise ValueError("ID is required for get operation")

        cmd = ["data-protection", "dpg-policies", "get", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _create_dpg_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new DPG policy."""
        if "jsonfile" not in params:
            raise ValueError("jsonfile is required for create operation")

        cmd = ["data-protection", "dpg-policies", "create", "--jsonfile", params["jsonfile"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _modify_dpg_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modify a DPG policy."""
        if "id" not in params or "jsonfile" not in params:
            raise ValueError("ID and jsonfile are required for modify operation")

        cmd = ["data-protection", "dpg-policies", "modify", "--id", params["id"], "--jsonfile", params["jsonfile"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _delete_dpg_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a DPG policy."""
        if "id" not in params:
            raise ValueError("ID is required for delete operation")

        cmd = ["data-protection", "dpg-policies", "delete", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _handle_masking_formats(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle masking format operations."""
        if action == "list":
            return await self._list_masking_formats(params)
        elif action == "get":
            return await self._get_masking_format(params)
        elif action == "create":
            return await self._create_masking_format(params)
        elif action == "update":
            return await self._update_masking_format(params)
        elif action == "delete":
            return await self._delete_masking_format(params)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _list_masking_formats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List masking formats."""
        cmd = ["data-protection", "masking-formats", "list"]
        
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _get_masking_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a masking format by ID."""
        if "id" not in params:
            raise ValueError("ID is required for get operation")

        cmd = ["data-protection", "masking-formats", "get", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _create_masking_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new masking format."""
        if "name" not in params:
            raise ValueError("Name is required for create operation")

        cmd = ["data-protection", "masking-formats", "create", "--name", params["name"]]

        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "ending_characters" in params:
            cmd.extend(["--ending-characters", str(params["ending_characters"])])
        if "mask_char" in params:
            cmd.extend(["--mask-char", params["mask_char"]])
        if "show" in params:
            cmd.extend(["--show"])
        if "starting_characters" in params:
            cmd.extend(["--starting-characters", str(params["starting_characters"])])
        if "static" in params:
            cmd.extend(["--static"])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _update_masking_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a masking format."""
        if "id" not in params:
            raise ValueError("ID is required for update operation")

        cmd = ["data-protection", "masking-formats", "update", "--id", params["id"]]

        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "ending_characters" in params:
            cmd.extend(["--ending-characters", str(params["ending_characters"])])
        if "mask_char" in params:
            cmd.extend(["--mask-char", params["mask_char"]])
        if "show" in params:
            cmd.extend(["--show"])
        if "starting_characters" in params:
            cmd.extend(["--starting-characters", str(params["starting_characters"])])
        if "static" in params:
            cmd.extend(["--static"])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _delete_masking_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a masking format."""
        if "id" not in params:
            raise ValueError("ID is required for delete operation")

        cmd = ["data-protection", "masking-formats", "delete", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _handle_protection_policies(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle protection policy operations."""
        if action == "list":
            return await self._list_protection_policies(params)
        elif action == "get":
            return await self._get_protection_policy(params)
        elif action == "create":
            return await self._create_protection_policy(params)
        elif action == "update":
            return await self._update_protection_policy(params)
        elif action == "delete":
            return await self._delete_protection_policy(params)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _list_protection_policies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List protection policies."""
        cmd = ["data-protection", "protection-policies", "list"]
        
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _get_protection_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a protection policy by name."""
        if "name" not in params:
            raise ValueError("Name is required for get operation")

        cmd = ["data-protection", "protection-policies", "get", "--name", params["name"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _create_protection_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new protection policy."""
        if "name" not in params:
            raise ValueError("Name is required for create operation")

        cmd = ["data-protection", "protection-policies", "create", "--name", params["name"]]

        if "access_policy_name" in params:
            cmd.extend(["--access-policy-name", params["access_policy_name"]])
        if "algorithm" in params:
            cmd.extend(["--algorithm", params["algorithm"]])
        if "character_set_id" in params:
            cmd.extend(["--character-set-id", params["character_set_id"]])
        if "data_format" in params:
            cmd.extend(["--data-format", params["data_format"]])
        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "disable_versioning" in params:
            cmd.extend(["--disable-versioning"])
        if "iv" in params:
            cmd.extend(["--iv", params["iv"]])
        if "key" in params:
            cmd.extend(["--key", params["key"]])
        if "masking_format_id" in params:
            cmd.extend(["--masking-format-id", params["masking_format_id"]])
        if "nonce" in params:
            cmd.extend(["--nonce", params["nonce"]])
        if "prefix" in params:
            cmd.extend(["--prefix", params["prefix"]])
        if "tweak" in params:
            cmd.extend(["--tweak", params["tweak"]])
        if "tweak_algorithm" in params:
            cmd.extend(["--tweak-algorithm", params["tweak_algorithm"]])
        if "use_external_versioning" in params:
            cmd.extend(["--use-external-versioning"])
        if "aad" in params:
            cmd.extend(["--aad", params["aad"]])
        if "allow_small_input" in params:
            cmd.extend(["--allow-small-input"])
        if "random_nonce" in params:
            cmd.extend(["--random-nonce", params["random_nonce"]])
        if "tag_length" in params:
            cmd.extend(["--tag-length", str(params["tag_length"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _update_protection_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a protection policy."""
        if "name" not in params:
            raise ValueError("Name is required for update operation")

        cmd = ["data-protection", "protection-policies", "update", "--name", params["name"]]

        if "access_policy_name" in params:
            cmd.extend(["--access-policy-name", params["access_policy_name"]])
        if "algorithm" in params:
            cmd.extend(["--algorithm", params["algorithm"]])
        if "character_set_id" in params:
            cmd.extend(["--character-set-id", params["character_set_id"]])
        if "data_format" in params:
            cmd.extend(["--data-format", params["data_format"]])
        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "disable_versioning" in params:
            cmd.extend(["--disable-versioning"])
        if "iv" in params:
            cmd.extend(["--iv", params["iv"]])
        if "key" in params:
            cmd.extend(["--key", params["key"]])
        if "masking_format_id" in params:
            cmd.extend(["--masking-format-id", params["masking_format_id"]])
        if "nonce" in params:
            cmd.extend(["--nonce", params["nonce"]])
        if "prefix" in params:
            cmd.extend(["--prefix", params["prefix"]])
        if "tweak" in params:
            cmd.extend(["--tweak", params["tweak"]])
        if "tweak_algorithm" in params:
            cmd.extend(["--tweak-algorithm", params["tweak_algorithm"]])
        if "use_external_versioning" in params:
            cmd.extend(["--use-external-versioning"])
        if "aad" in params:
            cmd.extend(["--aad", params["aad"]])
        if "allow_small_input" in params:
            cmd.extend(["--allow-small-input"])
        if "random_nonce" in params:
            cmd.extend(["--random-nonce", params["random_nonce"]])
        if "tag_length" in params:
            cmd.extend(["--tag-length", str(params["tag_length"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _delete_protection_policy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a protection policy."""
        if "name" not in params:
            raise ValueError("Name is required for delete operation")

        cmd = ["data-protection", "protection-policies", "delete", "--name", params["name"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _handle_protection_profiles(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle protection profile operations."""
        if action == "list":
            return await self._list_protection_profiles(params)
        elif action == "get":
            return await self._get_protection_profile(params)
        elif action == "create":
            return await self._create_protection_profile(params)
        elif action == "modify":
            return await self._modify_protection_profile(params)
        elif action == "delete":
            return await self._delete_protection_profile(params)
        else:
            raise ValueError(f"Unsupported action: {action}")

    async def _list_protection_profiles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List protection profiles."""
        cmd = ["data-protection", "protection-profiles", "list"]
        
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _get_protection_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a protection profile by ID."""
        if "id" not in params:
            raise ValueError("ID is required for get operation")

        cmd = ["data-protection", "protection-profiles", "get", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _create_protection_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new protection profile."""
        if "jsonfile" in params:
            cmd = ["data-protection", "protection-profiles", "create", "--jsonfile", params["jsonfile"]]
        else:
            if "name" not in params:
                raise ValueError("Name is required for create operation when not using jsonfile")

            cmd = ["data-protection", "protection-profiles", "create", "--name", params["name"]]

            if "aad" in params:
                cmd.extend(["--aad", params["aad"]])
            if "algorithm" in params:
                cmd.extend(["--algorithm", params["algorithm"]])
            if "allow_single_char_input" in params:
                cmd.extend(["--allow-single-char-input", params["allow_single_char_input"]])
            if "allow_small_input" in params:
                cmd.extend(["--allow-small-input", params["allow_small_input"]])
            if "auth_tag_length" in params:
                cmd.extend(["--auth-tag-length", params["auth_tag_length"]])
            if "ca_list" in params:
                cmd.extend(["--ca-list", params["ca_list"]])
            if "character_set_id" in params:
                cmd.extend(["--character-set-id", params["character_set_id"]])
            if "copy_runt_data" in params:
                cmd.extend(["--copy-runt-data", params["copy_runt_data"]])
            if "encoding" in params:
                cmd.extend(["--encoding", params["encoding"]])
            if "format" in params:
                cmd.extend(["--format", params["format"]])
            if "iv" in params:
                cmd.extend(["--iv", params["iv"]])
            if "keep_left" in params:
                cmd.extend(["--keep-left", str(params["keep_left"])])
            if "keep_right" in params:
                cmd.extend(["--keep-right", str(params["keep_right"])])
            if "key_id" in params:
                cmd.extend(["--key-id", params["key_id"]])
            if "luhn_check" in params:
                cmd.extend(["--luhn-check", params["luhn_check"]])
            if "md_name" in params:
                cmd.extend(["--md-name", params["md_name"]])
            if "mgf_name" in params:
                cmd.extend(["--mgf-name", params["mgf_name"]])
            if "p_src" in params:
                cmd.extend(["--p-src", params["p_src"]])
            if "prefix" in params:
                cmd.extend(["--prefix", params["prefix"]])
            if "salt_length" in params:
                cmd.extend(["--salt-length", str(params["salt_length"])])
            if "save_exceptions" in params:
                cmd.extend(["--save-exceptions", params["save_exceptions"]])
            if "suffix" in params:
                cmd.extend(["--suffix", params["suffix"]])
            if "tweak" in params:
                cmd.extend(["--tweak", params["tweak"]])

        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _modify_protection_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Modify a protection profile."""
        if "id" not in params:
            raise ValueError("ID is required for modify operation")

        if "jsonfile" in params:
            cmd = ["data-protection", "protection-profiles", "modify", "--id", params["id"], "--jsonfile", params["jsonfile"]]
        else:
            cmd = ["data-protection", "protection-profiles", "modify", "--id", params["id"]]

            if "name" in params:
                cmd.extend(["--name", params["name"]])
            if "aad" in params:
                cmd.extend(["--aad", params["aad"]])
            if "algorithm" in params:
                cmd.extend(["--algorithm", params["algorithm"]])
            if "allow_single_char_input" in params:
                cmd.extend(["--allow-single-char-input", params["allow_single_char_input"]])
            if "allow_small_input" in params:
                cmd.extend(["--allow-small-input", params["allow_small_input"]])
            if "auth_tag_length" in params:
                cmd.extend(["--auth-tag-length", params["auth_tag_length"]])
            if "ca_list" in params:
                cmd.extend(["--ca-list", params["ca_list"]])
            if "character_set_id" in params:
                cmd.extend(["--character-set-id", params["character_set_id"]])
            if "copy_runt_data" in params:
                cmd.extend(["--copy-runt-data", params["copy_runt_data"]])
            if "encoding" in params:
                cmd.extend(["--encoding", params["encoding"]])
            if "format" in params:
                cmd.extend(["--format", params["format"]])
            if "iv" in params:
                cmd.extend(["--iv", params["iv"]])
            if "keep_left" in params:
                cmd.extend(["--keep-left", str(params["keep_left"])])
            if "keep_right" in params:
                cmd.extend(["--keep-right", str(params["keep_right"])])
            if "key_id" in params:
                cmd.extend(["--key-id", params["key_id"]])
            if "luhn_check" in params:
                cmd.extend(["--luhn-check", params["luhn_check"]])
            if "md_name" in params:
                cmd.extend(["--md-name", params["md_name"]])
            if "mgf_name" in params:
                cmd.extend(["--mgf-name", params["mgf_name"]])
            if "p_src" in params:
                cmd.extend(["--p-src", params["p_src"]])
            if "prefix" in params:
                cmd.extend(["--prefix", params["prefix"]])
            if "salt_length" in params:
                cmd.extend(["--salt-length", str(params["salt_length"])])
            if "save_exceptions" in params:
                cmd.extend(["--save-exceptions", params["save_exceptions"]])
            if "suffix" in params:
                cmd.extend(["--suffix", params["suffix"]])
            if "tweak" in params:
                cmd.extend(["--tweak", params["tweak"]])

        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _delete_protection_profile(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a protection profile."""
        if "id" not in params:
            raise ValueError("ID is required for delete operation")

        cmd = ["data-protection", "protection-profiles", "delete", "--id", params["id"]]
        
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        return self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))

    async def _handle_data_sources(self, action: str, params: Dict[str, Any]) -> Any:
        """Handle data source operations"""
        if action == "list":
            return await self._list_data_sources(params)
        elif action == "get":
            return await self._get_data_source(params)
        elif action == "create":
            return await self._create_data_source(params)
        elif action == "update":
            return await self._update_data_source(params)
        elif action == "delete":
            return await self._delete_data_source(params)
        else:
            raise ValueError(f"Unsupported action for data sources: {action}")

    async def _list_data_sources(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List data sources with optional filtering"""
        cmd = ["data-protection", "data-sources", "list"]

        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _get_data_source(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific data source"""
        if "id" not in params:
            raise ValueError("Data source ID is required for get operation")

        cmd = ["data-protection", "data-sources", "get", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _create_data_source(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new data source"""
        if "jsonfile" in params:
            cmd = ["data-protection", "data-sources", "create", "--jsonfile", params["jsonfile"]]
        else:
            if "name" not in params:
                raise ValueError("Name is required for create operation when not using jsonfile")

            cmd = ["data-protection", "data-sources", "create", "--name", params["name"]]

            if "type" in params:
                cmd.extend(["--type", params["type"]])
            if "description" in params:
                cmd.extend(["--description", params["description"]])

        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _update_data_source(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing data source"""
        if "id" not in params:
            raise ValueError("Data source ID is required for update operation")

        cmd = ["data-protection", "data-sources", "update", "--id", params["id"]]

        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "type" in params:
            cmd.extend(["--type", params["type"]])
        if "description" in params:
            cmd.extend(["--description", params["description"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _delete_data_source(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a data source"""
        if "id" not in params:
            raise ValueError("Data source ID is required for delete operation")

        cmd = ["data-protection", "data-sources", "delete", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _handle_user_sets(self, action: str, params: Dict[str, Any]) -> Any:
        """Handle user set operations"""
        if action == "list":
            return await self._list_user_sets(params)
        elif action == "get":
            return await self._get_user_set(params)
        elif action == "create":
            return await self._create_user_set(params)
        elif action == "update":
            return await self._update_user_set(params)
        elif action == "delete":
            return await self._delete_user_set(params)
        elif action == "list_users":
            return await self._list_user_set_users(params)
        else:
            raise ValueError(f"Unsupported action for user sets: {action}")

    async def _list_user_sets(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List user sets with optional filtering"""
        cmd = ["data-protection", "user-sets", "list"]

        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _get_user_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details of a specific user set"""
        if "id" not in params:
            raise ValueError("User set ID is required for get operation")

        cmd = ["data-protection", "user-sets", "get", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _create_user_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user set"""
        if "name" not in params:
            raise ValueError("Name is required for create operation")

        cmd = ["data-protection", "user-sets", "create", "--name", params["name"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _update_user_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user set"""
        if "id" not in params:
            raise ValueError("User set ID is required for update operation")

        cmd = ["data-protection", "user-sets", "update", "--id", params["id"]]
        if "name" in params:
            cmd.extend(["--name", params["name"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _delete_user_set(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user set"""
        if "id" not in params:
            raise ValueError("User set ID is required for delete operation")

        cmd = ["data-protection", "user-sets", "delete", "--id", params["id"]]
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

    async def _list_user_set_users(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """List users in a user set"""
        if "id" not in params:
            raise ValueError("User set ID is required for list_users operation")

        cmd = ["data-protection", "user-sets", "list-users", "--id", params["id"]]
        if "limit" in params:
            cmd.extend(["--limit", str(params["limit"])])
        if "skip" in params:
            cmd.extend(["--skip", str(params["skip"])])
        if "user" in params:
            cmd.extend(["--user", params["user"]])
        if "domain" in params:
            cmd.extend(["--domain", params["domain"]])
        if "auth_domain" in params:
            cmd.extend(["--auth-domain", params["auth_domain"]])

        result = self.execute_with_domain(cmd, params.get("domain"), params.get("auth_domain"))
        return result.get("data", result.get("stdout", ""))

# Export the tool
DATA_PROTECTION_TOOLS = [DataProtectionTool] 
