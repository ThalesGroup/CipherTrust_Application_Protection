"""OCI Keys operations for CCKM."""

from typing import Any, Dict


def get_key_operations() -> Dict[str, Any]:
    """Return schema and action requirements for OCI key operations."""
    return {
        "schema_properties": {
            "oci_keys_params": {
                "type": "object",
                "properties": {
                    # Basic key parameters
                    "key_name": {"type": "string", "description": "Name for the key"},
                    "oci_vault": {
                        "type": "string", 
                        "description": "Vault ID, OCID, or display name. Smart resolver automatically converts vault display names to OCIDs. AI assistants can use vault names like 'my-vault' instead of OCIDs."
                    },
                    "oci_algorithm": {
                        "type": "string", 
                        "description": "Algorithm of the key. Supported: AES, RSA, ECDSA"
                    },
                    "length": {
                        "type": "integer", 
                        "description": "Key length. Smart resolver automatically converts bits to bytes for OCI. Supported sizes: AES (128, 192, 256 bits or 16, 24, 32 bytes), RSA (256, 384, 512 bits), ECDSA (256, 384, 521 bits or 32, 48, 66 bytes)"
                    },
                    "protection_mode": {"type": "string", "description": "Protection mode (SOFTWARE, HSM)"},
                    "oci_compartment_id": {"type": "string", "description": "Compartment ID where the key will belong"},
                    
                    # Key attributes
                    "description": {"type": "string", "description": "Key description"},
                    "oci_curve": {"type": "string", "description": "Elliptic curve (NIST_P256, NIST_P384, NIST_P521)"},
                    
                    # Common parameters
                    "id": {
                        "type": "string", 
                        "description": "OCI key ID, OCID, or key name. Smart resolution automatically handles key name to OCID conversion. CRITICAL FOR AI ASSISTANTS: Always use this 'id' parameter for key identification operations, even when users specify key names - never use 'name' or 'key_name' parameters."
                    },
                    "oci_version_id": {"type": "string", "description": "Version ID for version operations"},
                    
                    # List parameters
                    "limit": {"type": "integer", "description": "Maximum number of results"},
                    "skip": {"type": "integer", "description": "Number of results to skip"},
                    "sort": {"type": "string", "description": "Sort field and order"},
                    "oci_compartment_id": {"type": "string", "description": "Compartment ID for filtering"},
                    "key_name": {"type": "string", "description": "Key name for filtering"},
                    "oci_algorithm": {"type": "string", "description": "Algorithm for filtering"},
                    "length": {"type": "integer", "description": "Length for filtering"},
                    "protection_mode": {"type": "string", "description": "Protection mode for filtering"},
                    "oci_curve": {"type": "string", "description": "Curve for filtering"},
                    "oci_vault": {"type": "string", "description": "Vault for filtering"},
                    "job_config_id": {"type": "string", "description": "Job configuration ID"},
                    "key_material_origin": {"type": "string", "description": "Key material origin"},
                    "oci_compartment_name": {"type": "string", "description": "Compartment name for filtering"},
                    "oci_gone": {"type": "boolean", "description": "Gone status"},
                    "oci_key_display_name": {"type": "string", "description": "Key display name for filtering"},
                    "oci_key_id": {"type": "string", "description": "Key ID for filtering"},
                    "oci_lifecyclestate": {"type": "string", "description": "Lifecycle state for filtering"},
                    "oci_linked_state": {"type": "string", "description": "Linked state for filtering"},
                    "oci_local_hyok_key_id": {"type": "string", "description": "Local HYOK key ID"},
                    "oci_local_hyok_key_version_id": {"type": "string", "description": "Local HYOK key version ID"},
                    "oci_local_key_store_id": {"type": "string", "description": "Local key store ID"},
                    "oci_region": {"type": "string", "description": "Region for filtering"},
                    "oci_tenancy": {"type": "string", "description": "Tenancy for filtering"},
                    "oci_vault_display_name": {"type": "string", "description": "Vault display name for filtering"},
                    "oci_vault_name": {"type": "string", "description": "Vault name for filtering, preferred over oci_vault_display_name"},
                    "oci_vault_hyok": {"type": "string", "description": "Vault HYOK status"},
                    "state": {"type": "string", "description": "State for filtering"},
                    
                    # Deletion parameters
                    "days": {"type": "integer", "description": "Number of days for scheduled deletion (minimum 7 days)"},
                    
                    # Auto rotation
                    "time_of_rotation": {"type": "string", "description": "Time of rotation in ISO 8601 format"},
                    "rotation_interval_days": {"type": "integer", "description": "Rotation interval in days"},
                    
                    # Upload parameters
                    "oci_source_key_id": {"type": "string", "description": "The key ID which will be uploaded from the key source (local, dsm, hsm-luna, external-cm)"},
                    "source_key_tier": {"type": "string", "description": "Source key tier. Options: local, dsm, hsm-luna, external-cm"},
                    "oci_keyupload_jsonfile": {"type": "string", "description": "Path to JSON file containing OCI key upload parameters. Format: {\"key_name\": \"my-key\", \"oci_vault\": \"my-vault\", \"oci_algorithm\": \"AES\", \"length\": 256, \"protection_mode\": \"SOFTWARE\", \"oci_source_key_id\": \"local-key\", \"source_key_tier\": \"local\"}. Use absolute file paths for reliability. REQUIRES FILE INPUT."},
                    
                    # Add version parameters
                    "oci_is_native": {"type": "boolean", "description": "Determines whether the key version will be created natively (true) or uploaded from external source (false)"},
                    "oci_keyaddversion_jsonfile": {"type": "string", "description": "Path to JSON file containing OCI key version parameters in format: {\"is_native\": boolean, \"oci_source_key_id\": \"id\", \"source_key_tier\": \"local|dsm|hsm-luna|external-cm\"}. Use absolute file paths for reliability."},
                    
                    # Update parameters
                    "oci_updatekey_params_jsonfile": {"type": "string", "description": "Update key parameters passed in JSON format via a file"},
                    "oci_defined_tags_jsonfile": {"type": "string", "description": "To add the defined tags into a key. It consists of a namespace, a key, and a value"},
                    "oci_freeform_tags_jsonfile": {"type": "string", "description": "To add the freeform tags into a key. It consists of a key and a value"}
                }
            }
        },
        "action_requirements": {
            "keys_list": {"required": [], "optional": ["limit", "skip", "sort", "oci_compartment_id", "key_name", "oci_algorithm", "length", "protection_mode", "oci_curve", "oci_vault", "job_config_id", "key_material_origin", "oci_compartment_name", "oci_gone", "oci_key_display_name", "oci_key_id", "oci_lifecyclestate", "oci_linked_state", "oci_local_hyok_key_id", "oci_local_hyok_key_version_id", "oci_local_key_store_id", "oci_region", "oci_tenancy", "oci_vault_display_name", "oci_vault_name", "oci_vault_hyok", "state"]},
            "keys_get": {"required": ["id"], "optional": []},
            "keys_create": {
                "required": ["key_name", "oci_vault", "oci_algorithm", "length", "protection_mode", "oci_compartment_id"], 
                "optional": ["description", "oci_curve", "oci_keycreate_jsonfile", "oci_defined_tags_jsonfile", "oci_freeform_tags_jsonfile"],
                "notes": [
                    "Smart resolver automatically converts vault display names to OCIDs",
                    "Smart resolver automatically converts key sizes from bits to bytes for OCI",
                    "Supported key sizes: AES (128, 192, 256 bits), RSA (256, 384, 512 bits), ECDSA (256, 384, 521 bits)"
                ]
            },
            "keys_delete": {"required": ["id"], "optional": []},
            "keys_enable": {"required": ["id"], "optional": []},
            "keys_disable": {"required": ["id"], "optional": []},
            "keys_refresh": {"required": ["id"], "optional": []},
            "keys_restore": {"required": ["id"], "optional": []},
            "keys_schedule_deletion": {
                "required": ["id", "days"], 
                "optional": [],
                "notes": [
                    "Days parameter must be >= 7 for schedule deletion operations",
                    "Smart resolver automatically converts key names to OCIDs/UUIDs"
                ]
            },
            "keys_cancel_deletion": {"required": ["id"], "optional": []},
            "keys_change_compartment": {"required": ["id", "oci_compartment_id"], "optional": []},
            "keys_enable_auto_rotation": {"required": ["id"], "optional": ["time_of_rotation", "rotation_interval_days"]},
            "keys_disable_auto_rotation": {"required": ["id"], "optional": []},
            "keys_delete_backup": {"required": ["id"], "optional": []},
            "keys_download_metadata": {
                "required": [], 
                "optional": ["limit", "skip", "sort", "file", "oci_compartment_id", "oci_vault"],
                "notes": [
                    "Smart resolver automatically converts vault display names to OCIDs"
                ]
            },
            "keys_add_version": {
                "required": ["id"], 
                "optional": ["oci_keyaddversion_jsonfile", "oci_source_key_id", "source_key_tier", "oci_is_native"],
                "notes": [
                    "For uploading keys from external sources, oci_source_key_id and source_key_tier are required",
                    "oci_is_native flag determines if key version is created natively (true) or uploaded (false)"
                ]
            },
            "keys_get_version": {"required": ["id", "oci_version_id"], "optional": []},
            "keys_list_version": {"required": ["id"], "optional": ["limit", "skip"]},
            "keys_schedule_deletion_version": {
                "required": ["id", "oci_version_id", "days"], 
                "optional": [],
                "notes": [
                    "Days parameter must be >= 7 for schedule deletion operations",
                    "Smart resolver automatically converts key names to OCIDs/UUIDs"
                ]
            },
            "keys_cancel_schedule_deletion_version": {"required": ["id", "oci_version_id"], "optional": []},
            "keys_upload": {
                "required": [
                    "key_name",
                    "oci_vault",
                    "protection_mode",
                    "oci_source_key_id",
                    "source_key_tier"
                ], 
                "optional": [
                    "oci_compartment_id",
                    "oci_compartment_name",
                    "oci_keyupload_jsonfile"
                ],
                "notes": [
                    "Accepts compartment by name or ID. If only oci_compartment_name is provided, it will be resolved to oci_compartment_id automatically.",
                    "Smart resolver automatically converts vault display names to OCIDs",
                    "Required parameters: key_name, oci_vault, protection_mode, (oci_compartment_id or oci_compartment_name), oci_source_key_id, source_key_tier"
                ]
            },
            # Key synchronization/refresh operations (synchronize)
            "keys_sync_jobs_start": {
                "required": [], 
                "optional": ["oci_vault", "synchronize_all"],
                "notes": [
                    "Smart resolver automatically converts vault display names to OCIDs"
                ]
            },
            "keys_sync_jobs_get": {"required": ["job_id"], "optional": []},
            "keys_sync_jobs_status": {"required": [], "optional": ["limit", "skip", "sort"]},
            "keys_sync_jobs_cancel": {"required": ["job_id"], "optional": []},
            "keys_update": {"required": ["id"], "optional": ["oci_key_display_name", "oci_updatekey_params_jsonfile", "oci_defined_tags_jsonfile", "oci_freeform_tags_jsonfile"]},
        }
    }


