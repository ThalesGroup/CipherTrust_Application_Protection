"""Template management tools for CipherTrust Manager with built-in domain support.

This module provides comprehensive template management capabilities for CipherTrust Manager,
including creating, listing, getting, updating, and deleting templates. It supports individual
parameter specification for easy key attribute configuration as well as advanced JSON-based
configurations for complex scenarios.

Key Features:
- Full CRUD operations for templates (Create, Read, Update, Delete)
- Domain and authentication domain support for multi-tenant environments
- Individual parameter support for easy key attribute specification
- JSON-based key_attributes for advanced configurations
- Direct template name usage with ksctl --id parameter for get/delete/modify operations
- Comprehensive error handling and validation
- Support for all CipherTrust Manager template types (AES, RSA, EC, etc.)

Important Distinctions:
- 'desc' parameter: Description of the template itself (visible in template listings)
- 'key_description' parameter: Description that will be associated with keys generated using this template

Complete Key Attributes Support:
The tool supports all CipherTrust Manager key attributes including:
- Core: algorithm, size, curveid, usageMask, objectType, format, state
- Dates: activationDate, archiveDate, deactivationDate, processStartDate, processStopDate, protectStopDate  
- Flags: undeletable, unexportable, xts
- Metadata: meta (with ownerId), description (for generated keys)

Simplified Template Operations:
- get/delete/modify operations use ksctl --id parameter directly (accepts template names)
- No additional name-to-ID resolution needed as ksctl handles this natively
- Works with current ksctl behavior where --id accepts template names

All operations support domain-specific execution, making it suitable for enterprise
multi-tenant CipherTrust Manager deployments.
"""

