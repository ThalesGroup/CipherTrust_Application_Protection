"""OCI Tenancy operations for CCKM."""

from typing import Any, Dict


def get_tenancy_operations() -> Dict[str, Any]:
    """Return schema and action requirements for OCI tenancy operations."""
    return {
        "schema_properties": {
            "oci_tenancy_params": {
                "type": "object",
                "properties": {
                    # Basic tenancy parameters
                    "id": {
                        "type": "string", 
                        "description": "OCI tenancy ID, OCID, or tenancy name. Smart resolution automatically handles tenancy name to OCID conversion. CRITICAL FOR AI ASSISTANTS: Always use this 'id' parameter for tenancy identification operations, even when users specify tenancy names - never use 'name' or 'tenancy_name' parameters."
                    },
                    "oci_tenancy": {
                        "type": "string", 
                        "description": "Name of the tenancy. For add-tenancy: Use ONLY when NOT providing connection_identifier (mutually exclusive). For list: filter by tenancy name."
                    },
                    "tenancy_ocid": {
                        "type": "string", 
                        "description": "Tenancy OCID. For add-tenancy: Use ONLY when NOT providing connection_identifier (mutually exclusive). For list: filter by tenancy OCID."
                    },
                    "connection_identifier": {
                        "type": "string", 
                        "description": "Name or ID of the connection which has been created earlier. For add-tenancy: Use ONLY when NOT providing oci_tenancy and tenancy_ocid (mutually exclusive)."
                    },
                    
                    # Common parameters
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort the resources on the basis of the provided parameter"}
                }
            }
        },
        "action_requirements": {
            "tenancy_list": {"required": [], "optional": ["limit", "skip", "sort", "oci_tenancy", "tenancy_ocid"]},
            "tenancy_get": {"required": ["id"], "optional": []},
            "tenancy_add": {
                "required": [], 
                "optional": ["connection_identifier", "oci_tenancy", "tenancy_ocid"],
                "note": "MUTUALLY EXCLUSIVE PARAMETERS: For tenancy_add, you must provide EITHER: 1) connection_identifier (to use existing connection), OR 2) both oci_tenancy and tenancy_ocid (to add without connection). DO NOT provide both connection_identifier AND oci_tenancy/tenancy_ocid together."
            },
            "tenancy_delete": {"required": ["id"], "optional": []},
        }
    }


def build_tenancy_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI tenancy operation."""
    cmd = ["cckm", "oci", "tenancy"]
    
    # Extract the base operation name (remove 'tenancy_' prefix)
    base_action = action.replace("tenancy_", "")
    
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
        if "oci_tenancy" in oci_params:
            cmd.extend(["--oci-tenancy", oci_params["oci_tenancy"]])
        if "tenancy_ocid" in oci_params:
            cmd.extend(["--tenancy-ocid", oci_params["tenancy_ocid"]])
            
    elif base_action == "add":
        cmd.append("add-tenancy")
        
        # Check which method is being used - these are mutually exclusive
        if "connection_identifier" in oci_params:
            # Method 1: Using existing connection ONLY
            cmd.extend(["--connection-identifier", oci_params["connection_identifier"]])
            # DO NOT include oci_tenancy or tenancy_ocid when using connection_identifier
                
        elif "oci_tenancy" in oci_params and "tenancy_ocid" in oci_params:
            # Method 2: Without connection (requires both oci_tenancy and tenancy_ocid)
            cmd.extend(["--oci-tenancy", oci_params["oci_tenancy"]])
            cmd.extend(["--tenancy-ocid", oci_params["tenancy_ocid"]])
            
        else:
            raise ValueError("For tenancy_add, you must provide either: 1) connection_identifier, OR 2) both oci_tenancy and tenancy_ocid")
        
    else:
        raise ValueError(f"Unsupported OCI tenancy action: {action}")
    
    return cmd 