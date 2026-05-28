"""OCI Compartments operations for CCKM."""

from typing import Any, Dict


def get_compartment_operations() -> Dict[str, Any]:
    """Return schema and action requirements for OCI compartment operations."""
    return {
        "schema_properties": {
            "oci_compartments_params": {
                "type": "object",
                "properties": {
                    # Basic compartment parameters
                    "id": {"type": "string", "description": "Compartment ID"},
                    "connection_identifier": {"type": "string", "description": "Connection identifier"},
                    "oci_compartment_id": {"type": "string", "description": "OCI compartment ID (comma-separated for multiple)"},
                    "oci_compartment_name": {"type": "string", "description": "OCI compartment name for filtering"},
                    "oci_tenancy": {"type": "string", "description": "OCI tenancy name for filtering"},
                    
                    # List parameters
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort field and order"}
                }
            }
        },
        "action_requirements": {
            "compartments_list": {"required": [], "optional": ["limit", "skip", "sort", "oci_compartment_id", "oci_compartment_name", "oci_tenancy"]},
            "compartments_get": {"required": ["id"], "optional": []},
            "compartments_delete": {"required": ["id"], "optional": []},
            "compartments_get_compartments": {"required": ["connection_identifier"], "optional": []},
            "compartments_add_compartments": {"required": ["connection_identifier", "oci_compartment_id"], "optional": []},
        }
    }


def validate_compartment_filtering(oci_params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and correct compartment filtering parameters.
    
    This function validates the filtering parameters for compartment operations,
    similar to vault filtering validation. It provides warnings and recommendations
    for proper filtering practices.
    
    Args:
        oci_params: OCI parameters for the operation
        
    Returns:
        A dictionary with warnings, recommendations, and corrected parameters
    """
    validation_result = {
        "warnings": [],
        "recommendations": [],
        "corrected_params": oci_params.copy()
    }
    
    # Check if limit is set when filtering by name
    if "oci_compartment_name" in oci_params and "limit" not in oci_params:
        validation_result["warnings"].append(
            "MISSING: No limit parameter provided when filtering by compartment name. "
            "Always set limit to control result size and improve performance."
        )
        validation_result["recommendations"].append("Add limit parameter (e.g., limit: 10)")
        validation_result["corrected_params"]["limit"] = 10
    
    # Check if no filtering is provided for what might be a specific compartment operation
    if "oci_compartment_name" not in oci_params and not any(param in oci_params for param in ["oci_tenancy"]):
        validation_result["warnings"].append(
            "NO FILTERING: No filtering parameters provided. "
            "For specific compartment operations, use oci_compartment_name for exact name matching. "
            "For discovery operations, consider using oci_tenancy or other filters."
        )
    
    return validation_result


def build_compartment_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI compartment operation."""
    cmd = ["cckm", "oci", "compartments"]
    base_action = action.replace("compartments_", "")

    if base_action == "list":
        cmd.append("list")
        
        # Validate filtering parameters and provide guidance
        validation = validate_compartment_filtering(oci_params)
        
        # Add validation warnings and recommendations as comments
        if validation["warnings"]:
            cmd.append("# VALIDATION WARNINGS:")
            for warning in validation["warnings"]:
                cmd.append(f"# {warning}")
        
        if validation["recommendations"]:
            cmd.append("# RECOMMENDATIONS:")
            for recommendation in validation["recommendations"]:
                cmd.append(f"# {recommendation}")
        
        # Use corrected parameters if validation provided them
        if validation["corrected_params"] != oci_params:
            oci_params = validation["corrected_params"]
        
        # Check for filtering parameters
        filtering_params = ["oci_compartment_name", "oci_tenancy"]
        has_filters = any(param in oci_params for param in filtering_params)
        
        # Add note if no filters provided (but allow discovery operations)
        if not has_filters:
            cmd.append("# NOTE: No filtering parameters provided.")
            cmd.append("# This is acceptable for discovery operations.")
            cmd.append("# For specific compartment operations, consider using:")
            cmd.append("# --oci-compartment-name for exact name matching")
            cmd.append("# --oci-tenancy for tenancy filtering")
            cmd.append("# --limit to control result size")
        
        # Build command with parameters
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "oci_compartment_id" in oci_params:
            cmd.extend(["--oci-compartment-id", oci_params["oci_compartment_id"]])
        if "oci_compartment_name" in oci_params:
            cmd.extend(["--oci-compartment-name", oci_params["oci_compartment_name"]])
        if "oci_tenancy" in oci_params:
            cmd.extend(["--oci-tenancy", oci_params["oci_tenancy"]])

    elif base_action == "get":
        cmd.extend(["get", "--id", oci_params["id"]])

    elif base_action == "delete":
        cmd.extend(["delete", "--id", oci_params["id"]])

    elif base_action == "get_compartments":
        cmd.extend(["get-compartments", "--connection-identifier", oci_params["connection_identifier"]])

    elif base_action == "add_compartments":
        cmd.extend(["add-compartments", "--connection-identifier", oci_params["connection_identifier"], "--oci-compartment-id", oci_params["oci_compartment_id"]])

    else:
        raise ValueError(f"Unsupported OCI compartments action: {action}")

    return cmd 