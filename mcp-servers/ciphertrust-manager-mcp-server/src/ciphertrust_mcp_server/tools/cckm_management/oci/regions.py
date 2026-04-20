"""OCI Region operations for CCKM."""

from typing import Any, Dict


def get_region_operations() -> Dict[str, Any]:
    """Return schema and action requirements for OCI region operations."""
    return {
        "schema_properties": {
            "oci_regions_params": {
                "type": "object",
                "properties": {
                    "connection_identifier": {"type": "string", "description": "Name or ID of the connection which has been created earlier"},
                    # Common parameters
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort field and order"},
                    
                    # Filter parameters
                    "region_name": {"type": "string", "description": "Filter by region name"},
                    "region_key": {"type": "string", "description": "Filter by region key"},
                    "status": {"type": "string", "description": "Filter by region status"},
                    "is_home_region": {"type": "boolean", "description": "Filter by home region status"}
                }
            }
        },
        "action_requirements": {
            "regions_get_subscribed": {"required": ["connection_identifier"], "optional": ["limit", "skip", "sort", "region_name", "region_key", "status", "is_home_region"]},
        }
    }


def build_region_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI region operation."""
    cmd = ["cckm", "oci", "regions"]
    
    # Extract the base operation name (remove 'regions_' prefix)
    base_action = action.replace("regions_", "")
    
    if base_action == "get_subscribed":
        cmd.extend(["get-subscribed-regions", "--connection-identifier", oci_params["connection_identifier"]])
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "region_name" in oci_params:
            cmd.extend(["--region-name", oci_params["region_name"]])
        if "region_key" in oci_params:
            cmd.extend(["--region-key", oci_params["region_key"]])
        if "status" in oci_params:
            cmd.extend(["--status", oci_params["status"]])
        if "is_home_region" in oci_params:
            cmd.extend(["--is-home-region", str(oci_params["is_home_region"]).lower()])
    else:
        raise ValueError(f"Unsupported OCI regions action: {action}")
    
    return cmd 