import json
from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Core CRUD Parameter Models
class TemplateListParams(BaseModel):
    """Parameters for listing templates.
    
    Supports filtering by name, labels, creation dates, and metadata. Includes pagination
    controls and search capabilities. All operations support domain-specific execution.
    """
    limit: Optional[int] = Field(None, description="Maximum number of templates to return")
    skip: Optional[int] = Field(None, description="Offset at which to start the search")
    name: Optional[str] = Field(None, description="Filter by template name, ID, URI, or alias")
    id: Optional[str] = Field(None, description="Specify the type of identifier (name, id, uri, alias)")
    labels_query: Optional[str] = Field(None, description="Filter by label selector expressions")
    created_after: Optional[str] = Field(None, description="Time after which the template is created")
    created_before: Optional[str] = Field(None, description="Time before which the template is created")
    meta_contains: Optional[str] = Field(None, description="Search for Meta Data in Template")
    key_attributes_contains: Optional[str] = Field(None, description="Search for Key Attributes in Template")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list templates from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TemplateCreateParams(BaseModel):
    """Parameters for creating a template.
    
    Supports creation of templates with key attributes, metadata, and labels.
    Can accept either individual key attribute parameters or a complete JSON
    specification. All operations support domain-specific execution.
    
    Important: 'desc' is the template description, while 'key_description' 
    is the description that will be associated with keys generated from this template.
    """
    name: str = Field(..., description="Template name (no special characters like <,> or \\)")
    desc: Optional[str] = Field(None, description="Template description (describes the template itself)")
    labels: Optional[str] = Field(None, description="Comma-separated key=value labels")
    meta: Optional[str] = Field(None, description="Meta information in JSON format")
    key_attributes: Optional[str] = Field(None, description="Key attributes in JSON format")
    template_jsonfile: Optional[str] = Field(None, description="Template information passed in JSON format via a file")
    
    # Individual key attribute parameters (for easier use)
    algorithm: Optional[str] = Field(None, description="Template algorithm (AES, RSA, EC, etc.)")
    size: Optional[int] = Field(None, description="Template size in bits")
    curve_id: Optional[str] = Field(None, description="Elliptic curve ID for EC templates")
    usage_mask: Optional[int] = Field(None, description="Template usage mask")
    undeletable: Optional[bool] = Field(None, description="Template cannot be deleted")
    unexportable: Optional[bool] = Field(None, description="Template cannot be exported")
    activation_date: Optional[str] = Field(None, description="Date/time the object becomes active")
    archive_date: Optional[str] = Field(None, description="Date/time the object becomes archived")
    deactivation_date: Optional[str] = Field(None, description="Date/time the object becomes inactive")
    process_start_date: Optional[str] = Field(None, description="Date/time when object may begin processing crypto operations")
    process_stop_date: Optional[str] = Field(None, description="Date/time after which object will not be used for crypto processing")
    protect_stop_date: Optional[str] = Field(None, description="Date/time after which object will not be used for crypto protection")
    
    # Additional key attributes parameters
    object_type: Optional[str] = Field(None, description="Type of cryptographic object")
    key_meta: Optional[str] = Field(None, description="Meta information for keys in JSON format with ownerId")
    format: Optional[str] = Field(None, description="Key format specification")
    xts: Optional[bool] = Field(None, description="Whether to use XTS mode for AES")
    state: Optional[str] = Field(None, description="Initial state of objects created from template")
    key_description: Optional[str] = Field(None, description="Description for keys generated using this template")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create template in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TemplateGetParams(BaseModel):
    """Parameters for getting a template.
    
    Retrieves detailed information about a specific template by name.
    Uses ksctl --id parameter which accepts template names directly.
    Supports domain-specific execution for multi-tenant environments.
    """
    id: str = Field(..., description="Template name or ID (ksctl --id parameter accepts template names)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get template from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TemplateDeleteParams(BaseModel):
    """Parameters for deleting a template.
    
    Deletes a template by name using ksctl --id parameter.
    The --id parameter accepts template names directly in ksctl.
    Includes safety checks and domain-specific execution for secure template management.
    """
    id: str = Field(..., description="Template name or ID (ksctl --id parameter accepts template names)")
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to delete template from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class TemplateModifyParams(BaseModel):
    """Parameters for modifying a template.
    
    Updates template properties including name, description, key attributes, and metadata.
    Uses ksctl --id parameter which accepts template names directly.
    All operations support domain-specific execution.
    
    Important: 'desc' is the template description, while 'key_description' 
    is the description that will be associated with keys generated from this template.
    """
    id: str = Field(..., description="Template name or ID (ksctl --id parameter accepts template names)")
    name: Optional[str] = Field(None, description="New name for the template")
    desc: Optional[str] = Field(None, description="Template description (describes the template itself)")
    labels: Optional[str] = Field(None, description="Comma-separated key=value labels")
    meta: Optional[str] = Field(None, description="Meta information in JSON format")
    key_attributes: Optional[str] = Field(None, description="Key attributes in JSON format")
    template_jsonfile: Optional[str] = Field(None, description="Template information passed in JSON format via a file")
    
    # Individual key attribute parameters (for easier use)
    algorithm: Optional[str] = Field(None, description="Template algorithm")
    size: Optional[int] = Field(None, description="Template size in bits")
    curve_id: Optional[str] = Field(None, description="Elliptic curve ID for EC templates")
    usage_mask: Optional[int] = Field(None, description="Template usage mask")
    undeletable: Optional[bool] = Field(None, description="Template cannot be deleted")
    unexportable: Optional[bool] = Field(None, description="Template cannot be exported")
    activation_date: Optional[str] = Field(None, description="Date/time the object becomes active")
    archive_date: Optional[str] = Field(None, description="Date/time the object becomes archived")
    deactivation_date: Optional[str] = Field(None, description="Date/time the object becomes inactive")
    process_start_date: Optional[str] = Field(None, description="Date/time when object may begin processing crypto operations")
    process_stop_date: Optional[str] = Field(None, description="Date/time after which object will not be used for crypto processing")
    protect_stop_date: Optional[str] = Field(None, description="Date/time after which object will not be used for crypto protection")
    
    # Additional key attributes parameters
    object_type: Optional[str] = Field(None, description="Type of cryptographic object")
    key_meta: Optional[str] = Field(None, description="Meta information for keys in JSON format with ownerId")
    format: Optional[str] = Field(None, description="Key format specification")
    xts: Optional[bool] = Field(None, description="Whether to use XTS mode for AES")
    state: Optional[str] = Field(None, description="Initial state of objects created from template")
    key_description: Optional[str] = Field(None, description="Description for keys generated using this template")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to modify template in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Tool Implementations - Core CRUD
class TemplateManagementTool(BaseTool):
    """Manage templates in CipherTrust Manager.
    
    This tool provides comprehensive template management capabilities including:
    - Basic template operations (list, create, get, delete, modify)
    - Key attribute management with individual parameters or JSON specification
    - Direct template name usage with ksctl --id parameter
    - Domain and authentication domain support for multi-tenant environments
    - Smart key attribute merging for template modifications
    
    **Important: Template Key Attribute Merging**
    When modifying templates with individual key attribute parameters, the tool automatically:
    1. Retrieves the existing template's key attributes
    2. Merges the new attributes with existing ones
    3. Sends the complete merged key attributes to preserve all settings
    
    This ensures that modifying one key attribute (e.g., size) doesn't accidentally
    remove other existing attributes (e.g., algorithm, usageMask, etc.).
    
    All operations support domain-specific execution and include proper error handling
    and response formatting.
    """

    @property
    def name(self) -> str:
        return "template_management"

    @property
    def description(self) -> str:
        return "Template management operations (list, create, get, delete, modify)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "create", "get", "delete", "modify"]},
                **TemplateListParams.model_json_schema()["properties"],
                **TemplateCreateParams.model_json_schema()["properties"],
                **TemplateGetParams.model_json_schema()["properties"],
                **TemplateDeleteParams.model_json_schema()["properties"],
                **TemplateModifyParams.model_json_schema()["properties"],
            },
            "required": ["action"],
            "allOf": [
                {
                    "if": {"properties": {"action": {"enum": ["create"]}}},
                    "then": {"required": ["action", "name"]}
                },
                {
                    "if": {"properties": {"action": {"enum": ["get", "delete", "modify"]}}},
                    "then": {"required": ["action", "id"]}
                }
            ]
        }

    def _build_key_attributes_from_params(self, **kwargs) -> Optional[str]:
        """
        Build key_attributes JSON from individual parameters.
        
        This method converts individual key attribute parameters into a JSON string
        that can be used with the ksctl --key_attributes parameter.
        
        Supports all CipherTrust Manager key attributes including:
        - activationDate, archiveDate, deactivationDate, processStartDate, processStopDate, protectStopDate
        - algorithm, size, curveid, usageMask, format, objectType, state
        - undeletable, unexportable, xts
        - description (for keys generated from template), meta (with ownerId)
        
        Args:
            **kwargs: Individual key attribute parameters
            
        Returns:
            JSON string of key attributes or None if no attributes specified
            
        Raises:
            ValueError: If size value cannot be converted to integer
        """
        key_attrs = {}
        
        # Core algorithm and size parameters
        if kwargs.get('algorithm'):
            key_attrs['algorithm'] = kwargs['algorithm']
        if kwargs.get('size') is not None:
            # Ensure size is an integer
            size_val = kwargs['size']
            if isinstance(size_val, (int, float)):
                key_attrs['size'] = int(size_val)
            else:
                try:
                    key_attrs['size'] = int(size_val)
                except (ValueError, TypeError):
                    raise ValueError(f"Invalid size value: {size_val}. Size must be an integer.")
                    
        # Curve and usage parameters
        if kwargs.get('curve_id'):
            key_attrs['curveid'] = kwargs['curve_id']  # Note: API uses 'curveid'
        if kwargs.get('usage_mask') is not None:
            key_attrs['usageMask'] = kwargs['usage_mask']
            
        # Object properties
        if kwargs.get('object_type'):
            key_attrs['objectType'] = kwargs['object_type']
        if kwargs.get('format'):
            key_attrs['format'] = kwargs['format']
        if kwargs.get('state'):
            key_attrs['state'] = kwargs['state']
            
        # Boolean flags
        if kwargs.get('undeletable') is not None:
            key_attrs['undeletable'] = kwargs['undeletable']
        if kwargs.get('unexportable') is not None:
            key_attrs['unexportable'] = kwargs['unexportable']
        if kwargs.get('xts') is not None:
            key_attrs['xts'] = kwargs['xts']
            
        # Date parameters
        if kwargs.get('activation_date'):
            key_attrs['activationDate'] = kwargs['activation_date']
        if kwargs.get('archive_date'):
            key_attrs['archiveDate'] = kwargs['archive_date']
        if kwargs.get('deactivation_date'):
            key_attrs['deactivationDate'] = kwargs['deactivation_date']
        if kwargs.get('process_start_date'):
            key_attrs['processStartDate'] = kwargs['process_start_date']
        if kwargs.get('process_stop_date'):
            key_attrs['processStopDate'] = kwargs['process_stop_date']
        if kwargs.get('protect_stop_date'):
            key_attrs['protectStopDate'] = kwargs['protect_stop_date']
            
        # Description for keys (different from template description)
        if kwargs.get('key_description'):
            key_attrs['description'] = kwargs['key_description']
            
        # Meta information for keys
        if kwargs.get('key_meta'):
            try:
                # Parse the key_meta JSON string (json is already imported at module level)
                meta_obj = json.loads(kwargs['key_meta']) if isinstance(kwargs['key_meta'], str) else kwargs['key_meta']
                key_attrs['meta'] = meta_obj
            except (json.JSONDecodeError, TypeError):
                raise ValueError(f"Invalid key_meta value: {kwargs['key_meta']}. Must be valid JSON with ownerId.")
            
        return json.dumps(key_attrs) if key_attrs else None

    async def _get_existing_template(self, template_id: str, domain: Optional[str] = None, auth_domain: Optional[str] = None) -> dict:
        """
        Get existing template data for merging key attributes.
        
        Args:
            template_id: Template ID to retrieve
            domain: Domain to get template from
            auth_domain: Authentication domain
            
        Returns:
            Template data dictionary
            
        Raises:
            ValueError: If template cannot be retrieved
        """
        try:
            args = ["templates", "get", "--id", template_id]
            result = self.execute_with_domain(args, domain, auth_domain)
            
            # Parse the result to extract template data
            data = result.get("data", result.get("stdout", ""))
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, ValueError):
                    raise ValueError(f"Failed to parse template response")
            
            if not isinstance(data, dict):
                raise ValueError(f"Unexpected template response format")
                
            return data
            
        except Exception as e:
            raise ValueError(f"Failed to retrieve existing template: {str(e)}")

    def _merge_key_attributes(self, existing_attrs: dict, new_attrs: dict) -> str:
        """
        Merge new key attributes with existing ones.
        
        Args:
            existing_attrs: Current key attributes from template
            new_attrs: New key attributes to merge
            
        Returns:
            JSON string of merged attributes
        """
        # Start with existing attributes
        merged_attrs = existing_attrs.copy() if existing_attrs else {}
        
        # Update with new attributes (this overwrites existing keys)
        merged_attrs.update(new_attrs)
        
        return json.dumps(merged_attrs)

    def _has_key_attribute_changes(self, **kwargs) -> bool:
        """
        Check if any key attribute parameters are being modified.
        
        Returns:
            True if any key attribute parameters are present
        """
        key_attr_params = {
            'algorithm', 'size', 'curve_id', 'usage_mask', 'undeletable', 'unexportable',
            'activation_date', 'archive_date', 'deactivation_date', 'process_start_date', 
            'process_stop_date', 'protect_stop_date', 'object_type', 'key_meta', 'format',
            'xts', 'state', 'key_description'
        }
        
        return any(kwargs.get(param) is not None for param in key_attr_params)

    async def execute(self, action: str, **kwargs: Any) -> Any:
        """
        Execute a template management operation.
        
        Args:
            action: The operation to perform (list, create, get, delete, modify)
            **kwargs: Operation-specific parameters
            
        Returns:
            Operation result data
            
        Raises:
            ValueError: For validation errors, authentication issues, or operation failures
        """
        try:
            if action == "list":
                params = TemplateListParams(**kwargs)
                args = ["templates", "list"]
                
                if params.limit is not None:
                    args.extend(["--limit", str(params.limit)])
                if params.skip is not None:
                    args.extend(["--skip", str(params.skip)])
                if params.name:
                    args.extend(["--name", params.name])
                if params.id:
                    args.extend(["--id", params.id])
                if params.labels_query:
                    args.extend(["--labels-query", params.labels_query])
                if params.created_after:
                    args.extend(["--created_after", params.created_after])
                if params.created_before:
                    args.extend(["--created_before", params.created_before])
                if params.meta_contains:
                    args.extend(["--meta_contains", params.meta_contains])
                if params.key_attributes_contains:
                    args.extend(["--key_attributes_contains", params.key_attributes_contains])
                    
                result = self.execute_with_domain(args, params.domain, params.auth_domain)
                return result.get("data", result.get("stdout", ""))
                
            elif action == "create":
                params = TemplateCreateParams(**kwargs)
                args = ["templates", "create", "--name", params.name]
                
                if params.desc:
                    args.extend(["--desc", params.desc])
                if params.labels:
                    args.extend(["--labels", params.labels])
                if params.meta:
                    args.extend(["--meta", params.meta])
                
                # Use provided key_attributes or build from individual parameters
                key_attributes = params.key_attributes
                if not key_attributes:
                    # Build from individual parameters
                    key_attributes = self._build_key_attributes_from_params(**params.dict())
                
                if key_attributes:
                    args.extend(["--key_attributes", key_attributes])
                    
                if params.template_jsonfile:
                    args.extend(["--template_jsonfile", params.template_jsonfile])
                    
                result = self.execute_with_domain(args, params.domain, params.auth_domain)
                return result.get("data", result.get("stdout", ""))
                
            elif action == "get":
                params = TemplateGetParams(**kwargs)
                
                # Use --id parameter directly (ksctl accepts template names)
                args = ["templates", "get", "--id", params.id]
                    
                result = self.execute_with_domain(args, params.domain, params.auth_domain)
                return result.get("data", result.get("stdout", ""))
                
            elif action == "delete":
                params = TemplateDeleteParams(**kwargs)
                
                # Use --id parameter directly (ksctl accepts template names)
                args = ["templates", "delete", "--id", params.id]
                    
                result = self.execute_with_domain(args, params.domain, params.auth_domain)
                return result.get("data", result.get("stdout", ""))
                
            elif action == "modify":
                params = TemplateModifyParams(**kwargs)
                
                # Use --id parameter directly (ksctl accepts template names)
                args = ["templates", "update", "--id", params.id]
                
                # Optional parameters to update the template
                if params.name:
                    args.extend(["--name", params.name])
                if params.desc:
                    args.extend(["--desc", params.desc])
                if params.labels:
                    args.extend(["--labels", params.labels])
                if params.meta:
                    args.extend(["--meta", params.meta])
                
                # Handle key attributes with merging logic
                key_attributes = params.key_attributes
                if not key_attributes:
                    # Check if any individual key attribute parameters are being modified
                    if self._has_key_attribute_changes(**params.dict()):
                        # Get existing template to merge key attributes
                        existing_template = await self._get_existing_template(params.id, params.domain, params.auth_domain)
                        existing_key_attrs = existing_template.get("key_attributes", {})
                        
                        # Build new key attributes from individual parameters
                        new_key_attrs_json = self._build_key_attributes_from_params(**params.dict())
                        new_key_attrs = json.loads(new_key_attrs_json) if new_key_attrs_json else {}
                        
                        # Merge existing with new attributes
                        key_attributes = self._merge_key_attributes(existing_key_attrs, new_key_attrs)
                
                if key_attributes:
                    args.extend(["--key_attributes", key_attributes])
                    
                if params.template_jsonfile:
                    args.extend(["--template_jsonfile", params.template_jsonfile])
                    
                result = self.execute_with_domain(args, params.domain, params.auth_domain)
                return result.get("data", result.get("stdout", ""))
                
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            # Enhanced error handling
            error_msg = str(e)
            if "validation error" in error_msg.lower():
                raise ValueError(f"Parameter validation error: {error_msg}")
            elif "command not found" in error_msg.lower():
                raise ValueError(f"CipherTrust Manager command error: {error_msg}")
            elif "authentication" in error_msg.lower():
                raise ValueError(f"Authentication error: {error_msg}")
            else:
                raise ValueError(f"Template operation failed: {error_msg}")


