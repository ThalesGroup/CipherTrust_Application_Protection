"""OCI Issuer operations for CCKM."""

from typing import Any, Dict


def get_issuer_operations() -> Dict[str, Any]:
    """Return schema and action requirements for OCI issuer operations."""
    return {
        "schema_properties": {
            "oci_issuers_params": {
                "type": "object",
                "properties": {
                    # Basic issuer parameters
                    "id": {
                        "type": "string", 
                        "description": "OCI issuer ID, OCID, or issuer name. Smart resolution automatically handles issuer name to OCID conversion. CRITICAL FOR AI ASSISTANTS: Always use this 'id' parameter for issuer identification operations, even when users specify issuer names - never use 'name' or 'issuer_name' parameters."
                    },
                    "issuer_name": {"type": "string", "description": "Name for the issuer"},
                    "issuer_type": {"type": "string", "description": "Type of issuer"},
                    "issuer_config": {"type": "object", "description": "Configuration for the issuer"},
                    "jwks_uri_protected": {"type": "boolean", "description": "Set true for a protected JWSK URI and false for unprotected JWKS URI"},
                    "oci_issuer": {"type": "string", "description": "Issuer URL for the issuer"},
                    
                    # Common parameters
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort field and order"},
                    
                    # JSON file parameters
                    "oci_issuer_create_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing OCI issuer creation parameters. Use absolute file paths for reliability."
                    },
                    "oci_issuer_update_jsonfile": {
                        "type": "string", 
                        "description": "Path to JSON file containing OCI issuer update parameters. Use absolute file paths for reliability."
                    },
                    
                    # Description and metadata
                    "description": {"type": "string", "description": "Issuer description"},
                    "metadata": {"type": "object", "description": "Additional metadata for the issuer"},
                    
                    # Filter parameters
                    "issuer_type_filter": {"type": "string", "description": "Filter by issuer type"},
                    "status": {"type": "string", "description": "Filter by issuer status"}
                }
            }
        },
        "action_requirements": {
            "issuers_list": {"required": [], "optional": ["limit", "skip", "sort", "issuer_type_filter", "status", "issuer_name", "jwks_uri_protected", "oci_issuer"]},
            "issuers_get": {"required": ["id"], "optional": []},
            "issuers_create": {"required": ["issuer_name", "issuer_type"], "optional": ["issuer_config", "description", "metadata", "oci_issuer_create_jsonfile"]},
            "issuers_update": {"required": ["id"], "optional": ["issuer_name", "issuer_type", "issuer_config", "description", "metadata", "oci_issuer_update_jsonfile"]},
            "issuers_delete": {"required": ["id"], "optional": []},
        }
    }


def build_issuer_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI issuer operation."""
    cmd = ["cckm", "oci", "issuers"]
    
    # Extract the base operation name (remove 'issuers_' prefix)
    base_action = action.replace("issuers_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete"]
    
    if base_action in simple_actions:
        cmd.extend([base_action, "--id", oci_params["id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "issuer_type_filter" in oci_params:
            cmd.extend(["--issuer-type-filter", oci_params["issuer_type_filter"]])
        if "status" in oci_params:
            cmd.extend(["--status", oci_params["status"]])
        if "issuer_name" in oci_params:
            cmd.extend(["--issuer-name", oci_params["issuer_name"]])
        if "jwks_uri_protected" in oci_params:
            cmd.extend(["--jwks-uri-protected", str(oci_params["jwks_uri_protected"]).lower()])
        if "oci_issuer" in oci_params:
            cmd.extend(["--oci-issuer", oci_params["oci_issuer"]])
            
    elif base_action == "create":
        cmd.append("create")
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "oci_issuer_create_jsonfile" in oci_params:
            cmd.extend(["--oci-issuer-create-jsonfile", oci_params["oci_issuer_create_jsonfile"]])
        else:
            # Required parameters
            cmd.extend(["--issuer-name", oci_params["issuer_name"]])
            cmd.extend(["--issuer-type", oci_params["issuer_type"]])
            
            # Optional parameters
            if "issuer_config" in oci_params:
                cmd.extend(["--issuer-config", str(oci_params["issuer_config"])])
            if "description" in oci_params:
                cmd.extend(["--description", oci_params["description"]])
            if "metadata" in oci_params:
                cmd.extend(["--metadata", str(oci_params["metadata"])])
            
    elif base_action == "update":
        cmd.extend(["update", "--id", oci_params["id"]])
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "oci_issuer_update_jsonfile" in oci_params:
            cmd.extend(["--oci-issuer-update-jsonfile", oci_params["oci_issuer_update_jsonfile"]])
        else:
            # Optional parameters
            if "issuer_name" in oci_params:
                cmd.extend(["--issuer-name", oci_params["issuer_name"]])
            if "issuer_type" in oci_params:
                cmd.extend(["--issuer-type", oci_params["issuer_type"]])
            if "issuer_config" in oci_params:
                cmd.extend(["--issuer-config", str(oci_params["issuer_config"])])
            if "description" in oci_params:
                cmd.extend(["--description", oci_params["description"]])
            if "metadata" in oci_params:
                cmd.extend(["--metadata", str(oci_params["metadata"])])
        
    else:
        raise ValueError(f"Unsupported OCI issuers action: {action}")
    
    return cmd 