def validate_key_filtering(oci_params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and correct key filtering parameters.
    
    This function validates the filtering parameters for key operations,
    providing warnings and recommendations for proper filtering practices.
    
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
    
    # Check filtering parameters
    filtering_params = [
        "key_name", "oci_vault_name", "oci_region", "oci_tenancy", 
        "oci_compartment_name", "oci_vault_display_name"
    ]
    has_filters = any(param in oci_params for param in filtering_params)
    
    # Check if limit is set when filtering by name
    if has_filters and "limit" not in oci_params:
        validation_result["warnings"].append(
            "MISSING: No limit parameter provided when filtering keys. "
            "Always set limit to control result size and improve performance."
        )
        validation_result["recommendations"].append("Add limit parameter (e.g., limit: 10)")
        validation_result["corrected_params"]["limit"] = 10
    
    # If both oci_vault_name and oci_vault_display_name are provided, warn
    if "oci_vault_name" in oci_params and "oci_vault_display_name" in oci_params:
        validation_result["warnings"].append(
            "DUPLICATE FILTERING: Both oci_vault_name and oci_vault_display_name are provided. "
            "Use oci_vault_name for consistency with the CLI command parameter."
        )
        validation_result["recommendations"].append(
            f"Remove oci_vault_display_name and keep oci_vault_name"
        )
    
    # If no filtering provided
    if not has_filters:
        validation_result["warnings"].append(
            "NO FILTERING: No filtering parameters provided. "
            "For specific key operations, consider using filtering parameters."
        )
        validation_result["recommendations"].append(
            "Consider adding filtering parameters like key_name, oci_vault_name, oci_tenancy, or oci_region"
        )
    
    return validation_result


def validate_schedule_deletion_params(oci_params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate schedule deletion parameters.
    
    This function validates the parameters for schedule deletion operations,
    ensuring the days parameter meets the minimum requirement.
    
    Args:
        oci_params: OCI parameters for the operation
        
    Returns:
        A dictionary with validation results and any corrections
    """
    validation_result = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "corrected_params": oci_params.copy()
    }
    
    # Validate days parameter for schedule deletion operations
    if "days" in oci_params:
        days = oci_params["days"]
        try:
            days_int = int(days)
            if days_int < 7:
                validation_result["is_valid"] = False
                validation_result["errors"].append(
                    f"Invalid days value: {days}. Days must be >= 7 for schedule deletion operations."
                )
        except (ValueError, TypeError):
            validation_result["is_valid"] = False
            validation_result["errors"].append(
                f"Invalid days value: {days}. Days must be a valid integer >= 7."
            )
    
    return validation_result


def build_key_command(action: str, oci_params: Dict[str, Any]) -> list:
    """Build the ksctl command for a given OCI key operation."""
    cmd = ["cckm", "oci", "keys"]
    
    # Extract the base operation name (remove 'keys_' prefix)
    base_action = action.replace("keys_", "")
    
    # Simple actions that only need --id parameter
    simple_actions = ["get", "delete", "enable", "disable", "refresh", "restore", "cancel_deletion", "disable_auto_rotation", "delete_backup"]
    
    if base_action in simple_actions:
        cmd.extend([base_action.replace("_", "-"), "--id", oci_params["id"]])
        return cmd
    
    if base_action == "list":
        cmd.append("list")
        
        # Validate filtering parameters and provide guidance
        validation = validate_key_filtering(oci_params)
        
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
        
        # Basic parameters
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "oci_compartment_id" in oci_params:
            cmd.extend(["--oci-compartment-id", oci_params["oci_compartment_id"]])
            
        # Key-specific filtering parameters
        if "key_name" in oci_params:
            cmd.extend(["--key-name", oci_params["key_name"]])
            
        # Vault filtering - support both oci_vault_name (preferred) and oci_vault_display_name
        if "oci_vault_name" in oci_params:
            cmd.extend(["--oci-vault-name", oci_params["oci_vault_name"]])
        elif "oci_vault_display_name" in oci_params:
            cmd.extend(["--oci-vault-display-name", oci_params["oci_vault_display_name"]])
            
        # Region and tenancy filtering
        if "oci_region" in oci_params:
            cmd.extend(["--oci-region", oci_params["oci_region"]])
        if "oci_tenancy" in oci_params:
            cmd.extend(["--oci-tenancy", oci_params["oci_tenancy"]])
            
        # Additional filtering parameters
        if "oci_algorithm" in oci_params:
            cmd.extend(["--oci-algorithm", oci_params["oci_algorithm"]])
        if "length" in oci_params:
            cmd.extend(["--length", str(oci_params["length"])])
        if "protection_mode" in oci_params:
            cmd.extend(["--protection-mode", oci_params["protection_mode"]])
        if "oci_curve" in oci_params:
            cmd.extend(["--oci-curve", oci_params["oci_curve"]])
        if "oci_vault" in oci_params:
            cmd.extend(["--oci-vault", oci_params["oci_vault"]])
        if "job_config_id" in oci_params:
            cmd.extend(["--job-config-id", oci_params["job_config_id"]])
        if "key_material_origin" in oci_params:
            cmd.extend(["--key-material-origin", oci_params["key_material_origin"]])
        if "oci_compartment_name" in oci_params:
            cmd.extend(["--oci-compartment-name", oci_params["oci_compartment_name"]])
        if "oci_gone" in oci_params:
            cmd.extend(["--oci-gone", str(oci_params["oci_gone"]).lower()])
        if "oci_key_display_name" in oci_params:
            cmd.extend(["--oci-key-display-name", oci_params["oci_key_display_name"]])
        if "oci_key_id" in oci_params:
            cmd.extend(["--oci-key-id", oci_params["oci_key_id"]])
        if "oci_lifecyclestate" in oci_params:
            cmd.extend(["--oci-lifecyclestate", oci_params["oci_lifecyclestate"]])
        if "oci_linked_state" in oci_params:
            cmd.extend(["--oci-linked-state", oci_params["oci_linked_state"]])
        if "oci_local_hyok_key_id" in oci_params:
            cmd.extend(["--oci-local-hyok-key-id", oci_params["oci_local_hyok_key_id"]])
        if "oci_local_hyok_key_version_id" in oci_params:
            cmd.extend(["--oci-local-hyok-key-version-id", oci_params["oci_local_hyok_key_version_id"]])
        if "oci_local_key_store_id" in oci_params:
            cmd.extend(["--oci-local-key-store-id", oci_params["oci_local_key_store_id"]])
        if "oci_vault_hyok" in oci_params:
            cmd.extend(["--oci-vault-hyok", oci_params["oci_vault_hyok"]])
        if "state" in oci_params:
            cmd.extend(["--state", oci_params["state"]])
            
    elif base_action == "create":
        cmd.append("create")
        # Required parameters
        cmd.extend(["--key-name", oci_params["key_name"]])
        cmd.extend(["--oci-vault", oci_params["oci_vault"]])
        cmd.extend(["--oci-algorithm", oci_params["oci_algorithm"]])
        cmd.extend(["--length", str(oci_params["length"])])
        cmd.extend(["--protection-mode", oci_params["protection_mode"]])
        cmd.extend(["--oci-compartment-id", oci_params["oci_compartment_id"]])
        
        # Optional parameters
        if "description" in oci_params:
            cmd.extend(["--description", oci_params["description"]])
        if "oci_curve" in oci_params:
            cmd.extend(["--oci-curve", oci_params["oci_curve"]])
        if "oci_keycreate_jsonfile" in oci_params:
            cmd.extend(["--oci-keycreate-jsonfile", oci_params["oci_keycreate_jsonfile"]])
        if "oci_defined_tags_jsonfile" in oci_params:
            cmd.extend(["--oci-defined-tags-jsonfile", oci_params["oci_defined_tags_jsonfile"]])
        if "oci_freeform_tags_jsonfile" in oci_params:
            cmd.extend(["--oci-freeform-tags-jsonfile", oci_params["oci_freeform_tags_jsonfile"]])
            
    elif base_action == "schedule_deletion":
        # Validate schedule deletion parameters
        validation = validate_schedule_deletion_params(oci_params)
        if not validation["is_valid"]:
            raise ValueError(f"Schedule deletion validation failed: {'; '.join(validation['errors'])}")
        
        cmd.extend(["schedule-deletion", "--id", oci_params["id"], "--days", str(oci_params["days"])])
        
    elif base_action == "change_compartment":
        cmd.extend(["change-compartment", "--id", oci_params["id"], "--oci-compartment-id", oci_params["oci_compartment_id"]])
        
    elif base_action == "enable_auto_rotation":
        cmd.extend(["enable-auto-rotation", "--id", oci_params["id"]])
        if "time_of_rotation" in oci_params:
            cmd.extend(["--time-of-rotation", oci_params["time_of_rotation"]])
        if "rotation_interval_days" in oci_params:
            cmd.extend(["--rotation-interval-days", str(oci_params["rotation_interval_days"])])
            
    elif base_action == "download_metadata":
        cmd.extend(["download-metadata"])
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
        if "file" in oci_params:
            cmd.extend(["--file", oci_params["file"]])
        if "oci_compartment_id" in oci_params:
            cmd.extend(["--oci-compartment-id", oci_params["oci_compartment_id"]])
        if "oci_vault" in oci_params:
            cmd.extend(["--oci-vault", oci_params["oci_vault"]])
            
    elif base_action == "add_version":
        cmd.extend(["add-version", "--id", oci_params["id"]])
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "oci_keyaddversion_jsonfile" in oci_params:
            cmd.extend(["--oci-keyaddversion-jsonfile", oci_params["oci_keyaddversion_jsonfile"]])
        else:
            # Individual parameters
            if "oci_is_native" in oci_params:
                cmd.extend(["--oci-is-native", str(oci_params["oci_is_native"]).lower()])
            if "oci_source_key_id" in oci_params:
                cmd.extend(["--oci-source-key-id", oci_params["oci_source_key_id"]])
            if "source_key_tier" in oci_params:
                cmd.extend(["--source-key-tier", oci_params["source_key_tier"]])
            
    elif base_action == "get_version":
        cmd.extend(["get-version", "--id", oci_params["id"], "--oci-version-id", oci_params["oci_version_id"]])
        
    elif base_action == "list_version":
        cmd.extend(["list-version", "--id", oci_params["id"]])
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
            
    elif base_action == "schedule_deletion_version":
        # Validate schedule deletion parameters
        validation = validate_schedule_deletion_params(oci_params)
        if not validation["is_valid"]:
            raise ValueError(f"Schedule deletion validation failed: {'; '.join(validation['errors'])}")
        
        cmd.extend(["schedule-deletion-version", "--id", oci_params["id"], "--oci-version-id", oci_params["oci_version_id"], "--days", str(oci_params["days"])])
        
    elif base_action == "cancel_schedule_deletion_version":
        cmd.extend(["cancel-schedule-deletion-version", "--id", oci_params["id"], "--oci-version-id", oci_params["oci_version_id"]])
        
    elif base_action == "upload":
        cmd.append("upload-key")
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "oci_keyupload_jsonfile" in oci_params:
            cmd.extend(["--oci-keyupload-jsonfile", oci_params["oci_keyupload_jsonfile"]])
        else:
            # Individual parameters
            if "key_name" in oci_params:
                cmd.extend(["--key-name", oci_params["key_name"]])
            if "oci_vault" in oci_params:
                cmd.extend(["--oci-vault", oci_params["oci_vault"]])
            if "protection_mode" in oci_params:
                # Convert protection_mode to uppercase
                protection_mode = oci_params["protection_mode"].upper()
                cmd.extend(["--protection-mode", protection_mode])
            if "oci_compartment_id" in oci_params:
                cmd.extend(["--oci-compartment-id", oci_params["oci_compartment_id"]])
            if "oci_source_key_id" in oci_params:
                cmd.extend(["--oci-source-key-id", oci_params["oci_source_key_id"]])
            if "source_key_tier" in oci_params:
                cmd.extend(["--source-key-tier", oci_params["source_key_tier"]])
        
    # Key synchronization/refresh operations (synchronize and refresh are equivalent terms)
    elif base_action == "sync_jobs_start":
        cmd.extend(["synchronization-jobs", "start"])
        if "oci_vault" in oci_params:
            cmd.extend(["--oci-vault", oci_params["oci_vault"]])
        if "synchronize_all" in oci_params and oci_params["synchronize_all"]:
            cmd.append("--synchronize-all")
            
    elif base_action == "sync_jobs_get":
        cmd.extend(["synchronization-jobs", "get", "--id", oci_params["job_id"]])
        
    elif base_action == "sync_jobs_status":
        cmd.extend(["synchronization-jobs", "status"])
        if "limit" in oci_params:
            cmd.extend(["--limit", str(oci_params["limit"])])
        if "skip" in oci_params:
            cmd.extend(["--skip", str(oci_params["skip"])])
        if "sort" in oci_params:
            cmd.extend(["--sort", oci_params["sort"]])
            
    elif base_action == "sync_jobs_cancel":
        cmd.extend(["synchronization-jobs", "cancel", "--id", oci_params["job_id"]])
        
    elif base_action == "update":
        cmd.extend(["update", "--id", oci_params["id"]])
        
        # Handle JSON file parameter first (overrides individual parameters)
        if "oci_updatekey_params_jsonfile" in oci_params:
            cmd.extend(["--oci-updatekey-params-jsonfile", oci_params["oci_updatekey_params_jsonfile"]])
        else:
            # Individual parameters
            if "oci_key_display_name" in oci_params:
                cmd.extend(["--oci-key-display-name", oci_params["oci_key_display_name"]])
            if "oci_defined_tags_jsonfile" in oci_params:
                cmd.extend(["--oci-defined-tags-jsonfile", oci_params["oci_defined_tags_jsonfile"]])
            if "oci_freeform_tags_jsonfile" in oci_params:
                cmd.extend(["--oci-freeform-tags-jsonfile", oci_params["oci_freeform_tags_jsonfile"]])
        
    else:
        raise ValueError(f"Unsupported OCI keys action: {action}")
    
    return cmd 