# Helper functions for building key_attributes JSON
def build_key_attributes_json(**attributes) -> str:
    """
    Build key_attributes JSON string for template creation.
    
    This helper function creates a properly formatted JSON string for use with
    the --key_attributes parameter in ksctl commands.
    
    Valid attributes according to CipherTrust Manager documentation:
    - activationDate: string - Date/time the object becomes active
    - algorithm: string - Encryption algorithm (AES, RSA, EC, etc.)
    - objectType: string - Type of cryptographic object
    - archiveDate: string - Date/time the object becomes archived
    - curveid: string - Elliptic curve identifier for EC keys
    - deactivationDate: string - Date/time the object becomes inactive
    - meta: {"ownerId": string} - Metadata with owner information
    - processStartDate: string - Date/time when object may begin processing
    - processStopDate: string - Date/time after which object won't be used for processing
    - protectStopDate: string - Date/time after which object won't be used for protection
    - size: integer - Key size in bits (128, 192, 256 for AES; 1024, 2048, 4096 for RSA)
    - undeletable: boolean - Whether the template cannot be deleted
    - unexportable: boolean - Whether the template cannot be exported
    - usageMask: integer - Bitmask defining allowed operations
    - format: string - Key format specification
    - xts: boolean - Whether to use XTS mode for AES
    - state: string - Initial state of objects created from template
    - description: string - Description for keys generated using this template (different from template description)
    
    Args:
        **attributes: Key-value pairs of template attributes
        
    Returns:
        JSON string representation of the attributes
        
    Raises:
        ValueError: If unknown attributes are provided
        
    Example:
        >>> build_key_attributes_json(algorithm="AES", size=256, undeletable=True, description="Customer data encryption key")
        '{"algorithm": "AES", "size": 256, "undeletable": true, "description": "Customer data encryption key"}'
    """
    # Filter out None values
    filtered_attributes = {k: v for k, v in attributes.items() if v is not None}
    
    # Validate known attributes (Both processStopDate and protectStopDate are valid)
    valid_attrs = {
        'activationDate', 'algorithm', 'objectType', 'archiveDate', 'curveid',
        'deactivationDate', 'meta', 'processStartDate', 'processStopDate', 'protectStopDate',
        'size', 'undeletable', 'unexportable', 'usageMask', 'format',
        'xts', 'state', 'description'
    }
    
    unknown_attrs = set(filtered_attributes.keys()) - valid_attrs
    if unknown_attrs:
        raise ValueError(f"Unknown key attributes: {unknown_attrs}")
    
    return json.dumps(filtered_attributes)


