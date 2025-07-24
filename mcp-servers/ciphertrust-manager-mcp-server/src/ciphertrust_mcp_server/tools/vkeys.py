"""Versioned Keys management tools for CipherTrust Manager with built-in domain support."""

from typing import Any, Optional

from pydantic import BaseModel, Field

from .base import BaseTool


# Versioned Keys Parameter Models
class VKeysCreateParams(BaseModel):
    """Parameters for creating a new version of an existing key."""
    name: str = Field(..., description="Key name, ID or URI to create new version of")
    
    # Key material and certificates
    material: Optional[str] = Field(None, description="Key material or certificate material")
    cert_filename: Optional[str] = Field(None, description="Certificate file name (X.509 in PEM or DER format)")
    cert_type: Optional[str] = Field(None, description="Certificate type: 'x509-pem' or 'x509-der'")
    
    # Key properties
    aliases: Optional[str] = Field(None, description="Comma separated list of key aliases")
    defaultiv: Optional[str] = Field(None, description="Hex encoded default IV for the key")
    description: Optional[str] = Field(None, description="Key description")
    encoding: Optional[str] = Field(None, description="Encoding for material field: 'hex' or 'base64'")
    format: Optional[str] = Field(None, description="Key format: 'pkcs1' or 'pkcs8' (default: pkcs8)")
    id_size: Optional[int] = Field(None, description="Size of ID for the key")
    key_id: Optional[str] = Field(None, description="Additional key identifier")
    muid: Optional[str] = Field(None, description="Additional key MUID")
    uuid: Optional[str] = Field(None, description="Key UUID (32 hex digits with 4 dashes)")
    
    # Key management
    include_material: Optional[bool] = Field(None, description="Include key bytes in response")
    labels: Optional[str] = Field(None, description="Comma separated key/value pairs for labels")
    remove_labels: Optional[str] = Field(None, description="Comma separated label keys to remove")
    offset: Optional[int] = Field(None, description="Offset for dates from existing key")
    
    # Key wrapping
    padded: Optional[bool] = Field(None, description="Use RFC-5649 for wrap-key-name")
    wrap_key_name: Optional[str] = Field(None, description="Key name for wrapping material")
    wrap_public_key: Optional[str] = Field(None, description="RSA public key for wrapping (PEM format)")
    wrap_public_key_file: Optional[str] = Field(None, description="File containing public key for wrapping")
    
    # Identification
    type: Optional[str] = Field(None, description="Type of id parameter: 'id', 'name', or 'slug'")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to create key version in (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class VKeysListParams(BaseModel):
    """Parameters for listing all versions of a key."""
    name: str = Field(..., description="Key name, ID or URI to list versions for")
    
    # Filtering
    alias: Optional[str] = Field(None, description="Key alias filter (supports '?' and '*' wildcards)")
    fields: Optional[str] = Field(None, description="Fields to include: 'meta', 'links' (comma separated)")
    link_type: Optional[str] = Field(None, description="Link type filter (supports wildcards)")
    state: Optional[str] = Field(None, description="Key state: 'Pre-Active', 'Active', 'Deactivated', 'Destroyed', 'Compromised', 'Destroyed Compromised'")
    
    # Pagination
    limit: int = Field(10, description="Maximum number of key versions to return")
    skip: int = Field(0, description="Offset to start search from")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to list key versions from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class VKeysGetParams(BaseModel):
    """Parameters for getting a specific version of a key."""
    name: str = Field(..., description="Key name, ID or URI")
    version: int = Field(..., description="Key version number (starts at 0)")
    
    # Key properties
    usage_mask: Optional[int] = Field(None, description="Key usage mask (bitwise OR of usage values)")
    type: Optional[str] = Field(None, description="Type of id parameter: 'id', 'name', or 'slug'")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to get key version from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


class VKeysExportParams(BaseModel):
    """Parameters for exporting a specific version of a key."""
    name: str = Field(..., description="Key name, ID or URI")
    version: int = Field(..., description="Key version number (starts at 0)")
    
    # Export format
    encoding: Optional[str] = Field(None, description="Encoding for material field: 'hex' or 'base64'")
    format: Optional[str] = Field(None, description="Key format: 'pkcs1' or 'pkcs8' (default: pkcs8)")
    type: Optional[str] = Field(None, description="Type of id parameter: 'id', 'name', or 'slug'")
    
    # Key wrapping
    padded: Optional[bool] = Field(None, description="Use RFC-5649 for wrap-key-name")
    wrap_key_name: Optional[str] = Field(None, description="Key name for wrapping material")
    wrap_public_key: Optional[str] = Field(None, description="RSA public key for wrapping (PEM format)")
    wrap_public_key_file: Optional[str] = Field(None, description="File containing public key for wrapping")
    wrap_public_key_padding: Optional[str] = Field(None, description="Padding scheme: 'pkcs1', 'oaep', 'oaep256'")
    
    # Deprecated (maintained for compatibility)
    wrapfmt: Optional[str] = Field(None, description="Deprecated: use 'format' instead")
    wrappubk: Optional[str] = Field(None, description="Deprecated: use 'wrap-public-key' instead")
    
    # Domain support
    domain: Optional[str] = Field(None, description="Domain to export key version from (defaults to global setting)")
    auth_domain: Optional[str] = Field(None, description="Authentication domain (defaults to global setting)")


# Versioned Keys Management Tools
class VKeysManagementTool(BaseTool):
    name = "vkeys_management"
    description = "Versioned key management operations (create, list, get, export)"

    def get_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "list", "get", "export"]},
                **VKeysCreateParams.model_json_schema()["properties"],
                **VKeysListParams.model_json_schema()["properties"],
                **VKeysGetParams.model_json_schema()["properties"],
                **VKeysExportParams.model_json_schema()["properties"],
            },
            "required": ["action"],
        }

    async def execute(self, action: str, **kwargs: Any) -> Any:
        if action == "create":
            params = VKeysCreateParams(**kwargs)
            args = ["vkeys", "create", "--name", params.name]
            if params.material:
                args.extend(["--material", params.material])
            if params.cert_filename:
                args.extend(["--cert-filename", params.cert_filename])
            if params.cert_type:
                args.extend(["--cert-type", params.cert_type])
            if params.aliases:
                args.extend(["--aliases", params.aliases])
            if params.defaultiv:
                args.extend(["--defaultiv", params.defaultiv])
            if params.description:
                args.extend(["--description", params.description])
            if params.encoding:
                args.extend(["--encoding", params.encoding])
            if params.format:
                args.extend(["--format", params.format])
            if params.id_size is not None:
                args.extend(["--id-size", str(params.id_size)])
            if params.key_id:
                args.extend(["--key-id", params.key_id])
            if params.muid:
                args.extend(["--muid", params.muid])
            if params.uuid:
                args.extend(["--uuid", params.uuid])
            if params.include_material:
                args.append("--include-material")
            if params.labels:
                args.extend(["--labels", params.labels])
            if params.remove_labels:
                args.extend(["--remove-labels", params.remove_labels])
            if params.offset is not None:
                args.extend(["--offset", str(params.offset)])
            if params.padded:
                args.append("--padded")
            if params.wrap_key_name:
                args.extend(["--wrap-key-name", params.wrap_key_name])
            if params.wrap_public_key:
                args.extend(["--wrap-public-key", params.wrap_public_key])
            if params.wrap_public_key_file:
                args.extend(["--wrap-public-key-file", params.wrap_public_key_file])
            if params.type:
                args.extend(["--type", params.type])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "list":
            params = VKeysListParams(**kwargs)
            args = ["vkeys", "list", "--name", params.name, "--limit", str(params.limit), "--skip", str(params.skip)]
            if params.alias:
                args.extend(["--alias", params.alias])
            if params.fields:
                args.extend(["--fields", params.fields])
            if params.link_type:
                args.extend(["--link-type", params.link_type])
            if params.state:
                args.extend(["--state", params.state])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "get":
            params = VKeysGetParams(**kwargs)
            args = ["vkeys", "get", "--name", params.name, "--version", str(params.version)]
            if params.usage_mask is not None:
                args.extend(["--usage-mask", str(params.usage_mask)])
            if params.type:
                args.extend(["--type", params.type])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        elif action == "export":
            params = VKeysExportParams(**kwargs)
            args = ["vkeys", "export", "--name", params.name, "--version", str(params.version)]
            if params.encoding:
                args.extend(["--encoding", params.encoding])
            if params.format:
                args.extend(["--format", params.format])
            if params.type:
                args.extend(["--type", params.type])
            if params.padded:
                args.append("--padded")
            if params.wrap_key_name:
                args.extend(["--wrap-key-name", params.wrap_key_name])
            if params.wrap_public_key:
                args.extend(["--wrap-public-key", params.wrap_public_key])
            if params.wrap_public_key_file:
                args.extend(["--wrap-public-key-file", params.wrap_public_key_file])
            if params.wrap_public_key_padding:
                args.extend(["--wrap-public-key-padding", params.wrap_public_key_padding])
            if params.wrapfmt:
                args.extend(["--wrapfmt", params.wrapfmt])
            if params.wrappubk:
                args.extend(["--wrappubk", params.wrappubk])
            result = self.execute_with_domain(args, params.domain, params.auth_domain)
            return result.get("data", result.get("stdout", ""))
        else:
            raise ValueError(f"Unknown action: {action}")

VKEYS_TOOLS = [VKeysManagementTool]
