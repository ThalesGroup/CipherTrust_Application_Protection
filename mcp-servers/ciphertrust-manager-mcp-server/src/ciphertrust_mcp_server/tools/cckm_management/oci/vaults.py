"""OCI Vaults operations for CCKM."""

from typing import Any, Dict


def validate_vault_filtering(oci_params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and provide guidance for vault filtering parameters.
    
    This function ensures that AI assistants use the correct filtering parameters:
    - oci_vault_display_name for exact name matching (MANDATORY when user provides exact vault name)
    - No partial name matching - list all vaults without filtering for pattern searches
    
    Args:
        oci_params: The parameters provided by the AI assistant
        
    Returns:
        Dict with validation results and guidance
    """
    validation_result = {
        "is_valid": True,
        "warnings": [],
        "recommendations": [],
        "corrected_params": oci_params.copy()
    }
    
    # Check if oci_vault_name is used (should be removed)
    if "oci_vault_name" in oci_params:
        vault_name_value = oci_params["oci_vault_name"]
        validation_result["warnings"].append(
            f"INVALID PARAMETER: oci_vault_name='{vault_name_value}' is not supported. "
            "Use oci_vault_display_name for exact name matching, or list all vaults without filtering for pattern searches."
        )
        validation_result["recommendations"].append(
            f"Remove oci_vault_name parameter. For exact name '{vault_name_value}', use oci_vault_display_name instead."
        )
        # Remove the invalid parameter
        del validation_result["corrected_params"]["oci_vault_name"]
    
    # Check if limit is set when filtering by display_name
    if "oci_vault_display_name" in oci_params and "limit" not in oci_params:
        validation_result["warnings"].append(
            "MISSING: No limit parameter provided when filtering by vault name. "
            "Always set limit to control result size and improve performance."
        )
        validation_result["recommendations"].append("Add limit parameter (e.g., limit: 10)")
        validation_result["corrected_params"]["limit"] = 10
    
    # Check if no filtering is provided for what might be a specific vault operation
    if not "oci_vault_display_name" in oci_params and not any(param in oci_params for param in ["oci_region", "oci_tenancy", "oci_compartment_name"]):
        validation_result["warnings"].append(
            "NO FILTERING: No filtering parameters provided. "
            "For specific vault operations, use oci_vault_display_name for exact name matching. "
            "For discovery operations, consider using oci_region, oci_tenancy, or other filters."
        )
    
    return validation_result


def get_vault_operations() -> Dict[str, Any]:
    """Get OCI vault operations configuration.
    
    SMART ID RESOLUTION:
    The vaults_delete operation supports smart ID resolution, allowing users to specify
    vault names instead of UUIDs. The system will automatically:
    1. Check if the provided identifier is already a UUID or OCID
    2. If it's a vault name, search for vaults with matching display_name
    3. Resolve the name to the corresponding CCKM vault UUID
    4. Execute the delete operation with the resolved UUID
    
    EXAMPLES:
    - Delete by UUID: {"id": "56a9044e-2e9d-4089-8d19-028a135decd1"}
    - Delete by name: {"vault_name": "oci-vault-us-west"}
    - Delete by OCID: {"id": "ocid1.vault.oc1.us-sanjose-1..."}
    
    ERROR HANDLING:
    - If no vault is found with the given name, a clear error message is provided
    - If multiple vaults match the name, an error suggests using a more specific name or UUID
    - The operation requires either 'id' or 'vault_name' parameter
    
    FILTERING BEST PRACTICES:
    - MANDATORY: Use filtering when user supplies a vault name (oci_vault_display_name, oci_vault_name)
    - RECOMMENDED: Use filtering for discovery operations (oci_region, oci_tenancy)
    - ALWAYS: Set limit parameter to control result size
    - NEVER: Use unfiltered lists to find specific vaults when user provides a name
    
    EXAMPLES OF PROPER FILTERING:
    - User provides vault name: {"oci_vault_display_name": "my-vault-01"} (MANDATORY)
    - Discovery by region: {"oci_region": "us-ashburn-1"} (RECOMMENDED)
    - Discovery by tenancy: {"oci_tenancy": "my-tenancy"} (RECOMMENDED)
    - Combined filtering: {"oci_vault_display_name": "prod-vault", "oci_region": "us-west-1"}
    """
    return {
        "schema_properties": {
            "oci_vaults_params": {
                "type": "object",
                "properties": {
                    # Basic vault parameters
                    "oci_compartment_id": {"type": "string", "description": "OCI compartment ID"},
                    "connection_identifier": {"type": "string", "description": "Connection identifier"},
                    "id": {"type": "string", "description": "Vault ID"},
                    "vault_name": {"type": "string", "description": "Vault name for filtering"},
                    "oci_region": {"type": "string", "description": "OCI region"},
                    "oci_vaults": {"type": "string", "description": "List of OCI vaults"},
                    "oci_bucket_name": {"type": "string", "description": "OCI bucket name"},
                    "oci_bucket_namespace": {"type": "string", "description": "OCI bucket namespace"},

                    # List parameters
                    "limit": {"type": "integer", "description": "Maximum number of results (ALWAYS set this to control result size)"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort field and order"},
                    "cloud_name": {"type": "string", "description": "Filter by cloud name"},
                    "oci_compartment_name": {"type": "string", "description": "Filter by compartment name"},
                    "oci_external_vault_type": {"type": "string", "description": "Filter by external vault type"},
                    "oci_issuer_id": {"type": "string", "description": "Filter by issuer ID"},
                    "oci_lifecyclestate": {"type": "string", "description": "Filter by lifecycle state"},
                    "oci_linked_state": {"type": "string", "description": "Filter by linked state"},
                    "oci_tenancy": {"type": "string", "description": "Filter by tenancy name (RECOMMENDED: Use this to narrow results)"},
                    "oci_vault_display_name": {"type": "string", "description": "Filter by vault display name (MANDATORY: Use this when user provides exact vault name)"},
                    "oci_vault_id": {"type": "string", "description": "Filter by vault ID"},
                    "oci_vault_type": {"type": "string", "description": "Filter by vault type"},
                    "state": {"type": "string", "description": "Filter by state"},

                    # Get vaults parameters
                    "ociNextToken": {"type": "string", "description": "Token for the next set of items to return"},
                    "oci_vaults_get_jsonfile": {"type": "string", "description": "Get vaults parameters in JSON format from a file"},
                    "oci_vaults_add_jsonfile": {"type": "string", "description": "Add vaults parameters in JSON format from a file"},
                }
            }
        },
        "action_requirements": {
            "vaults_list": {
                "required": [], 
                "optional": ["limit", "skip", "sort", "vault_name", "cloud_name", "oci_compartment_name", "oci_external_vault_type", "oci_issuer_id", "oci_lifecyclestate", "oci_linked_state", "oci_tenancy", "oci_vault_display_name", "oci_vault_id", "oci_vault_type", "state"],
                "mandatory_when_user_provides_name": ["oci_vault_display_name", "limit"],
                "recommended": ["oci_region", "oci_tenancy"],
                "description": "List OCI vaults. MANDATORY: Use oci_vault_display_name when user provides exact vault name. For pattern searches, list all vaults without filtering."
            },
            "vaults_get": {"required": ["id"], "optional": []},
            "vaults_delete": {"required": [], "optional": ["id", "vault_name"]},
            "vaults_get_vaults": {"required": ["connection_identifier", "oci_compartment_id", "oci_region"], "optional": ["limit", "ociNextToken", "oci_vaults_get_jsonfile"]},
            "vaults_add_vaults": {"required": ["connection_identifier", "oci_region", "oci_vaults"], "optional": ["oci_bucket_name", "oci_bucket_namespace", "oci_vaults_add_jsonfile"]},
        }
    }


def build_vault_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI vault operation.
    
    FILTERING ENFORCEMENT:
    For vaults_list operations, this function will:
    1. Validate filtering parameters and provide guidance
    2. Check if any filtering parameters are provided
    3. If no filters are provided, add a warning comment in the command
    4. Recommend specific filtering parameters based on common use cases
    """
    cmd = ["cckm", "oci", "vaults"]
    base_action = action.replace("vaults_", "")
    
    if base_action == "list":
        cmd.append("list")
        
        # Validate filtering parameters and provide guidance
        validation = validate_vault_filtering(oci_params)
        
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
        filtering_params = [
            "oci_vault_display_name", "oci_region", "oci_tenancy",
            "oci_compartment_name", "cloud_name", "state", "oci_vault_type"
        ]
        has_filters = any(param in oci_params for param in filtering_params)
        
        # Add note if no filters provided (but allow discovery operations)
        if not has_filters:
            cmd.append("# NOTE: No filtering parameters provided.")
            cmd.append("# This is acceptable for discovery operations.")
            cmd.append("# For specific vault operations, consider using:")
            cmd.append("# --oci-vault-display-name for exact name matching")
            cmd.append("# --oci-region for region filtering")
            cmd.append("# --oci-tenancy for tenancy filtering")
            cmd.append("# --limit to control result size")
        
        # Build command with parameters
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "vault_name" in oci_params:
            cmd.extend(["--oci-vault-name", oci_params["vault_name"]])
        if "cloud_name" in oci_params:
            cmd.extend(["--cloud-name", oci_params["cloud_name"]])
        if "oci_compartment_name" in oci_params:
            cmd.extend(["--oci-compartment-name", oci_params["oci_compartment_name"]])
        if "oci_external_vault_type" in oci_params:
            cmd.extend(["--oci-external-vault-type", oci_params["oci_external_vault_type"]])
        if "oci_issuer_id" in oci_params:
            cmd.extend(["--oci-issuer-id", oci_params["oci_issuer_id"]])
        if "oci_lifecyclestate" in oci_params:
            cmd.extend(["--oci-lifecyclestate", oci_params["oci_lifecyclestate"]])
        if "oci_linked_state" in oci_params:
            cmd.extend(["--oci-linked-state", oci_params["oci_linked_state"]])
        if "oci_tenancy" in oci_params:
            cmd.extend(["--oci-tenancy", oci_params["oci_tenancy"]])
        if "oci_vault_display_name" in oci_params:
            cmd.extend(["--oci-vault-display-name", oci_params["oci_vault_display_name"]])
        if "oci_vault_id" in oci_params:
            cmd.extend(["--oci-vault-id", oci_params["oci_vault_id"]])
        if "oci_vault_type" in oci_params:
            cmd.extend(["--oci-vault-type", oci_params["oci_vault_type"]])
        if "state" in oci_params:
            cmd.extend(["--state", oci_params["state"]])
        
    elif base_action == "get":
        cmd.extend(["get", "--id", oci_params["id"]])
        
    elif base_action == "delete":
        cmd.extend(["delete", "--id", oci_params["id"]])
        # Note: Smart ID resolution will handle converting vault names to IDs automatically

    elif base_action == "get_vaults":
        cmd.append("get-vaults")
        if "oci_vaults_get_jsonfile" in oci_params:
            cmd.extend(["--oci-vaults-get-jsonfile", oci_params["oci_vaults_get_jsonfile"]])
        else:
            cmd.extend(["--connection-identifier", oci_params["connection_identifier"]])
            cmd.extend(["--oci-compartment-id", oci_params["oci_compartment_id"]])
            cmd.extend(["--oci-region", oci_params["oci_region"]])
            if "limit" in oci_params:
                cmd.extend(["--limit", str(oci_params["limit"])])
            if "ociNextToken" in oci_params:
                cmd.extend(["--ociNextToken", oci_params["ociNextToken"]])

    elif base_action == "add_vaults":
        cmd.append("add-vaults")
        if "oci_vaults_add_jsonfile" in oci_params:
            cmd.extend(["--oci-vaults-add-jsonfile", oci_params["oci_vaults_add_jsonfile"]])
        else:
            cmd.extend(["--connection-identifier", oci_params["connection_identifier"]])
            cmd.extend(["--oci-region", oci_params["oci_region"]])
            cmd.extend(["--oci-vaults", oci_params["oci_vaults"]])
            if "oci_bucket_name" in oci_params:
                cmd.extend(["--oci-bucket-name", oci_params["oci_bucket_name"]])
            if "oci_bucket_namespace" in oci_params:
                cmd.extend(["--oci-bucket-namespace", oci_params["oci_bucket_namespace"]])
    else:
        raise ValueError(f"Unsupported OCI vaults action: {action}")
    
    return cmd 