def build_meta_json(**meta_data) -> str:
    """
    Build meta JSON string for template creation.
    
    This helper function creates a properly formatted JSON string for use with
    the --meta parameter in ksctl commands.
    
    Args:
        **meta_data: Key-value pairs of metadata
        
    Returns:
        JSON string representation of the metadata
        
    Example:
        >>> build_meta_json(ownerId="user123", department="security")
        '{"ownerId": "user123", "department": "security"}'
    """
    return json.dumps(meta_data)


# Usage examples
def get_template_examples():
    """
    Get template usage examples.
    
    This function provides comprehensive examples of how to use the template
    management tool for various scenarios, including the distinction between
    template description (--desc) and key description (description in key_attributes).
    
    Returns:
        Dictionary containing example usage patterns for all template operations
    """
    return {
        "create_basic_template_with_individual_params": {
            "description": "Create a basic AES template using individual parameters",
            "action": "create",
            "name": "aes_256_template",
            "desc": "AES 256-bit encryption template for customer data",  # Template description
            "algorithm": "AES",
            "size": 256,
            "usage_mask": 12,  # Encrypt + Decrypt
            "undeletable": False,
            "unexportable": False,
            "key_description": "Customer data encryption key"  # Description for keys generated from template
        },
        "create_comprehensive_template": {
            "description": "Create a comprehensive template with all key attributes",
            "action": "create",
            "name": "comprehensive_aes_template",
            "desc": "Comprehensive AES template with all attributes",  # Template description
            "algorithm": "AES",
            "size": 256,
            "usage_mask": 12,
            "object_type": "Symmetric Key",
            "format": "raw",
            "xts": False,
            "state": "Active",
            "undeletable": True,
            "unexportable": False,
            "activation_date": "2025-01-01T00:00:00Z",
            "process_start_date": "2025-01-01T00:00:00Z",
            "key_description": "Production encryption key for sensitive data",  # Key description
            "key_meta": '{"ownerId": "admin"}'  # Meta for keys
        },
        "create_template_with_json": {
            "description": "Create a template using key_attributes JSON",
            "action": "create",
            "name": "aes_256_json_template",
            "desc": "AES 256-bit template created with JSON attributes",  # Template description
            "key_attributes": build_key_attributes_json(
                algorithm="AES",
                size=256,
                usageMask=12,  # Encrypt + Decrypt
                undeletable=False,
                unexportable=False,
                description="JSON-defined customer encryption key",  # Key description
                meta={"ownerId": "security_team"},
                state="Active"
            )
        },
        "create_rsa_template": {
            "description": "Create an RSA template for signing operations",
            "action": "create", 
            "name": "rsa_2048_template",
            "desc": "RSA 2048-bit signing template for document verification",  # Template description
            "algorithm": "RSA",
            "size": 2048,
            "usage_mask": 8,  # Sign
            "undeletable": True,
            "labels": "key_type=rsa,purpose=signing",
            "key_description": "Document signing key",  # Key description
            "object_type": "Private Key"
        },
        "create_ec_template": {
            "description": "Create an Elliptic Curve template",
            "action": "create",
            "name": "ec_p256_template", 
            "desc": "EC P-256 template for digital signatures",  # Template description
            "algorithm": "EC",
            "curve_id": "secp256r1",
            "usage_mask": 8,  # Sign
            "key_description": "ECDSA signing key",  # Key description
            "format": "PKCS#1"
        },
        "list_templates": {
            "description": "List all templates with pagination",
            "action": "list",
            "limit": 20
        },
        "list_with_filter": {
            "description": "List templates with label-based filtering",
            "action": "list",
            "labels_query": "key_type=rsa",
            "limit": 10
        },
        "get_template_by_name": {
            "description": "Retrieve a specific template by name using --id parameter",
            "action": "get",
            "id": "aes_256_template"  # Template name directly
        },
        "get_template_by_id": {
            "description": "Retrieve a specific template by ID using --id parameter",
            "action": "get",
            "id": "ece51cf0-bbf9-47ad-9d28-f2d82707cccc"  # UUID directly
        },
        "update_template_name": {
            "description": "Update template name using template name",
            "action": "modify",
            "id": "old_template_name",  # Template name
            "name": "new_template_name"
        },
        "update_template_description": {
            "description": "Update template description using template name",
            "action": "modify",
            "id": "aes_256_template",  # Template name
            "desc": "Updated template description"  # Template description
        },
        "update_template_key_attributes": {
            "description": "Update template key attributes (automatically merges with existing attributes)",
            "action": "modify",
            "id": "temp_aes",  # Template name
            "algorithm": "AES",
            "size": 128,  # Changed from 256 to 128
            "key_description": "Updated key description for generated keys",  # Key description
            "state": "Pre-Active"
            # Note: Tool automatically preserves other existing key attributes
        },
        "update_template_comprehensive": {
            "description": "Comprehensive template update with multiple key attributes (preserves existing attributes)",
            "action": "modify",
            "id": "comprehensive_template",  # Template name
            "desc": "Updated comprehensive template",  # Template description
            "algorithm": "AES",
            "size": 256,
            "usage_mask": 15,  # All operations
            "key_description": "Multi-purpose encryption key",  # Key description
            "xts": True,
            "state": "Active",
            "undeletable": True,
            "key_meta": '{"ownerId": "updated_owner"}'
            # Important: Tool automatically merges these with existing key attributes
        },
        "delete_template_by_name": {
            "description": "Delete a template by name using --id parameter",
            "action": "delete",
            "id": "aes_256_template"  # Template name directly
        },
        "delete_template_by_id": {
            "description": "Delete a template by ID using --id parameter",
            "action": "delete",
            "id": "ece51cf0-bbf9-47ad-9d28-f2d82707cccc"  # UUID directly
        }
    }


# Export the tools
TEMPLATE_TOOLS = [TemplateManagementTool]